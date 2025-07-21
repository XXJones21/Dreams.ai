"""
PipelineInstance: Encapsulates a full agent pipeline for a single dream (IMN file)

This class manages the lifecycle, state, and execution of the agent pipeline for one user dream.
It is designed for use in a pool of pipeline instances, enabling parallel, isolated dream generation.
"""

import threading
from typing import Any, Dict
from langgraph.graph import StateGraph, START, END
from core.agents import State, Carthir, Narnion, CarthirReview, Cenedril, convert_prompt_to_imn, print_imn_agent
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class PipelineInstance:
    """
    PipelineInstance
    ---------------
    Represents a single, isolated agent pipeline for one dream (IMN file).
    Each instance manages its own state, agent graph, and execution lifecycle.
    """
    def __init__(self, initial_state: Dict[str, Any]):
        """
        Initialize a new PipelineInstance.

        Args:
            initial_state (dict): The initial state for the pipeline (e.g., user prompt, user_id).
        """
        self.state = initial_state.copy()
        self.dream_id = self.state.get("id")
        self.lock = threading.Lock()  # For thread safety if needed
        self.graph = self._build_graph()
        self.completed = False
        self.result = None

    def _build_graph(self):
        """
        Build and return a new StateGraph for this pipeline instance.
        Returns:
            StateGraph: The compiled agent pipeline graph.
        """
        graph_builder = StateGraph(State)
        graph_builder.add_node("carthir", Carthir)
        graph_builder.add_node("narnion", Narnion)
        graph_builder.add_node("cenedril", Cenedril)
        graph_builder.add_node("convert_prompt", convert_prompt_to_imn)
        graph_builder.add_node("print_imn", print_imn_agent)
        graph_builder.add_node("carthir_review", CarthirReview)
        graph_builder.add_edge(START, "carthir")
        graph_builder.add_edge("carthir", "convert_prompt")
        graph_builder.add_edge("convert_prompt", "narnion")
        graph_builder.add_edge("narnion", "carthir_review")
        graph_builder.add_edge("carthir_review", "cenedril")
        graph_builder.add_edge("cenedril", END)
        return graph_builder.compile()

    def run(self):
        """
        Execute the agent pipeline for this dream instance.
        Returns:
            dict: The final state after pipeline execution.
        """
        with self.lock:
            self.result = self.graph.invoke(self.state)
            self.completed = True
            return self.result

    def run_parallel_agents(self, timeout=15):
        """
        Run Carthir, Narnion, and Cenedril in parallel using ThreadPoolExecutor.
        Each agent receives a copy of the state and works independently.
        Logs start/end times for each agent and returns a dict of results.
        """
        agents = [
            ("carthir", Carthir),
            ("narnion", Narnion),
            ("cenedril", Cenedril)
        ]
        results = {}
        timings = {}
        with ThreadPoolExecutor(max_workers=len(agents)) as executor:
            future_to_agent = {}
            for name, agent_fn in agents:
                agent_state = self.state.copy()
                start_time = time.time()
                future = executor.submit(agent_fn, agent_state)
                future_to_agent[future] = (name, start_time)
            for future in as_completed(future_to_agent):
                name, start_time = future_to_agent[future]
                try:
                    result = future.result(timeout=timeout)
                    end_time = time.time()
                    results[name] = result
                    timings[name] = end_time - start_time
                    print(f"[Parallel] Agent '{name}' completed in {timings[name]:.2f}s")
                except Exception as e:
                    results[name] = f"Error: {e}"
                    timings[name] = None
                    print(f"[Parallel] Agent '{name}' failed: {e}")
        print(f"[Parallel] All agents completed. Timings: {timings}")
        return results

    def is_complete(self) -> bool:
        """
        Check if the pipeline execution is complete.
        Returns:
            bool: True if completed, False otherwise.
        """
        return self.completed

    def get_result(self) -> Dict[str, Any]:
        """
        Get the result of the pipeline execution.
        Returns:
            dict: The final state/result, or None if not run yet.
        """
        return self.result

    # Future extension: add monitoring, cleanup, cancellation, etc. 

class PipelinePool:
    """
    PipelinePool
    ------------
    Manages a pool of active PipelineInstance objects, each representing a single dream (IMN file).
    Provides thread-safe methods to add, retrieve, and remove pipeline instances by dream_id.
    Handles resource cleanup for completed or idle pipelines.
    """
    def __init__(self):
        """
        Initialize a new PipelinePool.
        """
        self._instances = {}
        self._lock = threading.Lock()

    def add_instance(self, dream_id: str, instance: PipelineInstance):
        """
        Add a new PipelineInstance to the pool.
        Args:
            dream_id (str): The unique identifier for the dream/IMN file.
            instance (PipelineInstance): The pipeline instance to add.
        """
        with self._lock:
            self._instances[dream_id] = instance

    def get_instance(self, dream_id: str) -> PipelineInstance:
        """
        Retrieve a PipelineInstance by dream_id.
        Args:
            dream_id (str): The unique identifier for the dream/IMN file.
        Returns:
            PipelineInstance or None if not found.
        """
        with self._lock:
            return self._instances.get(dream_id)

    def remove_instance(self, dream_id: str):
        """
        Remove a PipelineInstance from the pool and clean up resources.
        Args:
            dream_id (str): The unique identifier for the dream/IMN file.
        """
        with self._lock:
            instance = self._instances.pop(dream_id, None)
            # Future: call instance.cleanup() if implemented
            return instance

    def cleanup_completed(self):
        """
        Remove all completed pipeline instances from the pool.
        """
        with self._lock:
            completed = [k for k, v in self._instances.items() if v.is_complete()]
            for k in completed:
                self._instances.pop(k)

    def get_all_active(self) -> dict:
        """
        Get a snapshot of all active pipeline instances.
        Returns:
            dict: Mapping of dream_id to PipelineInstance.
        """
        with self._lock:
            return dict(self._instances)

    # Future extension: add monitoring, timeouts, status reporting, etc. 