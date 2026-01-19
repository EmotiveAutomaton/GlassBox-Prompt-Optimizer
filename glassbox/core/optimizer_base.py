"""
Abstract Optimizer Base - Strategy Pattern interface for all optimization engines.

All engines (OPro, APE, Promptbreeder, S2A) must inherit from this class
to ensure consistent behavior and visualization support.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Callable, Dict, Any
from enum import Enum
import threading
import logging
from queue import Queue

from glassbox.core.api_client import BoeingAPIClient
from glassbox.core.evaluator import Evaluator
from glassbox.models.session import (
    OptimizerSession, 
    CandidateResult, 
    TrajectoryEntry,
    SchematicState
)

logger = logging.getLogger(__name__)


class OptimizerStatus(Enum):
    """Status of the optimization run."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


@dataclass
class StepResult:
    """Result of a single optimization step."""
    candidates: List[CandidateResult]
    best_candidate: Optional[CandidateResult]
    step_number: int
    schematic_state: SchematicState
    active_node: str
    internal_monologue: str
    should_stop: bool = False
    error_message: str = ""


class AbstractOptimizer(ABC):
    """
    Abstract base class for all optimization engines.
    
    Implements the Strategy Pattern to allow dynamic engine swapping
    while maintaining consistent interface for the UI.
    """

    def __init__(
        self,
        api_client: BoeingAPIClient,
        evaluator: Evaluator,
        session: OptimizerSession
    ):
        self.api_client = api_client
        self.evaluator = evaluator
        self.session = session
        
        # Threading support (Boeing spec 2.3)
        self._stop_requested = threading.Event()
        self._result_queue: Queue = Queue()
        self._status = OptimizerStatus.IDLE
        self._current_thread: Optional[threading.Thread] = None
        
        # Progress callbacks for UI updates
        self._on_step_complete: Optional[Callable[[StepResult], None]] = None
        self._on_status_change: Optional[Callable[[OptimizerStatus], None]] = None

    @property
    @abstractmethod
    def engine_name(self) -> str:
        """Return the display name of this engine."""
        pass

    @property
    @abstractmethod
    def schematic_type(self) -> str:
        """Return the schematic layout type (loop, funnel, tree, conveyor)."""
        pass

    @abstractmethod
    def step(self) -> StepResult:
        """
        Execute a single optimization step.
        
        This is the core method each engine must implement.
        Must update session.schematic_state and session.internal_monologue
        for Glass Box visualization.
        
        Returns:
            StepResult with candidates, state, and visualization data
        """
        pass

    @abstractmethod
    def get_schematic_nodes(self) -> List[Dict[str, Any]]:
        """
        Return the node definitions for the Graphviz schematic.
        
        Each node should have:
        - id: Unique identifier
        - label: Display text
        - active: Whether currently processing
        - color: Current state color
        """
        pass

    @abstractmethod
    def get_schematic_edges(self) -> List[Dict[str, Any]]:
        """
        Return the edge definitions for the Graphviz schematic.
        
        Each edge should have:
        - source: Source node id
        - target: Target node id
        - color: Edge color (blue=instruction, yellow=data)
        - active: Whether currently animating
        """
        pass

    def get_current_status(self) -> Dict[str, Any]:
        """Get current optimizer status for UI display."""
        return {
            "engine": self.engine_name,
            "status": self._status.value,
            "step": self.session.current_step,
            "best_score": self._get_best_score(),
            "num_candidates": len(self.session.candidates),
            "schematic_state": self.session.schematic_state.value,
            "active_node": self.session.active_node,
            "monologue": self.session.internal_monologue
        }

    def run(self, max_steps: int = 100) -> List[StepResult]:
        """
        Run optimization loop until stop condition or max steps.
        
        Checks _stop_requested between each step for user interruption.
        """
        self._status = OptimizerStatus.RUNNING
        self._notify_status_change()
        
        results = []
        
        try:
            for step_num in range(max_steps):
                # Check stop signal (Boeing spec 2.3)
                if self._stop_requested.is_set():
                    self._status = OptimizerStatus.STOPPED
                    logger.info("Optimization stopped by user")
                    break

                result = self.step()
                results.append(result)
                self._result_queue.put(result)
                
                if self._on_step_complete:
                    self._on_step_complete(result)

                # Check stop conditions
                if result.should_stop:
                    self._status = OptimizerStatus.COMPLETED
                    break
                    
                if result.error_message:
                    self._status = OptimizerStatus.FAILED
                    break

                # Check score threshold
                if self._get_best_score() >= self.session.config.stop_score_threshold:
                    self._status = OptimizerStatus.COMPLETED
                    logger.info(f"Reached target score: {self._get_best_score()}")
                    break

            if self._status == OptimizerStatus.RUNNING:
                self._status = OptimizerStatus.COMPLETED
                
        except Exception as e:
            logger.exception("Optimization failed")
            self._status = OptimizerStatus.FAILED
            
        self._notify_status_change()
        return results

    def run_async(self, max_steps: int = 100) -> threading.Thread:
        """
        Run optimization in a daemon thread (Boeing spec 2.3).
        
        Results are available via _result_queue or callbacks.
        """
        def _worker():
            self.run(max_steps)
        
        self._current_thread = threading.Thread(target=_worker, daemon=True)
        self._current_thread.start()
        return self._current_thread

    def request_stop(self):
        """Request stop of current optimization run."""
        self._stop_requested.set()
        self.api_client.request_stop()

    def reset(self):
        """Reset optimizer state for new run."""
        self._stop_requested.clear()
        self.api_client.reset_stop()
        self._status = OptimizerStatus.IDLE
        self.session.current_step = 0
        self.session.candidates.clear()
        self.session.trajectory.clear()
        self.session.schematic_state = SchematicState.IDLE
        self.session.active_node = ""
        self.session.internal_monologue = ""

    def set_callbacks(
        self,
        on_step_complete: Optional[Callable[[StepResult], None]] = None,
        on_status_change: Optional[Callable[[OptimizerStatus], None]] = None
    ):
        """Set callbacks for UI updates."""
        self._on_step_complete = on_step_complete
        self._on_status_change = on_status_change

    def _get_best_score(self) -> float:
        """Get the best score from current candidates."""
        if not self.session.candidates:
            return 0.0
        return max(c.global_score for c in self.session.candidates)

    def _notify_status_change(self):
        """Notify UI of status change."""
        if self._on_status_change:
            self._on_status_change(self._status)

    def _add_trajectory_entry(self, candidate: CandidateResult):
        """Add entry to optimization trajectory."""
        entry = TrajectoryEntry(
            step=self.session.current_step,
            score=candidate.global_score,
            prompt=candidate.prompt_text
        )
        self.session.trajectory.append(entry)

    def _execute_prompt(self, prompt: str, input_text: str) -> str:
        """
        Execute a prompt with input and return the response.
        
        This is a helper for evaluator's executor_fn.
        """
        from glassbox.core.api_client import Message
        
        messages = [
            Message(role="system", content=prompt),
            Message(role="user", content=input_text)
        ]
        
        response = self.api_client.send_message(messages)
        if response.success:
            return response.content
        else:
            raise RuntimeError(f"API call failed: {response.error_message}")
