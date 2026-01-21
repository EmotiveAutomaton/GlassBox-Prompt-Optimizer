
import sys
import os
import json
import uuid

# Add project root to path
sys.path.append(os.getcwd())

def run_verification():
    print("Starting verification...")
    failures = []

    try:
        print("1. Verifying UnifiedCandidate model...")
        from glassbox.models import UnifiedCandidate, EngineType
        c = UnifiedCandidate(
            id=uuid.uuid4(),
            engine_type=EngineType.OPRO,
            generation_index=1,
            display_text="test",
            full_content="test",
            score_aggregate=99.0,
            test_results={"input_a": 100.0},
            meta={}
        )
        if c.score_aggregate != 99.0:
            failures.append("UnifiedCandidate instantiation failed")
        else:
            print("   PASS: UnifiedCandidate instantiation")
            
    except Exception as e:
        failures.append(f"UnifiedCandidate error: {e}")

    try:
        print("2. Verifying OptimizerSession serialization...")
        from glassbox.models import OptimizerSession
        session = OptimizerSession()
        session.seed_prompt = "Verify"
        from glassbox.models import UnifiedCandidate, EngineType
        c = UnifiedCandidate(
            id=uuid.uuid4(),
            engine_type=EngineType.APE,
            generation_index=0,
            display_text="verify",
            full_content="verify",
            score_aggregate=50.0,
            test_results={},
            meta={}
        )
        session.candidates.append(c)
        json_str = session.to_json()
        data = json.loads(json_str)
        
        if data["candidates"][0]["display_text"] != "verify":
             failures.append("Session serialization mismatch")
        else:
             print("   PASS: Session serialization")

    except Exception as e:
        failures.append(f"Session error: {e}")

    try:
        print("3. Verifying Engine imports...")
        from glassbox.core import OProEngine, APEEngine, S2AEngine, PromptbreederEngine
        print("   PASS: Engine imports")
    except Exception as e:
        failures.append(f"Engine import error: {e}")

    if failures:
        print("\nFAILURES FOUND:")
        for f in failures:
            print(f"- {f}")
        sys.exit(1)
    else:
        print("\nALL CHECKS PASSED.")
        sys.exit(0)

if __name__ == "__main__":
    run_verification()
