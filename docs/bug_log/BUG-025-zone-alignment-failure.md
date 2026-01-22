# BUG-025: Zone Alignment Failures & Header Regression

## Description
Attempts to align "Initial Prompt and Data" (Left) and "Glass Box" (Right) using spacer divs caused regressions:
1.  **Alignment Failure:** Injecting 22px spacer did not correctly align the tops of the containers. Visual measurements showed significant discrepancies.
2.  **Header Regression (Glass Box):** Injecting a hidden CSS marker (`<div class="glassbox-height-marker" ...>`) *inside* the Glass Box container pushed the "GLASS BOX" header down.
    -   **Cause:** Streamlit wraps the marker in a `div` that participates in the flex/grid layout of `stVerticalBlock`, triggering the default `gap` (1rem/16px) before the Header.

## Diagnosis
-   **Spacers:** Adding `st.markdown` spacers injects a prompt/data row item, which pushes content down but might behave unpredictably with top alignment in columns.
-   **Markers:** Invisible markers must be placed *after* visible content or hidden via CSS (`display: none` on the *wrapper*) to avoid layout shifts.

## Corrective Plan
1.  **Revert:** Remove all spacer divs and the top-placed marker in GlassBox.
2.  **Align via CSS:**
    -   Target the **Glass Box container** and potentially the **Initial Prompt container** using reliable selectors (or markers placed at the *bottom*).
    -   Use `margin-top` on the Initial Prompt container to push it down precisely.
    -   Alternatively, simply leave them flush and check if the "9px difference" was a measurement artifact or real. (User said "Initial prompt... is cut off").
    -   If "cut off", the container might be overflowing or clipped by a parent. "Cut off" usually implies `overflow: hidden` or negative margins.
3.  **Glass Box Height:**
    -   Move the height marker to the **end** of the container so it doesn't affect the header position.
    -   Apply `min-height` via CSS.

## Goal
-   Both headers aligned at the top (flush or with equal gap).
-   Full text visible (no cutoff).
-   Glass Box height matches Initial Prompt (~384px).
