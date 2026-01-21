import pytest
import json
from uuid import UUID
from datetime import datetime
from glassbox.models.candidate import UnifiedCandidate, EngineType
from glassbox.models.session import OptimizerSession

def test_unified_candidate_creation():
    """Test standard creation of UnifiedCandidate."""
    candidate = UnifiedCandidate(
        engine_type=EngineType.OPRO,
        generation_index=1,
        display_text="Test Prompt Snippet",
        full_content="Full content of the prompt",
        score_aggregate=85.5,
        test_results={'input_a': 90, 'input_b': 81}
    )
    
    assert isinstance(candidate.id, UUID)
    assert isinstance(candidate.timestamp, datetime)
    assert candidate.engine_type == EngineType.OPRO
    assert candidate.score_aggregate == 85.5
    assert candidate.meta == {}

def test_unified_candidate_serialization():
    """Test JSON serialization via Pydantic model_dump."""
    candidate = UnifiedCandidate(
        engine_type=EngineType.APE,
        generation_index=2,
        display_text="Instruction X",
        full_content="Full Instruction X",
        score_aggregate=92.0,
        meta={'deduced_from': [1, 2]}
    )
    
    # Serialize
    data = candidate.model_dump()
    assert data['engine_type'] == "APE"
    assert data['meta']['deduced_from'] == [1, 2]
    
    # Deserialize
    restored = UnifiedCandidate(**data)
    assert restored.id == candidate.id
    assert restored.score_aggregate == 92.0

def test_session_integration():
    """Test that OptimizerSession can hold and serialize UnifiedCandidates."""
    session = OptimizerSession()
    session.candidates.append(
        UnifiedCandidate(
            engine_type=EngineType.S2A,
            generation_index=0,
            display_text="Filter Strategy 1",
            full_content="Remove noise...",
            score_aggregate=50.0,
            test_results={'input_a': 50}
        )
    )
    
    # Test to_json (which uses to_dict internally)
    json_str = session.to_json()
    data = json.loads(json_str)
    
    assert len(data['candidates']) == 1
    assert data['candidates'][0]['engine_type'] == "S2A"
    assert data['candidates'][0]['display_text'] == "Filter Strategy 1"

if __name__ == "__main__":
    test_unified_candidate_creation()
    test_unified_candidate_serialization()
    test_session_integration()
    print("All UnifiedCandidate tests passed!")
