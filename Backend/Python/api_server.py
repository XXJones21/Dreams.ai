from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from main import graph  # Import your LangGraph pipeline

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