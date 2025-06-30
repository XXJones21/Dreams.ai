from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from main import graph  # Import your LangGraph pipeline
import os
import json

app = FastAPI()

# Allow CORS for your Netlify frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://sparkling-souffle-39b291.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DreamPrompt(BaseModel):
    prompt: str

DREAMS_DIR = os.path.join("Backend", "Dreams")

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
    state = {"messages": [{"role": "user", "content": dream.prompt}]}
    result = graph.invoke(state)
    return {
        "dream_name": result.get("dream_name"),
        "story_prompt": result.get("story_prompt"),
        "initial_goal": result.get("initial_goal"),
        "pitch": result.get("pitch"),
        "imn_filename": result.get("imn_filename"),
    }

@app.get("/api/dreams/{dream_id}")
def get_dream(dream_id: str):
    filename = os.path.join(DREAMS_DIR, f"{dream_id}.imn")
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="Dream not found")
    with open(filename, "r") as f:
        imn_data = json.load(f)
    return imn_to_dreamcard(imn_data)