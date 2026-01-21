
import sys
import os
import json
from uuid import uuid4
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from glassbox.models.session import OptimizerSession, SessionMetadata, TestBenchConfig
from glassbox.models.candidate import UnifiedCandidate, EngineType

def test_persistence():
    print("--- Testing Session Persistence ---")
    
    # 1. Create a session with data
    session = OptimizerSession()
    session.metadata = SessionMetadata(engine_used="S2A", session_id=str(uuid4()))
    session.seed_prompt = "Test seed prompt"
    
    # Create a dummy candidate
    cand = UnifiedCandidate(
        id=uuid4(),
        engine_type=EngineType.S2A,
        generation_index=1,
        display_text="Test Candidate",
        full_content="This is the full content of the test candidate.",
        score_aggregate=95.5,
        test_results={"input_a": 95.5, "input_b": 90.0},
        meta={"clean_context": "Clean context data", "filtered_items": ["item1", "item2"]}
    )
    session.candidates.append(cand)
    session.winner = cand
    
    # Save
    filepath = "test_persistence.opro"
    print(f"Saving to {filepath}...")
    session.save(filepath)
    
    # Load
    print(f"Loading from {filepath}...")
    loaded_session = OptimizerSession.load(filepath)
    
    # Verify
    print("Verifying loaded data...")
    assert loaded_session.metadata.session_id == session.metadata.session_id
    assert loaded_session.seed_prompt == session.seed_prompt
    assert len(loaded_session.candidates) == 1
    
    loaded_cand = loaded_session.candidates[0]
    assert loaded_cand.id == cand.id
    assert loaded_cand.score_aggregate == cand.score_aggregate
    assert loaded_cand.meta["clean_context"] == "Clean context data"
    assert loaded_cand.engine_type == EngineType.S2A
    
    # Verify Winner
    assert loaded_session.winner is not None
    assert loaded_session.winner.id == cand.id
    
    print("✅ Persistence Verification SUCCESS!")
    
    # Cleanup
    if os.path.exists(filepath):
        os.remove(filepath)

if __name__ == "__main__":
    try:
        test_persistence()
    except Exception as e:
        print(f"❌ Persistence Verification FAILED: {e}")
        import traceback
        traceback.print_exc()
