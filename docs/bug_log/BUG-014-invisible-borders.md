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

The browser automation subagent *can* see the borders in the DOM and screenshot, but the user cannot. This suggests:
-   A monitor contrast issue (unlikely given "totally invisible").
-   Browser caching of old CSS.
-   A specific clipping/rendering issue on the user's display/browser engine.
-   Streamlit `border=True` wrapper being overridden by global resets.

## Steps to Reproduce
1.  Open App.
2.  Look at the main cards (Initial Prompt, Glass Box, etc.).
3.  Observe white background merging with card background (no outline).

## Proposed Fix
1.  **Robust Borders:** use `box-shadow` to simulate borders, as it paints outside the box model and is often less susceptible to `box-sizing` quirks.
    -   `box-shadow: 0 0 0 2px #000000 !important;`
2.  **Fallback:** Apply border to the internal `stVerticalBlock` as well.
