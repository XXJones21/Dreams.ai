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
