"""
Prompt Templates - Meta-prompts for optimization engines and evaluation.

These prompts are based on the original research papers where available:
- OPro: Yang et al. (DeepMind, 2023) - "Large Language Models as Optimizers"
- APE: Zhou et al. (2022) - "Large Language Models Are Human-Level Prompt Engineers"
- Promptbreeder: Fernando et al. (Google DeepMind, 2023)
- S2A: Weston et al. (Meta, 2023) - "System 2 Attention"
"""

# =============================================================================
# LLM JUDGE / EVALUATOR PROMPTS
# =============================================================================

EVALUATOR_SYSTEM_PROMPT = """You are an expert prompt evaluator. Your task is to score how well an AI assistant's response addresses the given task.

EVALUATION CRITERIA:
1. **Accuracy** (0-25): Is the response factually correct and complete?
2. **Relevance** (0-25): Does the response directly address the task/question?
3. **Clarity** (0-25): Is the response well-structured and easy to understand?
4. **Instruction Following** (0-25): Does the response follow the exact instructions in the prompt?

SCORING RULES:
- Provide a score from 0-100 (sum of all criteria)
- Be strict but fair - reserve 90+ scores for exceptional responses
- Consider edge cases and adversarial inputs when scoring

OUTPUT FORMAT (JSON only):
{
    "score": <0-100>,
    "breakdown": {
        "accuracy": <0-25>,
        "relevance": <0-25>,
        "clarity": <0-25>,
        "instruction_following": <0-25>
    },
    "reasoning": "<1-2 sentence explanation of the score>"
}"""

EVALUATOR_USER_TEMPLATE = """TASK PROMPT:
{prompt}

INPUT PROVIDED:
{input_text}

AI RESPONSE TO EVALUATE:
{response}

Evaluate this response and provide your JSON score."""


# =============================================================================
# OPRO ENGINE PROMPTS (Yang et al., 2023)
# =============================================================================

OPRO_OPTIMIZER_SYSTEM_PROMPT = """You are an optimization expert. Your goal is to improve prompts to maximize their effectiveness.

You will be given:
1. A task description
2. A history of previous prompt attempts with their scores
3. (Optional) Patterns observed in high-scoring prompts

Your job is to generate a NEW prompt variation that is:
- Different from all previous attempts
- Likely to score higher than the current best
- Clear and specific in its instructions

Learn from the trajectory: What made high-scoring prompts work? What caused low scores?"""

OPRO_OPTIMIZER_USER_TEMPLATE = """TASK DESCRIPTION:
{task_description}

OPTIMIZATION HISTORY:
{trajectory}

Current best score: {best_score}

Generate {num_variations} new prompt variations that could score higher. 
For each variation, briefly explain your reasoning.

FORMAT:
---
VARIATION 1:
[Your improved prompt here]
REASONING: [Why this might score higher]

VARIATION 2:
[Your improved prompt here]
REASONING: [Why this might score higher]
---"""


# =============================================================================
# APE ENGINE PROMPTS (Zhou et al., 2022)
# =============================================================================

APE_INDUCTION_SYSTEM_PROMPT = """You are a reverse-engineering expert. Given examples of inputs and their ideal outputs, you must deduce the EXACT instruction that was used to produce those outputs.

Think step by step:
1. What transformation happened from input to output?
2. What specific style/format requirements are implied?
3. What constraints or rules seem to be in effect?

Be precise - the instruction should be reproducible."""

APE_INDUCTION_USER_TEMPLATE = """I gave a friend the following inputs, and they wrote these outputs.
What was the EXACT instruction I gave them?

EXAMPLE 1:
Input: {input_1}
Output: {output_1}

EXAMPLE 2:
Input: {input_2}
Output: {output_2}

EXAMPLE 3:
Input: {input_3}
Output: {output_3}

Deduce the instruction that would produce these outputs from these inputs."""

APE_RESAMPLE_TEMPLATE = """Given this instruction:
"{base_instruction}"

Generate {num_variations} variations of this instruction that:
1. Preserve the core intent
2. Vary in phrasing, specificity, or structure
3. Might perform better on edge cases

FORMAT each variation on its own line, numbered 1-{num_variations}."""


# =============================================================================
# PROMPTBREEDER ENGINE PROMPTS (Fernando et al., 2023)
# =============================================================================

PROMPTBREEDER_ZERO_ORDER_MUTATION = """Rewrite the following prompt to be more {mutation_direction}.

ORIGINAL PROMPT:
{prompt}

MUTATION DIRECTION: {mutation_direction}
(Examples: formal, concise, detailed, step-by-step, creative, technical)

Provide only the rewritten prompt, no explanation."""

PROMPTBREEDER_FIRST_ORDER_MUTATION = """You are a meta-optimizer. You have two components:
1. TASK-PROMPT: The prompt used to solve a task
2. MUTATION-PROMPT: Instructions on how to improve the task-prompt

Apply the mutation-prompt to improve the task-prompt.

TASK-PROMPT:
{task_prompt}

MUTATION-PROMPT:
{mutation_prompt}

Generate the improved task-prompt only."""

PROMPTBREEDER_MUTATION_PROMPTS = [
    "Add a 'Think step by step' instruction at the beginning",
    "Make the constraints more explicit and numbered",
    "Add an example of the expected output format",
    "Simplify the language to be more direct",
    "Add a role-play instruction (e.g., 'You are an expert...')",
    "Break the task into numbered sub-tasks",
    "Add validation criteria at the end",
    "Emphasize what NOT to do (negative constraints)",
]

PROMPTBREEDER_CROSSOVER_TEMPLATE = """Combine the best elements of these two prompts into a single improved prompt.

PROMPT A (Score: {score_a}):
{prompt_a}

PROMPT B (Score: {score_b}):
{prompt_b}

Create a new prompt that combines the strengths of both. Provide only the combined prompt."""


# =============================================================================
# S2A ENGINE PROMPTS (Weston et al., 2023)
# =============================================================================

S2A_FILTER_SYSTEM_PROMPT = """You are a context filter. Your job is to extract ONLY the unbiased, relevant information from a given text.

You must:
1. Remove any irrelevant tangents or off-topic content
2. Remove any biased or opinionated statements that could mislead
3. Preserve all factual, relevant information
4. Separate the cleaned context from the actual question/query

This filtered context will be used by another AI to answer a question accurately."""

S2A_FILTER_USER_TEMPLATE = """Given the following text, extract the part that is unbiased and relevant to answering questions accurately.

RAW CONTEXT:
{raw_context}

QUESTION/QUERY:
{query}

Respond in this format:
UNBIASED CONTEXT:
[Only the relevant, factual parts of the context]

FILTERED OUT:
[List what was removed and why]"""

S2A_OPTIMIZER_TEMPLATE = """The current S2A filter prompt achieved a score of {score}.

CURRENT FILTER PROMPT:
{current_prompt}

ISSUES OBSERVED:
- False positives (relevant info removed): {false_positives}
- False negatives (noise kept): {false_negatives}

Generate an improved filter prompt that addresses these issues.
Provide only the improved prompt."""


# =============================================================================
# GLASS BOX MONOLOGUE TEMPLATES
# =============================================================================

MONOLOGUE_OPRO = """[OPRO Engine - Step {step}]
History: {history_summary}
Best Score: {best_score}%
Strategy: {strategy}
Optimizing for: {optimization_target}"""

MONOLOGUE_APE = """[APE Engine - Induction Phase]
Examples analyzed: {num_examples}
Confidence: {confidence}%
Deduced instruction: "{instruction_preview}..."
Generating {num_variations} variations..."""

MONOLOGUE_PROMPTBREEDER = """[Promptbreeder - Generation {generation}]
Population size: {population_size}
Operator: {mutation_operator}
Best fitness: {best_fitness}%
Attempting: {mutation_description}"""

MONOLOGUE_S2A = """[S2A Filter - Pass {pass_num}]
Input tokens: {input_tokens}
Output tokens: {output_tokens}
Compression: {compression_ratio}%
Noise detected: {noise_items} items removed"""
