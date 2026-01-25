# Software Requirements Specification: Front-End Visuals & Interactions (Part 2)

**Version:** 0.0.6-alpha (Revised Post-Rollback)
**Date:** 2026-01-25
**Status:** DRAFT (Ready for Implementation Plan)

**Section 8: Zone A - The Unified Input & "Hydraulic" Glass Box**

## 8.1 Zone A: Unified Input Architecture

We are moving away from the "Split Header" failure of the previous attempt. Zone A must remain a **Single Cohesive Banner** titled "initial prompt and data" (or similar unified header). Inside this unified zone, we use internal boxing.

### 8.1.1 The Two Internal Boxes
Inside the unified Zone A container, visual separation is achieved via colored borders on internal `st.container` elements, **NOT** separate top-level headers.

*   **Box 1 (Left/Top): "Initial Prompt"**
    *   **Visual:** Blue Border (Boeing Primary).
    *   **Label:** Small internal label "Initial Prompt".
    *   **Content:** Text Area for seed prompt.
    *   **Connection:** Blue Arrow -> Center (12:00).

*   **Box 2 (Left/Bottom): "Data"**
    *   **Visual:** Yellow Border (Boeing Warning/Data color).
    *   **Label:** Small internal label "Data".
    *   **Content:** Tab Selector + File Uploader.
    *   **Connection:** Yellow Arrow -> Center (09:00).

*   **Constraint:** These boxes must be clearly contained within the left column of Zone A. No negative margins or overlapping headers that obscure content.

---

## 8.2 The "Hydraulic" Schematic Diagram (Zone A - Center)

The visualization remains the "Hydraulic" state machine (CCW Loop), but with robust implementation.

### 8.2.1 Node Topology (Counter-Clockwise)
*   **Node 1 (12:00):** `CURRENT PROMPT` (Blue).
*   **Node 2 (09:00):** `TEST` (Yellow).
*   **Node 3 (06:00):** `RATE` (Gray).
*   **Node 4 (03:00):** `CHANGE` (Gray).

### 8.2.2 Animation & Real-time Feedback
*   **Start Trigger:** When Optimization begins, the Blue Arrow (Input -> 12:00) disappears.
*   **Active State:** Nodes fill with color gradients.
*   **Zone D Linkage:** See Section 9.1 below.

---

## 8.3 Zone A - Right Panel (Readout)

*   **Split View:** Two stacked logic boxes.
    *   **Top:** "System Logic / Input"
    *   **Bottom:** "Result / Output"
*   **Behavior:** Updates synchronously with the active node.

---

**Section 9: Zone D - Telemetry Graph (The "Instant Dot")**

## 9.1 The "Instant Dot" Requirement

*   **Problem:** Currently, the Telemetry Graph (Zone D) is empty until a full cycle completes.
*   **Requirement:** As soon as an iteration begins (Cycle Start):
    *   A **"Pending Dot"** must appear on the **Zone D Telemetry Graph** immediately.
    *   **State 1 (Pending):** The dot exists at `X = Iteration N`, but with `Y = 0` (or a baseline). It should be visually distinct (e.g., hollow, gray, or pulsing).
    *   **State 2 (Scored):** Once the `RATE` step completes and a score is available, the Dot "moves up" (animates or updates) to its final `Y = Score` position and becomes solid.
*   **Goal:** The user "sees" the iteration birth immediately in the history graph, providing confidence the system is working.