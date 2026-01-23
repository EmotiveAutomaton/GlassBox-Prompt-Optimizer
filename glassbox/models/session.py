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


from glassbox.models.candidate import UnifiedCandidate, EngineType

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
class SessionConfig:
    """Runtime configuration for optimization session."""
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    generations_per_step: int = 1
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
    
    # Results - NOW USING UnifiedCandidate
    candidates: List[UnifiedCandidate] = field(default_factory=list)
    trajectory: List[TrajectoryEntry] = field(default_factory=list)
    winner: Optional[UnifiedCandidate] = None
    
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
            "winner": self.winner.model_dump() if self.winner else None,
            "trajectory": [
                {"step": t.step, "score": t.score, "prompt": t.prompt}
                for t in self.trajectory
            ],
            "candidates": [c.model_dump() for c in self.candidates]
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def save(self, filepath: str):
        """Save session to .opro file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OptimizerSession':
        """Create session from dictionary."""
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
                generations_per_step=data['config'].get('generations_per_step', 3),
                stop_score_threshold=data['config'].get('stop_score_threshold', 95.0),
                noise_level=data['config'].get('noise_level', 0.0),
                top_k=data['config'].get('top_k', 5),
                vector_store_path=data['config'].get('vector_store_path', "")
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
                prompt=entry['prompt'],
                timestamp=entry.get('timestamp', datetime.utcnow().isoformat()),
                evaluator_reasoning=entry.get('evaluator_reasoning', ""),
                mutation_operator=entry.get('mutation_operator', "")
            ))
            
        # Load candidates
        if 'candidates' in data:
            # Pydantic's parse_obj_as or just list comprehension with validation
            # Since UnifiedCandidate is a Pydantic model, it accepts dict unpacking
            try:
                session.candidates = [UnifiedCandidate(**c) for c in data['candidates']]
            except Exception as e:
                print(f"Error loading candidates: {e}")
                session.candidates = []
            
        # Load winner
        if 'winner' in data and data['winner']:
             session.winner = UnifiedCandidate(**data['winner'])
        
        return session

    @classmethod
    def load(cls, filepath: str) -> 'OptimizerSession':
        """Load session from .opro file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)

    @classmethod
    def from_json(cls, json_str: str) -> 'OptimizerSession':
        """Load session from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def get_best_candidate(self) -> Optional[UnifiedCandidate]:
        """Return highest-scoring candidate."""
        if not self.candidates:
            return None
        return max(self.candidates, key=lambda c: c.score_aggregate)

    def get_trajectory_summary(self, max_entries: int = 5) -> str:
        """Format trajectory for meta-prompt (OPro pattern)."""
        recent = self.trajectory[-max_entries:] if self.trajectory else []
        lines = [f"[Prompt: {t.prompt[:50]}... | Score: {t.score:.1f}]" for t in recent]
        return "\n".join(lines)
