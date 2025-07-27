import json
import re
import uuid
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from typing import Annotated, Literal, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_community.chat_models import ChatLlamaCpp
from langgraph.channels import last_value

from core.pipeline_instance import PipelineInstance, PipelinePool
from core.agents import State, Carthir, Narnion, Cenedril, CarthirReview, convert_prompt_to_imn, print_imn_agent
from core.imn_utils import read_imn, write_imn


load_dotenv()

# Initialize the local GGUF model with chat interface for compatibility
llm = ChatLlamaCpp(
    model_path="models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
    temperature=0.7,
    max_tokens=2048,
    top_p=0.9,
    verbose=False,  # Set to True for debugging
    n_ctx=4096,  # Context window size
    n_threads=8,  # Adjust based on your CPU cores
)


# Note: Agent functions are imported from core.agents module


# Initialize the global pipeline pool
pipeline_pool = PipelinePool()


def run_chatbot():
    """
    Interactive chatbot loop. Each new user prompt creates a new PipelineInstance (per dream),
    adds it to the PipelinePool, and runs it. Demonstrates per-dream pipeline instance logic.
    """
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the chatbot.")
            break

        # Create a new state for this dream
        state = {"messages": [{"role": "user", "content": user_input}]}
        # Optionally, add user_id or other metadata here

        # Create a new PipelineInstance for this dream
        pipeline_instance = PipelineInstance(state)
        # Use dream_id from state or assign after pipeline runs
        dream_id = pipeline_instance.dream_id or str(uuid.uuid4())
        pipeline_instance.dream_id = dream_id

        # Add to the pool
        pipeline_pool.add_instance(dream_id, pipeline_instance)

        # Run the pipeline (synchronously for now)
        result = pipeline_instance.run()

        # Print the result (last message)
        if result.get("messages") and len(result["messages"]) > 0:
            last_message = result["messages"][-1]
            print(f"Bot: {last_message['content']}")
        else:
            print("Bot: [No response generated]")

        # Optionally, clean up completed pipelines
        pipeline_pool.cleanup_completed()


if __name__ == "__main__":
    run_chatbot()