# BUG-023: Persistent Column Width and Hover Issues in Results Table

**Status:** Open
**Severity:** Medium
**Component:** UI / Zone C

## Description
Despite multiple attempts to constrain column widths (`Score`, `Iter`) and enable hover-to-expand behavior for the `Prompt` column in `st.dataframe`, the user reports:
1.  Columns are "still far too wide".
2.  Hover does not show the full prompt; user must double-click.

## History
- **Attempt 1:** Used `width="small"`. Result: Too wide.
- **Attempt 2:** Used `width=80` (px). Result: Too wide.
- **Attempt 3:** Used `width=40` (px). Result: Still reported as too wide / visual issues.
- **Hover:** `max_chars` removed, `help` added. Still requires double-click.

## Root Cause Analysis
- **Widths:** Streamlit's `st.dataframe` has minimum column widths enforced by the underlying AG Grid implementation. 40px might be below the threshold where it forces a minimum, or the header text ("Score") is forcing width.
- **Hover:** Standard `TextColumn` behavior truncates. Use `st.dataframe` textual tooltips might require specific configuration or `st.data_editor` read-only mode.

## Proposed Resolution
- Investigate `st.dataframe` minimums. Consider renaming headers to be shorter if text wrapping isn't happening (e.g. "S", "#").
- Explore `st.table` (static, full text) if `dataframe` interactivity isn't strictly needed, OR `st.components.v1.html` for a custom table if pixel-perfect control is needed. (Prefer `st.dataframe` config tweaks first).
