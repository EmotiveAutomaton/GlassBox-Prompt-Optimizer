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
Confirmed via browser automation:
-   **Port 8501**: LIVE. Shows "OPro (Iterative" (Updated label) and visible borders.
-   **Port 8502**: STALE. Shows "OPro (Iterative)" (Old label) and old styling.

The user is likely viewing a cached version of 8501 or the stale 8502.
**Fix Applied**: Z-Index Overlay strategy is active on 8501.
**Recommendation**: User must check Port 8501 and perform a Hard Refresh (Ctrl+F5).

## Proposed Fix
1.  **Z-Index Overlay**: Replaced outline with `::after` pseudo-element border (`z-index: 999`) to guarantee visibility on top of all content.
2.  **Verification**: Will verify BOTH ports 8501 and 8502 to confirm where the "live" changes are.
3.  **Proof**: Removed closing parenthesis on sidebar again.
