# Core package - exports all engines and utilities
from glassbox.core.api_client import BoeingAPIClient, Message, APIResponse, APIConfig
from glassbox.core.gemini_client import GeminiAPIClient, GeminiConfig, GeminiResponse, get_api_client
from glassbox.core.evaluator import Evaluator, HumanOverrideEvaluator, EvaluationResult
from glassbox.core.optimizer_base import AbstractOptimizer, OptimizerStatus, StepResult
from glassbox.core.opro_engine import OProEngine
from glassbox.core.ape_engine import APEEngine
from glassbox.core.promptbreeder import PromptbreederEngine
from glassbox.core.s2a_engine import S2AEngine

__all__ = [
    # API - Boeing
    "BoeingAPIClient",
    "Message", 
    "APIResponse",
    "APIConfig",
    # API - Gemini (for local dev)
    "GeminiAPIClient",
    "GeminiConfig",
    "GeminiResponse",
    "get_api_client",
    # Evaluator
    "Evaluator",
    "HumanOverrideEvaluator",
    "EvaluationResult",
    # Base
    "AbstractOptimizer",
    "OptimizerStatus",
    "StepResult",
    # Engines
    "OProEngine",
    "APEEngine",
    "PromptbreederEngine",
    "S2AEngine",
]

# Engine registry for dynamic selection
ENGINE_REGISTRY = {
    "OPro (Iterative)": OProEngine,
    "APE (Reverse Eng)": APEEngine,
    "Promptbreeder (Evolutionary)": PromptbreederEngine,
    "S2A (Context Filter)": S2AEngine,
}


def get_engine_class(engine_name: str):
    """Get engine class by name."""
    return ENGINE_REGISTRY.get(engine_name)


def list_engines():
    """List available engine names."""
    return list(ENGINE_REGISTRY.keys())
