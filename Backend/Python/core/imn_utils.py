"""
Utility functions for .imn (Imagination) file operations
"""
import json
import os
import re
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from filelock import FileLock


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


def get_imn_filelock(imn_path: str):
    """
    Returns a FileLock object for the given IMN file path.
    Ensures atomic read/write operations across threads and processes.
    """
    lock_path = imn_path + ".lock"
    return FileLock(lock_path)


# =====================================================================
# ROBUST JSON PARSING FOR AGENTS - IMN Schema Aligned
# =====================================================================

def _clean_json_content(raw_content: str) -> str:
    """
    Clean and extract JSON content from LLM response.
    Handles common formatting issues like code blocks, extra characters, etc.
    """
    content = raw_content.strip()
    
    # Extract from code blocks if present
    codeblock_match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", content)
    if codeblock_match:
        content = codeblock_match.group(1).strip()
    
    # Remove control characters except newlines and tabs
    content = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', content)
    
    # Find JSON object boundaries
    json_start = content.find('{')
    json_end = content.rfind('}')
    
    if json_start != -1 and json_end != -1 and json_end > json_start:
        content = content[json_start:json_end + 1]
    
    # Handle common malformed JSON issues
    # Remove trailing parentheses that sometimes appear after JSON
    content = re.sub(r'\s*\)\s*$', '', content)
    
    return content


def parse_carthir_response(llm_response: str) -> Optional[Dict[str, str]]:
    """
    Parse Carthir's JSON response and validate against IMN pre_production schema.
    
    Expected schema:
    {
        "dream_name": str,
        "story_prompt": str, 
        "initial_goal": str,
        "pitch": str
    }
    
    Returns:
        Optional[Dict[str, str]]: Parsed and validated data, or None if parsing failed
    """
    try:
        content = _clean_json_content(llm_response)
        result = json.loads(content)
        
        # Validate required fields
        required_fields = ["dream_name", "story_prompt", "initial_goal", "pitch"]
        validated_result = {}
        
        for field in required_fields:
            value = result.get(field, "").strip()
            if not value:  # Empty or missing field
                print(f"[Carthir Parser] Missing or empty field: {field}")
                return None
            validated_result[field] = value
        
        print(f"[Carthir Parser] Successfully parsed response")
        return validated_result
        
    except json.JSONDecodeError as e:
        print(f"[Carthir Parser] JSON decode error: {e}")
        print(f"[Carthir Parser] Attempted to parse: {content[:200]}...")
        return None
    except Exception as e:
        print(f"[Carthir Parser] Unexpected error: {e}")
        return None


def parse_director_vision_response(llm_response: str) -> Dict[str, str]:
    """
    Parse CarthirReview's director vision response and validate against IMN schema.
    
    Expected schema:
    {
        "director_vision": str,
        "image_prompt": str,
        "visual_notes": str, 
        "approval_criteria": str
    }
    
    Returns:
        Dict[str, str]: Parsed data with fallbacks for missing fields
    """
    try:
        content = _clean_json_content(llm_response)
        result = json.loads(content)
        
        # Required fields with fallbacks
        required_fields = ["director_vision", "image_prompt", "visual_notes", "approval_criteria"]
        validated_result = {}
        
        for field in required_fields:
            value = result.get(field, "").strip()
            if value:
                validated_result[field] = value
            else:
                # Provide meaningful fallbacks aligned with IMN schema
                fallbacks = {
                    "director_vision": "Create a compelling first-person view of the scene",
                    "image_prompt": "First-person perspective of the dream scene",
                    "visual_notes": "Use warm lighting and immersive composition",
                    "approval_criteria": "Image should feel immersive and match the story context"
                }
                validated_result[field] = fallbacks[field]
                print(f"[Director Parser] Using fallback for {field}")
        
        print(f"[Director Parser] Successfully parsed director vision")
        return validated_result
        
    except json.JSONDecodeError as e:
        print(f"[Director Parser] JSON decode error: {e}")
        print(f"[Director Parser] Using complete fallback response")
        return {
            "director_vision": "Create a compelling first-person view of the scene",
            "image_prompt": "First-person perspective of the dream scene", 
            "visual_notes": "Use warm lighting and immersive composition",
            "approval_criteria": "Image should feel immersive and match the story context"
        }
    except Exception as e:
        print(f"[Director Parser] Unexpected error: {e}")
        return {
            "director_vision": "Create a compelling first-person view of the scene",
            "image_prompt": "First-person perspective of the dream scene",
            "visual_notes": "Use warm lighting and immersive composition", 
            "approval_criteria": "Image should feel immersive and match the story context"
        }


def parse_narnion_response(llm_response: str) -> Optional[Dict[str, Any]]:
    """
    Parse Narnion's scene response and validate against IMN in_production schema.
    
    Expected schema:
    {
        "scene_context": str,
        "actions": [str, str, str]
    }
    
    Returns:
        Optional[Dict[str, Any]]: Parsed scene data ready for IMN in_production, or None if failed
    """
    try:
        content = _clean_json_content(llm_response)
        result = json.loads(content)
        
        # Validate required fields
        scene_context = result.get("scene_context", "").strip()
        actions = result.get("actions", [])
        
        if not scene_context:
            print(f"[Narnion Parser] Missing scene_context")
            return None
            
        if not isinstance(actions, list) or len(actions) == 0:
            print(f"[Narnion Parser] Missing or invalid actions array")
            return None
        
        # Clean actions list
        cleaned_actions = [action.strip() for action in actions if isinstance(action, str) and action.strip()]
        
        if len(cleaned_actions) == 0:
            print(f"[Narnion Parser] No valid actions found")
            return None
        
        validated_result = {
            "scene_context": scene_context,
            "actions": cleaned_actions
        }
        
        print(f"[Narnion Parser] Successfully parsed scene with {len(cleaned_actions)} actions")
        return validated_result
        
    except json.JSONDecodeError as e:
        print(f"[Narnion Parser] JSON decode error: {e}")
        print(f"[Narnion Parser] Attempted to parse: {content[:200]}...")
        return None
    except Exception as e:
        print(f"[Narnion Parser] Unexpected error: {e}")
        return None


def create_scene_for_imn(scene_data: Dict[str, Any], scene_number: int) -> Dict[str, Any]:
    """
    Create a complete scene structure for IMN in_production section.
    
    Args:
        scene_data: Parsed scene data from parse_narnion_response
        scene_number: Sequential scene number
        
    Returns:
        Dict[str, Any]: Complete scene structure for IMN file
    """
    return {
        "scene_id": scene_number,
        "frame_image": None,  # To be filled by image generation
        "timestamp": None,    # To be filled when user interacts
        "scene_context": scene_data["scene_context"],
        "user_action": None,  # To be filled after user acts
        "tap_location": None, # To be filled after user acts
        "object_tapped": None,# To be filled after user acts
        "actions": scene_data["actions"]
    } 