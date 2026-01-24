
import sys
import os
import traceback

# Print Environment Info
print(f"CWD: {os.getcwd()}")
print(f"PYTHONPATH: {sys.path}")

# Ensure CWD is in path
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

try:
    print("Importing glassbox...")
    import glassbox
    print(f"Glassbox imported: {glassbox}")
    
    print("Importing models...")
    from glassbox.models.session import OptimizerSession, OptimizerConfig, TestBench
    from glassbox.models.candidate import UnifiedCandidate
    print("Models imported.")
    
    print("Importing engine...")
    from glassbox.core.opro_engine import OProEngine
    from glassbox.core.api_client import APIResponse
    print("Engine imported.")
    
    from unittest.mock import MagicMock
except Exception as e:
    print("CRITICAL IMPORT ERROR:")
    traceback.print_exc()
    sys.exit(1)

def run_debug():
    print("=== STARTING BACKEND REPRODUCTION ===")
    
    # 1. Setup Session
    # Explicitly testing generations_per_step=1
    config = OptimizerConfig(temperature=0.7, generations_per_step=1) 
    
    session = OptimizerSession(
        seed_prompt="Write a poem",
        config=config,
        test_bench=TestBench(input_a="Inputs", input_b="Inputs", input_c="Inputs")
    )
    
    # 2. Mock API Client
    mock_client = MagicMock()
    mock_client.send_message.return_value = APIResponse(
        success=True,
        content="VARIATION 1: Variation A\nREASONING: Better."
    )
    
    # 3. Init Engine
    evaluator_mock = MagicMock()
    # Need to mock evaluate method to return a valid result object or just mock the object
    # OProEngine._evaluate_candidate calls self.evaluator.evaluate()
    # It returns EvalResult(score, reasoning)
    
    # We need to construct a real Evaluator or mock it well.
    # Let's mock the evaluate method return value
    from glassbox.core.evaluator import EvalResult
    evaluator_mock.evaluate.return_value = EvalResult(score=88.5, reasoning="Good.")

    engine = OProEngine(mock_client, evaluator_mock, session)
    
    # 4. Run Step 1
    print("\n--- Running Step 1 ---")
    result = engine.step()
    
    print(f"Step Candidates Generated: {len(result.candidates)}")
    for c in result.candidates:
        print(f" - Iter: {c.generation_index}, Prompt: {c.display_text}")
        
    print(f"Total Session Candidates: {len(session.candidates)}")
    
    # 5. Run Step 2
    print("\n--- Running Step 2 ---")
    mock_client.send_message.return_value = APIResponse(
        success=True,
        content="VARIATION 1: Variation B\nREASONING: Even Better."
    )
    # mock evaluate again just in case
    evaluator_mock.evaluate.return_value = EvalResult(score=92.0, reasoning="Better.")
    
    result = engine.step()
    
    print(f"Step Candidates Generated: {len(result.candidates)}")
    for c in result.candidates:
        print(f" - Iter: {c.generation_index}, Prompt: {c.display_text}")
        
    print(f"Total Session Candidates: {len(session.candidates)}")
    
    # Check for duplicates
    from collections import Counter
    iters = [c.generation_index for c in session.candidates]
    counts = Counter(iters)
    print(f"\nIteration Counts: {counts}")
    
    if any(v > 1 for v in counts.values()):
        print("FAIL: DUPLICATES FOUND! (Backend is generating multiple candidates per step)")
    elif len(iters) > len(set(iters)):
         print("FAIL: DUPLICATE ITERATION INDICES FOUND!")
    else:
        print("PASS: NO DUPLICATES. (If 1-1-2-2 appears in UI, it is DISPLAY LOGIC)")

if __name__ == "__main__":
    run_debug()
