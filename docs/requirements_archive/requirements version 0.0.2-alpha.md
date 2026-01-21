
# Software Requirements Specification: GlassBox Prompt Optimizer v0.0.2-alpha

**Section 5: "Glass Box" Visualization & Logic**

## 5.1 The "Glass Box" Readout Panel (Zone A - Right)

* **Purpose:** To inspect the exact system prompt driving any node in the diagram.
* **Component:** Read-only `st.code` block with a colored border matching the active node.
* **Header Controls:**
* **"Follow Along" Toggle (Checkbox):**
* **ON (Default):** The panel automatically updates to show the System Prompt of the currently *active* (glowing) node in the loop.
* **OFF:** The panel stays static until the user manually clicks a node in the diagram.




* **Interaction:** Clicking a node in the Graphviz diagram (Zone A - Center) forces the Readout Panel to display that node's underlying prompt, effectively unchecking "Follow Along".

---

## 5.2 Engine A: OPro (Optimization by PROmpting)

**Concept:** The Basic Optimization Loop.

### 5.2.1 Input Area (Zone A - Left)

* **Label 1:** `Starting Prompt` (Text Area)
* **Label 2:** `Test Data` (Text Area)

### 5.2.2 Graphviz Diagram Schema (Zone A - Center)

* **Topology:** Circular Loop (Clockwise).
* **Node Labels:**
1. `START` [Label: "Current Prompt"]
2. `TEST` [Label: "Test"]
3. `RATE` [Label: "Rate"]
4. `CHANGE` [Label: "Change"]


* **Edges:**
* `START` -> `TEST`
* `TEST` -> `RATE`
* `RATE` -> `CHANGE`
* `CHANGE` -> `START`



---

## 5.3 Engine B: APE (Automatic Prompt Engineer)

**Concept:** The Instruction Induction Loop (Functionally mirrored to OPro).

### 5.3.1 Input Area (Zone A - Left)

* **Label 1:** `Input Data` (Text Area)
* **Label 2:** `Ideal Output` (Text Area)
* **Interaction:** When both fields have text, a generic "Tab" appears below (e.g., `[Ex 1]`, `[+]`), allowing the user to click `[+]` to add a second pair of input/output examples.

### 5.3.2 Graphviz Diagram Schema (Zone A - Center)

* **Topology:** Circular Loop (Clockwise) - Identical visual structure to Engine A for consistency.
* **Node Labels:**
1. `START` [Label: "Current Instruction"]
2. `TEST` [Label: "Test"] (Runs instruction against the Input/Output pairs).
3. `RATE` [Label: "Rate"] (Calculates accuracy of instruction).
4. `CHANGE` [Label: "Resample"] (Generates new instruction variations).


* **Edges:**
* `START` -> `TEST` -> `RATE` -> `CHANGE` -> `START`



---

## 5.4 Engine C: PromptBreeder (Evolutionary)

**Concept:** The Evolutionary Cycle.

### 5.4.1 Input Area (Zone A - Left)

* **Label 1:** `Starting Prompt` (Text Area)
* **Label 2:** `Population Size` (Slider)

### 5.4.2 Graphviz Diagram Schema (Zone A - Center)

* **Topology:** Two Concentric Circles (or Figure-8).
* **Inner Circle:** The Task Loop (Testing the prompt).
* **Outer Circle:** The Evolution Loop (Improving the prompt).


* **Node Labels:**
1. `POOL` [Label: "Population"] (Center Node).
2. `TEST` [Label: "Test"] (Inner Loop).
3. `RATE` [Label: "Rate"] (Inner Loop).
4. `MUTATE` [Label: "Mutate"] (Outer Loop - Changing the prompt).
5. `CROSS` [Label: "Cross"] (Outer Loop - Mixing prompts).


* **Edges:**
* **Evaluation Flow:** `POOL` -> `TEST` -> `RATE` -> `POOL`
* **Evolution Flow:** `POOL` -> `MUTATE` -> `CROSS` -> `POOL`



---

## 5.5 Engine D: S2A (System 2 Attention)

**Concept:** The Context Refinement Pipeline.

### 5.5.1 Input Area (Zone A - Left)

* **Label 1:** `Starting Query` (Text Area)
* **Label 2:** `Raw Context` (Text Area)

### 5.5.2 Graphviz Diagram Schema (Zone A - Center)

* **Topology:** Linear Pipeline (Left-to-Right).
* **Node Labels:**
1. `READ` [Label: "Read Context"]
2. `FILTER` [Label: "Filter"] (The S2A Agent removing noise).
3. `REFINE` [Label: "Refine"] (Re-writing the clean context).
4. `ANSWER` [Label: "Answer"] (Final Generation).


* **Edges:**
* `READ` -> `FILTER` -> `REFINE` -> `ANSWER`
* *(Optional)* `ANSWER` -> `READ` (Dotted line if processing multiple chunks).



---

### Implementation Note for the Agent (Graphviz Naming)

Ensure the internal node IDs in Graphviz (e.g., `node_A`, `node_B`) remain consistent so the Streamlit animation logic can target them reliably by name to apply the "Green/Bold" style attributes during updates.