# BUG-026: Zone C Selection Logic Regression

## Description
After fixing the "Hover Select All" bug (BUG-025) by adding strict scoping to the hover CSS, a similar issue appeared for the **Selection** state.
**Issue:** When clicking a row, the `ghost-marker-primary` class is applied. The CSS rule for this state likely lacks the same strict scoping/exclusion logic as the hover fix, causing it to match the **Parent Layout Block** (which contains the row with the marker).
**Result:** Clicking ONE row causes ALL rows to turn permanently blue.

## Root Cause
- The CSS rule for `.ghost-marker-primary` was updated to use `var(--boeing-blue)` but was NOT updated to use the `:not(:has(...))` exclusion logic or the `.zone-c-row-scope` descendant check.

## Proposed Resolution
1.  **Apply Scoping:** Update the `.ghost-marker-primary` (and secondary) CSS rules to use the exact same selector strategy as the hover fix:
    ```css
    div[data-testid="stHorizontalBlock"]:not(:has(div[data-testid="stHorizontalBlock"])):has(.ghost-marker-primary) button
    ```
