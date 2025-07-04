import json
import re
import uuid
import os
from datetime import datetime

from dotenv import load_dotenv
from typing import Annotated, Literal, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI


load_dotenv()

llm = ChatOpenAI(model="gemma3:12b", base_url="http://10.1.95.9:11434/v1")


class State(TypedDict):
    messages: Annotated[list, add_messages]
    dream_name: str | None
    story_prompt: str | None
    initial_goal: str | None
    pitch: str | None
    imn_filename: str | None
    id: str | None
    user_id: str | None


class convert_prompt_to_imn(TypedDict):

    message_type: Literal["story_prompt", "dream_name", "initial_goal", "pitch"]


def write_imn(data: dict, directory: str):
    """
    Write the IMN structure to a file in the specified directory.
    """
    os.makedirs(directory, exist_ok=True)
    # Get the id from the new schema location
    dream_id = data.get("pre_production", {}).get("id", "unknown_id")
    filename = os.path.join(directory, f"{dream_id}.imn")
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Successfully wrote .imn file: {filename}")
    except Exception as e:
        print(f"Error writing to .imn file: {e}")


### Converts a user's inital prompt into a basic .imn file stucture
def convert_prompt_to_imn(state: State):
    """
    Creates the .imn file using Carthir's output in the state.
    """
    print(f"\n[DEBUG] State at start of convert_prompt_to_imn:\n{json.dumps(state, indent=2, default=str)}\n")
    dream_name = state.get("dream_name")
    story_prompt = state.get("story_prompt")
    initial_goal = state.get("initial_goal")
    pitch = state.get("pitch")
    user_id = state.get("user_id", "user-uuid-placeholder")  # Replace with real user_id logic

    dream_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat() + "Z"

    imn_data = {
        "pre_production": {
             "id": dream_id,
             "user_id": user_id,
             "dream_name": dream_name or "untitled_dream",
             "story_prompt": story_prompt,
             "initial_goal": initial_goal,
             "pitch": pitch,
             "created_at": created_at
        },
        "in_production":[],
        "post_production": {}
    }

    directory = os.path.join("Backend", "Dreams")
    write_imn(imn_data, directory)

    # Pass along the state, adding the filename and IDs
    state["imn_filename"] = os.path.join(directory, f"{dream_id}.imn")
    state["id"] = dream_id
    state["user_id"] = user_id

    # Remove top-level keys that cause merge conflicts in parallel steps
    for k in ["dream_name", "story_prompt", "initial_goal", "pitch"]:
        state.pop(k, None)
    return state


def Carthir(state: State):
    """
    Generates a film pitch based on the user's prompt and returns structured data.
    Stores its output in state['carthir_memory'] for persistent memory.
    """
    # If memory exists, skip re-generation (could be used for review step)
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

    # Debug: print the raw LLM reply before any parsing
    print(f"\n[DEBUG] Raw LLM reply from Carthir:\n{reply.content}\n")

    # Try to parse the reply as JSON, robustly extracting the JSON block if present
    try:
        import json as _json
        content = reply.content.strip()
        # Use regex to extract JSON block inside code block, if present
        codeblock_match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", content)
        if codeblock_match:
            content = codeblock_match.group(1).strip()
        result = _json.loads(content)
        # Update and return the state with new fields
        state.update({
            "dream_name": result.get("dream_name"),
            "story_prompt": result.get("story_prompt"),
            "initial_goal": result.get("initial_goal"),
            "pitch": result.get("pitch"),
            "messages": [{"role": "assistant", "content": result.get("pitch", "")}]
        })
        # Store Carthir's memory
        state["carthir_memory"] = {
            "dream_name": result.get("dream_name"),
            "story_prompt": result.get("story_prompt"),
            "initial_goal": result.get("initial_goal"),
            "pitch": result.get("pitch")
        }
        print(f"\n[DEBUG] State at end of Carthir (before return):\n{json.dumps(state, indent=2, default=str)}\n")
        return state
    except Exception as e:
        print(f"Error parsing Carthir's response as JSON: {e}\nRaw reply: {reply.content}")
        state.update({
            "dream_name": None,
            "story_prompt": None,
            "initial_goal": None,
            "pitch": reply.content,
            "messages": [{"role": "assistant", "content": reply.content}]
        })
        return state


def CarthirReview(state: State):
    """
    Carthir reviews the outputs from Narnion and Cenedril using its persistent memory.
    Outputs a verification/critique of each agent's result for testing.
    """
    print("\n[CarthirReview] --- AGENT REVIEW STEP ---")
    carthir_mem = state.get("carthir_memory")
    filename = state.get("imn_filename")
    if not filename:
        print("No .imn filename found in state.")
        return state
    imn_data = read_imn(filename)
    narnion_result = None
    cenedril_result = None
    # Get Narnion's latest scene (if any)
    if imn_data["in_production"]:
        narnion_result = imn_data["in_production"][-1]
    # Get Cenedril's first frame prompt
    cenedril_result = imn_data["pre_production"].get("first_frame_prompt")

    print("\n[CarthirReview] Carthir's Memory:")
    print(json.dumps(carthir_mem, indent=2, default=str))
    print("\n[CarthirReview] Narnion's Latest Scene:")
    print(json.dumps(narnion_result, indent=2, default=str))
    print("\n[CarthirReview] Cenedril's First Frame Prompt:")
    print(json.dumps(cenedril_result, indent=2, default=str))

    # Simple verification/critique logic (could be expanded)
    print("\n[CarthirReview] VERIFICATION TEST:")
    if carthir_mem and narnion_result and cenedril_result:
        print("All agent outputs present. Review successful!")
    else:
        print("Missing output from one or more agents.")
    return state


def Narnion(state: State):
    """
    Narnion writes the next scene and suggested actions, appending to in_production.
    """
    filename = state.get("imn_filename")
    if not filename:
        print("No .imn filename found in state.")
        return state
    imn_data = read_imn(filename)
    pre = imn_data["pre_production"]

    # Get the last pitch from Carthir
    last_message = state["messages"][-1]
    narnion_prompt = last_message.content

    # Build the prompt
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

    # Parse the LLM's JSON output
    try:
        import json as _json
        content = reply.content.strip()
        # Extract JSON block if present
        match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", content)
        if match:
            content = match.group(1).strip()
        result = _json.loads(content)
        scene_context = result.get("scene_context")
        actions = result.get("actions", [])

        # Build the new in_production entry
        new_scene = {
            "scene_id": len(imn_data["in_production"]) + 1,
            "frame_image": None,  # To be filled in later
            "timestamp": None,    # To be filled in later
            "scene_context": scene_context,
            "user_action": None,  # To be filled in after user acts
            "tap_location": None, # To be filled in after user acts
            "object_tapped": None,# To be filled in after user acts
            "actions": actions
        }
        imn_data["in_production"].append(new_scene)
        write_imn(imn_data, os.path.dirname(filename))
        print(f"[Narnion] Added new scene to in_production.")
    except Exception as e:
        print(f"Error parsing Narnion's response: {e}\nRaw reply: {reply.content}")

    return state

def Cenedril(state: State):
    """
    Cenedril writes the initial frame image prompt (first person) for the dream.
    """
    filename = state.get("imn_filename")
    if not filename:
        print("No .imn filename found in state.")
        return state
    imn_data = read_imn(filename)
    pre = imn_data["pre_production"]

    # Get the last pitch from Carthir
    last_message = state["messages"][-1]
    cenedril_prompt = last_message.content

    # Build the prompt
    prompt = (
        f"Pitch: {cenedril_prompt}\n\n"
        "Write a vivid, first-person visual prompt for an AI image generator to create the very first frame of the dream. "
        "Describe what the dreamer sees as if they are experiencing it themselves, using 'I' perspective."
    )
    image_prompt = [
        {"role": "system", "content": "You are Cenedril, a master of visual storytelling."},
        {"role": "user", "content": prompt}
    ]
    reply = llm.invoke(image_prompt)

    # Save the result in the .imn file
    first_frame_prompt = reply.content.strip()
    imn_data["pre_production"]["first_frame_prompt"] = first_frame_prompt
    write_imn(imn_data, os.path.dirname(filename))
    print(f"[Cenedril] Saved first frame prompt to .imn file.")

    return state

def read_imn(filename: str):
    """
    Read the IMN structure from a file and return as a dictionary.
    """
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading .imn file: {e}")
        return None

# Placeholder downstream agent for demonstration
def print_imn_agent(state: State):
    """
    Reads and prints the .imn file using the filename from the state.
    """
    filename = state.get("imn_filename")
    if not filename:
        print("No .imn filename found in state.")
        return state
    imn_data = read_imn(filename)
    print(f"\n[print_imn_agent] .imn file contents for '{filename}':\n{json.dumps(imn_data, indent=2)}\n")
    return state

# Build the state graph
graph_builder = StateGraph(State)

# Add the agents
graph_builder.add_node("carthir", Carthir)
graph_builder.add_node("narnion", Narnion)
graph_builder.add_node("cenedril", Cenedril)

graph_builder.add_node("convert_prompt", convert_prompt_to_imn)
# Add the print_imn_agent as the final node for demonstration
graph_builder.add_node("print_imn", print_imn_agent)

graph_builder.add_node("carthir_review", CarthirReview)

graph_builder.add_edge(START, "carthir")
graph_builder.add_edge("carthir", "convert_prompt")
graph_builder.add_edge("convert_prompt", "narnion")
graph_builder.add_edge("convert_prompt", "cenedril")
graph_builder.add_edge("narnion", "carthir_review")
graph_builder.add_edge("cenedril", "carthir_review")
graph_builder.add_edge("carthir_review", END)

### Compile the graph to finalize its structure
graph = graph_builder.compile()


def run_chatbot():
    state = {"messages": [], "imn_filename": None, "id": None, "user_id": None}

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the chatbot.")
            break

        state["messages"] = state.get("messages", []) + [
            {"role": "user", "content": user_input}
        ]

        ## imn_data = convert_prompt_to_imn(initial_state)
        state = graph.invoke(state)

        if state.get("messages") and len(state["messages"]) > 0:
                last_message = state["messages"][-1]
                print(f"Bot: {last_message.content}")


if __name__ == "__main__":
    run_chatbot()