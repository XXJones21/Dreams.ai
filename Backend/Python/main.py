import json
import re

from dotenv import load_dotenv
from typing import Annotated, Literal, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI


load_dotenv()

llm = ChatOpenAI(model="gemma3:12b", base_url="http://10.1.95.9:11434/v1")


class State(TypedDict):
    messages: Annotated[list, add_messages]
    message_type: str | None
    dream_name: str | None
    story_prompt: str | None
    initial_goal: str | None
    pitch: str | None
    imn_filename: str | None


class convert_prompt_to_imn(TypedDict):

    message_type: Literal["story_prompt", "dream_name", "initial_goal"]


def write_imn(data: dict):
    """
    Write the IMN structure to a file.
    """
    filename = data["dream_name"] + ".imn"

    try:
        with open(filename, "w") as f:  # 'w' for write mode - overwrites existing file
            json.dump(data, f, indent=4)  # Use json.dump to write the dictionary to the file with indentation for readability
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

    if not dream_name:
        dream_name = "untitled_dream"
        print("Warning: dream_name missing, using default.")

    imn_data = {
        "dream_name": dream_name,
        "story_prompt": story_prompt,
        "initial_goal": initial_goal,
    }

    filename = dream_name + ".imn"
    write_imn(imn_data)

    # Pass along the state, adding the filename
    state["imn_filename"] = filename
    return state


def Carthir(state: State):
    """
    Generates a film pitch based on the user's prompt and returns structured data.
    """

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
            "messages": [{"role": "assistant", "content": result.get("pitch", "")}]  # for display
        })
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

graph_builder.add_node("carthir", Carthir)
graph_builder.add_node("convert_prompt", convert_prompt_to_imn)
# Add the print_imn_agent as the final node for demonstration
graph_builder.add_node("print_imn", print_imn_agent)

graph_builder.add_edge(START, "carthir")
graph_builder.add_edge("carthir", "convert_prompt")
graph_builder.add_edge("convert_prompt", "print_imn")
graph_builder.add_edge("print_imn", END)

### Compile the graph to finalize its structure
graph = graph_builder.compile()


def run_chatbot():
    state = {"messages": [], "message_type": None, "dream_name": None, "story_prompt": None, "initial_goal": None, "pitch": None, "imn_filename": None}

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