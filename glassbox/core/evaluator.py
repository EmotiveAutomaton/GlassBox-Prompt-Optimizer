"""
Evaluator - LLM Judge for scoring prompt effectiveness.

Implements hybrid scoring approach:
- Default: LLM Judge rates responses (0-100)
- Override: Human can manually adjust scores via UI
"""

import json
import logging
import re
from dataclasses import dataclass
from typing import Optional, Tuple

from glassbox.core.api_client import BoeingAPIClient, Message
from glassbox.prompts.templates import EVALUATOR_SYSTEM_PROMPT, EVALUATOR_USER_TEMPLATE

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """Result from evaluating a single response."""
    score: float
    reasoning: str
    breakdown: dict  # accuracy, relevance, clarity, instruction_following
    raw_response: str = ""
    is_human_override: bool = False


class Evaluator:
    """
    LLM Judge for evaluating prompt effectiveness.
    
    Uses the Boeing API to rate responses on a 0-100 scale with breakdown
    across four criteria: accuracy, relevance, clarity, instruction following.
    """

    def __init__(
        self, 
        api_client: BoeingAPIClient,
        custom_system_prompt: Optional[str] = None,
        evaluation_temperature: float = 0.0  # Low temp for consistent scoring
    ):
        self.api_client = api_client
        self.system_prompt = custom_system_prompt or EVALUATOR_SYSTEM_PROMPT
        self.temperature = evaluation_temperature

    def evaluate(
        self,
        prompt: str,
        input_text: str,
        response: str
    ) -> EvaluationResult:
        """
        Evaluate a single prompt-input-response triplet.
        
        Args:
            prompt: The prompt being evaluated
            input_text: The input provided to the prompt
            response: The AI's response to evaluate
            
        Returns:
            EvaluationResult with score, reasoning, and breakdown
        """
        user_message = EVALUATOR_USER_TEMPLATE.format(
            prompt=prompt,
            input_text=input_text,
            response=response
        )

        messages = [
            Message(role="system", content=self.system_prompt),
            Message(role="user", content=user_message)
        ]

        api_response = self.api_client.send_message(
            messages,
            temperature=self.temperature
        )

        if not api_response.success:
            logger.error(f"Evaluation API call failed: {api_response.error_message}")
            return EvaluationResult(
                score=0.0,
                reasoning=f"Evaluation failed: {api_response.error_message}",
                breakdown={"accuracy": 0, "relevance": 0, "clarity": 0, "instruction_following": 0},
                raw_response=""
            )

        return self._parse_evaluation_response(api_response.content)

    def _parse_evaluation_response(self, response_text: str) -> EvaluationResult:
        """Parse the JSON evaluation response from the LLM Judge."""
        try:
            # Try to extract JSON from response (may have surrounding text)
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise ValueError("No JSON found in response")

            score = float(data.get("score", 0))
            reasoning = data.get("reasoning", "No reasoning provided")
            breakdown = data.get("breakdown", {
                "accuracy": 0,
                "relevance": 0,
                "clarity": 0,
                "instruction_following": 0
            })

            # Clamp score to 0-100
            score = max(0, min(100, score))

            return EvaluationResult(
                score=score,
                reasoning=reasoning,
                breakdown=breakdown,
                raw_response=response_text
            )

        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse evaluation JSON: {e}")
            
            # Fallback: try to extract just a number
            numbers = re.findall(r'\b(\d{1,3})\b', response_text)
            if numbers:
                score = min(100, max(0, int(numbers[0])))
                return EvaluationResult(
                    score=score,
                    reasoning=f"Parsed from raw response (JSON parse failed): {response_text[:200]}",
                    breakdown={"accuracy": 0, "relevance": 0, "clarity": 0, "instruction_following": 0},
                    raw_response=response_text
                )

            return EvaluationResult(
                score=0.0,
                reasoning=f"Failed to parse evaluation response: {response_text[:200]}",
                breakdown={"accuracy": 0, "relevance": 0, "clarity": 0, "instruction_following": 0},
                raw_response=response_text
            )

    def evaluate_tristate(
        self,
        prompt: str,
        input_a: str,
        input_b: str,
        input_c: str,
        executor_fn: callable
    ) -> Tuple[EvaluationResult, EvaluationResult, EvaluationResult]:
        """
        Evaluate a prompt against all three test bench inputs.
        
        Args:
            prompt: The prompt to evaluate
            input_a: Golden Path input
            input_b: Edge Case input
            input_c: Adversarial input
            executor_fn: Function that takes (prompt, input) and returns response
            
        Returns:
            Tuple of (result_a, result_b, result_c)
        """
        results = []
        
        for input_text in [input_a, input_b, input_c]:
            if not input_text.strip():
                # Empty input - skip with neutral score
                results.append(EvaluationResult(
                    score=50.0,
                    reasoning="Test input was empty - using neutral score",
                    breakdown={"accuracy": 12.5, "relevance": 12.5, "clarity": 12.5, "instruction_following": 12.5}
                ))
                continue

            # Execute the prompt with the input
            try:
                response = executor_fn(prompt, input_text)
                result = self.evaluate(prompt, input_text, response)
                results.append(result)
            except Exception as e:
                logger.error(f"Execution failed: {e}")
                results.append(EvaluationResult(
                    score=0.0,
                    reasoning=f"Execution failed: {str(e)}",
                    breakdown={"accuracy": 0, "relevance": 0, "clarity": 0, "instruction_following": 0}
                ))

        return tuple(results)

    def set_custom_rubric(self, rubric: str):
        """
        Allow users to customize the evaluation criteria.
        
        Args:
            rubric: Custom evaluation criteria to append to system prompt
        """
        self.system_prompt = f"""{EVALUATOR_SYSTEM_PROMPT}

ADDITIONAL USER-DEFINED CRITERIA:
{rubric}"""


class HumanOverrideEvaluator(Evaluator):
    """
    Extended evaluator that stores human override scores.
    
    The UI can call human_override() to replace LLM scores with human judgment.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._overrides: dict = {}  # candidate_id -> (score, reasoning)

    def human_override(self, candidate_id: str, score: float, reasoning: str = ""):
        """Store a human override for a candidate."""
        self._overrides[candidate_id] = (score, reasoning)

    def get_override(self, candidate_id: str) -> Optional[Tuple[float, str]]:
        """Get human override if exists."""
        return self._overrides.get(candidate_id)

    def clear_override(self, candidate_id: str):
        """Remove a human override."""
        self._overrides.pop(candidate_id, None)
