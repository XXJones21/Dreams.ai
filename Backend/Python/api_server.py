import asyncio
import json
import os
import sys
import uuid

# Windows consoles default to cp1252; the pipeline's emoji prints would raise
# UnicodeEncodeError and 500 the request. Force UTF-8 stdout/stderr so the
# server doesn't depend on PYTHONIOENCODING being set at launch.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.pipeline_instance import PipelineInstance
from core.progress_broker import subscribe as subscribe_progress, unsubscribe as unsubscribe_progress

# MVP defaults: talk to ComfyUI directly on :8188. Override via env to point at
# the Rust supervisor (COMFY_TRANSPORT=rust, COMFY_BASE_URL=http://127.0.0.1:8765).
os.environ.setdefault("COMFY_TRANSPORT", "direct")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://sparkling-souffle-39b291.netlify.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DreamPrompt(BaseModel):
    prompt: str

# The pipeline agents write IMN files to ../Dreams (relative to the backend cwd
# Backend/Python). Read from the same place so GET /api/dreams/{id} resolves.
DREAMS_DIR = os.path.join("..", "Dreams")

def imn_to_dreamcard(imn_data):
    # Map .imn fields to DreamCard props, fill in defaults as needed
    return {
        "id": imn_data.get("id"),
        "title": imn_data.get("dream_name"),
        "excerpt": imn_data.get("story_prompt", "")[:120],  # or other logic
        "content": imn_data.get("pitch", ""),
        "creator": {
            "id": imn_data.get("user_id"),
            "name": "Dreamer",  # Replace with user lookup if available
            "avatar": None,
            "verified": False,
        },
        "engagement": {
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "views": 0,
        },
        "tags": [],
        "category": "",
        "emotion": "",
        "theme": "",
        "created_at": imn_data.get("created_at"),
        "is_trending": False,
        "is_featured": False,
        "similarity_score": None,
    }

@app.post("/api/dream")
async def create_dream(dream: DreamPrompt):
    dream_id = str(uuid.uuid4())
    state = {
        "id": dream_id,
        "messages": [{"role": "user", "content": dream.prompt}],
        "generate_video": True,
        "video_cinematic": False,
    }
    pipeline = PipelineInstance(state)
    # PipelineInstance.run is synchronous and CPU/GPU-bound. Run it off the
    # event loop so /api/dream/:id/progress WS subscribers stay responsive.
    result = await asyncio.to_thread(pipeline.run)
    # Carthir writes the story fields into the .imn (pre_production), not into
    # top-level state, so read them back to populate the response.
    pre = {}
    imn_path = os.path.join(DREAMS_DIR, f"{dream_id}.imn")
    if os.path.exists(imn_path):
        try:
            with open(imn_path, "r", encoding="utf-8") as f:
                pre = json.load(f).get("pre_production") or {}
        except (OSError, json.JSONDecodeError):
            pre = {}
    return {
        "id": dream_id,
        "dream_name": pre.get("dream_name") or result.get("dream_name"),
        "story_prompt": pre.get("story_prompt") or result.get("story_prompt"),
        "initial_goal": pre.get("initial_goal") or result.get("initial_goal"),
        "pitch": pre.get("pitch") or result.get("pitch"),
        "imn_filename": f"{dream_id}.imn",
    }

@app.get("/api/dreams/{dream_id}")
def get_dream(dream_id: str):
    filename = os.path.join(DREAMS_DIR, f"{dream_id}.imn")
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="Dream not found")
    with open(filename, "r") as f:
        imn_data = json.load(f)
    return imn_to_dreamcard(imn_data)


@app.websocket("/api/dream/{dream_id}/progress")
async def dream_progress(ws: WebSocket, dream_id: str):
    """Stream Cenedril image/video progress events for a dream.

    Events: ``{"stage": "submit"|"progress"|"completed"|"error"|"skipped", "kind": "image"|"video", ...}``
    The agent calls ``progress_broker.publish`` from a worker thread; this
    handler drains the per-subscription queue using ``asyncio.to_thread`` so
    the event loop stays responsive.
    """
    await ws.accept()
    q = subscribe_progress(dream_id)
    try:
        while True:
            try:
                event = await asyncio.wait_for(asyncio.to_thread(q.get, True, 30.0), timeout=35.0)
            except asyncio.TimeoutError:
                await ws.send_text(json.dumps({"stage": "heartbeat"}))
                continue
            await ws.send_text(json.dumps(event))
            if event.get("stage") in {"completed", "error"} and event.get("kind") == "video":
                break
            if event.get("stage") in {"completed", "error"} and event.get("kind") == "image":
                # Image done; keep socket open for the optional video stage.
                # Close after a short grace if no further events arrive.
                try:
                    follow = await asyncio.wait_for(
                        asyncio.to_thread(q.get, True, 2.0), timeout=3.0
                    )
                    await ws.send_text(json.dumps(follow))
                    if follow.get("stage") in {"completed", "error"} and follow.get("kind") == "video":
                        break
                except (asyncio.TimeoutError, Exception):
                    break
    except WebSocketDisconnect:
        pass
    finally:
        unsubscribe_progress(dream_id, q)