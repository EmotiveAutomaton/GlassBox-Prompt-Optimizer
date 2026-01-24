# BUG-014: Invisible Card Borders Regression

## Status: Active
**Date:** 2026-01-21
**Severity:** High (UI Regression)
**Component:** Styles / CSS

## Description
The user reports that the borders around the 5 main UI cards ("INITIAL PROMPT", "GLASS BOX", etc.) are "totally invisible".
This persists despite:
1.  Adding `border: 1px solid #e0e0e0`
2.  Adding `border: 1px solid #B0B0B0`
3.  Adding `border: 2px solid #555555`

## Failed Attempts
1.  **Iter 32:** Overlay (`::after`) and Box-Shadow. **FAILED** (Invisible).
2.  **Iter 33:** Anchor Targeting (`:has(.card-anchor)`) + Outline. **FAILED** (Invisible).
3.  **Iter 34:** Alert Masquerade (`st.info`). **FAILED**.
    -   Result: "Whole center white space has been gutted."
    -   Cause: `st.info` has strict internal padding/flex rules that collapsed the layout content.

## Analysis
"Invisible Borders" is proving to be a persistent issue likely tied to:
1.  **Theme Injection:** Streamlit's iframe might be stripping custom non-standard CSS properties on containers.
2.  **Structure:** `st.container(border=True)` might simply render as a `div` without the classes we expect in this specific deployment environment.

## Current State (Reverted to Iter 31)
We are back to the standard `st.container(border=True)` which the user reports as invisible.
We need to explore solutions that do NOT rely on standard container styling (perhaps drawing the box manually with HTML around the content block).
