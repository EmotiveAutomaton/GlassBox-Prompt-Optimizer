# BUG-025: Zone C Hover Logic Failure

## Description
When implementing the "Linked Row Hover" in Zone C, a CSS selector was used that targeted `div[data-testid="stHorizontalBlock"]:has(.ghost-col-marker)`.
**Issue:** This selector inadvertently matched the **Top-Level Layout Block** (splitting the page into [2, 1.5] columns) because that block *contains* the rows as descendants.
**Result:** Hovering anywhere in Zone C triggers the hover state for *every* row simultaneously, as the parent block considers itself hovered and applies the style to all its button descendants.

## Symptoms
- Hovering `Score` on Row 1 highlights Row 1, Row 2, Row 3... ALL rows.
- The color is also incorrect (User reported "Wrong shade of blue", likely `selected-blue` vs `boeing-blue`).

## Root Cause
- CSS Selector Over-reach. `:has()` checks all descendants. The outer layout block has the markers as descendants.
- Need to scope the selector to *only* the inner row blocks.

## Proposed Resolution
1.  **Scope Injection:** Inject a unique marker class (e.g., `<div class="zone-c-row-scope"></div>`) inside the container that holds the rows.
2.  **Descendant Selector:** Update CSS to only target `stHorizontalBlock` elements that are *descendants* of this scope marker's container. The outer layout block is an *ancestor*, so it will be excluded.
3.  **Color Fix:** Switch `var(--selected-blue)` to `var(--boeing-blue)`.
