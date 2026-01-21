# Software Requirements Specification: Backend Architecture & Persistence

**Section 6: Data Models & Execution Flow**

## 6.1 Unified Candidate Data Model

To ensure the **Candidate List (Zone C)** and **Telemetry Graph (Zone D)** can render data from *any* engine without custom UI code for each, all engines must output data conforming to a strict `UnifiedCandidate` schema.

* **Class Name:** `UnifiedCandidate` (Pydantic Model)
* **Purpose:** The atomic unit of a "Result" displayed in the bottom-left list.

### 6.1.1 Core Fields (Universal)

| Field | Type | Description |
| --- | --- | --- |
| `id` | `UUID` | Unique identifier for the candidate. |
| `timestamp` | `DateTime` | When this candidate was generated. |
| `engine_type` | `Enum` | `OPRO`, `APE`, `BREEDER`, `S2A`. |
| `generation_index` | `Int` | Which "step" or "generation" produced this (for the X-Axis graph). |
| **`display_text`** | `String` | **The text shown in the list preview.** (See 6.2 for engine mapping). |
| **`full_content`** | `String` | The complete prompt/instruction text (shown in Detail Bucket). |
| `score_aggregate` | `Float` | The final 0-100 score (Mean of Test Bench). |
| `test_results` | `Dict` | `{'input_a': 90, 'input_b': 85, 'input_c': 50}` (For "Traffic Light" UI). |

### 6.1.2 Metadata Fields (Engine-Specific Storage)

* **Field:** `meta` (Dictionary)
* **Purpose:** Stores the "how" needed for the **Glass Box Readout** and **Diff Engine**.
* *OPro:* `{'mutation_type': 'rephrase', 'parent_id': '...'}`
* *APE:* `{'deduced_from_indices': [0, 1, 2]}` (Which examples created this).
* *PromptBreeder:* `{'mutation_operator': 'zero_order', 'parent_a_id': '...', 'parent_b_id': '...'}`.
* *S2A:* `{'noise_reduction_rate': 0.45}` (Metrics specific to filtering).



---

## 6.2 Engine-to-List Mapping

The "List at the bottom left" is a generic container. Here is how each engine populates the `display_text` and `full_content` fields to make sense to the user.

### 6.2.1 Engine A: OPro (The Optimizer)

* **List Display (`display_text`):** The Candidate Prompt.
* *Example:* "Write a poem about fish styled as a noir novel..."


* **Detail View (`full_content`):** The exact system instruction used.
* **Persistence Strategy:** Append-only list. Best score is tracked as "Current Champion."

### 6.2.2 Engine B: APE (The Inductor)

* **List Display (`display_text`):** The **Deduced Instruction**.
* *Example:* "Instruction: Summarize the user's input into JSON format."


* **Detail View (`full_content`):** The full instruction text.
* **Persistence Strategy:** Ranked List. The loop resamples the *best* instruction to find variations.

### 6.2.3 Engine C: PromptBreeder (The Evolver)

* **List Display (`display_text`):** Unit ID + Mutation Strategy.
* *Example:* "Unit #42 (Gen 5) | Strategy: Hyper-Mutation"


* **Detail View (`full_content`):**
* **Task Prompt:** (The actual prompt being tested).
* **Mutation Prompt:** (The prompt used to evolve this unit).


* **Persistence Strategy:** Population Snapshot. The backend must store the *entire* current population (N=20) plus a history of "Elites" (Best of each Gen).

### 6.2.4 Engine D: S2A (The Filter)

* **List Display (`display_text`):** The **Filter Strategy**.
* *Example:* "Strategy: Remove all sentences containing dates prior to 2020."


* **Detail View (`full_content`):** The full system prompt used by the S2A Agent to prune the context.
* **Persistence Strategy:** Append-only list of strategies.

---

## 6.3 State Management & The Update Loop

### 6.3.1 Session State Structure (`st.session_state`)

The application state must hold the "Live" data to drive the UI refresh.

```python
st.session_state = {
    "is_running": False,            # Controls the Step Loop
    "active_engine": "OPRO",        # Current Engine Strategy
    "current_step": 0,              # X-Axis Tracker
    "candidates": [ ... ],          # List of UnifiedCandidate objects (Zone C Source)
    "global_best_score": 0.0,       # For "New High Score" Star Animation
    "visualization_status": {       # Drives the Graphviz Animation
        "active_node": "SCORER",
        "current_log": "Evaluating Candidate #4..."
    }
}

```

### 6.3.2 The `step()` Function Protocol

Every time the backend performs one "tick" of the loop, it must update the state and yield control back to the UI for rendering.

**Pseudocode for the Backend Loop:**

```python
def run_optimization_cycle():
    while st.session_state.is_running:
        
        # 1. Get Active Strategy
        engine = get_strategy(st.session_state.active_engine)
        
        # 2. Update Visuals: Start Phase
        st.session_state.visualization_status = {"active_node": "START", "log": "Preparing..."}
        update_frontend() # Trigger re-render

        # 3. Generate Candidate (The "Change" Step)
        st.session_state.visualization_status = {"active_node": "CHANGE", "log": "Mutating..."}
        update_frontend()
        new_candidate_data = engine.generate(st.session_state.candidates)

        # 4. Test Bench Execution (The "Test/Rate" Step)
        st.session_state.visualization_status = {"active_node": "TEST", "log": "Running Test Bench..."}
        update_frontend()
        
        scores = test_bench.evaluate(new_candidate_data) # Runs Input A, B, C
        
        # 5. Create Unified Candidate
        candidate = UnifiedCandidate(
            display_text=new_candidate_data.text,
            score_aggregate=mean(scores),
            test_results=scores,
            meta=new_candidate_data.meta
        )

        # 6. Update List & Graph State
        st.session_state.candidates.append(candidate)
        st.session_state.current_step += 1
        
        # 7. Check for High Score
        if candidate.score_aggregate > st.session_state.global_best_score:
            st.session_state.global_best_score = candidate.score_aggregate
            # Trigger "Star" animation on Graph

```

---

## 6.4 Data Persistence (File Save)

To support the "Zip Drive" transfer, the state must be serializable to a single JSON file.

* **Trigger:** "Export Run" button in Sidebar.
* **Format:** `.opro` (JSON).
* **Structure:**
```json
{
    "meta": { "version": "2.0", "engine": "OPRO" },
    "config": { "model": "gpt-4o", "temperature": 0.7 },
    "history": [
        {
            "id": "uuid...",
            "step": 1,
            "text": "Write a poem...",
            "score": 45.0,
            "metrics": {"a": 40, "b": 50, "c": 45}
        },
        ...
    ]
}

```


* **Requirement:** The loader must be able to read this file and populate `st.session_state.candidates` instantly, restoring the list and graph state.

---

# Software Requirements Specification: Backend Logic (Part 1)

## 7.0 Engine A: OPro (Optimization by PROmpting)

**Backend Goal:** Iterative trajectory optimization. The system improves a prompt by analyzing the history of previous scores.

### 7.1.1 Step 1: `TEST` (Execution)

* **Action:** Run the current `candidate_prompt` against the user-defined `Test Bench` (Inputs A, B, and C).
* **API Call:** Standard Completion (x3 calls).
* **Model:** User-selected Model (e.g., `gpt-4o`).
* **Temperature:** `0.0` (Deterministic for testing).
* **Payload Construction:**
```text
System: {candidate_prompt}
User: {Test_Bench_Input_X}

```




* **Data Flow:** `Candidate` + `Test Data` -> `LLM Response`.

### 7.1.2 Step 2: `RATE` (Evaluation)

* **Action:** Score the `LLM Response` against the `Intent`.
* **API Call:** Evaluator Agent (LLM-based Judge).
* **Model:** `gpt-4o` (Fixed, high-reasoning model).
* **Temperature:** `0.0`.
* **Prompt Structure (The Judge):**
> **System:** You are an impartial judge. Rate the quality of the following response on a scale of 0 to 100 based on how well it satisfies the user's intent. Output ONLY a JSON object: `{"score": <int>, "reasoning": "<string>"}`.
> **User:**
> **Intent:** {seed_task_description}
> **Input Used:** {Test_Bench_Input_X}
> **Model Response:** {LLM_Response}


* **Data Flow:** `Response` + `Intent` -> `Score` (Integer).

### 7.1.3 Step 3: `CHANGE` (Mutation/Optimization)

* **Action:** Generate `N` new prompt variations based on the history of scores.
* **API Call:** Optimizer Agent (Meta-Prompter).
* **Model:** `gpt-4o` (High reasoning required).
* **Temperature:** `1.0` (High creativity needed for mutation).
* **Prompt Structure (The Meta-Prompt):**
> **System:** You are an expert prompt engineer. Your goal is to rewrite the following prompt to maximize its score.
> **Context - Optimization History:**
> (The system injects the top 5 previous results sorted by score)


> 1. Prompt: "{prev_prompt_A}" | Score: 95 | Flaw: {judge_reasoning}
> 2. Prompt: "{prev_prompt_B}" | Score: 40 | Flaw: {judge_reasoning}
> 
> 


> **Instructions:**
> Analyze the high-scoring prompts for patterns. Avoid the flaws listed in low-scoring prompts. Generate {N} new, distinct variations of the prompt.


> **Output Format:**
> Separate each prompt with: `---PROMPT BREAK---`



---

## 7.2 Engine B: APE (Automatic Prompt Engineer)

**Backend Goal:** Inverse Induction. The system deduces the instruction that connects specific data inputs to desired outputs.

### 7.2.1 Step 1: `START` (Induction - First Run Only)

* **Action:** Deduce the hidden instruction.
* **API Call:** Inductor Agent.
* **Model:** `gpt-4o` (Requires strong logical inference).
* **Temperature:** `0.7` (Balanced).
* **Prompt Structure:**
> **System:** I gave a helpful assistant a set of inputs and they produced specific outputs. I need you to deduce the *exact* system instruction I gave them to achieve this.
> **Examples:**
> Input: {User_Input_Example_1} -> Output: {User_Ideal_Output_1}
> Input: {User_Input_Example_2} -> Output: {User_Ideal_Output_2}
> **Task:** Write the system instruction that forces the model to perform this transformation. Provide 3 distinct possibilities.



### 7.2.2 Step 2: `TEST` & `RATE` (Validation)

* **Action:** Identical to OPro. The deduced instruction becomes the `candidate_prompt`. It is run against the **Test Bench** (which must be distinct from the induction examples to prevent leakage) and scored by the Judge.

### 7.2.3 Step 3: `CHANGE` (Resampling/Refinement)

* **Action:** Generate variations of the *best* deduced instruction found so far.
* **API Call:** Resampler Agent.
* **Model:** `gpt-4o`.
* **Temperature:** `0.9`.
* **Prompt Structure:**
> **System:** The following instruction scored {current_score}/100 on the test bench.
> **Instruction:** "{current_best_instruction}"
> **Task:** Generate {N} semantic variations of this instruction that retain the core logic but change the tone, structure, or formatting constraints to potentially improve performance.



---

## 7.3 Errata & Design Adjustments (Engines A & B)

Based on the deep dive above, the following adjustments are required for the requirements document to ensure the backend actually functions as described.

### **Errata 1: The "Test Bench" vs. "APE Inputs" Conflict**

* **Issue:** APE requires `Input Examples` + `Ideal Output` to *generate* the prompt (Induction). However, the `Test Bench` (Section 1.6) serves a different purpose: *validating* the prompt.
* **Fix:** The **Zone A Input Area** for APE must explicitly separate "Induction Data" (used to write the prompt) from "Validation Data" (used to score it).
* **Design Decision:**
* **Induction Data:** Input/Output pairs entered in the "Glass Box" top area.
* **Validation Data:** The standard "Test Bench" at the bottom right (Zone E).
* *Constraint:* The backend must enforce that these are not identical, otherwise the score is meaningless (overfitting).



### **Errata 2: The "Judge" Needs Ground Truth**

* **Issue:** In OPro Step 2 (Rate), the Judge is asked to rate the response. But without a "Gold Standard" or "Ideal Output," the Judge is hallucinating the quality.
* **Fix:** The **Test Bench (Zone E)** must accommodate an *optional* "Ideal Output" field for each of the 3 test cases.
* If "Ideal Output" is present: Judge uses **Semantic Similarity** (e.g., "How close is Response X to Ideal Y?").
* If "Ideal Output" is missing: Judge uses **Intent Compliance** (e.g., "Does Response X satisfy the task description?").



### **Errata 3: APE Loop Mechanics**

* **Issue:** APE is traditionally a linear process (Induct -> Validate -> Select). Forcing it into the visual "Loop" of OPro requires a slight conceptual shift.
* **Fix:** Reframe APE's loop as **"Iterative Resampling"**.
* *Pass 1:* Induct instructions from data.
* *Pass 2+:* Take the winner, mutate it (Resample), and re-test. This aligns APE perfectly with the `Start -> Test -> Rate -> Change` topology without breaking the visual metaphor.


## 7.4 Engine C: PromptBreeder (Evolutionary)

**Backend Goal:** Self-Referential Evolution. The system evolves not just the *Task-Prompt* (the solution) but also the *Mutation-Prompt* (the strategy for improving the solution).

### 7.4.1 Data Structure: The "Unit"

Unlike other engines, the atomic unit of optimization is a tuple, not a single string.

* **Class:** `EvolutionUnit`
* **Components:**
* `P` (Task-Prompt): The prompt that solves the user's problem.
* `M` (Mutation-Prompt): The instruction used to modify `P`.
* *Initial State:* `P` = User Seed. `M` = "Rewrite the prompt to be more clear and precise."



### 7.4.2 Step 1: `TEST` & `RATE` (Population Evaluation)

* **Action:** Evaluate the fitness of every Unit in the active population (N=10 to 20).
* **Logic:**
1. Extract `P` from the Unit.
2. Run `P` against the **Test Bench** (Inputs A, B, C).
3. Judge scores the outputs.
4. Assign `Unit.fitness` = Average Score.


* *Note:* This step is computationally expensive ( LLM calls).

### 7.4.3 Step 2: `TOURNAMENT` (Selection)

* **Action:** Select parents for the next generation.
* **Algorithm:** Binary Tournament.
1. Pick 2 Units at random.
2. Compare `Unit.fitness`.
3. The winner becomes a **Parent**.
4. Repeat until  parents are selected.



### 7.4.4 Step 3: `MUTATE` & `CROSS` (The Evolution Operators)

* **Action:** Generate Offspring. The backend randomly selects an operator for each Parent.
* **Operator A: First-Order Mutation (The "Hyper-Mutation")**
* *Goal:* Improve the *Mutation-Prompt* (`M`), then use it to improve `P`.
* **API Call 1 (Mutate M):**
> **System:** You are a meta-heuristic optimizer.
> **User:** Improve this mutation instruction to be more specific and novel: "{Parent.M}"
> **Output:** "{Child.M}"


* **API Call 2 (Apply M):**
> **System:** {Child.M}
> **User:** {Parent.P}
> **Output:** "{Child.P}"




* **Operator B: Crossover (The "Idea Sex")**
* *Goal:* Combine the Strategy of Parent A with the Task of Parent B.
* **Logic:**
* `Child.M` = `Parent_A.M`
* `Child.P` = Apply `Parent_A.M` to `Parent_B.P`.





---

## 7.5 Engine D: S2A (System 2 Attention)

**Backend Goal:** Context Optimization. The system optimizes the *Filtering Instruction* that cleans RAG context before the final answer is generated.

### 7.5.1 The Optimization Target

* **Candidate:** The `Filter_Instruction`.
* *Seed:* "Given the context, remove any sentences irrelevant to the query."
* *Goal:* Find a variation of this instruction that maximizes robustness against the "Noise Injection" from the Barista Simulator.

### 7.5.2 Step 1: `READ` & `FILTER` (The S2A Pass)

* **Action:** The Agent reads the Noisy Context and rewrites it.
* **API Call:** S2A Agent.
* **Model:** `gpt-4o` (Must be capable of distinguishing nuance).
* **Temperature:** `0.0`.
* **Prompt Structure:**
> **System:** {Candidate_Filter_Instruction}
> **User:**
> **Query:** {Test_Bench_Input_Query}
> **Raw Context:**
> {Chunk 1 (Valid)}
> {Chunk 2 (Noise)}
> {Chunk 3 (Valid)}
> **Task:** Output the refined context ONLY.


* **Data Flow:** `Noisy Context` + `Filter Instruction` -> `Clean Context`.

### 7.5.3 Step 2: `REFINE` & `ANSWER` (End-to-End Execution)

* **Action:** Answer the query using *only* the `Clean Context`.
* **API Call:** Solver Agent.
* **Prompt Structure:**
> **System:** Answer the query using only the provided context.
> **Context:** {Clean_Context_From_Step_1}
> **Query:** {Test_Bench_Input_Query}



### 7.5.4 Step 3: `EVALUATE` (Hallucination & Noise Check)

* **Action:** The Judge evaluates if the answer was correct *and* if it ignored the noise.
* **API Call:** Judge Agent.
* **Prompt Structure:**
> **System:** Rate the answer.
> **Criterion 1:** Did the answer address the query?
> **Criterion 2 (Crucial):** Did the answer reference the "Distractor" information (e.g., weather reports in a safety query)? If yes, score = 0.



---

## 7.6 Errata & Design Adjustments (Engines C & D)

### **Errata 4: PromptBreeder Initialization (The "Cold Start" Problem)**

* **Issue:** PromptBreeder relies on `M` (Mutation-Prompts) to evolve. If we start with just *one* generic "Improve this" prompt, the population will lack diversity for the first 10 generations.
* **Fix:** The backend must include a **Library of Seed Mutators** (hardcoded in `src/engine/mutators.py`).
* *Examples:* "Make it shorter", "Think step-by-step", "Adopt a persona", "Add constraints".


* **Logic:** When initializing the population, assign random Mutators from this library to the initial units.

### **Errata 5: S2A Visualization (The "Context Diff")**

* **Issue:** The standard "Visual Diff" (Section 1.4.3) is designed to compare *Prompts*. For Engine D, comparing the *Filter Instruction* is useful, but the user really wants to see **what data was removed**.
* **Design Decision:**
* **List View:** Displays the *Filter Instruction* (The Candidate).
* **Detail Bucket:** Displays a special **"Context Reduction View"**.
* *Left Col:* Raw Context (with Noise highlighted in Red borders).
* *Right Col:* Clean Context (with removed text shown as Strikethrough).


* *Constraint:* The backend `UnifiedCandidate` object for S2A must store the `clean_context` string in its `meta` field to enable this view.



### **Errata 6: PromptBreeder Cost Control**

* **Issue:** A population of 20 units running against 3 test cases = 60 API calls per generation. This will hit rate limits or token budgets instantly.
* **Fix:** Implement **"Survival of the Fittest" Micro-Batching**.
* *Generation 1-5:* Run against *only* Test Case A (The Golden Path). Cheap and fast.
* *Generation 6+:* Run survivors against Test Case A + B.
* *Final Check:* Only the top 3 candidates of the final generation run against the full A+B+C bench.