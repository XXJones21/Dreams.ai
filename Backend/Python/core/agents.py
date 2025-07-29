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
from langgraph.types import Command
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
    pipeline_step: Annotated[str | None, last_value]

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

    # Get dream ID from state (should already be set by PipelineInstance)
    dream_id = state.get("id")
    if not dream_id:
        raise ValueError("[convert_prompt_to_imn] No dream ID found in state - pipeline initialization error")

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

    # Handle both old and new message formats
    messages = state.get("messages", [])
    if not messages:
        print("[Carthir] ❌ No messages found in state")
        return state
        
    last_message = messages[-1]
    
    # Extract content from either dict or object format
    if hasattr(last_message, 'content'):
        # LangChain message object
        prompt_content = last_message.content
    elif isinstance(last_message, dict):
        # Dictionary format
        prompt_content = last_message.get('content', '')
    else:
        # String format
        prompt_content = str(last_message)
    
    if not prompt_content:
        print("[Carthir] ❌ No content found in last message")
        return state

    pitch_prompt = [
        {
            "role": "system",
            "content": (
                """
                You are a creative film pitch generator. Given the user's prompt, generate a compelling minute-long film pitch in first person perspective.
                
                CRITICAL JSON FORMATTING RULES:
                1. Respond ONLY with valid JSON - no additional text before or after
                2. Use \\n for line breaks within strings (not actual newlines)
                3. Escape all quotes within strings using \"
                4. Keep all content on single lines within JSON values
                5. Do not use any control characters or unescaped newlines
                
                Respond with this exact JSON structure:
                {
                  "dream_name": "A short, evocative title",
                  "story_prompt": "A one-sentence summary of the narrative",
                  "initial_goal": "A single sentence describing the initial goal",
                  "pitch": "The full pitch as a single paragraph with \\n for line breaks"
                }
                
                Example format:
                {
                  "dream_name": "Root & Whisper",
                  "story_prompt": "You are a child exploring a mysterious, ancient forest where the trees seem to whisper secrets.",
                  "initial_goal": "To understand what the woods are trying to tell you.",
                  "pitch": "Opening shot of small hands touching ancient bark.\\n\\nCut to close-up of curious eyes looking up at towering trees.\\n\\nThe forest seems alive with whispered secrets only you can hear."
                }
                """
            )
        },
        {
            "role": "user",
            "content": prompt_content
        }
    ]

    reply = llm.invoke(pitch_prompt)
    print(f"\n[DEBUG] Raw LLM reply from Carthir:\n{reply.content}\n")

    # Use centralized, robust JSON parsing
    parsed_data = parse_carthir_response(reply.content)
    
    if parsed_data:
        # Successfully parsed - store in state for IMN structure
        state["carthir_memory"] = parsed_data
        # Update messages to maintain compatibility
        state["messages"] = [{"role": "assistant", "content": parsed_data["pitch"]}]
        print(f"\n[DEBUG] State at end of Carthir (before return):\n{json.dumps(state, indent=2, default=str)}\n")
        return state
    else:
        # Failed to parse - use fallback
        print(f"[Carthir] Failed to parse response, using fallback")
        state["carthir_memory"] = None
        state["messages"] = [{"role": "assistant", "content": reply.content}]
        return state


def CarthirReview(state: State) -> Command[Literal["carthir_supervisor"]]:
    """
    Enhanced Carthir review that generates director's vision for image generation.
    Uses persistent memory to ensure the visual matches the original creative vision.
    Now works with IMN-based context retrieval for resource-aware execution.
    """
    print("\n[CarthirReview] --- DIRECTOR'S VISION REVIEW ---")
    
    dream_id = state.get("id")
    if not dream_id:
        print("[CarthirReview] ❌ No dream ID found in state.")
        return state
    
    imn_file_path = os.path.join("..", "Dreams", f"{dream_id}.imn")

    # Use file lock for reading fresh context
    with get_imn_filelock(imn_file_path):
        imn_data = read_imn(imn_file_path)
    if imn_data is None:
        print("[CarthirReview] ❌ Error reading .imn file")
        return state

    # Get context from IMN data
    carthir_mem = imn_data["pre_production"]
    narnion_result = None
    if imn_data["in_production"]:
        narnion_result = imn_data["in_production"][-1]

    print(f"\n[CarthirReview] Carthir's Memory:")
    print(json.dumps(carthir_mem, indent=2, default=str))
    print(f"\n[CarthirReview] Narnion's Latest Scene:")
    print(json.dumps(narnion_result, indent=2, default=str))

    # Get story context for director vision
    story_prompt = carthir_mem.get("story_prompt", "")
    pitch = carthir_mem.get("pitch", "")
    
    if story_prompt:
        original_vision = pitch or f"A dream based on: {story_prompt}"
    else:
        print(f"[CarthirReview] ⚠️ Using fallback vision - no story context found")
        original_vision = "A compelling dream scene"

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
    return Command(goto="carthir_supervisor")


def Narnion(state: State) -> Command[Literal["carthir_supervisor"]]:
    """
    Narnion writes the next scene and suggested actions, appending to in_production.
    Now works with IMN-based context retrieval for resource-aware execution.
    """
    dream_id = state.get("id")
    if not dream_id:
        print("[Narnion] ❌ No dream ID found in state.")
        return state
    
    imn_file_path = os.path.join("..", "Dreams", f"{dream_id}.imn")
    
    # Use file lock for reading fresh context
    with get_imn_filelock(imn_file_path):
        imn_data = read_imn(imn_file_path)
    if imn_data is None:
        print("[Narnion] ❌ Error reading .imn file")
        return state
    
    # Get story context from IMN data instead of state messages
    pre = imn_data["pre_production"]
    story_prompt = pre.get("story_prompt", "")
    pitch = pre.get("pitch", "")
    
    # Use story prompt for context instead of last message
    narnion_prompt = story_prompt or pitch or "A mysterious adventure"
    
    prompt = (
        f"Story Context: {narnion_prompt}\n\n"
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
        
        print(f"[Narnion] ✅ Added new scene to in_production.")
    else:
        print(f"[Narnion] ❌ Failed to parse scene response - skipping scene creation")
        print(f"[Narnion] Raw reply: {reply.content}")
    
    return Command(goto="carthir_supervisor")


def Cenedril(state: State) -> Command[Literal["carthir_supervisor"]]:
    """
    Cenedril: Creates structured, optimized image prompts using director's vision.
    Now generates enhanced prompts with structured elements for superior image generation.
    """
    print(f"[Cenedril] 🎬 Starting image prompt generation...")
    
    dream_id = state.get("id")
    if not dream_id:
        print("[Cenedril] ❌ No dream ID found in state.")
        return state
    imn_file_path = os.path.join("..", "Dreams", f"{dream_id}.imn")
    # Use file lock for reading
    with get_imn_filelock(imn_file_path):
        imn_data = read_imn(imn_file_path)
    if imn_data is None:
        print("[Cenedril] ❌ Error reading .imn file")
        return state
    
    director_vision = imn_data["pre_production"].get("director_vision")
    if director_vision:
        image_prompt = director_vision.get("image_prompt", "")
        visual_notes = director_vision.get("visual_notes", "")
        director_vision_text = director_vision.get("director_vision", "")
        
        print(f"[Cenedril] 📝 Using director's vision for image generation.")
        print(f"[Cenedril] 📏 Original prompt length: {len(image_prompt)} characters")
        print(f"[Cenedril] 🎯 Original prompt: {image_prompt[:100]}...")

        
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
            
            print(f"[Cenedril] 📖 Story context: {len(story_prompt)} chars")
            print(f"[Cenedril] 🎭 Latest scene: {len(latest_scene)} chars")
            
            enhancement_prompt = f"""
You are Cenedril, master cinematographer specializing in SDXL image generation. Create a professional, structured prompt optimized for photorealistic results.

STORY CONTEXT:
Story: {story_prompt}
Scene: {latest_scene}
Vision: {director_vision_text}

SDXL PROMPT STRUCTURE - Generate ONLY the final prompt, no explanations:

[Subject/Character]: Detailed first-person perspective description
[Photography]: Camera model, lens, lighting style, composition
[Environment]: Setting, atmosphere, background elements  
[Style & Quality]: Art style, quality tags, material descriptions

EXAMPLES:
"First-person POV of a corgi on sandy beach, Canon EOS R5 with 85mm lens, golden hour lighting, shallow depth of field, warm sunlight filtering through palm trees, photorealistic, masterpiece, detailed textures, professional photography"

"Through corgi eyes: mystical forest clearing, Sony A7 III, 50mm f/1.8, soft natural lighting, dappled shadows, glowing mushrooms, moss-covered trees, cinematic composition, high quality, detailed, fantasy realism"

Generate a complete structured prompt (40-60 words) with professional photography elements:"""
            
            enhancement_request = [
                {"role": "system", "content": "You are Cenedril, a master cinematographer specializing in structured prompt engineering for AI image generation. You excel at extracting character details from story context."},
                {"role": "user", "content": enhancement_prompt}
            ]
            
            print(f"[Cenedril] 🚀 Generating enhanced structured prompt...")
            reply = llm.invoke(enhancement_request)
            raw_response = reply.content.strip()
            
            # Clean the prompt - remove any explanatory text or prefixes
            enhanced_prompt = raw_response
            
            # Remove common prefixes that LLM might add
            prefixes_to_remove = [
                "Here's a structured prompt:",
                "Here's the enhanced prompt:",
                "Generated prompt:",
                "Final prompt:",
                "Structured prompt:",
                "SDXL prompt:",
                "Here's a ",
                "This is a ",
                "The prompt is:",
                "\n"
            ]
            
            for prefix in prefixes_to_remove:
                if enhanced_prompt.startswith(prefix):
                    enhanced_prompt = enhanced_prompt[len(prefix):].strip()
            
            # Remove quotes if the entire prompt is wrapped in them
            if enhanced_prompt.startswith('"') and enhanced_prompt.endswith('"'):
                enhanced_prompt = enhanced_prompt[1:-1].strip()
                
            print(f"[Cenedril] 📨 LLM response length: {len(raw_response)} characters")
            print(f"[Cenedril] ✂️ Cleaned prompt: {enhanced_prompt}")
            
            # Store both original and enhanced prompts
            imn_data["pre_production"]["first_frame_prompt"] = image_prompt
            imn_data["pre_production"]["enhanced_image_prompt"] = enhanced_prompt
            imn_data["pre_production"]["visual_notes"] = visual_notes
            
            directory = os.path.join("..", "Dreams")
            # Use file lock for writing
            with get_imn_filelock(imn_file_path):
                write_imn(imn_data, directory)
            
            print(f"[Cenedril] ✅ Enhanced structured prompt generated and saved")
            print(f"[Cenedril] 📏 Final prompt length: {len(enhanced_prompt)} characters")
            print(f"[Cenedril] 🎯 SDXL optimization: {'✅ Professional structure' if 30 <= len(enhanced_prompt.split()) <= 80 else '⚠️ Consider adjusting length'}")
            
        except Exception as e:
            print(f"[Cenedril] ⚠️ Error generating enhanced prompt: {e}")
            print(f"[Cenedril] 🔧 Error type: {type(e).__name__}")
            
            # Create structured fallback prompt
            fallback_prompt = f"First-person POV, {image_prompt.lower()}, Canon EOS R5, 85mm lens, natural lighting, photorealistic, high quality, detailed"
            
            # Store fallback with structured format
            imn_data["pre_production"]["first_frame_prompt"] = image_prompt
            imn_data["pre_production"]["enhanced_image_prompt"] = fallback_prompt
            imn_data["pre_production"]["visual_notes"] = visual_notes
            imn_data["pre_production"]["enhancement_error"] = str(e)
            directory = os.path.join("..", "Dreams")
            # Use file lock for writing
            with get_imn_filelock(imn_file_path):
                write_imn(imn_data, directory)
            print(f"[Cenedril] 💾 Structured fallback prompt saved: {fallback_prompt}")
    else:
        print(f"[Cenedril] ⚠️ No director's vision found - skipping image prompt generation")
    
    return Command(goto="carthir_supervisor")


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


def CarthirSupervisor(state: State) -> Command[Literal["narnion", "carthir_review", "cenedril", "__end__"]]:
    """
    Carthir Supervisor: Manages the pipeline flow and routing decisions.
    Combines original Carthir story generation with supervisor routing logic.
    """
    pipeline_step = state.get("pipeline_step", "start")
    
    print(f"[CarthirSupervisor] Current pipeline step: {pipeline_step}")
    
    if pipeline_step == "start" or pipeline_step is None:
        # First run: Generate the story content (original Carthir logic)
        print("[CarthirSupervisor] 🎬 Starting story generation...")
        
        # Run original Carthir logic
        state = Carthir(state)
        
        # Update IMN file with rich Carthir content
        dream_id = state.get("id")
        if dream_id and state.get("carthir_memory"):
            carthir_mem = state["carthir_memory"]
            imn_file_path = os.path.join("..", "Dreams", f"{dream_id}.imn")
            
            # Read existing IMN file
            with get_imn_filelock(imn_file_path):
                imn_data = read_imn(imn_file_path)
            
            if imn_data:
                # Update with rich Carthir content
                imn_data["pre_production"]["dream_name"] = carthir_mem.get("dream_name", imn_data["pre_production"]["dream_name"])
                imn_data["pre_production"]["story_prompt"] = carthir_mem.get("story_prompt", imn_data["pre_production"]["story_prompt"])
                imn_data["pre_production"]["initial_goal"] = carthir_mem.get("initial_goal", imn_data["pre_production"]["initial_goal"])
                imn_data["pre_production"]["pitch"] = carthir_mem.get("pitch", imn_data["pre_production"]["pitch"])
                
                # Write updated IMN file
                directory = os.path.join("..", "Dreams")
                with get_imn_filelock(imn_file_path):
                    write_imn(imn_data, directory)
                
                print("[CarthirSupervisor] ✅ Updated IMN file with rich story content")
        
        print("[CarthirSupervisor] ✅ Story generated, routing to Narnion for scene creation")
        return Command(
            goto="narnion",
            update={"pipeline_step": "narnion_complete"}
        )
    
    elif pipeline_step == "narnion_complete":
        print("[CarthirSupervisor] 📝 Narnion completed, routing to CarthirReview for director's vision")
        return Command(
            goto="carthir_review",
            update={"pipeline_step": "review_complete"}
        )
    
    elif pipeline_step == "review_complete":
        print("[CarthirSupervisor] 🎭 CarthirReview completed, routing to Cenedril for image generation")
        return Command(
            goto="cenedril",
            update={"pipeline_step": "cenedril_complete"}
        )
    
    elif pipeline_step == "cenedril_complete":
        print("[CarthirSupervisor] 🎨 All agents completed, finishing pipeline")
        return Command(goto="__end__")
    
    else:
        print(f"[CarthirSupervisor] ⚠️ Unknown pipeline step: {pipeline_step}, ending")
        return Command(goto="__end__") 