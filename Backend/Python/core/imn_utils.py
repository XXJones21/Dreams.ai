"""
Utility functions for .imn (Imagination) file operations
"""
import json
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional


def write_imn(data: dict, directory: str) -> bool:
    """
    Write the IMN structure to a file in the specified directory.
    
    Args:
        data: Dictionary containing the IMN data
        directory: Directory path where to save the file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        os.makedirs(directory, exist_ok=True)
        filename = os.path.join(directory, f"{data.get('pre_production', {}).get('id', 'unknown_id')}.imn")
        
        with open(filename, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        print(f"Successfully wrote .imn file: {filename}")
        return True
        
    except Exception as e:
        print(f"Error writing to .imn file: {e}")
        return False


def read_imn(filename: str) -> Optional[Dict[str, Any]]:
    """
    Read the IMN structure from a file and return as a dictionary.
    
    Args:
        filename: Path to the .imn file
        
    Returns:
        Optional[Dict[str, Any]]: The IMN data or None if error
    """
    try:
        with open(filename, "r", encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f'Error: .imn file not found at {filename}')
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing .imn file: {e}")
        return None
    except Exception as e:
        print(f"Error reading .imn file: {e}")
        return None


def create_imn_structure(dream_id: str, user_id: str, dream_name: str = None, 
                        story_prompt: str = None, initial_goal: str = None, 
                        pitch: str = None) -> Dict[str, Any]:
    """
    Create a new IMN file structure with basic pre-production data.
    
    Args:
        dream_id: Unique identifier for the dream
        user_id: ID of the user who created the dream
        dream_name: Name of the dream
        story_prompt: Initial story prompt
        initial_goal: Initial goal for the dream
        pitch: Creative pitch for the dream
        
    Returns:
        Dict[str, Any]: Complete IMN structure
    """
    created_at = datetime.now(timezone.utc).isoformat()
    
    return {
        "pre_production": {
            "id": dream_id,
            "user_id": user_id,
            "dream_name": dream_name or "untitled_dream",
            "story_prompt": story_prompt,
            "initial_goal": initial_goal,
            "pitch": pitch,
            "created_at": created_at
        },
        "in_production": [],
        "post_production": {}
    }


def validate_imn_structure(data: Dict[str, Any]) -> bool:
    """
    Validate that an IMN structure has the required fields.
    
    Args:
        data: IMN data to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    required_sections = ["pre_production", "in_production", "post_production"]
    required_pre_production = ["id", "user_id", "dream_name", "created_at"]
    
    # Check required sections exist
    for section in required_sections:
        if section not in data:
            print(f"Missing required section: {section}")
            return False
    
    # Check required pre_production fields
    pre_prod = data.get("pre_production", {})
    for field in required_pre_production:
        if field not in pre_prod:
            print(f"Missing required pre_production field: {field}")
            return False
    
    return True 