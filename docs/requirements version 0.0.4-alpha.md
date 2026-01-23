**Focus:** Zone A (Glass Box) Topology & Animation Logic

## 5.0 Global Visualization Standards

To replace the linear/flat diagrams seen in the Alpha build, all optimization engines must adhere to a strict **Cyclical Topology**.

### 5.0.1 The "Oval" Layout Constraint

* **Layout Engine:** Graphviz `circo` (Circular Layout) or `neato` (with fixed coordinates) must be used instead of the default hierarchical `dot` engine.
* **Shape:** Nodes must be arranged in a distinct **Oval** or **Circle**.
* **Flow Direction:** Clockwise.

### 5.0.2 The "Input Bridging" Animation

To visually demonstrate the shift from "User Initialization" to "System Autonomy," the diagram must dynamically alter its connections to the Input Panel (Zone A Left).

* **Static Nodes (The Anchors):**
* `INPUT_UI_PROMPT` (Invisible Node anchored to Left side of container).
* `INPUT_UI_DATA` (Invisible Node anchored to Left side of container).


* **The "Severing" Logic:**
* **State: Cycle 0 (Initialization):**
* Draw **Blue Edge**: `INPUT_UI_PROMPT`  `CURRENT_PROMPT_NODE`.
* *Meaning:* "The system is reading your seed prompt."


* **State: Cycle > 0 (Optimization Loop):**
* **REMOVE** the Blue Edge from `INPUT_UI_PROMPT`.
* *Meaning:* "The system has detached. It is now evolving its own prompts internally."




* **The "Persistent Data" Logic:**
* **State: All Cycles:**
* Draw **Yellow Edge**: `INPUT_UI_DATA`  `TEST_NODE`.
* *Meaning:* "The system continuously pulls from your test data/context at every step."





---

## 5.1 Engine A: OPro (Iterative Oval)

*Refines the diagram in `OPro.png`.*

### 5.1.1 Visual Topology

* **Layout:** Perfect Oval.
* **Nodes & Positions:**
* `START` (9:00 position - Left)
* `TEST` (12:00 position - Top)
* `RATE` (3:00 position - Right)
* `CHANGE` (6:00 position - Bottom)


* **Color Logic:**
* **Blue Path (Prompt):** `START`  `TEST` (Input)  `RATE` (Output)  `CHANGE` (Score)  `START` (Mutation).
* **Yellow Path (Data):** Persistent edge from `INPUT_UI_DATA`  `TEST`.



### 5.1.2 Animation Trigger

* **Cycle 1:** Blue Line connects User Input Textbox  `START`.
* **Cycle 2+:** Blue Line disappears. The Loop `CHANGE`  `START` glows brighter to emphasize self-correction.

---

## 5.2 Engine B: APE (The Resampling Oval)

*Refines the diagram in `APE.png`.*

### 5.2.1 Visual Topology

* **Layout:** Oval (mirrors OPro for consistency).
* **Nodes & Positions:**
* `INSTRUCT` (9:00 position) - *Replaces "Instruction"*
* `TEST` (12:00 position)
* `RATE` (3:00 position)
* `RESAMPLE` (6:00 position) - *Replaces "Resample"*


* **Data Flow Difference:**
* APE requires **Input Examples** to generate the instruction.
* **Yellow Path:** Persistent edge from `INPUT_UI_DATA`  `INSTRUCT` (Induction) **AND** `TEST` (Validation).



---

## 5.3 Engine C: PromptBreeder (The "Figure-8" / Concentric)

*Refines the diagram in `PromptBreeder.png` to reduce visual clutter.*

### 5.3.1 Visual Topology

* **Layout:** **Double Oval (Concentric)** or **Figure-8**.
* **Inner Oval (The Execution Loop):**
* `POPULATION` (Center/Left)  `TEST` (Top)  `RATE` (Right).
* *Visual:* Thin solid lines. Fast pulsing animation (represents the "Grind").


* **Outer Oval (The Evolution Loop):**
* `POPULATION`  `MUTATE` (Bottom Left)  `CROSS` (Bottom Right)  `POPULATION`.
* *Visual:* Thick dashed lines. Slow pulsing animation (represents "Generational Change").



### 5.3.2 Animation Trigger

* **Cycle 0:** Blue Edge from User Input  `POPULATION`.
* **Cycle 1+:** Blue Edge Removed. The system is now visually "closed" and self-sustaining.

---

## 5.4 Engine D: S2A (The Optimization Wrapper)

*Refines `S2A.png`. The current screenshot shows the **Runtime Flow** (Read->Filter->Answer). The Visualization must show the **Optimization Flow** (how we improve the Filter).*

### 5.4.1 Visual Topology

* **Layout:** Oval (The Optimization Wrapper) containing a Linear Sequence (The Runtime).
* **The Loop Nodes (Oval):**
* `FILTER_PROMPT` (9:00) - *The "Candidate"*
* `TEST_BENCH` (12:00 -> 3:00) - *The "Runtime Simulation"*
* *(Note: This node conceptually contains the Read->Filter->Refine->Answer pipeline)*


* `EVALUATE` (4:00) - *Did it ignore noise?*
* `OPTIMIZE` (6:00) - *Rewrite the Filter Instruction*


* **Visual Logic:**
* The user optimizes the **Filter Prompt**.
* **Yellow Path:** `INPUT_UI_CONTEXT`  `TEST_BENCH`.
* **Blue Path:** `FILTER_PROMPT`  `TEST_BENCH`  `EVALUATE`  `OPTIMIZE`  `FILTER_PROMPT`.



---

## 5.5 Graphviz Implementation Spec

To ensure the "Oval" shape and "Input Bridging" works in Streamlit:

```python
# Pseudo-spec for the Agent
def render_graph(engine_type, cycle_count, active_node):
    dot = graphviz.Digraph(engine='neato') # 'neato' allows fixed positions
    
    # 1. Define Fixed Oval Positions (Normalized Coordinates)
    # 9:00 = (-2, 0), 12:00 = (0, 1), 3:00 = (2, 0), 6:00 = (0, -1)
    
    # 2. Define Bridging Logic
    if cycle_count == 0:
        # Draw invisible node for UI Anchor
        dot.node('UI_INPUT', pos='-4,0', style='invis')
        # Draw bridging edge
        dot.edge('UI_INPUT', 'START_NODE', color='blue', style='dashed', label='Init')
        
    # 3. Define Persistent Data Logic
    dot.node('UI_DATA', pos='-4,1', style='invis')
    dot.edge('UI_DATA', 'TEST_NODE', color='gold', penwidth='2.0')
    
    # ... Rest of graph generation ...

```