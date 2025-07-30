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
    NO FALLBACKS - Requires valid Carthir data or fails fast.
    """
    print(f"\n[DEBUG] State at start of convert_prompt_to_imn:\n{json.dumps(state, indent=2, default=str)}\n")
    
    # Validate Carthir memory exists
    carthir_mem = state.get("carthir_memory")
    
    if carthir_mem is None:
        raise ValueError("[convert_prompt_to_imn] CRITICAL ERROR: No carthir_memory found in state - Carthir agent failed to generate story data")
    
    # Validate all required Carthir fields
    required_fields = ["dream_name", "story_prompt", "initial_goal", "pitch"]
    missing_fields = [field for field in required_fields if not carthir_mem.get(field)]
    
    if missing_fields:
        raise ValueError(f"[convert_prompt_to_imn] CRITICAL ERROR: Missing required Carthir fields: {missing_fields} - Carthir agent generated incomplete data")
    
    # Extract validated Carthir data
    dream_name = carthir_mem["dream_name"]
    story_prompt = carthir_mem["story_prompt"]
    initial_goal = carthir_mem["initial_goal"]
    pitch = carthir_mem["pitch"]

    user_id = state.get("user_id", "user-uuid-placeholder")

    # Get dream ID from state (should already be set by PipelineInstance)
    dream_id = state.get("id")
    if not dream_id:
        raise ValueError("[convert_prompt_to_imn] CRITICAL ERROR: No dream ID found in state - pipeline initialization error")

    directory = os.path.join("..", "Dreams")

    # Create IMN structure with validated Carthir data
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
    
    print(f"[convert_prompt_to_imn] ✅ IMN file created successfully with validated Carthir data")
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

    # Validate LLM response
    if not reply or not reply.content:
        raise RuntimeError("[Carthir] CRITICAL ERROR: LLM failed to generate response - model or configuration issue")

    # Use centralized, robust JSON parsing - NO FALLBACKS
    parsed_data = parse_carthir_response(reply.content)
    
    if not parsed_data:
        raise ValueError(f"[Carthir] CRITICAL ERROR: Failed to parse LLM response as valid JSON - prompt or model issue\nRaw response: {reply.content}")
    
    # Validate all required fields exist
    required_fields = ["dream_name", "story_prompt", "initial_goal", "pitch"]
    missing_fields = [field for field in required_fields if not parsed_data.get(field)]
    
    if missing_fields:
        raise ValueError(f"[Carthir] CRITICAL ERROR: Parsed data missing required fields: {missing_fields}\nParsed data: {parsed_data}")
    
    # Successfully parsed and validated - store in state for IMN structure
    state["carthir_memory"] = parsed_data
    # Update messages to maintain compatibility
    state["messages"] = [{"role": "assistant", "content": parsed_data["pitch"]}]
    print(f"\n[DEBUG] State at end of Carthir (before return):\n{json.dumps(state, indent=2, default=str)}\n")
    print(f"[Carthir] ✅ Story data generated and validated successfully")
    return state


def CarthirReview(state: State) -> Command[Literal["carthir_supervisor"]]:
    """
    Enhanced Carthir review that generates director's vision for image generation.
    Uses persistent memory to ensure the visual matches the original creative vision.
    Now works with IMN-based context retrieval for resource-aware execution.
    NO FALLBACKS - Fails fast to identify pipeline issues.
    """
    print("\n[CarthirReview] --- DIRECTOR'S VISION REVIEW ---")
    
    dream_id = state.get("id")
    if not dream_id:
        raise ValueError("[CarthirReview] CRITICAL ERROR: No dream ID found in state - pipeline initialization failed")
    
    imn_file_path = os.path.join("..", "Dreams", f"{dream_id}.imn")

    # Use file lock for reading fresh context
    with get_imn_filelock(imn_file_path):
        imn_data = read_imn(imn_file_path)
    
    if imn_data is None:
        raise FileNotFoundError(f"[CarthirReview] CRITICAL ERROR: Cannot read IMN file: {imn_file_path}")

    # Validate pre_production data exists
    if "pre_production" not in imn_data:
        raise ValueError("[CarthirReview] CRITICAL ERROR: No pre_production data in IMN file - convert_prompt_to_imn failed")

    # Get context from IMN data
    carthir_mem = imn_data["pre_production"]
    narnion_result = None
    if imn_data["in_production"]:
        narnion_result = imn_data["in_production"][-1]

    print(f"\n[CarthirReview] Carthir's Memory:")
    print(json.dumps(carthir_mem, indent=2, default=str))
    print(f"\n[CarthirReview] Narnion's Latest Scene:")
    print(json.dumps(narnion_result, indent=2, default=str))

    # Validate required story context exists from Carthir
    story_prompt = carthir_mem.get("story_prompt")
    pitch = carthir_mem.get("pitch")
    
    if not story_prompt or not pitch:
        raise ValueError("[CarthirReview] CRITICAL ERROR: Missing story context from Carthir - story_prompt or pitch is empty")

    original_vision = pitch or f"A dream based on: {story_prompt}"

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

    # Generate director's vision - NO FALLBACKS
    reply = llm.invoke(director_vision_prompt)
    
    if not reply or not reply.content:
        raise RuntimeError("[CarthirReview] CRITICAL ERROR: LLM failed to generate response - model or configuration issue")
    
    # Use centralized, robust JSON parsing - NO FALLBACKS
    director_vision = parse_director_vision_response(reply.content, story_prompt)
    
    if not director_vision:
        raise ValueError(f"[CarthirReview] CRITICAL ERROR: Failed to parse director's vision response\nRaw response: {reply.content}")
    
    # Validate all required fields exist
    required_fields = ["director_vision", "image_prompt", "visual_notes", "approval_criteria"]
    missing_fields = [field for field in required_fields if not director_vision.get(field)]
    
    if missing_fields:
        raise ValueError(f"[CarthirReview] CRITICAL ERROR: Director vision missing required fields: {missing_fields}\nParsed data: {director_vision}")
    
    # Store in IMN structure
    imn_data["pre_production"]["director_vision"] = director_vision
    directory = os.path.join("..", "Dreams")
    
    # Use file lock for writing
    with get_imn_filelock(imn_file_path):
        write_imn(imn_data, directory)
    
    # Update state for next agent
    state["messages"] = [{"role": "assistant", "content": json.dumps(director_vision)}]
    
    print(f"[CarthirReview] ✅ Director's vision generated and validated successfully")
    print(f"Image Prompt: {director_vision['image_prompt']}")
    
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
    Cenedril: Master Cinematographer - Translates Director's Vision to Shot Composition
    
    Director-to-Artist Workflow:
    1. Receives director's creative brief (from CarthirReview)
    2. Analyzes story context (from Carthir & Narnion)
    3. Translates vision to technical shot composition
    4. Generates optimized SDXL prompt for image generation
    
    NO FALLBACKS - Fails fast to identify pipeline issues
    """
    print(f"[Cenedril] 🎬 Starting director-to-artist translation...")
    
    # Phase 1: Data Validation & Extraction (Director's Brief)
    dream_id = state.get("id")
    if not dream_id:
        raise ValueError("[Cenedril] CRITICAL ERROR: No dream ID found in state - pipeline initialization failed")
    
    imn_file_path = os.path.join("..", "Dreams", f"{dream_id}.imn")
    
    # Read IMN file with file lock
    with get_imn_filelock(imn_file_path):
        imn_data = read_imn(imn_file_path)
    
    if imn_data is None:
        raise FileNotFoundError(f"[Cenedril] CRITICAL ERROR: Cannot read IMN file: {imn_file_path}")
    
    # Validate Carthir data exists
    pre_production = imn_data.get("pre_production")
    if not pre_production:
        raise ValueError("[Cenedril] CRITICAL ERROR: No pre_production data found - Carthir pipeline failed")
    
    # Validate director's vision exists (from CarthirReview)
    director_vision = pre_production.get("director_vision")
    if not director_vision:
        raise ValueError("[Cenedril] CRITICAL ERROR: No director_vision found - CarthirReview failed to generate director's brief")
    
    # Validate required director components
    required_director_fields = ["director_vision", "image_prompt", "visual_notes", "approval_criteria"]
    missing_fields = [field for field in required_director_fields if not director_vision.get(field)]
    if missing_fields:
        raise ValueError(f"[Cenedril] CRITICAL ERROR: Missing director vision fields: {missing_fields} - CarthirReview incomplete")
    
    # Validate story context exists (from Carthir)
    story_prompt = pre_production.get("story_prompt")
    pitch = pre_production.get("pitch")
    dream_name = pre_production.get("dream_name")
    
    if not story_prompt or not pitch or not dream_name:
        raise ValueError("[Cenedril] CRITICAL ERROR: Missing story context - Carthir failed to generate complete story data")
    
    # Validate scene context exists (from Narnion)
    in_production = imn_data.get("in_production", [])
    if not in_production:
        raise ValueError("[Cenedril] CRITICAL ERROR: No scenes found - Narnion failed to generate scene context")
    
    latest_scene = in_production[-1].get("scene_context")
    if not latest_scene:
        raise ValueError("[Cenedril] CRITICAL ERROR: Latest scene has no context - Narnion scene generation failed")
    
    print(f"[Cenedril] ✅ All required data validated - proceeding with director-to-artist translation")
    
    # Phase 2: Director's Vision Analysis (Concept Art Brief)
    director_brief = {
        "creative_vision": director_vision["director_vision"],
        "visual_description": director_vision["image_prompt"],
        "style_notes": director_vision["visual_notes"],
        "approval_criteria": director_vision["approval_criteria"]
    }
    
    story_context = {
        "narrative": story_prompt,
        "pitch": pitch,
        "dream_title": dream_name,
        "current_scene": latest_scene
    }
    
    print(f"[Cenedril] 📋 Director's Brief: {director_brief['creative_vision'][:100]}...")
    print(f"[Cenedril] 📖 Story Context: {len(story_context['narrative'])} chars")
    print(f"[Cenedril] 🎭 Current Scene: {len(story_context['current_scene'])} chars")
    
    # Phase 3: Cinematographic Translation (Artist Interpretation)
    enhancement_prompt = f"""
You are Cenedril, master cinematographer translating a director's vision into a technical shot composition optimized for LoRA-enhanced SDXL generation.

DIRECTOR'S BRIEF:
Creative Vision: {director_brief['creative_vision']}
Visual Description: {director_brief['visual_description']}
Style Notes: {director_brief['style_notes']}

STORY CONTEXT:
Narrative: {story_context['narrative']}
Current Scene: {story_context['current_scene']}

CINEMATOGRAPHIC TRANSLATION TASK:
Convert the director's vision into a precise first-person perspective shot composition for LoRA-enhanced SDXL image generation.

TECHNICAL REQUIREMENTS:
1. CHARACTER PERSPECTIVE: Analyze who the protagonist is and their physical viewpoint
2. SPATIAL POSITIONING: Determine exact camera position based on character's eye level
3. VISUAL COMPOSITION: What they see, not what others see of them
4. POV TRIGGER WORDS: Must include LoRA activation keywords for first-person perspective
5. TECHNICAL SPECS: Camera settings, lighting, and professional photography tags

POV LORA REQUIREMENTS:
- MUST include at least 2 of these trigger words: "pov", "point of view", "subjective camera view", "1st person view"
- Place trigger words naturally at the beginning of the prompt
- Ensure they enhance rather than duplicate the perspective description

OUTPUT FORMAT:
Generate ONLY a clean, structured SDXL+LoRA prompt (45-60 words) with this structure:
[POV Trigger Words] + [Perspective Details] + [Environment] + [Camera/Technical] + [Quality Tags]

CRITICAL: No explanatory text, no prefixes, just the final prompt.
"""
    
    enhancement_request = [
        {
            "role": "system", 
            "content": "You are Cenedril, master cinematographer specializing in first-person perspective shot composition. You translate director's vision into precise technical prompts."
        },
        {
            "role": "user", 
            "content": enhancement_prompt
        }
    ]
    
    # Phase 4: Shot Composition Generation (Concept Art Creation)
    print(f"[Cenedril] 🎨 Generating shot composition from director's brief...")
    
    reply = llm.invoke(enhancement_request)
    if not reply or not reply.content:
        raise RuntimeError("[Cenedril] CRITICAL ERROR: LLM failed to generate response - model or prompt issue")
    
    enhanced_prompt = reply.content.strip()
    
    if not enhanced_prompt:
        raise RuntimeError("[Cenedril] CRITICAL ERROR: LLM returned empty response - prompt or model configuration issue")
    
    # Phase 5: Quality Assurance (Director Approval)
    word_count = len(enhanced_prompt.split())
    if word_count < 30 or word_count > 70:
        raise ValueError(f"[Cenedril] CRITICAL ERROR: Generated prompt has {word_count} words (expected 30-70) - LLM instruction following failed")
    
    # Check for common first-person perspective errors
    perspective_errors = []
    if "first-person pov of" in enhanced_prompt.lower():
        perspective_errors.append("Contains third-person description ('first-person POV of')")
    if "character" in enhanced_prompt.lower() and "viewpoint" in enhanced_prompt.lower():
        perspective_errors.append("Describes character instead of their view")
    
    if perspective_errors:
        raise ValueError(f"[Cenedril] CRITICAL ERROR: Perspective violations in generated prompt: {perspective_errors}")
    
    print(f"[Cenedril] ✅ Shot composition generated: {enhanced_prompt}")
    print(f"[Cenedril] 📏 Word count: {word_count} (optimal range)")
    print(f"[Cenedril] 🎯 First-person perspective: validated")
    
    # Store results in IMN structure
    imn_data["pre_production"]["original_director_prompt"] = director_brief["visual_description"]
    imn_data["pre_production"]["cenedril_shot_composition"] = enhanced_prompt
    imn_data["pre_production"]["cinematography_analysis"] = {
        "word_count": word_count,
        "director_brief_source": "CarthirReview",
        "story_context_source": "Carthir",
        "scene_context_source": "Narnion",
        "perspective_validated": True
    }
    
    directory = os.path.join("..", "Dreams")
    
    # Write updated IMN file with file lock
    with get_imn_filelock(imn_file_path):
        write_imn(imn_data, directory)
    
    print(f"[Cenedril] ✅ Shot composition saved to IMN file")
    print(f"[Cenedril] 🎬 Director-to-artist translation complete")
    
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


def CarthirSupervisor(state: State) -> Command[Literal["convert_prompt", "narnion", "carthir_review", "cenedril", "__end__"]]:
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
        
        # Validate Carthir succeeded before routing
        if not state.get("carthir_memory"):
            raise ValueError("[CarthirSupervisor] CRITICAL ERROR: Carthir failed to generate carthir_memory")
        
        print("[CarthirSupervisor] ✅ Story generated, routing to convert_prompt for IMN creation")
        print(f"[CarthirSupervisor] 📊 State has carthir_memory: {bool(state.get('carthir_memory'))}")
        
        return Command(
            goto="convert_prompt",
            update={
                "pipeline_step": "imn_created",
                "carthir_memory": state["carthir_memory"]  # Explicitly preserve carthir_memory
            }
        )
    
    elif pipeline_step == "imn_created":
        print("[CarthirSupervisor] 📁 IMN file created, routing to Narnion for scene creation")
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