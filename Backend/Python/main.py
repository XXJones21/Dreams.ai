import json

from dotenv import load_dotenv
from typing import Annotated, Literal, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
## from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

load_dotenv()

## Initialize the LLM client using the Ollama
llm = ChatOpenAI(model="gemma3:12b", base_url="http://10.1.95.9:11434/v1")

# Define the state structure using TypedDic
class State(TypedDict):
    messages: Annotated[list, add_messages]
    message_type: str | None 

class convert_prompt_to_imn(TypedDict):
    
    message_type: Literal["story_prompt","dream_name", "initial_goal"] 

def write_imn(data: dict):
    """
    Write the IMN structure to a file.
    """
    filename = data["dream_name"] + ".imn"
    
    try:
        with open(filename, "w") as f: # 'w' for write mode - overwrites existing file
            json.dump(data, f, indent=4)  # Use json.dump to write the dictionary to the file with indentation for readability
        print(f"Successfully wrote .imn file: {filename}")
    except Exception as e:
        print(f"Error writing to .imn file: {e}")


### Converts a user's inital prompt into a basic .imn file stucture
def convert_prompt_to_imn(state: State) -> dict:
    """
    Classifies a user prompt and extracts information.  Handles potential errors.
    """

    last_message = state["messages"][-1]

    try:
        narrative_llm = llm.with_structured_output(convert_prompt_to_imn)
        result = narrative_llm.invoke([
            {
                "role": "system",
                "content": """
                Classify the user's prompt into the following specific sections to draft an interactive narrative:
                - story_prompt: You are embarking on a dream in first person inspired by the following prompt: {last_message}.
                - dream_name: A name for the user's dream journey based on the 'story_prompt'.
                - initial_goal: An initial goal or natural conclusion of how you think the dream will end with an achieveable goal for the user.
                """       
            },
            {
                "role": "user",
                "content": str(last_message['content'])
            }
        ])

        message_type = result["message_type"]

        imn_data = {
            "story_prompt": last_message['content'],
            "dream_name": result.dream_name,
            "initial_goal": result.initial_goal,
            "message_type": message_type
        }

        write_imn(imn_data)
        return {
            "message_type": message_type
        }
    except Exception as e:
        print(f"Error in convert_prompt_to_imn: {e}")
        return {
            "message_type": None,
        }

    

def Carthir(state: State):
    """
    Generates a film pitch based on the .imn file.
    """
    
    last_message = state["messages"][-1]

    try:
        filename = last_message["dream_name"] + ".imn"
        with open(filename, "r") as f:
            imn_data = json.load(f)

        pitch = f"""
        Film Pitch for '{imn_data['dream_name']}' :

        Based on the story prompt: "{imn_data['story_prompt']}"

        Initial Goal: {imn_data['initial_goal']}

        This film will be a first-person interactive experience... [rest of pitch]
        """

        print("Carthir Film Pitch:\n", pitch)

        return {"film_pitch": pitch, "message_type": HumanMessage(content=pitch)}
    
    except FileNotFoundError:
        print("Error: .imn file not found. Please ensure the file exists.")
        return {}
    except Exception as e:
        print(f"Error in Carthir: {e}")
        return {}


# Build the state graph
graph_builder = StateGraph(State)

### Add nodes to the graph, each representing a step in the conversation
graph_builder.add_node("convert_prompt", convert_prompt_to_imn)
graph_builder.add_node("carthir", Carthir)

### Direct the flow of the conversation between each node. All graphs requires a START and END.
graph_builder.add_edge(START, "convert_prompt")
graph_builder.add_edge("convert_prompt", "carthir")
graph_builder.add_edge("carthir", END)

### Compile the graph to finalize its structure
graph = graph_builder.compile()

def run_chatbot():
    state = {"messages": [], "message_type": None}

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the chatbot.")
            break

        state["messages"] = state.get("messages", []) + [
            {"role": "user", "content": user_input}
        ]

        human_message = HumanMessage(content=user_input)

        initial_state = State(messages=state["messages"], message_type=None)
        imn_data = convert_prompt_to_imn(initial_state)
        state = graph.invoke(state)


        if state.get("messages") and len(state["messages"]) > 0:
            # Check if the last element is a dictionary containing 'message' key
            if isinstance(state["messages"][-1], dict) and "message" in state["messages"][-1]:
                last_message = str(state["messages"][-1]["message"].content) 
                print(f"Bot: {last_message}")
            else:
                last_message = str(state["messages"][-1].content) 
                print(f"Bot: {last_message}")

if __name__ == "__main__":
    run_chatbot()