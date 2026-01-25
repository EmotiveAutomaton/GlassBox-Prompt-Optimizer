# Software Requirements Specification: GlassBox Prompt Optimizer v2.0

**Section 1: Interface Architecture & User Experience**

## 1.1 General Design Standards

* **Framework:** Streamlit (Python).
* **Window Configuration:**
  * `layout="wide"` (Mandatory to support the card-box grid).
  * `initial_sidebar_state="expanded"`.
  * Sidebar collapse arrows are HIDDEN at all times (including hover); sidebar is always visible.
  * Sidebar has FIXED WIDTH (220px); user cannot resize it.
  
* **Theme:** Boeing Light Mode (Strict 4-Color Palette).
  * **Background:** `#FDFDFE` (Near White - Main Canvas).
  * **Top Bar:** `#1A409F` (Boeing Blue) with gradient shadow.
    * Title "GLASSBOX PROMPT OPTIMIZER" on the LEFT (not bold, font-weight: 400).
    * Boeing logo (`BoeingWhiteOnTransparentLogo.png` from `glassbox/assets/`) CENTERED.
  * **Sidebar:** `#394957` (Slate Gray) - Fixed width, full-height panel.
    * Navigation items are full-width horizontal blocks (edge-to-edge).
    * Active/selected item uses `#0D7CB1` (Selected Blue) background.
    * "Configuration" popover at BOTTOM of screen (flush), transparent by default, light on hover, blue when open.
    * Popover opens UPWARD (above button), arrow reversed.
  * **Section Headers:** `#394957` (Slate Gray) for all card headers.
  * **Accent:** `#0D7CB1` (Selected Blue) for active states.
  * **Text:** Black/Dark Gray on light backgrounds; White on Sidebar/Headers.

* **Robust UI Rendering Standards (Mandatory):**
  * **Card Borders:** Standard CSS `border` properties are notoriously unreliable in Streamlit iframe contexts. All valid implementations MUST use a **Z-Index Overlay Strategy**:
    * Construct borders using a `::after` pseudo-element on the card container.
    * Properties: `position: absolute`, `top/left/right/bottom: 0`, `z-index: 999`, `pointer-events: none`.
    * This ensures borders are drawn *topologically above* all content, bypassing specific browser rendering glitches or overflow clipping.
  * **Input Visibility:** Textbox backgrounds must be strictly `#FFFFFF` (White) with high-contrast placeholder text (e.g., `#555555`) explicitly styled via `::placeholder` pseudo-selectors.
  * **Button Colors:** Primary actions must use `!important` overrides for `background-color` to prevent theme leakage.
  
* **Typography:** Helvetica Neue. Regular weight for body. Medium for card headers.

* **Icons:** SVG only. No emoji icons anywhere in the UI.

* **Top Bar:**
  * Title "GLASSBOX PROMPT OPTIMIZER" on the LEFT (not bold).
  * Boeing logo (`BoeingWhiteOnTransparentLogo.png`) CENTERED.
  * Tiny gear icon (SVG) on far RIGHT - opens configuration menu.
  * Style: White icon on Blue header (Transparent background). No gray button styling.

* **Sidebar:**
  * Fixed 220px width (not resizable).
  * Collapse arrows hidden at all times.
  * Navigation items flush with all 4 edges (no dead space, no padding).
  * Hover Effect: Background lightens (translucent white overlay), Text remains White (no inner highlight).
  * No configuration button (config moved to top bar gear icon).

* **Animations:**
  * Fade-in transitions (0.25s) when switching between engines.
  * Top bar has gradient shadow for depth.
  * Buttons have press animation (scale 0.98 on click).
  * Cards have hover lift effect (subtle shadow).

* **Card Box Layout (5 Cards):**
  1. **INPUT STARTING PROMPT AND DATA** - Top left. Contains: Model Settings popover, seed prompt text area, file upload, RAG Settings popover, Start/Stop buttons.
  2. **GLASS BOX** - Top right. Contains: schematic visualization, internal log/status.
  3. **POTENTIAL PROMPTS** - Bottom left (wide). Contains: scrollable candidate list with scores.
  4. **PROMPT RATINGS** - Bottom right top. Contains: score graph (no extra header inside).
  5. **FINAL OUTPUT AND USER EVALUATION** - Bottom right bottom. Contains: test bench (Free Play, Input A/B/C).


---

## 1.2 Zone A: The "Glass Box" Banner (Top Full-Width) -> **Data & Task Input**

*Purpose: To define the optimization task and the test data used to validate it.*

### 1.2.1 Task Description (Top Left)
* **Start Prompt / Seed:** A multi-line `st.text_area` where the user defines the initial instruction.

### 1.2.2 Dataset Management (The "Test Bench" Integration)
* **Architecture:** Replaces the legacy "Zone E" static inputs with a dynamic **Tabbed Interface**.
* **Tabs:**
    * **Dynamic:** Users can standard `+` Add or `x` Delete tabs (datasets).
    * **Content:** Each tab contains a `st.text_area` (Raw Text) and `st.file_uploader` (Txt/PDF).
* **Persistence:** Datasets persist in `st.session_state` across reruns.
* **Delete Safety:** Deletion triggers a **Modal Dialog** (`st.dialog`) to prevent accidental data loss.
* **Default State:** Pre-loaded with "Dataset 1" (and optionally Dummy Data in Test Mode).

### 1.2.3 The "Schematic" Visualization (Center/Right)
* **Technology:** `graphviz` (via `st.graphviz_chart`).
* **State Indication:** The diagram dynamically updates (Pulse/Color) based on backend state.
* **Data Flow:**
    * **Blue Edge:** Instruction Flow (Mutations).
    * **Yellow Edge:** Input Data Flow (Validation against Datasets).

### 1.2.4 "Internal Monologue" (Far Right)
* **Component:** Read-only `st.code`.
* **Function:** displays the System Prompt of the active agent node.

---

## 1.3 Zone B: The Control Sidebar (Left Vertical)
... (No major changes, keep config logic) ...

---

## 1.4 Zone C: Results & Candidate Management (Bottom Left)

*Purpose: Reviewing and comparing outputs.*

### 1.4.1 The Candidate List (Table)
* **Layout Logic:**
    *   **Single-Dataset Mode:** `[Score] [Iter] [Prompt (Preview)] [Result (Preview)]`.
    *   **Multi-Dataset Mode:** `[Avg Score (Wide)] [Iter] [Prompt (Preview)] [Score D1] [Score D2]...`.
*   **Interaction (Queue Logic):**
    *   **Click (New):** Adds to queue. Queue Max Size = 2.
    *   **Click (Active/Primary):** Empties queue of all *other* items. (Collapse to Single).
    *   **Visuals:**
        *   Primary Selection: Dark Blue Background.
        *   Secondary Selection: Ghost/Light Indicator.

### 1.4.2 The "Visual Diff" Engine (Zone E Integration)
*Moved to Zone E.*

---

## 1.5 Zone D: Telemetry Graph (Top Right)

*Purpose: Visualizing progress over time.*

* **Technology:** `plotly.graph_objects`.
* **Data:**
    * **X-Axis:** Iteration.
    * **Y-Axis:** Aggregate Score.
* **Interaction (Bi-Directional Sync):**
    * **Highlight:** Selected candidates from Zone C are highlighted on the graph (e.g., larger size, different color).
    * **Click:** Clicking a node in the graph selects the corresponding row in Zone C.

---

## 1.6 Zone E: The Detail Inspector & Diff Viewer (Bottom Right)

*Purpose: Deep dive into specific results or comparison of changes.*

### 1.6.1 Single Selection Mode
*   **Trigger:** Only 1 candidate selected in Zone C.
*   **Layout:** Master-Detail Split (25% Left / 75% Right).
*   **Left Pane (Dataset Navigator):**
    *   Selectable list/pills of all active Datasets.
    *   Defaults to "Dataset 1" or currently active tab.
*   **Right Pane (Content Reader):**
    *   **Header:** Iteration #X | Score: 95.
    *   **Prompt Section:** Full Candidate Text (Scrollable).
    *   **Result Section:** Full Output generated for the *selected dataset* (Scrollable).

### 1.6.2 Dual Selection Mode (Diff)
*   **Trigger:** 2 candidates selected in Zone C.
*   **Content:** Text Diff of **Prompt A** vs **Prompt B**.
*   **Styling:**
    *   **Removals:** Muted Red background + Strikethrough.
    *   **Additions:** Muted Green background.
*   **Goal:** Instant visual understanding of *mutation* ("Oh, it changed 'explain' to 'elucidate'").

This is **Section 2: Backend Engine Logic & Visualization**, designed to be handed directly to your Agentic Coding Framework. It provides the exact algorithmic implementations and the corresponding "Glass Box" visualization requirements for the animated frontend.

---

**Section 2: Backend Engine Logic & Visualization Standards**

## 2.1 The Optimization Core (Strategy Pattern)

The system must utilize a **Strategy Pattern** to swap optimization logic dynamically.

* **Interface:** `AbstractOptimizer` class.
* **Methods:** `step(session_state)`, `get_current_status()`, `get_schematic_state()`.
* **Requirement:** All engines must output standard `PromptResult` objects to ensure the Graph and Candidate List (Section 1) function identically regardless of the active engine.

---

## 2.2 Engine A: OPro (Optimization by PROmpting)

**Source:** Yang et al. (DeepMind, 2023) - *"Large Language Models as Optimizers"*

### 2.2.1 Algorithmic Logic

1. **Input:** User Task Description (Seed) + Scored History (Trajectory).
2. **The Meta-Prompt:** The "Optimizer Agent" is fed the following System Prompt:
> "You are an optimization expert. Your goal is to improve the following prompt to maximize a score (0-100).
> Here is the history of past attempts and their scores:
> [Prompt: X | Score: 72]
> [Prompt: Y | Score: 85]
> Identify the patterns in high-scoring prompts. Generate a new variation that is different from the above but likely to score higher."


3. **Output:** Generates `N` variations.
4. **Selection:** Greedy (Best score is kept as the new baseline for the next step).

### 2.2.2 "Glass Box" Visualization: The Feedback Loop

* **Schematic Shape:** A **Circular Cycle** (Clockwise).
* **Nodes:** `[Seed Prompt]`  `[Executor]`  `[Scorer]`  `[Optimizer Agent]`  `(Back to Start)`
* **Animation State:**
* **Idle:** Gray dashed lines.
* **Optimization Phase:** The link between `[Scorer]` and `[Optimizer Agent]` glows **Yellow** (Data Flow).
* **Mutation Phase:** The link between `[Optimizer Agent]` and `[Seed Prompt]` glows **Blue** (Instruction Flow).


* **The "Glass Box" Text Panel:**
* Must display the **Trajectory Snippet**: *"History: Run #4 (85%), Run #5 (88%). Optimizing for brevity..."*



---

## 2.3 Engine B: APE (Automatic Prompt Engineer)

**Source:** Zhou et al. (2022) - *"Large Language Models Are Human-Level Prompt Engineers"*

### 2.3.1 Algorithmic Logic

* **Mode:** Reverse Engineering (Induction).
* **Step 1 (Data Ingestion):** User provides 3-5 examples of `[Input Data]` and `[Ideal Output]`.
* **Step 2 (Instruction Induction):** The Agent generates the "Hidden Instruction" that maps Input to Output.
* *Prompt:* "I gave a friend this input: [Input], and they wrote this output: [Output]. What was the exact instruction I gave them?"


* **Step 3 (Resampling):** Generate 10 variations of this deduced instruction.
* **Step 4 (Selection):** Run all 10 against the Test Bench; highest average score wins.

### 2.3.2 "Glass Box" Visualization: The Induction Funnel

* **Schematic Shape:** A **Funnel** (Wide Top, Narrow Bottom).
* **Nodes:** `[Examples]` (Top)  `[Induction Engine]` (Middle)  `[Candidate Prompts]` (Bottom).
* **Animation State:**
* **Step 1:** Multiple particles (dots) flow from Top  Middle.
* **Step 2:** The `[Induction Engine]` pulses rapidly.
* **Step 3:** A single solid beam shoots from Middle  Bottom.


* **The "Glass Box" Text Panel:**
* Must display the **deduced instruction** appearing character-by-character: *"Induction: 'Summarize this technical text in 3 bullet points...'"*



---

## 2.4 Engine C: Promptbreeder (Evolutionary)

**Source:** Fernando et al. (Google DeepMind, 2023) - *"Self-Referential Self-Improvement Via Prompt Evolution"*

### 2.4.1 Algorithmic Logic

* **Key Concept:** Evolves a **Population** (N=20) of *Units*.
* **Unit Structure:** `{ Task-Prompt, Mutation-Prompt }`. (It evolves the *way* it evolves).
* **The Mutation Operators (Must implement at least 3):**
1. **Zero-Order (Direct):** "Rewrite this prompt to be more formal."
2. **First-Order (Hyper-Mutation):** The `Mutation-Prompt` modifies the `Task-Prompt`. (e.g., Mutation Prompt: *"Add a 'Think Step by Step' instruction"*).
3. **Crossover:** Take the `Task-Prompt` from Unit A and the `Mutation-Prompt` from Unit B.


* **Survival:** Tournament Selection. Kill the bottom 50%; clone the top 50%.

### 2.4.2 "Glass Box" Visualization: The Phylogenetic Tree

* **Schematic Shape:** A **Horizontal Branching Tree** (Left-to-Right).
* **Nodes:** `[Gen 1]` roots branching into multiple `[Gen 2]` nodes.
* **Animation State:**
* **Growth:** New branches extend out.
* **Death:** Failed branches (Low Score) turn **Dark Grey** and stop growing.
* **Success:** The "Best" path glows **Gold**.


* **The "Glass Box" Text Panel:**
* Must display the **Mutation Strategy** used: *"Operator: Hyper-Mutation. Gen 4 attempting 'Chain-of-Thought' injection."*



---

## 2.5 Engine D: System 2 Attention (S2A)

**Source:** Weston et al. (Meta, 2023) - *"System 2 Attention (is something you might need too)"*

### 2.5.1 Algorithmic Logic

* **Goal:** Noise filtration for RAG (The "Barista Simulator").
* **Step 1 (S2A Rewrite):**
* *Prompt:* "Given the following text, extract the part that is unbiased and relevant... so that using that text alone would be good context... Separate this into 'Unbiased text context' and 'Question/Query'."


* **Step 2 (Response):** Pass *only* the `Unbiased text context` to the Model for the final answer.
* **Optimization Goal:** Find the phrasing of Step 1 that best filters the noise injected by the Simulator.

### 2.5.2 "Glass Box" Visualization: The Filter Conveyor

* **Schematic Shape:** A **Linear Assembly Line**.
* **Nodes:** `[Raw Context]`  `[S2A Filter]`  `[Clean Context]`  `[Final Response]`.
* **Animation State:**
* **Flow:** Blocks move from left to right.
* **The Filter:** When passing `[S2A Filter]`, the block shrinks (visually representing data reduction).


* **The "Glass Box" Text Panel:**
* **The Red Pen View:** Show the raw text with **Strikethroughs** on the removed sentences.
* *Example:* "The 737-10 is efficient. ~~The weather in Seattle is rainy.~~ It uses..."


Here are **Sections 3 and 4** of the Requirements Document. These sections define the simulation environment (RAG) and the rigorous testing protocol (The Lab Bench), completing the specification for your coding agent.

---

**Sections 3 & 4: RAG Simulation and Evaluation Framework**

## Section 3: The "Barista" Simulator (RAG Environment)

**Goal:** To simulate the internal Boeing RAG tool ("Barista") accurately, enabling the optimization of prompts that are robust against imperfect retrieval and "noisy" contexts.

### 3.1 Vector Store Integration

* **Library:** `chromadb` (Local Persistence).
* **Connection:**
* User supplies a directory path to an existing ChromaDB (`.chroma` folder).
* System validates connection on load.


* **Constraint:** The Optimizer **READS** from the store but **NEVER WRITES** to it. The store is immutable during the optimization session to ensure consistent benchmarking.

### 3.2 Simulation Parameters (The "Knobs")

The simulator must replicate the specific controls available in the internal tool:

* **`Top_K`:** Integer (1–10). Number of chunks to retrieve.
* **`Temperature`:** Float (0.0–1.0).
* **`System Prompt`:** The overarching instruction layer (e.g., "You are a helpful assistant...").

### 3.3 The "Noise Injection" Engine (Robustness Feature)

* **Concept:** To prevent the model from assuming perfect context, we intentionally degrade retrieval quality to test prompt adherence.
* **Control:** `Noise Level` Slider (0% – 100%).
* **Implementation Logic:**
1. **Retrieve:** Fetch `Top_K` chunks normally using Cosine Similarity.
2. **Inject:** Based on the Noise %, replace  legitimate chunks with **Distractor Chunks**.
* *Distractor Source:* Randomly selected chunks from the vector store that represent a *different* topic/cluster (low similarity score).


3. **Shuffle:** Randomize the order of chunks (to prevent "recency bias" where the model only reads the last chunk).


* **Visual Feedback ("Glass Box"):**
* In the **Detail Bucket** (Zone C), the Context Viewer must color-code chunks:
* 🟩 **Green Border:** High Similarity (Legitimate).
* 🟥 **Red Border:** Low Similarity (Injected Noise).





### 3.4 Context Assembly

The Simulator must construct the final prompt sent to the LLM exactly as follows (Standard RAG Pattern):

```text
System: {System Prompt}

User:
Context Information:
---
{Chunk 1}
---
{Chunk 2}
---
{Chunk 3 (Noise)}
---

Instruction: Based on the context above, {User_Task_Description}

```

---

## Section 4: Evaluation Framework ("The Lab Bench")

**Goal:** To prevent "overfitting" (optimizing a prompt that works for only one specific data point) by enforcing a "Unit Test" approach against multiple inputs.

### 4.1 The Dynamic Test Bench
The "Optimization Score" is **not** derived from a single run. The system attempts to generalize performance by running every candidate prompt against a set of **Test Datasets** configured in Zone A.
* **Flexibility:** Users can define 1 to N distinct datasets.
* **Minimum Recommendation:** At least 2 datasets (Standard + Edge Case) are recommended for robust optimization.

### 4.2 Scoring Logic (Aggregation)
* **Execution:** For every Candidate Prompt `P` and Dataset `D`:
    * Run `P(D_1)` -> Score_1
    * ...
    * Run `P(D_N)` -> Score_N
* **Final Metric:** `Global_Score = Average(Score_1 ... Score_N)`.
* **Visual Feedback:**
    * **Global:** The "Avg Score" is displayed in Zone C and plotted in Zone D.
    * **Breakdown:** Individual dataset scores/results are viewable in the **Detail Inspector** when a candidate is selected.

### 4.3 Manual "Checkride" (Validation)
* **Status:** Post-Optimization Validation.
* **Location:** Zone E (Detail Inspector).
* **Functionality:**
    * **Inspection:** Select the "Winner" (or high-scoring candidate) in Zone C.
    * **Visual Check:** Zone E displays the full generated output for the active test bench input.
    * **Comparison:** Select TWO candidates (e.g., Seed + Winner) to trigger the "Visual Diff" mode, showing exactly how the prompt evolved and improved.
    * **Generalization Check:** Use the "Datasets" tabs in Zone A to switch inputs and verify the prompt holds up across different test cases.



### 4.4 Data Persistence & Portability

To support the "Zip Drive" deployment strategy, the system must save state to a single portable file.

* **File Format:** `.opro` (JSON).
* **Schema (Pydantic - `OptimizerSession`):**
*   Root object containing `config`, `candidates`, `trajectories`, and `test_bench`.
*   Uses `UnifiedCandidate` model for all engines, ensuring polymorphic stability.
```json
{
  "metadata": {
    "version": "2.0",
    "engine_used": "APE",
    "timestamp": "2025-10-27T14:00:00Z"
  },
  "config": {
    "model": "gpt-4o",
    "temperature": 0.7,
    "noise_level": 0.2
  },
  "test_bench": {
    "input_a": "...",
    "input_b": "...",
    "input_c": "..."
  },
  "winner": {
    "prompt_text": "...",
    "final_score": 94.5
  },
  "trajectory": [
    { "step": 1, "score": 60, "prompt": "..." },
    { "step": 2, "score": 75, "prompt": "..." }
  ]
}

```


* **Import/Export:** Simple buttons in the Sidebar (Zone B) to Load/Save this JSON structure.
