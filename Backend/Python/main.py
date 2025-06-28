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

### 
class MessageClassifier(BaseModel):
    message_type: Literal["Emotional", "Logical"] = Field(
        ...,
        description="Classify if the message requires an emotional or logical response."
    )

## Define the state graph that will manage the conversation flow
class State(TypedDict):
    messages: Annotated[list, add_messages]
    message_type: str | None

## Detect the type of message that was sent by the user
def classify_message(state: State):
    last_message = state["messages"][-1]
    classifier_llm = llm.with_structured_output(MessageClassifier)

    result = classifier_llm.invoke([
        {
            "role": "system",
            "content": """Classify the user message as either:
            - 'Emotional': if it asks for emotional support, empathy, therapy, deals with feelings, or personal problems
            - 'Logical': if it asks for facts, logic, reasoning, or problem-solving.
            """
        },
        {
            "role": "user",
            "content": last_message.content
        }
    ])
    return {
        "message_type": result.message_type
    }

## Decide which agent to route the message to based on its type
def router(state: State):
    message_type = state.get("message_type", "logical")
    if message_type == "Emotional":
        return {"next": "emotional_agent"}
    
    return {"next": "logical_agent"}

## An emotional agent that provides empathetic responses
def emotional_agent(state: State):
    last_message = state["messages"][-1]

    messages = [
        {
            "role": "system",
            "content": """You are a compassionate therapist. Focus on the emotional aspects of the user's message.
                        Show empathy, validate their feelings, and help them process their emotions.
                        Ask thoughtful questions to help them explore their feelings more deeply.
                        Avoid giving logical solutions unless explicitly asked."""
        },
        {
            "role": "user", 
            "content": last_message.content
        }
    ]
    reply = llm.invoke(messages)
    return {"messages": [{"role": "assistant", "content": reply.content}]}

## A logical agent that provides factual and logical responses
def logical_agent(state: State):
    last_message = state["messages"][-1]

    messages = [
        {
            "role": "system",
            "content": """You are a purely logical assistant. Focus only on facts and information. 
                        Provide clear, concise answers based on logic and evidence.
                        Do not address emotions or provide emotional support.
                        Be direct and straightforward in your responses."""
        },
        {
            "role": "user", 
            "content": last_message.content
        }
    ]
    reply = llm.invoke(messages)
    return {"messages": [{"role": "assistant", "content": reply.content}]}

# Build the state graph
graph_builder = StateGraph(State)

### Add nodes to the graph, each representing a step in the conversation
graph_builder.add_node("classifier", classify_message)
graph_builder.add_node("router", router)
graph_builder.add_node("emotional_agent", emotional_agent)
graph_builder.add_node("logical_agent", logical_agent)

## Direct the flow of the conversation between each node. All graphs requires a START and END.
graph_builder.add_edge(START, "classifier")
graph_builder.add_edge("classifier", "router")

## Creates conditional edges based on the output of the classifier
graph_builder.add_conditional_edges(
    "router",
    lambda state: state.get("next"),
    {"emotional_agent": "emotional_agent", "logical_agent": "logical_agent"}
)

## Connect the agents to the end of the graph and ends the conversation
graph_builder.add_edge("emotional_agent", END)
graph_builder.add_edge("logical_agent", END)

## Compile the graph to finalize its structure
graph = graph_builder.compile()


# This is a simple chatbot that uses LangGraph to classify user messages
# and route them to either an emotional or logical agent based on the classification.
# The chatbot will continue to run until the user types "exit" or "quit".
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

        state = graph.invoke(state)

        if state.get("messages") and len(state["messages"]) > 0:
            last_message = state["messages"][-1]
            print(f"Bot: {last_message.content}")

if __name__ == "__main__":
    run_chatbot()
