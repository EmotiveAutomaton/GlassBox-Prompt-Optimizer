"""
S2A Engine - System 2 Attention (Weston et al., Meta, 2023)

Implements context filtering for RAG scenarios by training a filter
to remove noise and bias from retrieved context.
"""

import logging
import re
from typing import List, Dict, Any, Tuple

from glassbox.core.optimizer_base import AbstractOptimizer, StepResult
from glassbox.core.api_client import Message
from glassbox.models.session import SchematicState
from glassbox.models.candidate import UnifiedCandidate
from glassbox.prompts.templates import (
    S2A_FILTER_SYSTEM_PROMPT,
    S2A_FILTER_USER_TEMPLATE,
    S2A_OPTIMIZER_TEMPLATE,
    MONOLOGUE_S2A
)

logger = logging.getLogger(__name__)


class S2AEngine(AbstractOptimizer):
    """
    S2A (System 2 Attention) Engine.
    
    Algorithm:
    1. Take raw context with potential noise
    2. Apply S2A filter to extract unbiased, relevant content
    3. Pass filtered context to model for final response
    4. Optimize the filter prompt to minimize noise passing through
    
    Glass Box Visualization:
    - Schematic: Linear assembly line with filter gate
    - Nodes: [Raw Context] → [S2A Filter] → [Clean Context] → [Final Response]
    - Animation: Blocks shrink as they pass through filter
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_filter_prompt = S2A_FILTER_SYSTEM_PROMPT
        self._filter_variations: List[str] = []
        self._pass_number = 0

    @property
    def engine_name(self) -> str:
        return "S2A (Context Filter)"

    @property
    def schematic_type(self) -> str:
        return "conveyor"

    @property
    def engine_type_enum(self):
        from glassbox.models.candidate import EngineType
        return EngineType.S2A

    def set_context(self, raw_context: str, query: str):
        """Set the raw context and query for filtering."""
        self._raw_context = raw_context
        self._query = query

    def step(self) -> StepResult:
        """Execute one S2A optimization step."""
        self.session.current_step += 1
        self._pass_number += 1

        # Phase 1: Apply filter to get clean context
        self.session.schematic_state = SchematicState.FILTERING
        self.session.active_node = "filter"
        self._update_monologue("Filtering context...", self._pass_number, 0, 0)

        raw_context = getattr(self, '_raw_context', self.session.test_bench.input_a)
        query = getattr(self, '_query', self.session.seed_prompt)

        filter_result = self._apply_filter(raw_context, query)
        clean_context = filter_result.get("clean", raw_context)
        filtered_out = filter_result.get("filtered", [])

        # Phase 2: Generate response with clean context
        self.session.schematic_state = SchematicState.EVALUATION
        self.session.active_node = "response"

        response = self._generate_response(clean_context, query)

        # Phase 3: Evaluate quality
        eval_result = self.evaluator.evaluate(
            self._current_filter_prompt,
            f"Context: {raw_context}\nQuery: {query}",
            response
        )

        # Phase 4: Optimize filter (if score is low)
        if eval_result.score < 80 and self._pass_number < 5:
            self.session.schematic_state = SchematicState.OPTIMIZATION
            self.session.active_node = "optimizer"
            
            new_filter = self._optimize_filter(
                eval_result.score,
                filtered_out,
                []  # Would track false negatives with ground truth
            )
            if new_filter:
                self._filter_variations.append(new_filter)
                self._current_filter_prompt = new_filter

        # Create candidate result
        input_tokens = len(raw_context.split())
        output_tokens = len(clean_context.split())
        noise_reduction = (1 - output_tokens / max(input_tokens, 1)) if input_tokens else 0.0

        scores = {"input_a": eval_result.score} # Primary
        responses = {"input_a": response}
        
        candidate = UnifiedCandidate(
            engine_type=self.engine_type_enum,
            generation_index=self._pass_number,
            display_text=f"Strategy: {self._current_filter_prompt}",
            full_content=self._current_filter_prompt,
            score_aggregate=eval_result.score,
            test_results=scores,
            meta={
                "clean_context": clean_context,
                "filtered_items": filtered_out,
                "noise_reduction_rate": noise_reduction,
                "mutation_type": "s2a_optimization",
                "test_details": {
                    "responses": responses,
                    "reasoning": {"input_a": eval_result.reasoning}
                }
            }
        )

        # Quick evaluation on other test inputs
        for label, input_text in [("b", self.session.test_bench.input_b), 
                                   ("c", self.session.test_bench.input_c)]:
            key = f"input_{label}"
            if input_text.strip():
                try:
                    filtered = self._apply_filter(input_text, query)
                    resp = self._generate_response(filtered.get("clean", input_text), query)
                    ev = self.evaluator.evaluate(self._current_filter_prompt, input_text, resp)
                    
                    candidate.test_results[key] = ev.score
                    candidate.score_aggregate = (candidate.score_aggregate + ev.score) / 2 # simplified avg
                    candidate.meta["test_details"]["responses"][key] = resp
                    candidate.meta["test_details"]["reasoning"][key] = ev.reasoning
                    
                except Exception as e:
                    candidate.test_results[key] = 0.0
                    candidate.meta["test_details"]["responses"][key] = ""
                    candidate.meta["test_details"]["reasoning"][key] = f"Error: {e}"

        self.session.candidates.append(candidate)
        self._add_trajectory_entry(candidate)
        self.session.winner = self.session.get_best_candidate()

        self.session.schematic_state = SchematicState.IDLE
        self.session.active_node = ""

        self._update_monologue(
            f"Pass {self._pass_number} complete",
            self._pass_number,
            input_tokens,
            output_tokens
        )

        return StepResult(
            candidates=[candidate],
            best_candidate=candidate,
            step_number=self.session.current_step,
            schematic_state=SchematicState.IDLE,
            active_node="",
            internal_monologue=self.session.internal_monologue,
            should_stop=eval_result.score >= 90 or self._pass_number >= 5
        )

    def _apply_filter(self, raw_context: str, query: str) -> Dict[str, Any]:
        """Apply S2A filter to extract clean context."""
        user_prompt = S2A_FILTER_USER_TEMPLATE.format(
            raw_context=raw_context,
            query=query
        )

        messages = [
            Message(role="system", content=self._current_filter_prompt),
            Message(role="user", content=user_prompt)
        ]

        response = self.api_client.send_message(messages, temperature=0.3)

        if not response.success:
            return {"clean": raw_context, "filtered": []}

        # Parse the structured response
        content = response.content
        
        # Extract UNBIASED CONTEXT section
        clean_match = re.search(
            r'UNBIASED CONTEXT:\s*(.*?)(?:FILTERED OUT:|$)',
            content,
            re.DOTALL | re.IGNORECASE
        )
        clean_context = clean_match.group(1).strip() if clean_match else raw_context

        # Extract FILTERED OUT section
        filtered_match = re.search(
            r'FILTERED OUT:\s*(.*?)$',
            content,
            re.DOTALL | re.IGNORECASE
        )
        filtered_items = []
        if filtered_match:
            filtered_text = filtered_match.group(1).strip()
            filtered_items = [line.strip() for line in filtered_text.split('\n') if line.strip()]

        return {"clean": clean_context, "filtered": filtered_items}

    def _generate_response(self, clean_context: str, query: str) -> str:
        """Generate final response using filtered context."""
        # Standard RAG pattern from Boeing spec Section 3.4
        prompt = f"""Context Information:
---
{clean_context}
---

Instruction: Based on the context above, {query}"""

        messages = [
            Message(role="system", content=self.session.seed_prompt),
            Message(role="user", content=prompt)
        ]

        response = self.api_client.send_message(
            messages,
            temperature=self.session.config.temperature
        )

        return response.content if response.success else "Response generation failed"

    def _optimize_filter(
        self,
        score: float,
        false_positives: List[str],
        false_negatives: List[str]
    ) -> str:
        """Generate improved filter prompt based on observed issues."""
        prompt = S2A_OPTIMIZER_TEMPLATE.format(
            score=score,
            current_prompt=self._current_filter_prompt,
            false_positives=", ".join(false_positives[:3]) if false_positives else "None observed",
            false_negatives=", ".join(false_negatives[:3]) if false_negatives else "Unknown"
        )

        messages = [Message(role="user", content=prompt)]
        response = self.api_client.send_message(messages, temperature=0.5)

        return response.content if response.success else ""

    def _update_monologue(self, status: str, pass_num: int, input_tokens: int, output_tokens: int):
        """Update Glass Box monologue."""
        compression = int((1 - output_tokens / max(input_tokens, 1)) * 100) if input_tokens else 0
        self.session.internal_monologue = MONOLOGUE_S2A.format(
            pass_num=pass_num,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            compression_ratio=compression,
            noise_items=len(getattr(self, '_last_filtered', []))
        )

    def get_schematic_nodes(self) -> List[Dict[str, Any]]:
        """Return conveyor schematic nodes."""
        active = self.session.active_node

        def node_color(node_id: str) -> str:
            if active == node_id:
                return "#20C20E"
            return "#31333F"

        return [
            {"id": "raw", "label": "Raw\\nContext", "active": active == "raw",
             "color": node_color("raw"), "shape": "box"},
            {"id": "filter", "label": "S2A\\nFilter", "active": active == "filter",
             "color": node_color("filter"), "shape": "octagon"},
            {"id": "clean", "label": "Clean\\nContext", "active": active == "clean",
             "color": node_color("clean"), "shape": "box"},
            {"id": "response", "label": "Final\\nResponse", "active": active == "response",
             "color": node_color("response"), "shape": "box"}
        ]

    def get_schematic_edges(self) -> List[Dict[str, Any]]:
        """Return conveyor schematic edges."""
        state = self.session.schematic_state
        return [
            {"source": "raw", "target": "filter", "color": "#EAB308",
             "active": state == SchematicState.FILTERING, "label": ""},
            {"source": "filter", "target": "clean", "color": "#3B82F6",
             "active": state == SchematicState.FILTERING, "label": ""},
            {"source": "clean", "target": "response", "color": "#3B82F6",
             "active": state == SchematicState.EVALUATION, "label": ""}
        ]

    def generate_graphviz(self) -> str:
        """Generate Graphviz DOT for conveyor schematic."""
        nodes = self.get_schematic_nodes()
        edges = self.get_schematic_edges()

        dot_lines = [
            "digraph S2A {",
            '    rankdir=LR;',
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

        for edge in edges:
            penwidth = "3" if edge["active"] else "1"
            dot_lines.append(
                f'    {edge["source"]} -> {edge["target"]} [color="{edge["color"]}", penwidth={penwidth}];'
            )

        dot_lines.append("}")
        return "\n".join(dot_lines)
