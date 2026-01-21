"""
APE Engine - Automatic Prompt Engineer (Zhou et al., 2022)

Implements reverse-engineering/induction approach where the LLM
deduces the instruction from input-output examples.
"""

import logging
import re
from typing import List, Dict, Any, Tuple

from glassbox.core.optimizer_base import AbstractOptimizer, StepResult
from glassbox.core.api_client import Message
from glassbox.models.session import SchematicState
from glassbox.models.candidate import UnifiedCandidate
from glassbox.prompts.templates import (
    APE_INDUCTION_SYSTEM_PROMPT,
    APE_INDUCTION_USER_TEMPLATE,
    APE_RESAMPLE_TEMPLATE,
    MONOLOGUE_APE
)

logger = logging.getLogger(__name__)


class APEEngine(AbstractOptimizer):
    """
    APE (Automatic Prompt Engineer) Engine.
    
    Algorithm:
    1. User provides 3-5 input-output examples
    2. Induction: LLM deduces the "hidden instruction" that maps input→output
    3. Resampling: Generate N variations of the deduced instruction
    4. Evaluation: Run all variations against test bench
    5. Selection: Highest average score wins
    
    Glass Box Visualization:
    - Schematic: Funnel (wide top → narrow bottom)
    - Nodes: [Examples] → [Induction Engine] → [Candidate Prompts]
    - Animation: Particles flow from examples through funnel
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.examples: List[Tuple[str, str]] = []  # (input, output) pairs
        self._deduced_instruction: str = ""
        self._induction_complete: bool = False

    @property
    def engine_name(self) -> str:
        return "APE (Reverse Eng)"

    @property
    def schematic_type(self) -> str:
        return "funnel"

    def set_examples(self, examples: List[Tuple[str, str]]):
        """Set the input-output examples for induction."""
        self.examples = examples
        self._induction_complete = False
        self._deduced_instruction = ""

    def step(self) -> StepResult:
        """
        Execute one APE optimization step.
        
        Step 1: Induction (if not done)
        Step 2+: Resampling and evaluation
        """
        self.session.current_step += 1
        step_num = self.session.current_step

        # Phase 1: Induction (first step only)
        if not self._induction_complete:
            self.session.schematic_state = SchematicState.INDUCTION
            self.session.active_node = "induction"
            self._update_monologue("Analyzing examples...", "induction", 0)
            
            self._deduced_instruction = self._perform_induction()
            self._induction_complete = True
            
            if not self._deduced_instruction:
                return StepResult(
                    candidates=[],
                    best_candidate=None,
                    step_number=step_num,
                    schematic_state=SchematicState.IDLE,
                    active_node="",
                    internal_monologue="Induction failed - no instruction deduced",
                    should_stop=True,
                    error_message="Induction failed"
                )

        # Phase 2: Resampling
        self.session.schematic_state = SchematicState.MUTATION
        self.session.active_node = "induction"
        self._update_monologue(f"Generating variations of: {self._deduced_instruction[:50]}...", "resampling", 75)
        
        variations = self._generate_variations()

        # Phase 3: Evaluation
        self.session.schematic_state = SchematicState.EVALUATION
        self.session.active_node = "candidates"
        
        step_candidates = []
        for i, prompt_text in enumerate(variations):
            if self._stop_requested.is_set():
                break
            
            candidate = self._evaluate_candidate(prompt_text, step_num)
            step_candidates.append(candidate)
            self.session.candidates.append(candidate)

        # Select best
        best = max(step_candidates, key=lambda c: c.score_aggregate) if step_candidates else None
        
        if best:
            self._add_trajectory_entry(best)
            self.session.winner = self.session.get_best_candidate()

        self.session.schematic_state = SchematicState.IDLE
        self.session.active_node = ""

        return StepResult(
            candidates=step_candidates,
            best_candidate=best,
            step_number=step_num,
            schematic_state=SchematicState.IDLE,
            active_node="",
            internal_monologue=self.session.internal_monologue,
            should_stop=step_num >= 3  # APE typically converges in few steps
        )

    def _perform_induction(self) -> str:
        """Deduce the hidden instruction from examples."""
        if len(self.examples) < 2:
            # Use seed prompt and test bench as examples
            self.examples = [
                (self.session.test_bench.input_a, ""),  # Will use API to generate ideal
                (self.session.test_bench.input_b, ""),
            ]
            return self.session.seed_prompt  # Fallback to seed

        # Format examples for induction prompt
        example_texts = {}
        for i, (inp, out) in enumerate(self.examples[:3], 1):
            example_texts[f"input_{i}"] = inp
            example_texts[f"output_{i}"] = out

        user_prompt = APE_INDUCTION_USER_TEMPLATE.format(**example_texts)

        messages = [
            Message(role="system", content=APE_INDUCTION_SYSTEM_PROMPT),
            Message(role="user", content=user_prompt)
        ]

        response = self.api_client.send_message(messages, temperature=0.3)
        
        if response.success:
            return response.content.strip()
        else:
            logger.error(f"Induction failed: {response.error_message}")
            return ""

    def _generate_variations(self) -> List[str]:
        """Generate variations of the deduced instruction."""
        num_variations = self.session.config.generations_per_step

        user_prompt = APE_RESAMPLE_TEMPLATE.format(
            base_instruction=self._deduced_instruction,
            num_variations=num_variations
        )

        messages = [
            Message(role="user", content=user_prompt)
        ]

        response = self.api_client.send_message(
            messages,
            temperature=self.session.config.temperature
        )

        if not response.success:
            return [self._deduced_instruction]  # Fallback to base

        # Parse numbered variations
        variations = []
        lines = response.content.strip().split('\n')
        current_var = ""
        
        for line in lines:
            # Check for numbered line
            if re.match(r'^\d+[\.\)]\s*', line):
                if current_var:
                    variations.append(current_var.strip())
                current_var = re.sub(r'^\d+[\.\)]\s*', '', line)
            else:
                current_var += " " + line
        
        if current_var:
            variations.append(current_var.strip())

        # Always include the original
        if self._deduced_instruction not in variations:
            variations.insert(0, self._deduced_instruction)

        return variations[:num_variations + 1]

    def _evaluate_candidate(self, prompt_text: str, generation: int) -> UnifiedCandidate:
        """Evaluate candidate against test bench."""
        test_inputs = [
            (self.session.test_bench.input_a, "a"),
            (self.session.test_bench.input_b, "b"),
            (self.session.test_bench.input_c, "c"),
        ]

        scores = {}
        responses = {}
        reasoning = {}
        
        for input_text, label in test_inputs:
            key = f"input_{label}"
            
            if not input_text.strip():
                scores[key] = 50.0
                responses[key] = ""
                reasoning[key] = "Test input empty"
                continue

            try:
                response = self._execute_prompt(prompt_text, input_text)
                responses[key] = response
                
                eval_result = self.evaluator.evaluate(prompt_text, input_text, response)
                scores[key] = eval_result.score
                reasoning[key] = eval_result.reasoning
                
            except Exception as e:
                scores[key] = 0.0
                responses[key] = ""
                reasoning[key] = f"Error: {str(e)}"
        
        # Calculate aggregate
        valid_scores = [v for v in scores.values()]
        aggregate = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0

        return UnifiedCandidate(
            engine_type=self.engine_type_enum,
            generation_index=generation,
            display_text=f"Instruction: {prompt_text}", # Per spec 6.2.2 requirement
            full_content=prompt_text,
            score_aggregate=aggregate,
            test_results=scores,
            meta={
                "test_details": {
                    "responses": responses,
                    "reasoning": reasoning
                },
                "deduced_from_indices": list(range(len(self.examples))) if self.examples else []
            }
        )

    @property
    def engine_type_enum(self):
        from glassbox.models.candidate import EngineType
        return EngineType.APE

    def _update_monologue(self, instruction_preview: str, phase: str, confidence: int):
        """Update Glass Box monologue."""
        self.session.internal_monologue = MONOLOGUE_APE.format(
            num_examples=len(self.examples),
            confidence=confidence,
            instruction_preview=instruction_preview,
            num_variations=self.session.config.generations_per_step
        )

    def get_schematic_nodes(self) -> List[Dict[str, Any]]:
        """Return funnel schematic nodes."""
        active = self.session.active_node

        def node_color(node_id: str) -> str:
            if active == node_id:
                return "#20C20E"
            return "#31333F"

        return [
            {"id": "examples", "label": "Examples\\n(Input→Output)", "active": active == "examples", 
             "color": node_color("examples"), "shape": "box"},
            {"id": "induction", "label": "Induction\\nEngine", "active": active == "induction",
             "color": node_color("induction"), "shape": "trapezium"},
            {"id": "candidates", "label": "Candidate\\nPrompts", "active": active == "candidates",
             "color": node_color("candidates"), "shape": "box"}
        ]

    def get_schematic_edges(self) -> List[Dict[str, Any]]:
        """Return funnel schematic edges."""
        state = self.session.schematic_state
        return [
            {"source": "examples", "target": "induction", "color": "#EAB308",
             "active": state == SchematicState.INDUCTION, "label": ""},
            {"source": "induction", "target": "candidates", "color": "#3B82F6",
             "active": state == SchematicState.MUTATION, "label": ""}
        ]

    def generate_graphviz(self) -> str:
        """Generate Graphviz DOT for funnel schematic."""
        nodes = self.get_schematic_nodes()
        edges = self.get_schematic_edges()

        dot_lines = [
            "digraph APE {",
            '    rankdir=TB;',
            '    bgcolor="#0E1117";',
            '    node [style=filled, fontcolor=white, fontname="Helvetica"];',
            ""
        ]

        for node in nodes:
            penwidth = "3" if node["active"] else "1"
            dot_lines.append(
                f'    {node["id"]} [label="{node["label"]}", fillcolor="{node["color"]}", '
                f'shape={node["shape"]}, penwidth={penwidth}];'
            )

        dot_lines.append("")

        for edge in edges:
            penwidth = "3" if edge["active"] else "1"
            dot_lines.append(
                f'    {edge["source"]} -> {edge["target"]} [color="{edge["color"]}", penwidth={penwidth}];'
            )

        dot_lines.append("}")
        return "\n".join(dot_lines)
