# Bug: Button Style Swap Regression

## Issue Description
User requested a style swap:
1.  **Plus Button (+):** Should be **Solid Gray** (Standard Secondary).
2.  **Stop Optimization:** Should be **Ghost Blue** (White BG, Blue Text/Border).

## Regression (Iter 16)
Attempted to implement this via `data-type` markers injected into columns.
**Result:** "The style for the stop optimization button was applied incorrectly to ALL other buttons (Start, Dataset 1, Dataset 2, Plus)."
**Cause (Hypothesis):**
-   CSS Selector Specificity/Leakage.
-   Possible malformed CSS or cascaded inheritance where the "Ghost" rule overwhelmed the defaults.
-   Structural Selectors (`:has`, `:last-child`) are fragile in Streamlit's nested DOM.

## Proposed Logic (Attribute Selectors)
Instead of relying on DOM structure or Markers, utilize Streamlit's `help` parameter which renders as `title` or `aria-label` attributes on the button element (or its container).
**Strategy:**
1.  Ensure `help` text is unique and descriptive.
    -   Plus: `help="Add new dataset"`
    -   Stop: `help="Stop Optimization"`
    -   Start: `help="Start Optimization"` (Add if missing)
2.  Target via CSS Attribute Selectors:
    ```css
    button[title="Add new dataset"] { ... }
    button[title="Stop Optimization"] { ... }
    ```
    *Note: Streamlit sometimes puts the title on the `<button>` and sometimes on the wrapper. Need to verify.*
    *If title is on the button:* `button[title="..."]` works.
    *If title is on the parent:* `div:has(button[title="..."])`.

## Plan
1.  Verify where `help` text appears in the DOM.
2.  Apply targeted CSS using these attributes.
3.  Clean up any previous "Last Child" or "Marker" logic that was causing instability.
