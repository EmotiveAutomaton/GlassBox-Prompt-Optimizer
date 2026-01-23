# BUG-023: UI Layout Regressions & Interaction Flakiness

**Status:** Open
**Priority:** High
**Date:** 2026-01-23

## Description
Recent attempts to "fix" Zone A and Zone C UI resulted in regressions and non-functional features.

### 1. Zone A Layout "Wrecked"
*   **Attempt:** Replaced CSS Flexbox buttons with native `st.columns` constraints.
*   **Result:** User reports layout is "wrecked". Visual alignment of "Dataset" pills and "X" buttons likely lost consistency or broke on zoom. The previous CSS solution, while complex, maintained better specific positioning.
*   **Action:** Rollback to previous CSS-based implementation required.

### 2. Zone C Table Column Widths
*   **Attempt:** Used `st.column_config.NumberColumn(width=30)` to force "Score" and "Iter" columns to be narrow.
*   **Result:** Streamlit/AG Grid ignores the strict width constraint, likely expanding to fill available space or respecting a minimum auto-calculated width. "Did not fix ... at all".

### 3. Zone C Hover Functionality
*   **Attempt:** CSS injection (`.ag-cell-value:hover`).
*   **Result:** Failed to render. Tooltips do not appear.
*   **Second Attempt:** Implemented "Click-to-Select" row detail view.
*   **Result:**  User rejected workflow. Requirement is strict **Hover** behavior.

### 4. Button Interaction Flakiness
*   **Observation:** "Start", "Stop", and other buttons require multiple presses to register.
*   **Potential Cause:** Streamlit state sync race conditions. When a button sets a session state key and `rerun` is triggered, the immediate re-render might process before the event loop fully propagates the state change, or the button `key` binding is resetting the widget state unexpectedly.

## Next Steps
*   Reverting `zone_a_banner.py` and `ui/styles.py` to pre-modification state.
*   Re-applying *only* logic fixes (Batch Size, Session Reset).
*   Investigating non-CSS methods for Zone C Hover (e.g. strict AG Grid options if exposed, or HTML table fallback).
