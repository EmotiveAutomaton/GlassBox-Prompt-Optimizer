# Bug: File List Container Overflow

## Issue Description
When users upload multiple files (>3) to the "Browse files" area, the list of files extends vertically, spilling out of its visual container ("Preset Area"). It does not scroll.

## Constraints
- **Streamlit Containers:** `st.container(height=100)` *should* implicitly create a scrollable area.
- **Global CSS Conflict:** The "Dataset Removal Badges" (on the main tab strip) rely on `position: absolute` + `overflow: visible !important` on all `stVerticalBlock`/`stColumn` divs.
- **Conflict:** `overflow: visible` prevents scrollbars (`overflow: auto`) from working, effectively enforcing infinite height behavior visually.

## Attempt 1 Verification (Failed)
- **Observation:** User reports file list still extends past the viewable box. 4 files are fully visible instead of scrolling.
- **Analysis:** The CSS selector `div[data-testid="stVerticalBlockBorderWrapper"] > div > div[data-testid="stVerticalBlock"]` might be incorrect or overridden by the global rule due to specificity or inheritance issues. The container itself likely needs the scrolling behavior directly, or the internal height calculation is bypassing the constraint.
- **Next Step:** Mock 4 files in UI, Inspect DOM, apply direct scroll to the wrapper.

## Failed Attempt (Iteration 20)
- Removing `overflow: visible` fixed the scroll but broke the Badges (hidden/clipped).
- Rolled back.

## Required Solution
- Implement a scrollable area for the File List (`overflow-y: auto`).
- **MUST NOT** remove the global `overflow: visible` rule (or must refactor Badges first, which is out of scope).
- **Strategy Idea:**
    - Use a highly specific CSS selector for the File List Container that overrides the global rule?
    - `overflow: auto !important` on the *child* (File List) should work if the *parent* has a defined height?
    - If the global rule targets `div[data-testid="stVerticalBlock"]`, we need to target the *specific* Vertical Block of the list and apply `overflow: auto !important`.
    - We need to ensure the specific selector has higher specificity than the global one.
