"""
Session Models - Pydantic models for .opro file format and session state.

Implements the schema defined in Boeing Living Specs Section 4.4.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import json
import uuid


class EngineType(Enum):
    """Available optimization engines."""
    OPRO = "OPro (Iterative)"
    APE = "APE (Reverse Eng)"
    PROMPTBREEDER = "Promptbreeder (Evolutionary)"
    S2A = "S2A (Context Filter)"


class SchematicState(Enum):
    """Visual states for the Glass Box schematic."""
    IDLE = "idle"
    OPTIMIZATION = "optimization"
    MUTATION = "mutation"
    EVALUATION = "evaluation"
    INDUCTION = "induction"
    GROWTH = "growth"
    FILTERING = "filtering"


@dataclass
class TrajectoryEntry:
    """Single step in the optimization trajectory."""
    step: int
    score: float
    prompt: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    evaluator_reasoning: str = ""
    mutation_operator: str = ""  # For Promptbreeder


@dataclass
class TestBenchConfig:
    """Configuration for the Tri-State Test Bench."""
    input_a: str = ""  # Golden Path
    input_b: str = ""  # Edge Case
    input_c: str = ""  # Adversarial/OOD
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "input_a": self.input_a,
            "input_b": self.input_b,
            "input_c": self.input_c
        }


@dataclass
class CandidateResult:
    """Result from evaluating a single candidate prompt."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    prompt_text: str = ""
    
    # Tri-state scores
    score_a: float = 0.0  # Golden Path score
    score_b: float = 0.0  # Edge Case score
    score_c: float = 0.0  # Adversarial score
    
    # Responses for each test
    response_a: str = ""
    response_b: str = ""
    response_c: str = ""
    
    # Evaluator details
    evaluator_reasoning_a: str = ""
    evaluator_reasoning_b: str = ""
    evaluator_reasoning_c: str = ""
    
    # Human override
    human_override_score: Optional[float] = None
    human_override_reasoning: str = ""
    
    # Metadata
    generation: int = 0
    parent_id: Optional[str] = None  # For evolutionary tracking
    mutation_operator: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    @property
    def global_score(self) -> float:
        """Calculate aggregate score per Boeing spec 4.2."""
        if self.human_override_score is not None:
            return self.human_override_score
        return (self.score_a + self.score_b + self.score_c) / 3

    @property
    def pass_status(self) -> tuple:
        """Return traffic light status for each test (True = pass)."""
        threshold = 50  # Configurable threshold
        return (
            self.score_a >= threshold,
            self.score_b >= threshold,
            self.score_c >= threshold
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "prompt_text": self.prompt_text,
            "scores": {
                "a": self.score_a,
                "b": self.score_b,
                "c": self.score_c,
                "global": self.global_score
            },
            "responses": {
                "a": self.response_a,
                "b": self.response_b,
                "c": self.response_c
            },
            "reasoning": {
                "a": self.evaluator_reasoning_a,
                "b": self.evaluator_reasoning_b,
                "c": self.evaluator_reasoning_c
            },
            "human_override": {
                "score": self.human_override_score,
                "reasoning": self.human_override_reasoning
            },
            "metadata": {
                "generation": self.generation,
                "parent_id": self.parent_id,
                "mutation_operator": self.mutation_operator,
                "timestamp": self.timestamp
            }
        }


@dataclass
class SessionConfig:
    """Runtime configuration for optimization session."""
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    generations_per_step: int = 3
    stop_score_threshold: float = 95.0
    noise_level: float = 0.0  # RAG noise injection (0-1)
    top_k: int = 5  # RAG retrieval count
    vector_store_path: str = ""


@dataclass
class SessionMetadata:
    """Metadata for .opro file format."""
    version: str = "2.0"
    engine_used: str = "OPro"
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class OptimizerSession:
    """
    Complete session state for .opro file format.
    
    This is the portable file format per Boeing spec Section 4.4.
    """
    metadata: SessionMetadata = field(default_factory=SessionMetadata)
    config: SessionConfig = field(default_factory=SessionConfig)
    test_bench: TestBenchConfig = field(default_factory=TestBenchConfig)
    
    # Current state
    seed_prompt: str = ""
    current_step: int = 0
    
    # Results
    candidates: List[CandidateResult] = field(default_factory=list)
    trajectory: List[TrajectoryEntry] = field(default_factory=list)
    winner: Optional[CandidateResult] = None
    
    # Schematic state for visualization
    schematic_state: SchematicState = SchematicState.IDLE
    active_node: str = ""
    internal_monologue: str = ""  # For Glass Box text panel

    def to_dict(self) -> Dict[str, Any]:
        """Convert to .opro JSON format."""
        return {
            "metadata": {
                "version": self.metadata.version,
                "engine_used": self.metadata.engine_used,
                "timestamp": self.metadata.timestamp,
                "session_id": self.metadata.session_id
            },
            "config": {
                "model": self.config.model,
                "temperature": self.config.temperature,
                "noise_level": self.config.noise_level
            },
            "test_bench": self.test_bench.to_dict(),
            "seed_prompt": self.seed_prompt,
            "current_step": self.current_step,
            "winner": self.winner.to_dict() if self.winner else None,
            "trajectory": [
                {"step": t.step, "score": t.score, "prompt": t.prompt}
                for t in self.trajectory
            ],
            "candidates": [c.to_dict() for c in self.candidates]
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def save(self, filepath: str):
        """Save session to .opro file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())

    @classmethod
    def load(cls, filepath: str) -> 'OptimizerSession':
        """Load session from .opro file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        session = cls()
        
        # Load metadata
        if 'metadata' in data:
            session.metadata = SessionMetadata(
                version=data['metadata'].get('version', '2.0'),
                engine_used=data['metadata'].get('engine_used', 'OPro'),
                timestamp=data['metadata'].get('timestamp', ''),
                session_id=data['metadata'].get('session_id', str(uuid.uuid4()))
            )
        
        # Load config
        if 'config' in data:
            session.config = SessionConfig(
                model=data['config'].get('model', 'gpt-4o-mini'),
                temperature=data['config'].get('temperature', 0.7),
                noise_level=data['config'].get('noise_level', 0.0)
            )
        
        # Load test bench
        if 'test_bench' in data:
            session.test_bench = TestBenchConfig(
                input_a=data['test_bench'].get('input_a', ''),
                input_b=data['test_bench'].get('input_b', ''),
                input_c=data['test_bench'].get('input_c', '')
            )
        
        session.seed_prompt = data.get('seed_prompt', '')
        session.current_step = data.get('current_step', 0)
        
        # Load trajectory
        for entry in data.get('trajectory', []):
            session.trajectory.append(TrajectoryEntry(
                step=entry['step'],
                score=entry['score'],
                prompt=entry['prompt']
            ))
        
        return session

    def get_best_candidate(self) -> Optional[CandidateResult]:
        """Return highest-scoring candidate."""
        if not self.candidates:
            return None
        return max(self.candidates, key=lambda c: c.global_score)

    def get_trajectory_summary(self, max_entries: int = 5) -> str:
        """Format trajectory for meta-prompt (OPro pattern)."""
        recent = self.trajectory[-max_entries:] if self.trajectory else []
        lines = [f"[Prompt: {t.prompt[:50]}... | Score: {t.score:.1f}]" for t in recent]
        return "\n".join(lines)
