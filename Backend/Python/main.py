from dotenv import load_dotenv
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
## from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

load_dotenv()

## Initialize the LLM client using the Ollama
llm = ChatOpenAI(model="sulivan:latest", base_url="http://10.1.95.9:11434/v1")

## State model for the conversation
class State(TypedDict):
    messages: Annotated[list, add_messages]
    message_type: str | None

### Converts a user's inital prompt into a basic .imn file stucture
def convert_prompt_to_imn(state: State) -> Dict:

    dream_name = "Untitled Dream"
    story_prompt = f"You are embarking on a dream inspired by the following prompt: {user_prompt}. "
    initial_goal = "Begin your journey and explore yyour surroundings."

    imn_structure = {
        "dream_name": dream_name,
        "story_prompt": story_prompt,
        "user_prompt": user_prompt,
        "initial_goal": initial_goal,
    }
    