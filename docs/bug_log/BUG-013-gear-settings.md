# BUG-013: Gear Icon Does Not Open Settings Panel

**Status:** In Progress  
**Severity:** High  
**Created:** 2026-01-19  

## Description
The gear icon in the top-right of the blue top bar does not open a settings panel when clicked.

## Expected Behavior
Clicking the gear icon should open a dropdown/popover containing:
- Light/Dark mode toggle (disabled by default, set to Light)
- Import session option
- Export session option

## Root Cause
The gear icon is rendered as an SVG with an onclick handler, but Streamlit's popover cannot be triggered via JavaScript. The onclick causes a page rerun but no popover appears.

## Implementation Attempt
Created a settings popover with `st.popover("⚙️")` containing:
- Light/Dark mode toggle (disabled, set to Light)
- Export Session button
- Import Session file uploader

**Issue:** The popover appears in the content flow (top-left of content area) rather than the intended top-right position. CSS `position: fixed` is not applying as expected to the container.
