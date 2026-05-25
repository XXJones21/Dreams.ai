import asyncio
import json
import os
import queue
import sys
import threading
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
from core.progress_broker import subscribe as subscribe_progress, unsubscribe as unsubscribe_progress, publish as publish_progress

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
    # Carthir writes the story fields into pre_production; top-level is usually
    # empty (-> "Untitled dream"), so prefer pre_production with a top fallback.
    pre = imn_data.get("pre_production") or {}
    pp = imn_data.get("post_production") or {}
    _img = pp.get("image_generation") or {}
    _vid = pp.get("video_generation") or {}
    _name = imn_data.get("dream_name") or pre.get("dream_name") or ""
    _story = imn_data.get("story_prompt") or pre.get("story_prompt") or ""
    _pitch = imn_data.get("pitch") or pre.get("pitch") or ""
    return {
        "id": imn_data.get("id"),
        "title": _name,
        "excerpt": _story[:120],
        "content": _pitch,
        # Progressive media: the .imn is the source of truth for assets, so the
        # client can show the first image / video even if it missed the live WS
        # event (e.g. navigated in after the image stage finished).
        "image_url": _img.get("asset_url"),
        "image_status": _img.get("status"),
        "video_url": _vid.get("asset_url"),
        "video_status": _vid.get("status"),
        "story_prompt": _story,
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

# Single-flight guard: one dream pipeline at a time (the 16 GB GPU can't run two
# without thrashing). A concurrent request gets 409 instead of contending.
_gen_lock = threading.Lock()
_active_dream = {"id": None}


def _run_pipeline_bg(state: dict, dream_id: str) -> None:
    try:
        PipelineInstance(state).run()
    except Exception as exc:  # surface pipeline-level failure to WS subscribers
        try:
            publish_progress(dream_id, {"stage": "error", "kind": "pipeline", "message": str(exc)})
        except Exception:
            pass
    finally:
        _active_dream["id"] = None
        _gen_lock.release()


@app.post("/api/dream")
async def create_dream(dream: DreamPrompt):
    """Start the dream pipeline and return its id IMMEDIATELY.

    The pipeline (narrative → image → video) runs for minutes; running it
    synchronously blocked the HTTP response long enough to hit proxy/tunnel
    timeouts (Cloudflare 524) on phone testing. Instead, kick it off on a
    background thread and return the id so the client can navigate to the dream
    page and stream progress over the WS — and progressively show the title,
    story, and first image while the video renders.
    """
    if not _gen_lock.acquire(blocking=False):
        raise HTTPException(
            status_code=409,
            detail=f"A dream is already generating ({_active_dream['id']}). One at a time on this GPU.",
        )
    dream_id = str(uuid.uuid4())
    _active_dream["id"] = dream_id
    state = {
        "id": dream_id,
        "messages": [{"role": "user", "content": dream.prompt}],
        "generate_video": True,
        "video_cinematic": False,
    }
    threading.Thread(
        target=_run_pipeline_bg, args=(state, dream_id), daemon=True, name=f"dream-{dream_id[:8]}"
    ).start()
    return {"id": dream_id, "status": "started"}

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
            except (asyncio.TimeoutError, queue.Empty):
                # No event within the window (normal during long renders) — send a
                # heartbeat and keep the socket open instead of erroring out.
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