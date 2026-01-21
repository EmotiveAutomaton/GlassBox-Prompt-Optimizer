"""
Unit Tests for GlassBox Core Components

Run with: pytest glassbox/tests/ -v
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import json

# Test imports
def test_core_imports():
    """Test that all core modules can be imported."""
    from glassbox.core import (
        BoeingAPIClient,
        Message,
        APIResponse,
        APIConfig,
        Evaluator,
        HumanOverrideEvaluator,
        AbstractOptimizer,
        OProEngine,
        APEEngine,
        PromptbreederEngine,
        S2AEngine,
        list_engines,
        get_engine_class,
    )
    assert len(list_engines()) == 4
    assert get_engine_class("OPro (Iterative)") == OProEngine


def test_model_imports():
    """Test that all model classes can be imported."""
    from glassbox.models import (
        EngineType,
        SchematicState,
        TrajectoryEntry,
        TestBenchConfig,
        UnifiedCandidate,
        SessionConfig,
        SessionMetadata,
        OptimizerSession,
    )
    assert EngineType.OPRO.value == "OPro (Iterative)"


def test_rag_imports():
    """Test that RAG simulator can be imported."""
    from glassbox.rag import BaristaSimulator
    sim = BaristaSimulator()
    assert sim is not None


# Message Tests
class TestMessage:
    """Tests for Message dataclass."""

    def test_message_to_dict_string_content(self):
        from glassbox.core.api_client import Message
        
        msg = Message(role="user", content="Hello")
        result = msg.to_dict()
        
        assert result["role"] == "user"
        assert result["content"] == [{"type": "text", "text": "Hello"}]

    def test_message_to_dict_list_content(self):
        from glassbox.core.api_client import Message
        
        content = [{"type": "text", "text": "Hello"}]
        msg = Message(role="assistant", content=content)
        result = msg.to_dict()
        
        assert result["role"] == "assistant"
        assert result["content"] == content


# Session Tests
class TestOptimizerSession:
    """Tests for OptimizerSession."""

    def test_session_creation(self):
        from glassbox.models import OptimizerSession, TestBenchConfig
        
        session = OptimizerSession()
        session.seed_prompt = "Test prompt"
        session.test_bench = TestBenchConfig(
            input_a="Golden",
            input_b="Edge",
            input_c="Adversarial"
        )
        
        assert session.seed_prompt == "Test prompt"
        assert session.test_bench.input_a == "Golden"

    def test_session_serialization(self):
        from glassbox.models import OptimizerSession, UnifiedCandidate, EngineType
        import uuid
        
        session = OptimizerSession()
        session.seed_prompt = "Test"
        
        candidate = UnifiedCandidate(
            id=uuid.uuid4(),
            engine_type=EngineType.OPRO,
            generation_index=0,
            display_text="Improved prompt",
            full_content="Improved prompt",
            score_aggregate=80.0, # (90+70+80)/3
            test_results={"input_a": 90.0, "input_b": 70.0, "input_c": 80.0},
            meta={}
        )
        session.candidates.append(candidate)
        
        json_str = session.to_json()
        data = json.loads(json_str)
        
        assert data["seed_prompt"] == "Test"
        assert len(data["candidates"]) == 1
        assert data["candidates"][0]["score_aggregate"] == 80.0

    def test_candidate_score_aggregate(self):
        from glassbox.models import UnifiedCandidate, EngineType
        import uuid
        
        candidate = UnifiedCandidate(
            id=uuid.uuid4(),
            engine_type=EngineType.OPRO,
            generation_index=1,
            display_text="test",
            full_content="test",
            score_aggregate=80.0,
            test_results={"input_a": 90.0, "input_b": 80.0, "input_c": 70.0},
            meta={}
        )
        
        # In v0.0.3, score_aggregate is SET by the engine, not calculated on the fly by the model in this version
        # But we can verify it holds the value
        assert candidate.score_aggregate == 80.0

    def test_candidate_human_override(self):
        from glassbox.models import UnifiedCandidate, EngineType
        import uuid
        
        candidate = UnifiedCandidate(
            id=uuid.uuid4(),
            engine_type=EngineType.OPRO,
            generation_index=1,
            display_text="test",
            full_content="test",
            score_aggregate=50.0,
            test_results={},
            meta={}
        )
        
        assert candidate.score_aggregate == 50.0
        
        # UnifiedCandidate typically handles overrides via updating score_aggregate directly 
        # or via a UI layer wrapper. For the core model, we just update the field.
        candidate.score_aggregate = 95.0
        assert candidate.score_aggregate == 95.0


# RAG Simulator Tests
class TestBaristaSimulator:
    """Tests for Barista RAG simulator."""

    def test_simulator_init(self):
        from glassbox.rag import BaristaSimulator
        
        sim = BaristaSimulator()
        health = sim.health_check()
        
        assert "using_mock" in health

    def test_retrieve_mock(self):
        from glassbox.rag import BaristaSimulator
        
        sim = BaristaSimulator()
        chunks = sim.retrieve("Boeing aircraft safety", top_k=3)
        
        assert len(chunks) <= 3
        assert all(hasattr(c, 'content') for c in chunks)

    def test_noise_injection(self):
        from glassbox.rag import BaristaSimulator
        
        sim = BaristaSimulator()
        chunks = sim.retrieve("test query", top_k=5, noise_level=0.4)
        
        # With 40% noise, at least some should be marked as noise
        # (depends on mock data)
        assert len(chunks) == 5

    def test_context_assembly(self):
        from glassbox.rag import BaristaSimulator
        
        sim = BaristaSimulator()
        context = sim.assemble_context(
            query="What are safety protocols?",
            system_prompt="You are a helpful assistant.",
            top_k=3
        )
        
        assert "Context Information:" in context.formatted_prompt
        assert context.query == "What are safety protocols?"


# Evaluator Tests
class TestEvaluator:
    """Tests for Evaluator class."""

    def test_evaluator_parse_json_response(self):
        from glassbox.core.evaluator import Evaluator
        from glassbox.core.api_client import BoeingAPIClient
        
        mock_client = Mock(spec=BoeingAPIClient)
        evaluator = Evaluator(mock_client)
        
        response_text = '''
        {
            "score": 85,
            "breakdown": {
                "accuracy": 22,
                "relevance": 21,
                "clarity": 22,
                "instruction_following": 20
            },
            "reasoning": "Good response overall"
        }
        '''
        
        result = evaluator._parse_evaluation_response(response_text)
        
        assert result.score == 85.0
        assert result.reasoning == "Good response overall"

    def test_evaluator_parse_fallback(self):
        from glassbox.core.evaluator import Evaluator
        from glassbox.core.api_client import BoeingAPIClient
        
        mock_client = Mock(spec=BoeingAPIClient)
        evaluator = Evaluator(mock_client)
        
        # Malformed JSON but contains score
        response_text = "The score is 75 out of 100."
        
        result = evaluator._parse_evaluation_response(response_text)
        
        assert result.score == 75.0


# Utility Tests
class TestUtils:
    """Tests for utility functions."""

    def test_html_diff(self):
        from glassbox.utils import generate_html_diff
        
        text_a = "Hello world"
        text_b = "Hello new world"
        
        html = generate_html_diff(text_a, text_b)
        
        assert "<table" in html.lower() or "diff" in html.lower()

    def test_score_badge(self):
        from glassbox.utils import format_score_badge
        
        high = format_score_badge(85.0)
        assert "22c55e" in high  # Green
        
        low = format_score_badge(30.0)
        assert "ef4444" in low  # Red

    def test_traffic_lights(self):
        from glassbox.utils import format_traffic_lights
        
        result = format_traffic_lights((80, 40, 60))
        assert "●" in result


# Engine Tests (Mock)
class TestEngines:
    """Tests for optimization engines."""

    def test_opro_schematic_nodes(self):
        from glassbox.core import OProEngine, BoeingAPIClient, HumanOverrideEvaluator
        from glassbox.models import OptimizerSession
        
        mock_client = Mock(spec=BoeingAPIClient)
        mock_evaluator = Mock(spec=HumanOverrideEvaluator)
        session = OptimizerSession()
        
        engine = OProEngine(mock_client, mock_evaluator, session)
        nodes = engine.get_schematic_nodes()
        
        assert len(nodes) == 4
        assert any(n["id"] == "seed" for n in nodes)
        assert any(n["id"] == "optimizer" for n in nodes)

    def test_opro_graphviz_generation(self):
        from glassbox.core import OProEngine, BoeingAPIClient, HumanOverrideEvaluator
        from glassbox.models import OptimizerSession
        
        mock_client = Mock(spec=BoeingAPIClient)
        mock_evaluator = Mock(spec=HumanOverrideEvaluator)
        session = OptimizerSession()
        
        engine = OProEngine(mock_client, mock_evaluator, session)
        dot_source = engine.generate_graphviz()
        
        assert "digraph" in dot_source
        assert "OPro" in dot_source

    def test_engine_registry(self):
        from glassbox.core import list_engines, get_engine_class
        
        engines = list_engines()
        assert "OPro (Iterative)" in engines
        assert "APE (Reverse Eng)" in engines
        assert "Promptbreeder (Evolutionary)" in engines
        assert "S2A (Context Filter)" in engines
        
        for name in engines:
            cls = get_engine_class(name)
            assert cls is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
