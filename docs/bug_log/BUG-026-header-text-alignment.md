# BUG-026: Persistent Header Misalignment & Text Cutoff

## Description
User reports and verifies that despite CSS container alignment, the "Initial Prompt and Data" header appears **cut off** at the top and visually misaligned with "Glass Box".
Measurements show:
-   **Text Top Misalignment:** Left Header Text is 9px *higher* than Right Header Text (72.75px vs 81.75px).
-   **Container Misalignment:** Left Container is 9px *higher* than Right Container.
-   **Visual:** "Lower end of the header" doesn't line up.

## Root Cause Analysis
-   Previous iterations attempted to fix this by adding `margin-top` to the Left Column.
-   Current CSS: `margin-top: 37px` on Left Column.
-   Despite this, the Browser measures the Left Column as starting at ~88px (Container) or 72px (Text).
-   Wait, 72.75px (Text) < 81.75px (Text). Delta = 9px.
-   If we added 37px margin, why is it still higher?
    -   Maybe GlassBox has implicit margin?
    -   Maybe the "Initial Prompt" container has negative margin or `st.container` padding issues.
    -   Or maybe my 37px margin isn't applying correctly or is being overridden.

## Corrective Plan
1.  **Increase Spacing:** The gap is consistent (9px). Increase Left Margin by another 9px -> **46px**.
2.  **Verify Text Base:** Align based on *Text Top* metric (Target: 81.75px).
    -   Current: 72.75px.
    -   Delta: 9px.
    -   Required Adjustment: +9px.
    -   New Margin: 37px + 9px = **46px**.
3.  **Check Padding:** Also ensure the header *background* isn't cut off. If text moves down, background moves down.

## Implementation
-   Update `styles.py`.
-   Selector: `div[data-testid="stVerticalBlockBorderWrapper"]:has(.zone-a-left-marker)`
-   Value: `margin-top: 46px !important;`
