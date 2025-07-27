import json
import re
import uuid
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from typing import Annotated, Literal, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_community.llms import LlamaCpp
from langgraph.channels import last_value

from core.pipeline_instance import PipelineInstance, PipelinePool
from core.agents import State, Carthir, Narnion, Cenedril, CarthirReview, convert_prompt_to_imn, print_imn_agent
from core.imn_utils import read_imn, write_imn


load_dotenv()

# Initialize the local GGUF model
llm = LlamaCpp(
    model_path="models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
    temperature=0.7,
    max_tokens=2048,
    top_p=0.9,
    verbose=False,  # Set to True for debugging
    n_ctx=4096,  # Context window size
    n_threads=8,  # Adjust based on your CPU cores
)


def format_prompt_for_llama(messages):
    """
    Convert message list format to a single string prompt for LlamaCpp.
    Uses Llama 3.1 chat template format.
    """
    prompt = "<|begin_of_text|>"
    
    for message in messages:
        role = message.get("role", "user")
        content = message.get("content", "")
        
        if role == "system":
            prompt += f"<|start_header_id|>system<|end_header_id|>\n\n{content}<|eot_id|>"
        elif role == "user":
            prompt += f"<|start_header_id|>user<|end_header_id|>\n\n{content}<|eot_id|>"
        elif role == "assistant":
            prompt += f"<|start_header_id|>assistant<|end_header_id|>\n\n{content}<|eot_id|>"
    
    # Add assistant header for response
    prompt += "<|start_header_id|>assistant<|end_header_id|>\n\n"
    
    return prompt


def invoke_llm(messages):
    """
    Helper function to invoke the LLM with proper prompt formatting.
    """
    formatted_prompt = format_prompt_for_llama(messages)
    return llm.invoke(formatted_prompt)


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