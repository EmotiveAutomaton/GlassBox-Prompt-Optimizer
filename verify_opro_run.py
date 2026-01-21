
import sys
import os
import json
from unittest.mock import MagicMock
from uuid import UUID

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from glassbox.models.session import OptimizerSession
from glassbox.core.opro_engine import OProEngine
from glassbox.core.evaluator import HumanOverrideEvaluator
from glassbox.models.candidate import EngineType

def test_opro_e2e():
    print("--- Testing OPro Engine End-to-End ---")
    
    # 1. Setup Session
    session = OptimizerSession()
    session.seed_prompt = "Summarize this text."
    session.test_bench.input_a = "Text to summarize."
    
    # 2. Mock API Client
    mock_client = MagicMock()
    # Mock response for meta-prompt (optimization step)
    # AND for evaluation if needed.
    # OPro flow: 
    #   1. get_meta_prompt -> API -> new_instructions
    #   2. evaluate -> API (if LLM evaluator) or just score.
    
    # Let's see OProEngine.step(). It calls self.llm.chat_completion(...)
    # We need to return a structure that has .content
    
    class MockResponse:
        def __init__(self, content):
            self.content = content
            self.success = True
            
    # Mocking behaviors
    def side_effect(*args, **kwargs):
        # args[0] is messages list in send_message(messages, temperature)
        messages = args[0] if args else kwargs.get('messages', [])
        prompt_str = str(messages)
        
        if "optimiz" in prompt_str.lower() or "meta-prompt" in prompt_str.lower():
            # Return simple text to hit fallback logic (lines 199-201 in opro_engine.py)
            return MockResponse("This is a much better summary instruction that is definitely long enough.")
        else:
            # Evaluation or Generation
            return MockResponse("This is a summary.")

    mock_client.send_message.side_effect = side_effect
    
    # 3. Setup Evaluator (Mock)
    mock_evaluator = MagicMock(spec=HumanOverrideEvaluator)
    # Mock evaluate return value
    from glassbox.core.evaluator import EvaluationResult
    mock_evaluator.evaluate.return_value = EvaluationResult(
        score=88.5, 
        reasoning="Good job",
        breakdown={"accuracy": 25, "relevance": 25, "clarity": 25, "instruction_following": 13.5}
    )
    
    # 4. Initialize Engine
    # AbstractOptimizer(api_client, evaluator, session)
    optimizer = OProEngine(mock_client, mock_evaluator, session)
    
    # 5. Run Step
    print("Running optimization step...")
    optimizer.step()
    
    # 6. Verify Session State
    print("Verifying session candidates...")
    assert len(session.candidates) == 1
    candidate = session.candidates[0]
    
    print(f"Candidate: {candidate.display_text} | Score: {candidate.score_aggregate}")
    
    assert candidate.score_aggregate == 88.5
    assert candidate.engine_type == EngineType.OPRO
    assert candidate.full_content == "Better summary instruction." # OPro uses new instruction as full content
    # OProEngine logic: new_prompt = create_candidate(response). 
    # Check OProEngine.step implementation for details if this fails.
    
    # 7. Persistence Check
    filepath = "test_opro_run.opro"
    print(f"Saving to {filepath}...")
    session.save(filepath)
    
    print(f"Loading from {filepath}...")
    loaded_session = OptimizerSession.load(filepath)
    
    loaded_cand = loaded_session.candidates[0]
    assert loaded_cand.id == candidate.id
    assert loaded_cand.score_aggregate == 88.5
    assert loaded_cand.full_content == candidate.full_content
    
    print("✅ OPro E2E Verification SUCCESS!")
    
    # Cleanup
    if os.path.exists(filepath):
        os.remove(filepath)

if __name__ == "__main__":
    try:
        test_opro_e2e()
    except Exception as e:
        print(f"❌ OPro E2E Verification FAILED: {e}")
        import traceback
        traceback.print_exc()
