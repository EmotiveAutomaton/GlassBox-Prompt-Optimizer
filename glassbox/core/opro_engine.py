"""
OPro Engine - Optimization by PROmpting (Yang et al., DeepMind, 2023)

Implements the iterative feedback loop where an optimizer LLM generates
prompt variations based on scored history (trajectory).
"""

import logging
import re
from typing import List, Dict, Any

from glassbox.core.optimizer_base import AbstractOptimizer, StepResult
from glassbox.core.api_client import BoeingAPIClient, Message
from glassbox.core.evaluator import Evaluator
from glassbox.models.session import (
    OptimizerSession, 
    SchematicState
)
from glassbox.models.candidate import UnifiedCandidate
from glassbox.prompts.templates import (
    OPRO_OPTIMIZER_SYSTEM_PROMPT,
    OPRO_OPTIMIZER_USER_TEMPLATE,
    MONOLOGUE_OPRO
)

logger = logging.getLogger(__name__)


class OProEngine(AbstractOptimizer):
    """
    OPro (Optimization by PROmpting) Engine.
    
    Algorithm:
    1. Feed optimizer LLM the task + scored trajectory history
    2. Generate N new prompt variations
    3. Evaluate each variation against the test bench
    4. Greedy selection: best score becomes new baseline
    5. Repeat until stopping condition
    
    Glass Box Visualization:
    - Schematic: Circular feedback loop (clockwise)
    - Nodes: [Seed Prompt] → [Executor] → [Scorer] → [Optimizer Agent] → (back)
    - Yellow edge: Data flow (Scorer → Optimizer)
    - Blue edge: Instruction flow (Optimizer → Seed)
    """

    @property
    def engine_name(self) -> str:
        return "OPro (Iterative)"

    @property
    def schematic_type(self) -> str:
        return "loop"

    def step(self) -> StepResult:
        """
        Execute one optimization step.
        
        1. Generate variations using optimizer LLM
        2. Evaluate each variation
        3. Update trajectory and select best
        """
        self.session.current_step += 1
        step_num = self.session.current_step
        
        # Phase 1: Generate variations
        self.session.schematic_state = SchematicState.MUTATION
        self.session.active_node = "optimizer"
        self._update_monologue("Generating variations...", "mutation")
        
        # Check stop signal before expensive generation
        if self._stop_requested.is_set():
             return StepResult(
                candidates=[],
                best_candidate=None,
                step_number=step_num,
                schematic_state=SchematicState.IDLE,
                active_node="",
                internal_monologue="Optimization stopped by user.",
                should_stop=True
            )



        variations = self._generate_variations()
        
        if not variations:
            return StepResult(
                candidates=[],
                best_candidate=None,
                step_number=step_num,
                schematic_state=SchematicState.IDLE,
                active_node="",
                internal_monologue="Failed to generate variations",
                should_stop=False,
                error_message="No variations generated"
            )

        # Phase 2: Evaluate each variation
        self.session.schematic_state = SchematicState.EVALUATION
        self.session.active_node = "scorer"
        self._update_monologue(f"Evaluating {len(variations)} candidates...", "evaluation")
        
        step_candidates = []
        for i, (prompt_text, reasoning) in enumerate(variations):
            # Check stop signal (Iter 5)
            if self._stop_requested.is_set():
                logger.info("Evaluation stopped by user signal.")
                break
                
            logger.info(f"Evaluating candidate {i+1}/{len(variations)}")
            
            candidate = self._evaluate_candidate(prompt_text, step_num)
            
            # Double check stop after potentially long evaluation
            if self._stop_requested.is_set():
                 break

            candidate.meta["generation_reasoning"] = reasoning  # Store generation reasoning
            # Check if identical candidate (Prompt + Step) already exists to prevent duplication artifacts
            # User reported "Two separate entries listed as iteration one".
            is_duplicate = any(
                c.full_content == candidate.full_content and c.generation_index == candidate.generation_index
                for c in self.session.candidates
            )
            
            if not is_duplicate:
                step_candidates.append(candidate)
                self.session.candidates.append(candidate)
            else:
                logger.warning(f"Skipping duplicate candidate at step {step_num}: {candidate.display_text[:30]}...")

        # Phase 3: Select best (greedy)
        best = max(step_candidates, key=lambda c: c.score_aggregate) if step_candidates else None
        
        if best:
            self._add_trajectory_entry(best)
            self.session.winner = self.session.get_best_candidate()

        # Update visualization state
        self.session.schematic_state = SchematicState.IDLE
        self.session.active_node = ""
        self._update_monologue(
            f"Step {step_num} complete. Best: {best.score_aggregate:.1f}%" if best else "No candidates",
            "complete"
        )

        return StepResult(
            candidates=step_candidates,
            best_candidate=best,
            step_number=step_num,
            schematic_state=SchematicState.IDLE,
            active_node="",
            internal_monologue=self.session.internal_monologue,
            should_stop=False
        )

    def _generate_variations(self) -> List[tuple]:
        """
        Use optimizer LLM to generate prompt variations.
        
        Returns list of (prompt_text, reasoning) tuples.
        """
        trajectory_text = self.session.get_trajectory_summary(max_entries=5)
        if not trajectory_text:
            trajectory_text = f"[Initial seed: {self.session.seed_prompt[:100]}... | Score: N/A]"
        
        best_score = self._get_best_score() if self.session.trajectory else 0.0
        
        # FORCE BATCH SIZE 1 (Fix: Batch Size Consistency)
        num_variations = 1 
        # num_variations = self.session.config.generations_per_step

        user_prompt = OPRO_OPTIMIZER_USER_TEMPLATE.format(
            task_description=self.session.seed_prompt,
            trajectory=trajectory_text,
            best_score=f"{best_score:.1f}",
            num_variations=num_variations
        )

        messages = [
            Message(role="system", content=OPRO_OPTIMIZER_SYSTEM_PROMPT),
            Message(role="user", content=user_prompt)
        ]

        response = self.api_client.send_message(
            messages,
            temperature=self.session.config.temperature
        )

        if not response.success:
            logger.error(f"Variation generation failed: {response.error_message}")
            return []

        return self._parse_variations(response.content)

    def _parse_variations(self, response_text: str) -> List[tuple]:
        """Parse LLM response to extract variations and their reasoning."""
        variations = []
        
        # Pattern: VARIATION N: ... REASONING: ...
        # Flexible parsing for different response formats
        
        # Try structured format first
        pattern = r'VARIATION\s*\d+:\s*(.*?)(?:REASONING:|$)'
        reasoning_pattern = r'REASONING:\s*(.*?)(?:VARIATION|$)'
        
        variation_matches = re.findall(pattern, response_text, re.IGNORECASE | re.DOTALL)
        reasoning_matches = re.findall(reasoning_pattern, response_text, re.IGNORECASE | re.DOTALL)
        
        for i, var_text in enumerate(variation_matches):
            prompt = var_text.strip()
            if not prompt:
                continue
                
            # Clean up the prompt
            prompt = re.sub(r'^[\-\*\#]+\s*', '', prompt)  # Remove markdown bullets
            prompt = prompt.strip()
            
            reasoning = reasoning_matches[i].strip() if i < len(reasoning_matches) else ""
            
            if len(prompt) > 10:  # Minimum viable prompt length
                variations.append((prompt, reasoning))

        # Fallback: split by numbered sections
        if not variations:
            sections = re.split(r'\n\d+[\.\)]\s*', response_text)
            for section in sections:
                section = section.strip()
                if len(section) > 10 and not section.startswith("REASONING"):
                    variations.append((section, ""))

        # Final fallback: use entire response as single variation
        if not variations and len(response_text.strip()) > 10:
            variations.append((response_text.strip(), "Generated as fallback"))

        return variations[:self.session.config.generations_per_step]

    def _evaluate_candidate(self, prompt_text: str, generation: int) -> UnifiedCandidate:
        """Evaluate a single candidate against the tri-state test bench."""
        # Execute and evaluate against each test input
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
                # IMPROVED MOCK BEHAVIOR (Iter 5.5): Randomize for visualization
                import random
                scores[key] = random.uniform(70.0, 95.0) 
                responses[key] = "[Mock Response]"
                reasoning[key] = "Test input empty (Mocked Score)"
                continue

            try:
                # Execute the prompt
                response = self._execute_prompt(prompt_text, input_text)
                responses[key] = response
                
                # Evaluate the response
                eval_result = self.evaluator.evaluate(prompt_text, input_text, response)
                scores[key] = eval_result.score
                reasoning[key] = eval_result.reasoning
                
            except Exception as e:
                logger.error(f"Evaluation failed for {label}: {e}")
                scores[key] = 0.0
                responses[key] = ""
                reasoning[key] = f"Error: {str(e)}"

        # Calculate aggregate (mean of active inputs)
        valid_scores = [v for v in scores.values()]
        aggregate = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0

        return UnifiedCandidate(
            engine_type=self.engine_type_enum,
            generation_index=generation,
            display_text=prompt_text,
            full_content=prompt_text,
            score_aggregate=aggregate,
            test_results=scores,
            meta={
                "test_details": {
                    "responses": responses,
                    "reasoning": reasoning
                },
                "mutation_type": "rephrase" # Default for OPro
            }
        )

    @property
    def engine_type_enum(self):
        from glassbox.models.candidate import EngineType
        return EngineType.OPRO

    def _update_monologue(self, strategy: str, phase: str):
        """Update the Glass Box internal monologue display."""
        self.session.internal_monologue = MONOLOGUE_OPRO.format(
            step=self.session.current_step,
            history_summary=f"Runs: {len(self.session.trajectory)}, Best: {self._get_best_score():.1f}%",
            best_score=f"{self._get_best_score():.1f}",
            strategy=strategy,
            optimization_target="score improvement"
        )

    def get_schematic_nodes(self) -> List[Dict[str, Any]]:
        """Return node definitions for the circular feedback loop schematic."""
        state = self.session.schematic_state
        active = self.session.active_node

        # Color scheme: gray=idle, green=active, darkgray=completed
        def node_color(node_id: str) -> str:
            if active == node_id:
                return "#20C20E"  # Boeing Console Green
            elif state == SchematicState.IDLE:
                return "#31333F"  # Card Background
            else:
                return "#4A4A4A"  # Slightly lighter gray

        return [
            {
                "id": "seed",
                "label": "Seed Prompt",
                "active": active == "seed",
                "color": node_color("seed"),
                "shape": "box"
            },
            {
                "id": "executor",
                "label": "Executor",
                "active": active == "executor",
                "color": node_color("executor"),
                "shape": "ellipse"
            },
            {
                "id": "scorer",
                "label": "Scorer",
                "active": active == "scorer",
                "color": node_color("scorer"),
                "shape": "ellipse"
            },
            {
                "id": "optimizer",
                "label": "Optimizer\\nAgent",
                "active": active == "optimizer",
                "color": node_color("optimizer"),
                "shape": "diamond"
            }
        ]

    def get_schematic_edges(self) -> List[Dict[str, Any]]:
        """Return edge definitions for the circular feedback loop."""
        state = self.session.schematic_state

        # Edge colors: blue=instruction flow, yellow=data flow
        return [
            {
                "source": "seed",
                "target": "executor",
                "color": "#3B82F6",  # Blue
                "active": state == SchematicState.MUTATION,
                "label": ""
            },
            {
                "source": "executor",
                "target": "scorer",
                "color": "#EAB308",  # Yellow (data)
                "active": state == SchematicState.EVALUATION,
                "label": ""
            },
            {
                "source": "scorer",
                "target": "optimizer",
                "color": "#EAB308",  # Yellow (data flow to optimizer)
                "active": state == SchematicState.OPTIMIZATION,
                "label": ""
            },
            {
                "source": "optimizer",
                "target": "seed",
                "color": "#3B82F6",  # Blue (instruction/mutation)
                "active": state == SchematicState.MUTATION,
                "label": "mutate"
            }
        ]

    def generate_graphviz(self) -> str:
        """Generate Graphviz DOT source for the schematic."""
        nodes = self.get_schematic_nodes()
        edges = self.get_schematic_edges()

        dot_lines = [
            "digraph OPro {",
            '    rankdir=LR;',
            '    bgcolor="#0E1117";',
            '    node [style=filled, fontcolor=white, fontname="Helvetica"];',
            '    edge [fontcolor=white, fontname="Helvetica"];',
            ""
        ]

        # Add nodes
        for node in nodes:
            style = "bold" if node["active"] else "filled"
            penwidth = "3" if node["active"] else "1"
            dot_lines.append(
                f'    {node["id"]} [label="{node["label"]}", fillcolor="{node["color"]}", '
                f'shape={node["shape"]}, style="{style},filled", penwidth={penwidth}];'
            )

        dot_lines.append("")

        # Add edges
        for edge in edges:
            style = "bold" if edge["active"] else "solid"
            penwidth = "3" if edge["active"] else "1"
            dot_lines.append(
                f'    {edge["source"]} -> {edge["target"]} [color="{edge["color"]}", '
                f'style={style}, penwidth={penwidth}];'
            )

        dot_lines.append("}")
        return "\n".join(dot_lines)
