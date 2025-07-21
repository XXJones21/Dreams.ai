"""
API routes for dream operations
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
import json

from core.imn_utils import read_imn, imn_to_dreamcard

router = APIRouter()

class DreamPrompt(BaseModel):
    prompt: str

class DreamResponse(BaseModel):
    dream_name: str
    story_prompt: str
    initial_goal: str
    pitch: str
    imn_filename: str

DREAMS_DIR = os.path.join("Backend", "Dreams")

def imn_to_dreamcard(imn_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert .imn data to DreamCard format for frontend consumption.
    
    Args:
        imn_data: Raw .imn file data
        
    Returns:
        Dict[str, Any]: Formatted dream card data
    """
    pre_prod = imn_data.get("pre_production", {})
    
    return {
        "id": pre_prod.get("id"),
        "title": pre_prod.get("dream_name"),
        "excerpt": pre_prod.get("story_prompt", "")[:120],
        "content": pre_prod.get("pitch", ""),
        "creator": {
            "id": pre_prod.get("user_id"),
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
        "created_at": pre_prod.get("created_at"),
        "is_trending": False,
        "is_featured": False,
        "similarity_score": None,
    }

@router.post("/dream", response_model=DreamResponse)
async def create_dream(dream: DreamPrompt):
    """
    Create a new dream from a user prompt.
    
    Args:
        dream: DreamPrompt containing the user's prompt
        
    Returns:
        DreamResponse: Generated dream information
    """
    # This will be implemented to call the LangGraph pipeline
    # For now, return a placeholder response
    return {
        "dream_name": "Sample Dream",
        "story_prompt": "A sample story prompt",
        "initial_goal": "Sample goal",
        "pitch": "Sample pitch",
        "imn_filename": "sample.imn"
    }

@router.get("/dreams/{dream_id}")
async def get_dream(dream_id: str):
    """
    Retrieve a dream by its ID.
    
    Args:
        dream_id: Unique identifier for the dream
        
    Returns:
        Dict[str, Any]: Dream card data
    """
    filename = os.path.join(DREAMS_DIR, f"{dream_id}.imn")
    
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="Dream not found")
    
    imn_data = read_imn(filename)
    if imn_data is None:
        raise HTTPException(status_code=500, detail="Error reading dream file")
    
    return imn_to_dreamcard(imn_data)

@router.get("/dreams")
async def list_dreams(limit: int = 10, offset: int = 0):
    """
    List available dreams with pagination.
    
    Args:
        limit: Maximum number of dreams to return
        offset: Number of dreams to skip
        
    Returns:
        Dict[str, Any]: List of dreams and pagination info
    """
    try:
        dreams = []
        dream_files = [f for f in os.listdir(DREAMS_DIR) if f.endswith('.imn')]
        
        # Sort by creation date (newest first)
        dream_files.sort(key=lambda x: os.path.getmtime(os.path.join(DREAMS_DIR, x)), reverse=True)
        
        # Apply pagination
        paginated_files = dream_files[offset:offset + limit]
        
        for filename in paginated_files:
            filepath = os.path.join(DREAMS_DIR, filename)
            imn_data = read_imn(filepath)
            if imn_data:
                dreams.append(imn_to_dreamcard(imn_data))
        
        return {
            "dreams": dreams,
            "total": len(dream_files),
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < len(dream_files)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing dreams: {str(e)}") 