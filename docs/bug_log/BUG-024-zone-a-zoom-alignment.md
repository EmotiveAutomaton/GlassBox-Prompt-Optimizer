# BUG-024: Zone A Dataset X Buttons Floating/Detaching on Zoom

**Status:** Open
**Severity:** Low (Visual)
**Component:** UI / Zone A

## Description
The "X" delete buttons for Datasets 2+ are implemented as separate buttons or using absolute positioning CSS.
User checks: "Moved to the right a little bit... sliding out and in depending" on browser zoom.

## Root Cause Analysis
- Likely using `position: absolute` or relative offsets in `styles.py` that don't scale linearly with Streamlit's REM/EM sizing or container flex behavior.
- Use of separate columns for the Badge might be creating a gap that varies with zoom.

## Proposed Resolution
- Avoid `position: absolute` if possible.
- Use `st.columns` inside the button container more strictly.
- Or use `st.error` / `st.pills` if they offer delete functionality (Streamlit 1.40+ `st.pills` has selection, maybe not delete).
- Refine CSS to use `%` or `flex` alignment instead of fixed pixels.
