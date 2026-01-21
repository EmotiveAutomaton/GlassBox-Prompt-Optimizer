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

## Description
The user reports that the borders around the 5 main UI cards ("INITIAL PROMPT", "GLASS BOX", etc.) are "totally invisible".
This persists despite:
1.  Adding `border: 1px solid #e0e0e0`
2.  Adding `border: 1px solid #B0B0B0`
3.  Adding `border: 2px solid #000000` AND `box-shadow: 0 0 0 2px #000000`

The browser automation subagent *can* see the black borders in the screenshot (`ui_debug_proof_final`), but the user cannot. This is a critical disconnect.

## Potential Causes
-   **CSS Injection Latency**: Maybe CSS applies late?
-   **Z-Index/Stacking Context**: Content inside the card might be rendering *over* the border (if using `inset` shadow) or the border is clipped.
-   **Browser Specificity**: User might be on a browser that handles `!important` on `data-testid` differently (unlikely).
-   **Outline vs Border**: `border` changes layout/size. `outline` sits on top.

## Investigation Update (latest)
Attempted pure black borders. User confirmed text update (app refreshed) but "still can see no borders".

## Proposed Fix
1.  **Use `outline`**: Switch to `outline: 2px solid #555555 !important;`. Outlines are drawn *outside* the element's border edge and do not take up space, often avoiding clipping.
2.  **Inset Shadow**: Try `box-shadow: inset 0 0 0 2px #555555 !important;` to draw border *inside* the card (on top of background).
3.  **Target Child**: Apply border to the direct child `div[data-testid="stVerticalBlock"]` if the wrapper is problematic.
