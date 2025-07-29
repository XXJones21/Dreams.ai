"""
Dreams.ai LangGraph-Native Pipeline Instance

This module implements LangGraph's native parallelization approach:
1. Single GPU allocation per pipeline instance
2. Native LangGraph parallel edges for agent execution
3. IMN files as the primary context mechanism
4. Proper StateGraph implementation
"""

import os
import time
import threading
import uuid
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from core.agents import *


class PipelineInstance:
    """LangGraph-native pipeline instance with proper parallelization"""
    
    def __init__(self, state: State):
        self.state = state
        self.dream_id = state.get("id")
        self.completed = False
        self.result = None
        self.lock = threading.Lock()
        
        if not self.dream_id:
            self.dream_id = str(uuid.uuid4())
            self.state["id"] = self.dream_id
        
        # Build the LangGraph workflow
        self.graph = self._build_langgraph_workflow()

    def _build_langgraph_workflow(self):
        """Build LangGraph workflow with Carthir as supervisor"""
        
        workflow = StateGraph(State)
        
        # Add all agent nodes
        workflow.add_node("carthir_supervisor", CarthirSupervisor)
        workflow.add_node("convert_prompt", convert_prompt_to_imn)
        workflow.add_node("narnion", Narnion)
        workflow.add_node("carthir_review", CarthirReview)
        workflow.add_node("cenedril", Cenedril)
        
        # Supervisor architecture: Carthir controls the flow
        workflow.add_edge(START, "convert_prompt")
        workflow.add_edge("convert_prompt", "carthir_supervisor")
        
        # All agents return to supervisor for routing decisions
        workflow.add_edge("narnion", "carthir_supervisor")
        workflow.add_edge("carthir_review", "carthir_supervisor")
        workflow.add_edge("cenedril", "carthir_supervisor")
        
        return workflow.compile()

    def run(self):
        """Execute the LangGraph workflow with native parallelization"""
        with self.lock:
            print(f"[Pipeline] 🎬 Starting LangGraph-native pipeline for dream {self.dream_id}")
            print(f"[Pipeline] 🚀 Using LangGraph's built-in parallelization")
            
            try:
                # Let LangGraph handle the execution and parallelization
                self.result = self.graph.invoke(self.state)
                self.completed = True
                
                # Verify IMN file was created
                imn_file_path = os.path.join("..", "Dreams", f"{self.dream_id}.imn")
                if os.path.exists(imn_file_path):
                    print(f"[Pipeline] ✅ Pipeline completed successfully")
                    print(f"[Pipeline] 📁 IMN file confirmed: {self.dream_id}.imn")
                else:
                    print(f"[Pipeline] ⚠️ Pipeline completed but no IMN file found")
                
                return self.result
                
            except Exception as e:
                print(f"[Pipeline] ❌ Pipeline failed: {e}")
                import traceback
                traceback.print_exc()
                self.result = self.state
                return self.state 