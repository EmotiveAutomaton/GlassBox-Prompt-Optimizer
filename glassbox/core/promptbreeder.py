"""
Promptbreeder Engine - Self-Referential Self-Improvement (Fernando et al., DeepMind, 2023)

Implements evolutionary approach with population of "units" containing
both task-prompts and mutation-prompts that co-evolve.
"""

import logging
import random
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from glassbox.core.optimizer_base import AbstractOptimizer, StepResult
from glassbox.core.api_client import Message
from glassbox.models.session import CandidateResult, SchematicState
from glassbox.prompts.templates import (
    PROMPTBREEDER_ZERO_ORDER_MUTATION,
    PROMPTBREEDER_FIRST_ORDER_MUTATION,
    PROMPTBREEDER_MUTATION_PROMPTS,
    PROMPTBREEDER_CROSSOVER_TEMPLATE,
    MONOLOGUE_PROMPTBREEDER
)

logger = logging.getLogger(__name__)


@dataclass
class EvolutionaryUnit:
    """A unit in the Promptbreeder population."""
    id: str
    task_prompt: str
    mutation_prompt: str
    fitness: float = 0.0
    generation: int = 0
    parent_ids: List[str] = field(default_factory=list)


class PromptbreederEngine(AbstractOptimizer):
    """
    Promptbreeder (Evolutionary) Engine.
    
    Algorithm:
    1. Initialize population of N units (task-prompt + mutation-prompt pairs)
    2. Evaluate fitness of each unit's task-prompt
    3. Apply mutation operators:
       - Zero-Order: Direct rewrite (e.g., "make more formal")
       - First-Order: Mutation-prompt modifies task-prompt
       - Crossover: Combine task from A with mutation from B
    4. Tournament selection: Kill bottom 50%, clone top 50%
    5. Repeat
    
    Glass Box Visualization:
    - Schematic: Horizontal branching tree (phylogenetic)
    - Nodes: Generation columns with branching
    - Animation: Branches grow, failed ones gray out
    """

    POPULATION_SIZE = 8  # Smaller than paper's 20 for hackathon
    MUTATION_OPERATORS = ["zero_order", "first_order", "crossover"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.population: List[EvolutionaryUnit] = []
        self._generation = 0
        self._mutation_directions = [
            "more formal", "more concise", "more detailed",
            "step-by-step", "more technical", "simpler"
        ]

    @property
    def engine_name(self) -> str:
        return "Promptbreeder (Evolutionary)"

    @property
    def schematic_type(self) -> str:
        return "tree"

    def _initialize_population(self):
        """Create initial population from seed prompt."""
        self.population = []
        seed = self.session.seed_prompt

        for i in range(self.POPULATION_SIZE):
            mutation_prompt = random.choice(PROMPTBREEDER_MUTATION_PROMPTS)
            unit = EvolutionaryUnit(
                id=f"g0_u{i}",
                task_prompt=seed if i == 0 else f"{seed}\n\n(Variation {i})",
                mutation_prompt=mutation_prompt,
                generation=0
            )
            self.population.append(unit)

    def step(self) -> StepResult:
        """Execute one evolutionary generation."""
        self.session.current_step += 1
        self._generation += 1

        # Initialize on first step
        if not self.population:
            self._initialize_population()

        # Phase 1: Evaluate fitness
        self.session.schematic_state = SchematicState.EVALUATION
        self.session.active_node = "evaluation"
        self._update_monologue("Evaluating population fitness...", "tournament")

        for unit in self.population:
            if self._stop_requested.is_set():
                break
            if unit.fitness == 0.0:  # Only evaluate unevaluated units
                unit.fitness = self._evaluate_fitness(unit.task_prompt)

        # Phase 2: Selection (Tournament)
        self.population.sort(key=lambda u: u.fitness, reverse=True)
        survivors = self.population[:len(self.population) // 2]
        
        # Phase 3: Mutation/Reproduction
        self.session.schematic_state = SchematicState.GROWTH
        self.session.active_node = "mutation"
        
        new_population = list(survivors)  # Clone survivors
        
        for survivor in survivors:
            if self._stop_requested.is_set():
                break
                
            operator = random.choice(self.MUTATION_OPERATORS)
            self._update_monologue(f"Applying {operator} to unit {survivor.id}", operator)
            
            child = self._apply_mutation(survivor, operator)
            if child:
                new_population.append(child)

        self.population = new_population[:self.POPULATION_SIZE]

        # Convert to CandidateResults for session tracking
        step_candidates = []
        for unit in self.population:
            candidate = CandidateResult(
                id=unit.id,
                prompt_text=unit.task_prompt,
                score_a=unit.fitness,
                score_b=unit.fitness * 0.9,  # Estimated
                score_c=unit.fitness * 0.8,
                generation=self._generation,
                mutation_operator=unit.mutation_prompt[:50]
            )
            step_candidates.append(candidate)
            
            # Add to session if not already there
            if not any(c.id == unit.id for c in self.session.candidates):
                self.session.candidates.append(candidate)

        best = max(step_candidates, key=lambda c: c.global_score)
        self._add_trajectory_entry(best)
        self.session.winner = self.session.get_best_candidate()

        self.session.schematic_state = SchematicState.IDLE
        self.session.active_node = ""

        return StepResult(
            candidates=step_candidates,
            best_candidate=best,
            step_number=self.session.current_step,
            schematic_state=SchematicState.IDLE,
            active_node="",
            internal_monologue=self.session.internal_monologue,
            should_stop=self._generation >= 10  # Max generations
        )

    def _evaluate_fitness(self, task_prompt: str) -> float:
        """Evaluate fitness using test bench input A (for speed)."""
        try:
            input_text = self.session.test_bench.input_a or "Test input"
            response = self._execute_prompt(task_prompt, input_text)
            eval_result = self.evaluator.evaluate(task_prompt, input_text, response)
            return eval_result.score
        except Exception as e:
            logger.error(f"Fitness evaluation failed: {e}")
            return 0.0

    def _apply_mutation(self, parent: EvolutionaryUnit, operator: str) -> Optional[EvolutionaryUnit]:
        """Apply mutation operator to create child unit."""
        try:
            if operator == "zero_order":
                return self._zero_order_mutation(parent)
            elif operator == "first_order":
                return self._first_order_mutation(parent)
            elif operator == "crossover":
                return self._crossover(parent)
        except Exception as e:
            logger.error(f"Mutation failed: {e}")
            return None

    def _zero_order_mutation(self, parent: EvolutionaryUnit) -> EvolutionaryUnit:
        """Direct rewrite mutation."""
        direction = random.choice(self._mutation_directions)
        
        prompt = PROMPTBREEDER_ZERO_ORDER_MUTATION.format(
            prompt=parent.task_prompt,
            mutation_direction=direction
        )

        messages = [Message(role="user", content=prompt)]
        response = self.api_client.send_message(messages, temperature=0.7)

        new_prompt = response.content if response.success else parent.task_prompt

        return EvolutionaryUnit(
            id=f"g{self._generation}_z{random.randint(0, 999)}",
            task_prompt=new_prompt,
            mutation_prompt=f"Zero-order: {direction}",
            generation=self._generation,
            parent_ids=[parent.id]
        )

    def _first_order_mutation(self, parent: EvolutionaryUnit) -> EvolutionaryUnit:
        """Mutation-prompt modifies task-prompt."""
        prompt = PROMPTBREEDER_FIRST_ORDER_MUTATION.format(
            task_prompt=parent.task_prompt,
            mutation_prompt=parent.mutation_prompt
        )

        messages = [Message(role="user", content=prompt)]
        response = self.api_client.send_message(messages, temperature=0.7)

        new_prompt = response.content if response.success else parent.task_prompt

        # Also evolve the mutation prompt
        new_mutation = random.choice(PROMPTBREEDER_MUTATION_PROMPTS)

        return EvolutionaryUnit(
            id=f"g{self._generation}_f{random.randint(0, 999)}",
            task_prompt=new_prompt,
            mutation_prompt=new_mutation,
            generation=self._generation,
            parent_ids=[parent.id]
        )

    def _crossover(self, parent: EvolutionaryUnit) -> EvolutionaryUnit:
        """Combine task from one unit with mutation from another."""
        # Find another high-fitness parent
        other_parents = [u for u in self.population if u.id != parent.id and u.fitness > 0]
        if not other_parents:
            return self._zero_order_mutation(parent)

        other = random.choice(other_parents)

        prompt = PROMPTBREEDER_CROSSOVER_TEMPLATE.format(
            prompt_a=parent.task_prompt,
            score_a=parent.fitness,
            prompt_b=other.task_prompt,
            score_b=other.fitness
        )

        messages = [Message(role="user", content=prompt)]
        response = self.api_client.send_message(messages, temperature=0.7)

        new_prompt = response.content if response.success else parent.task_prompt

        return EvolutionaryUnit(
            id=f"g{self._generation}_c{random.randint(0, 999)}",
            task_prompt=new_prompt,
            mutation_prompt=other.mutation_prompt,  # Take mutation from other parent
            generation=self._generation,
            parent_ids=[parent.id, other.id]
        )

    def _update_monologue(self, mutation_description: str, operator: str):
        """Update Glass Box monologue."""
        best_fitness = max((u.fitness for u in self.population), default=0)
        self.session.internal_monologue = MONOLOGUE_PROMPTBREEDER.format(
            generation=self._generation,
            population_size=len(self.population),
            mutation_operator=operator.replace("_", "-").title(),
            best_fitness=f"{best_fitness:.1f}",
            mutation_description=mutation_description
        )

    def get_schematic_nodes(self) -> List[Dict[str, Any]]:
        """Return tree schematic nodes (simplified for display)."""
        nodes = []
        # Show last 3 generations
        for gen in range(max(0, self._generation - 2), self._generation + 1):
            gen_units = [u for u in self.population if u.generation == gen]
            for i, unit in enumerate(gen_units[:4]):  # Max 4 per gen for display
                is_active = gen == self._generation
                color = "#20C20E" if unit.fitness >= 70 else "#EAB308" if unit.fitness >= 40 else "#EF4444"
                nodes.append({
                    "id": unit.id,
                    "label": f"G{gen}\\n{unit.fitness:.0f}%",
                    "active": is_active,
                    "color": color if is_active else "#4A4A4A",
                    "shape": "circle"
                })
        return nodes

    def get_schematic_edges(self) -> List[Dict[str, Any]]:
        """Return tree schematic edges based on parent relationships."""
        edges = []
        for unit in self.population:
            for parent_id in unit.parent_ids:
                if any(u.id == parent_id for u in self.population):
                    edges.append({
                        "source": parent_id,
                        "target": unit.id,
                        "color": "#3B82F6",
                        "active": unit.generation == self._generation,
                        "label": ""
                    })
        return edges

    def generate_graphviz(self) -> str:
        """Generate Graphviz DOT for tree schematic."""
        nodes = self.get_schematic_nodes()
        edges = self.get_schematic_edges()

        dot_lines = [
            "digraph Promptbreeder {",
            '    rankdir=LR;',
            '    bgcolor="#0E1117";',
            '    node [style=filled, fontcolor=white, fontname="Helvetica"];',
            ""
        ]

        for node in nodes:
            penwidth = "3" if node["active"] else "1"
            dot_lines.append(
                f'    "{node["id"]}" [label="{node["label"]}", fillcolor="{node["color"]}", '
                f'shape={node["shape"]}, penwidth={penwidth}];'
            )

        for edge in edges:
            penwidth = "2" if edge["active"] else "1"
            dot_lines.append(
                f'    "{edge["source"]}" -> "{edge["target"]}" [color="{edge["color"]}", penwidth={penwidth}];'
            )

        dot_lines.append("}")
        return "\n".join(dot_lines)
