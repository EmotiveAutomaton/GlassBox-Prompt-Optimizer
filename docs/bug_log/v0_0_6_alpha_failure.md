# Bug Log: v0.0.6-alpha Rollout Failure

**Date:** 2026-01-25
**Status:** ROLLED BACK to v0.0.5-alpha (Commit `eb7e984`)

## Incident Summary
The initial attempt to implement Requirements Version 0.0.6-alpha resulted in a "hard failure" of the User Interface, particularly in Zone A (The Header/Input Area). The application became unusable due to hidden controls and layout collapse.

## Critical Issues Identified

### 1. "Gutted" Zone A Layout
*   **Observation:** The user reported that Zone A looked "gutted." Buttons were missing, the data loading area was invisible, and only the "Starting Prompt" and "Start Optimization" elements were somewhat visible but broken.
*   **Cause:** The attempt to split Zone A into two separate columns or containers with aggressive custom CSS (`margins`, `z-index` overlays) likely caused:
    *   Container content clipping (overflow hidden).
    *   `pointer-events: none` overlay from the custom border logic blocking text inputs and buttons (User reported "couldn't see the area that we had to load data").
    *   Negative margins for "Flush Headers" pulling content out of the viewable viewport or behind other elements.

### 2. Header Strategy Failure
*   **Observation:** The implementation tried to place "Data Source" and "Starting Prompt" as separate high-level headers (H2/H3).
*   **User Feedback:** "It looks like you may have split it into two headers... We don't want that."
*   **Correction Requirement:** Zone A should remain a **Unified Zone** ("Initial Prompt and Data") containing two internal sub-boxes (Blue/Yellow) rather than breaking the high-level page flow.

### 3. Missing Feedback in Zone C
*   **Observation:** Users want immediate feedback when an iteration starts.
*   **Requirement:** The "Result Dot" (or placeholder) in Zone C must appear **as soon as the iteration begins**, floating or animating, rather than waiting for the cycle to complete before rendering anything.

## Corrective Actions (for Next Attempt)
1.  **Simplify CSS:** Avoid complex negative-margin hacks and z-index overlays for simple borders. Use standard Streamlit `border=True` or simpler wrapper divs.
2.  **Unified Layout:** Keep the top banner as a single cohesive "Zone A" unit.
3.  **Real-time State:** Ensure the backend pushes a "Pending Candidate" to the frontend state *immediately* upon clicking Start, so Zone C can render the "Dot".
