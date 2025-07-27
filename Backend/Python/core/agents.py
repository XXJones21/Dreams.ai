"""
Dreams.ai Agent Definitions and State

This module contains all agent functions and the State type used in the Dreams.ai pipeline.
It is the single source of truth for agent logic and state structure.
"""

import json
import re
import uuid
import os
from datetime import datetime, timezone
from typing import Annotated, Literal, TypedDict
from langgraph.graph.message import add_messages
from langgraph.channels import last_value
from core.imn_utils import write_imn, read_imn, create_imn_structure, validate_imn_structure, get_imn_filelock

# Import OptimizedLLM instead of Ollama
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'models'))
from optimized_llm import OptimizedLLM

# Load environment and initialize OptimizedLLM
from dotenv import load_dotenv
load_dotenv()

# Initialize OptimizedLLM with models directory
models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
llm = OptimizedLLM(models_dir=models_dir)

class State(TypedDict):
    messages: Annotated[list, add_messages]
    imn_filename: Annotated[str | None, last_value]
    id: Annotated[str | None, last_value]
    user_id: str | None
    carthir_memory: dict | None

class convert_prompt_to_imn(TypedDict):
    message_type: Literal["story_prompt", "dream_name", "initial_goal", "pitch"]


def convert_prompt_to_imn(state: State):
    """
    Creates the .imn file using Carthir's output in the state.
    """
    print(f"\n[DEBUG] ===== CONVERT_PROMPT_TO_IMN ANALYSIS =====")
    print(f"[DEBUG] State at start of convert_prompt_to_imn:")
    print(json.dumps(state, indent=2, default=str))
    
    # Detailed analysis of carthir_memory
    carthir_mem = state.get("carthir_memory", {})
    print(f"[DEBUG] carthir_memory type: {type(carthir_mem)}")
    print(f"[DEBUG] carthir_memory value: {carthir_mem}")
    
    if carthir_mem is None:
        print(f"[DEBUG] WARNING: carthir_memory is None!")
        carthir_mem = {}
    elif not isinstance(carthir_mem, dict):
        print(f"[DEBUG] WARNING: carthir_memory is not a dict, it's: {type(carthir_mem)}")
        carthir_mem = {}
    
    # Extract fields with detailed logging
    dream_name = carthir_mem.get("dream_name")
    story_prompt = carthir_mem.get("story_prompt")
    initial_goal = carthir_mem.get("initial_goal")
    pitch = carthir_mem.get("pitch")
    
    print(f"[DEBUG] Extracted fields:")
    print(f"[DEBUG]   dream_name: {repr(dream_name)} (type: {type(dream_name)})")
    print(f"[DEBUG]   story_prompt: {repr(story_prompt)} (type: {type(story_prompt)})")
    print(f"[DEBUG]   initial_goal: {repr(initial_goal)} (type: {type(initial_goal)})")
    print(f"[DEBUG]   pitch: {repr(pitch)} (type: {type(pitch)})")
    
    user_id = state.get("user_id", "user-uuid-placeholder")
    print(f"[DEBUG] user_id: {user_id}")

    if not state.get("id"):
        dream_id = str(uuid.uuid4())
        state["id"] = dream_id
        print(f"[DEBUG] Generated new dream_id: {dream_id}")
    else:
        dream_id = state["id"]
        print(f"[DEBUG] Using existing dream_id: {dream_id}")

    directory = os.path.join("..", "Dreams")
    filename = os.path.join(directory, f"{dream_id}.imn")
    print(f"[DEBUG] Target filename: {filename}")

    print(f"[DEBUG] Calling create_imn_structure with:")
    print(f"[DEBUG]   dream_id: {dream_id}")
    print(f"[DEBUG]   user_id: {user_id}")
    print(f"[DEBUG]   dream_name: {dream_name}")
    print(f"[DEBUG]   story_prompt: {story_prompt}")
    print(f"[DEBUG]   initial_goal: {initial_goal}")
    print(f"[DEBUG]   pitch: {pitch}")

    imn_data = create_imn_structure(
        dream_id=dream_id,
        user_id=user_id,
        dream_name=dream_name,
        story_prompt=story_prompt,
        initial_goal=initial_goal,
        pitch=pitch
    )
    
    print(f"[DEBUG] create_imn_structure returned: {type(imn_data)}")
    print(f"[DEBUG] IMN data keys: {list(imn_data.keys()) if isinstance(imn_data, dict) else 'Not a dict'}")

    imn_file_path = os.path.join(directory, f"{dream_id}.imn")
    print(f"[DEBUG] Writing to file: {imn_file_path}")
    
    # Use file lock for writing
    with get_imn_filelock(imn_file_path):
        write_imn(imn_data, directory)
    
    print(f"[DEBUG] ===== END CONVERT_PROMPT_TO_IMN ANALYSIS =====\n")
    return state


def Carthir(state: State):
    """
    Generates a film pitch based on the user's prompt and returns structured data.
    Stores its output in state['carthir_memory'] for persistent memory.
    """
    if state.get("carthir_memory"):
        print("[Carthir] Using existing memory.")
        return state

    last_message = state["messages"][-1]

    pitch_prompt = [
        {
            "role": "system",
            "content": (
                """
                You are a creative film pitch generator. Given the user's prompt, generate a compelling minute-long film pitch in first person perspective. 
                Respond ONLY with a valid JSON object with the following fields:\n
                - dream_name: A short, evocative title for the dream journey.\n
                - story_prompt: A one or two sentence summary of the narrative, suitable for use as a story prompt.\n
                - initial_goal: An initial goal or natural conclusion for the dream, as a single sentence.\n
                - pitch: The full, detailed pitch text (1-2 paragraphs, can include visual/audio notes).\n
                Example:\n
                {\n  \"dream_name\": \"Root & Whisper\",\n  \"story_prompt\": \"You are a child exploring a mysterious, ancient forest where the trees seem to whisper secrets.\",\n  \"initial_goal\": \"To understand what the woods are trying to tell you.\",\n  \"pitch\": \"(Full pitch text here...)\"\n}
                """
            )
        },
        {
            "role": "user",
            "content": last_message.content
        }
    ]

    # Use OptimizedLLM for Carthir (Creative Director)
    reply = llm.invoke("carthir", pitch_prompt)
    
    # COMPREHENSIVE LOGGING TO VALIDATE ASSUMPTIONS
    print(f"\n[DEBUG] ===== CARTHIR RESPONSE ANALYSIS =====")
    print(f"[DEBUG] Raw reply type: {type(reply)}")
    print(f"[DEBUG] Raw reply: {reply}")
    
    # Check if reply is a dict with metadata
    if isinstance(reply, dict):
        print(f"[DEBUG] Reply is a dict with keys: {list(reply.keys())}")
        if 'content' in reply:
            print(f"[DEBUG] Content field type: {type(reply['content'])}")
            print(f"[DEBUG] Content field value: {repr(reply['content'])}")
            print(f"[DEBUG] Content length: {len(reply['content']) if reply['content'] else 0}")
        if 'usage' in reply:
            print(f"[DEBUG] Usage field: {reply['usage']}")
        if 'inference_time' in reply:
            print(f"[DEBUG] Inference time: {reply['inference_time']}")
        if 'agent_name' in reply:
            print(f"[DEBUG] Agent name: {reply['agent_name']}")
    else:
        print(f"[DEBUG] Reply is not a dict, it's: {type(reply)}")
    
    print(f"[DEBUG] ===== END RESPONSE ANALYSIS =====\n")

    try:
        import json as _json
        
        # Handle the response format properly
        if isinstance(reply, dict) and 'content' in reply:
            content = reply['content'].strip()
        else:
            content = str(reply).strip()
            
        print(f"[DEBUG] Extracted content: {repr(content)}")
        print(f"[DEBUG] Content length after strip: {len(content)}")
        
        # Check if content looks like JSON
        if content.startswith('{') and content.endswith('}'):
            print(f"[DEBUG] Content appears to be JSON format")
        elif '```json' in content or '```' in content:
            print(f"[DEBUG] Content appears to have code blocks")
        else:
            print(f"[DEBUG] Content does not appear to be JSON format")
            print(f"[DEBUG] First 100 chars: {repr(content[:100])}")
            print(f"[DEBUG] Last 100 chars: {repr(content[-100:])}")
        
        # Use regex to extract JSON block inside code block, if present
        codeblock_match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", content)
        if codeblock_match:
            content = codeblock_match.group(1).strip()
            print(f"[DEBUG] Extracted JSON from code block: {repr(content)}")
        
        # Try to find JSON object boundaries if not already found
        if not (content.startswith('{') and content.endswith('}')):
            json_start = content.find('{')
            json_end = content.rfind('}')
            if json_start != -1 and json_end != -1 and json_end > json_start:
                content = content[json_start:json_end + 1]
                print(f"[DEBUG] Extracted JSON using boundaries: {repr(content)}")
        
        print(f"[DEBUG] Final content to parse: {repr(content)}")
        
        result = _json.loads(content)
        print(f"[DEBUG] Successfully parsed JSON: {result}")
        
        state["carthir_memory"] = {
            "dream_name": result.get("dream_name"),
            "story_prompt": result.get("story_prompt"),
            "initial_goal": result.get("initial_goal"),
            "pitch": result.get("pitch")
        }
        state["messages"] = [{"role": "assistant", "content": result.get("pitch", "")}] 
        print(f"\n[DEBUG] State at end of Carthir (before return):\n{json.dumps(state, indent=2, default=str)}\n")
        return state
    except Exception as e:
        print(f"[DEBUG] ===== JSON PARSING ERROR =====")
        print(f"[DEBUG] Error type: {type(e).__name__}")
        print(f"[DEBUG] Error message: {str(e)}")
        print(f"[DEBUG] Raw reply: {reply}")
        print(f"[DEBUG] ===== END ERROR ANALYSIS =====\n")
        
        state["carthir_memory"] = None
        if isinstance(reply, dict) and 'content' in reply:
            state["messages"] = [{"role": "assistant", "content": reply.get("content", "")}]
        else:
            state["messages"] = [{"role": "assistant", "content": str(reply)}]
        return state


def CarthirReview(state: State):
    """
    Enhanced Carthir review that generates director's vision for image generation.
    Uses persistent memory to ensure the visual matches the original creative vision.
    """
    print("\n[CarthirReview] --- DIRECTOR'S VISION REVIEW ---")
    carthir_mem = state.get("carthir_memory")

    dream_id = state.get("id")
    if not dream_id:
        print("No dream ID found in state.")
        return state
    imn_file_path = os.path.join("..", "Dreams", f"{dream_id}.imn")

    # Use file lock for reading
    with get_imn_filelock(imn_file_path):
        imn_data = read_imn(imn_file_path)
    if imn_data is None:
        print("Error reading .imn file")
        return state

    narnion_result = None
    if imn_data["in_production"]:
        narnion_result = imn_data["in_production"][-1]

    print(f"\n[CarthirReview] Carthir's Memory:")
    print(json.dumps(carthir_mem, indent=2, default=str))
    print(f"\n[CarthirReview] Narnion's Latest Scene:")
    print(json.dumps(narnion_result, indent=2, default=str))

    director_prompt = (
        f"Original Vision: {carthir_mem.get('pitch', '')}\n\n"
        f"Story Context: {narnion_result.get('scene_context', '') if narnion_result else 'No scene yet'}\n\n"
        f"As the Director, create a detailed visual prompt for the first frame that captures:\n"
        f"1. The mood and atmosphere from your original vision\n"
        f"2. The specific scene context from Narnion\n"
        f"3. Visual style and composition that matches your creative direction\n"
        f"4. First-person perspective that immerses the viewer\n\n"
        f"Respond with a JSON object:\n"
        f"{{\n"
        f"  \"director_vision\": \"Your creative vision for this frame\",\n"
        f"  \"image_prompt\": \"Detailed prompt for AI image generation\",\n"
        f"  \"visual_notes\": \"Specific style, lighting, composition notes\",\n"
        f"  \"approval_criteria\": \"What you're looking for in the final image\"\n"
        f"}}"
    )

    director_vision_prompt = [
        {
            "role": "system", 
            "content": "You are Carthir, the Director. You have a clear creative vision and ensure all visual elements align with your original concept."
        },
        {
            "role": "user", 
            "content": director_prompt
        }
    ]

    try:
        # Use OptimizedLLM for CarthirReview (Director's Vision)
        reply = llm.invoke("carthir", director_vision_prompt)
        content = reply.get("content", "").strip()
        codeblock_match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", content)
        if codeblock_match:
            content = codeblock_match.group(1).strip()
        content = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', content)
        json_start = content.find('{')
        json_end = content.rfind('}')
        if json_start != -1 and json_end != -1 and json_end > json_start:
            content = content[json_start:json_end + 1]
        director_vision = json.loads(content)
        required_fields = ["director_vision", "image_prompt", "visual_notes", "approval_criteria"]
        for field in required_fields:
            if field not in director_vision:
                director_vision[field] = f"Default {field.replace('_', ' ')}"
        imn_data["pre_production"]["director_vision"] = director_vision
        directory = os.path.join("..", "Dreams")
        # Use file lock for writing
        with get_imn_filelock(imn_file_path):
            write_imn(imn_data, directory)
        state["messages"] = [{"role": "assistant", "content": json.dumps(director_vision)}]
        print(f"[CarthirReview] Director's vision generated and stored.")
        print(f"Image Prompt: {director_vision.get('image_prompt', 'No prompt generated')}")
    except json.JSONDecodeError as e:
        print(f"JSON parsing error in CarthirReview: {e}")
        print(f"Attempted to parse: {content[:200]}...")
        fallback_vision = {
            "director_vision": f"Create a compelling first-person view of the scene",
            "image_prompt": f"First-person perspective of {narnion_result.get('scene_context', 'the dream world') if narnion_result else 'the scene'}",
            "visual_notes": "Use warm lighting and immersive composition",
            "approval_criteria": "Image should feel immersive and match the story context"
        }
        imn_data["pre_production"]["director_vision"] = fallback_vision
        directory = os.path.join("..", "Dreams")
        # Use file lock for writing
        with get_imn_filelock(imn_file_path):
            write_imn(imn_data, directory)
        state["messages"] = [{"role": "assistant", "content": json.dumps(fallback_vision)}]
        print(f"[CarthirReview] Using fallback director vision due to parsing error.")
    except Exception as e:
        print(f"Unexpected error in CarthirReview: {e}")
        print(f"Raw reply: {reply if 'reply' in locals() else 'No reply'}")
        # Fallback to basic prompt
        fallback_prompt = f"First-person view of {narnion_result.get('scene_context', 'the scene') if narnion_result else 'the dream world'}"
        state["messages"] = [{"role": "assistant", "content": fallback_prompt}]
    return state


def Narnion(state: State):
    """
    Narnion writes the next scene and suggested actions, appending to in_production.
    """
    dream_id = state.get("id")
    if not dream_id:
        print("No dream ID found in state.")
        return state
    imn_file_path = os.path.join("..", "Dreams", f"{dream_id}.imn")
    # Use file lock for reading
    with get_imn_filelock(imn_file_path):
        imn_data = read_imn(imn_file_path)
    if imn_data is None:
        print("Error reading .imn file")
        return state
    pre = imn_data["pre_production"]
    last_message = state["messages"][-1]
    narnion_prompt = last_message.content
    prompt = (
        f"Pitch: {narnion_prompt}\n\n"
        "Write a ten-second scene (no dialogue) for the next moment in the story, and suggest 2-3 actions the user could take next. "
        "Respond in JSON with:\n"
        "{\n"
        "  \"scene_context\": \"...\",\n"
        "  \"actions\": [\"...\", \"...\", \"...\"]\n"
        "}"
    )
    story_outline = [
        {"role": "system", "content": "You are Narnion, a master of interactive narrative."},
        {"role": "user", "content": prompt}
    ]
    # Use OptimizedLLM for Narnion (Storyteller)
    reply = llm.invoke("narnion", story_outline)
    try:
        import json as _json
        content = reply.get("content", "").strip()
        match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", content)
        if match:
            content = match.group(1).strip()
        result = _json.loads(content)
        scene_context = result.get("scene_context")
        actions = result.get("actions", [])
        new_scene = {
            "scene_id": len(imn_data["in_production"]) + 1,
            "frame_image": None,
            "timestamp": None,
            "scene_context": scene_context,
            "user_action": None,
            "tap_location": None,
            "object_tapped": None,
            "actions": actions
        }
        imn_data["in_production"].append(new_scene)
        directory = os.path.join("..", "Dreams")
        # Use file lock for writing
        with get_imn_filelock(imn_file_path):
            write_imn(imn_data, directory)
        print(f"[Narnion] Added new scene to in_production.")
    except Exception as e:
        print(f"Error parsing Narnion's response: {e}\nRaw reply: {reply}")
    return state


def Cenedril(state: State):
    """
    Cenedril uses the director's vision to create the first frame image prompt.
    """
    dream_id = state.get("id")
    if not dream_id:
        print("No dream ID found in state.")
        return state
    imn_file_path = os.path.join("..", "Dreams", f"{dream_id}.imn")
    # Use file lock for reading
    with get_imn_filelock(imn_file_path):
        imn_data = read_imn(imn_file_path)
    if imn_data is None:
        print("Error reading .imn file")
        return state
    director_vision = imn_data["pre_production"].get("director_vision")
    if director_vision:
        image_prompt = director_vision.get("image_prompt", "")
        visual_notes = director_vision.get("visual_notes", "")
        print(f"[Cenedril] Using director's vision for image generation.")
        print(f"Image Prompt: {image_prompt}")
        print(f"Visual Notes: {visual_notes}")
        imn_data["pre_production"]["first_frame_prompt"] = image_prompt
        imn_data["pre_production"]["visual_notes"] = visual_notes
        directory = os.path.join("..", "Dreams")
        # Use file lock for writing
        with get_imn_filelock(imn_file_path):
            write_imn(imn_data, directory)
        print(f"[Cenedril] Director's image prompt saved to .imn file.")
    else:
        print(f"[Cenedril] No director vision found, using fallback prompt generation.")
        last_message = state["messages"][-1]
        cenedril_prompt = last_message.content
        prompt = (
            f"Pitch: {cenedril_prompt}\n\n"
            "Write a vivid, first-person visual prompt for an AI image generator to create the very first frame of the dream. "
            "Describe what the dreamer sees as if they are experiencing it themselves, using 'I' perspective."
        )
        image_prompt = [
            {"role": "system", "content": "You are Cenedril, a master of visual storytelling."},
            {"role": "user", "content": prompt}
        ]
        try:
            # Use OptimizedLLM for Cenedril (Cinematographer)
            reply = llm.invoke("cenedril", image_prompt)
            first_frame_prompt = reply.get("content", "").strip()
            imn_data["pre_production"]["first_frame_prompt"] = first_frame_prompt
            directory = os.path.join("..", "Dreams")
            # Use file lock for writing
            with get_imn_filelock(imn_file_path):
                write_imn(imn_data, directory)
            print(f"[Cenedril] Fallback prompt generated and saved to .imn file.")
        except Exception as e:
            print(f"Error in Cenedril during fallback prompt generation: {e}")
            imn_data["pre_production"]["first_frame_prompt"] = "ERROR GENERATING PROMPT"
            directory = os.path.join("..", "Dreams")
            # Use file lock for writing
            with get_imn_filelock(imn_file_path):
                write_imn(imn_data, directory)
            state["messages"] = [{"role": "assistant", "content": f"Sorry, there was an error generating the initial frame prompt."}]
            return state
    return state


def print_imn_agent(state: State):
    """
    Reads and prints the .imn file using the filename from the state.
    """
    dream_id = state.get("id")
    if not dream_id:
        print("No dream ID found in state.")
        return state
    imn_file_path = os.path.join("..", "Dreams", f"{dream_id}.imn")
    # Use file lock for reading
    with get_imn_filelock(imn_file_path):
        imn_data = read_imn(imn_file_path)
    if imn_data is None:
        print("Error reading .imn file")
        return state
    print(f"\n[print_imn_agent] .imn file contents for '{imn_file_path}':\n{json.dumps(imn_data, indent=2)}\n")
    return state 