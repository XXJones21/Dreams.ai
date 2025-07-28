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
from core.imn_utils import (
    write_imn, read_imn, create_imn_structure, validate_imn_structure, get_imn_filelock,
    parse_carthir_response, parse_director_vision_response, parse_narnion_response, create_scene_for_imn
)
from langchain_community.chat_models import ChatLlamaCpp

# Load environment and initialize LLM (if needed)
from dotenv import load_dotenv
load_dotenv()

# Initialize the local GGUF model with optimized settings for performance
# Detect if running in Flask server environment and adjust accordingly
import threading
import os

# Check if we're running in a multi-threaded environment (Flask)
is_flask_server = threading.active_count() > 1 or os.environ.get('FLASK_RUN_PORT') is not None

# Optimize threads for environment
if is_flask_server:
    # Conservative threading for Flask server to avoid contention
    optimal_threads = min(8, os.cpu_count() // 2)
    print(f"[GGUF] Detected Flask server environment - using {optimal_threads} threads")
else:
    # Aggressive threading for CLI/standalone
    optimal_threads = min(16, os.cpu_count())
    print(f"[GGUF] Detected CLI environment - using {optimal_threads} threads")

llm = ChatLlamaCpp(
    model_path="models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
    temperature=0.7,
    max_tokens=512,  # Further reduced for faster generation
    top_p=0.9,
    verbose=False,  # Disable verbose for speed
    n_ctx=1024,  # Further reduced context window for speed
    n_threads=optimal_threads,  # Dynamic thread allocation
    n_batch=1024,  # Larger batch for GPU processing
    use_mmap=True,  # Memory mapping for faster loading
    use_mlock=False,  # Disable memory locking to allow OS management
    f16_kv=True,  # Use half precision for key-value cache to save memory
    n_gpu_layers=35,  # Offload layers to GPU (try max layers first)
)

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
    Handles both successful and failed Carthir parsing with graceful fallbacks.
    """
    print(f"\n[DEBUG] State at start of convert_prompt_to_imn:\n{json.dumps(state, indent=2, default=str)}\n")
    
    # Handle both successful parsing and None fallback from Carthir
    carthir_mem = state.get("carthir_memory")
    
    if carthir_mem is None:
        # Carthir parsing failed - create fallback dream data
        original_prompt = ""
        if state.get("messages") and len(state["messages"]) > 0:
            first_message = state["messages"][0]
            if hasattr(first_message, 'content'):
                original_prompt = first_message.content
            elif isinstance(first_message, dict):
                original_prompt = first_message.get("content", "")
        
        print(f"[convert_prompt_to_imn] Carthir parsing failed, using fallback data")
        dream_name = f"Dream: {original_prompt[:30]}..." if original_prompt else "Untitled Dream"
        story_prompt = original_prompt or "A mysterious dream adventure"
        initial_goal = "To explore and discover the dream's meaning"
        pitch = f"A dream journey based on: {original_prompt}" if original_prompt else "A mysterious dream adventure"
    else:
        # Carthir parsing succeeded - use the parsed data
        dream_name = carthir_mem.get("dream_name")
        story_prompt = carthir_mem.get("story_prompt")
        initial_goal = carthir_mem.get("initial_goal")
        pitch = carthir_mem.get("pitch")

    user_id = state.get("user_id", "user-uuid-placeholder")

    # Generate dream ID if not present
    if not state.get("id"):
        dream_id = str(uuid.uuid4())
        state["id"] = dream_id
    else:
        dream_id = state["id"]

    directory = os.path.join("..", "Dreams")

    # Create IMN structure with available data
    imn_data = create_imn_structure(
        dream_id=dream_id,
        user_id=user_id,
        dream_name=dream_name,
        story_prompt=story_prompt,
        initial_goal=initial_goal,
        pitch=pitch
    )

    imn_file_path = os.path.join(directory, f"{dream_id}.imn")
    # Use file lock for writing
    with get_imn_filelock(imn_file_path):
        write_imn(imn_data, directory)
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

    reply = llm.invoke(pitch_prompt)
    print(f"\n[DEBUG] Raw LLM reply from Carthir:\n{reply.content}\n")

    # Use centralized, robust JSON parsing
    parsed_data = parse_carthir_response(reply.content)
    
    if parsed_data:
        # Successfully parsed - store in state for IMN structure
        state["carthir_memory"] = parsed_data
        state["messages"] = [{"role": "assistant", "content": parsed_data["pitch"]}]
        print(f"\n[DEBUG] State at end of Carthir (before return):\n{json.dumps(state, indent=2, default=str)}\n")
        return state
    else:
        # Failed to parse - use fallback
        print(f"[Carthir] Failed to parse response, using fallback")
        state["carthir_memory"] = None
        state["messages"] = [{"role": "assistant", "content": reply.content}]
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

    # Handle both successful and failed Carthir parsing
    if carthir_mem is None:
        print(f"[CarthirReview] Carthir memory is None, using fallback vision")
        original_vision = "A compelling dream scene"
        # Try to get the original prompt from IMN data
        pre_prod = imn_data.get("pre_production", {})
        story_prompt = pre_prod.get("story_prompt", "")
        if story_prompt:
            original_vision = f"A dream based on: {story_prompt}"
    else:
        original_vision = carthir_mem.get('pitch', 'A compelling dream scene')

    director_prompt = (
        f"Original Vision: {original_vision}\n\n"
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

    # Get story context for better fallback generation
    story_context = imn_data.get("pre_production", {}).get("story_prompt", "")
    
    try:
        reply = llm.invoke(director_vision_prompt)
        
        # Use centralized, robust JSON parsing with story-specific fallbacks
        director_vision = parse_director_vision_response(reply.content, story_context)
        
        # Store in IMN structure
        imn_data["pre_production"]["director_vision"] = director_vision
        directory = os.path.join("..", "Dreams")
        
        # Use file lock for writing
        with get_imn_filelock(imn_file_path):
            write_imn(imn_data, directory)
        
        # Update state for next agent
        state["messages"] = [{"role": "assistant", "content": json.dumps(director_vision)}]
        
        print(f"[CarthirReview] Director's vision generated and stored.")
        print(f"Image Prompt: {director_vision.get('image_prompt', 'No prompt generated')}")
        
    except Exception as e:
        print(f"[CarthirReview] Unexpected error: {e}")
        # Even if LLM call fails, use robust fallback with story context
        fallback_vision = parse_director_vision_response("", story_context)  # Pass story context for better fallback
        imn_data["pre_production"]["director_vision"] = fallback_vision
        directory = os.path.join("..", "Dreams")
        
        with get_imn_filelock(imn_file_path):
            write_imn(imn_data, directory)
        
        state["messages"] = [{"role": "assistant", "content": json.dumps(fallback_vision)}]
        print(f"[CarthirReview] Using story-specific fallback due to LLM error.")
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
    reply = llm.invoke(story_outline)
    
    # Use centralized, robust JSON parsing
    parsed_scene = parse_narnion_response(reply.content)
    
    if parsed_scene:
        # Successfully parsed - create proper IMN scene structure
        scene_number = len(imn_data["in_production"]) + 1
        new_scene = create_scene_for_imn(parsed_scene, scene_number)
        
        # Add to IMN structure
        imn_data["in_production"].append(new_scene)
        directory = os.path.join("..", "Dreams")
        
        # Use file lock for writing
        with get_imn_filelock(imn_file_path):
            write_imn(imn_data, directory)
        
        print(f"[Narnion] Added new scene to in_production.")
    else:
        print(f"[Narnion] Failed to parse scene response - skipping scene creation")
        print(f"[Narnion] Raw reply: {reply.content}")
    return state


def Cenedril(state: State):
    """
    Cenedril: Creates structured, optimized image prompts using director's vision.
    Now generates enhanced prompts with structured elements for superior image generation.
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
        director_vision_text = director_vision.get("director_vision", "")
        
        print(f"[Cenedril] Using director's vision for image generation.")
        print(f"Image Prompt: {image_prompt}")
        print(f"Visual Notes: {visual_notes}")
        
        # Create enhanced structured prompt using LLM
        try:
            # Get additional story context for character details
            story_prompt = imn_data["pre_production"].get("story_prompt", "")
            pitch = imn_data["pre_production"].get("pitch", "")
            
            # Get latest scene context if available
            in_production = imn_data.get("in_production", [])
            latest_scene = ""
            if in_production:
                latest_scene = in_production[-1].get("scene_context", "")
            
            enhancement_prompt = f"""
You are Cenedril, the master cinematographer and SDXL optimization expert. Transform this basic image prompt into a precision-engineered, PHOTOREALISTIC first-person perspective prompt for Dreams.ai.

FULL STORY CONTEXT:
Story Prompt: {story_prompt}
Pitch: {pitch}
Latest Scene: {latest_scene}

DIRECTOR'S VISION:
Original Director's Vision: {director_vision_text}
Basic Image Prompt: {image_prompt}  
Visual Notes: {visual_notes}

CRITICAL INSTRUCTIONS FOR DREAMS.AI FIRST-PERSON PERSPECTIVES:
1. ANALYZE story context to identify character details (species, role, situation)
2. Generate what the CHARACTER SEES through their own eyes, NOT a portrait of them
3. Use PHOTOREALISTIC professional photography style - no fantasy/artistic rendering
4. Focus on realistic environments, lighting, and objects the character would actually see
5. If character is a corgi, show what a corgi-height perspective would see (lower viewpoint)

Create a structured prompt with these exact sections:

**MAIN SUBJECT & COMPOSITION:**
[First-person POV description: "Through my eyes as [character], I see..." Focus on what's IN FRONT of the character, not the character themselves. Include realistic environmental details at appropriate height/perspective for the character species.]

**VISUAL STYLE & TECHNIQUE:**
[ALWAYS: Professional photography, photorealistic, DSLR camera, natural lighting, realistic textures, sharp focus, high resolution]

**LIGHTING & ATMOSPHERE:**
[Realistic lighting only: natural sunlight, indoor lighting, streetlights, etc. NO fantasy lighting, NO mystical glows, NO magical elements]

**TECHNICAL PARAMETERS:**
[SDXL photorealism: masterpiece, best quality, ultra detailed, 8K resolution, professional photography, sharp focus, realistic, natural colors]

**NEGATIVE PROMPT:**
[Fantasy prevention: drawing, painting, cartoon, anime, fantasy, mystical, magical, artistic rendering, illustration, sketch, + standard quality controls: low quality, blurry, distorted, deformed, watermark, signature, text]

**COMPOSITION NOTES:**
[Camera settings: realistic depth of field, natural perspective, documentary style, environmental storytelling through realistic objects and settings]

EXAMPLE FOR CORGI CHARACTER: 
"Through my eyes as Finley the corgi, I see the wooden deck planks of the sailboat stretching out in front of me. The grain of the weathered wood is clearly visible, and I can see the metal cleats and rope coils at my eye level. Beyond the deck railing, the ocean extends to the horizon..."

Remember: Generate what the character SEES, not what they LOOK LIKE. Focus on photorealistic environments from their unique perspective.
"""
            
            enhancement_request = [
                {"role": "system", "content": "You are Cenedril, a master cinematographer specializing in structured prompt engineering for AI image generation. You excel at extracting character details from story context."},
                {"role": "user", "content": enhancement_prompt}
            ]
            
            print(f"[Cenedril] 🚀 Generating enhanced structured prompt...")
            reply = llm.invoke(enhancement_request)
            enhanced_prompt = reply.content.strip()
            
            # Store both original and enhanced prompts
            imn_data["pre_production"]["first_frame_prompt"] = image_prompt
            imn_data["pre_production"]["enhanced_image_prompt"] = enhanced_prompt
            imn_data["pre_production"]["visual_notes"] = visual_notes
            
            directory = os.path.join("..", "Dreams")
            # Use file lock for writing
            with get_imn_filelock(imn_file_path):
                write_imn(imn_data, directory)
            
            print(f"[Cenedril] ✅ Enhanced structured prompt generated and saved")
            print(f"[Cenedril] 📏 Enhanced prompt length: {len(enhanced_prompt)} characters")
            print(f"[Cenedril] 🎯 Structured elements optimized for SDXL")
            
        except Exception as e:
            print(f"[Cenedril] ⚠️ Error generating enhanced prompt: {e}")
            # Fallback to basic prompt storage
            imn_data["pre_production"]["first_frame_prompt"] = image_prompt
            imn_data["pre_production"]["visual_notes"] = visual_notes
            imn_data["pre_production"]["enhancement_error"] = str(e)
            directory = os.path.join("..", "Dreams")
            # Use file lock for writing
            with get_imn_filelock(imn_file_path):
                write_imn(imn_data, directory)
            print(f"[Cenedril] 💾 Basic prompt saved despite enhancement error")
            
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
            reply = llm.invoke(image_prompt)
            first_frame_prompt = reply.content.strip()
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