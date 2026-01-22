# Bug: Dataset Removal Badges Invisible (RESOLVED Iter 7)

## Issue Description
User reported "I cannot see any of the X's at all." Badges are meant to be superimposed on the top-right of dataset buttons.

## Attempted Fix (Failed)
**Strategy:** `overflow: visible` on `stVerticalBlock`, `stColumn`, and absolute positioning `top: -10px; right: -10px`.
**Assumption:** The overflow catch-all would prevent clipping. `z-index: 9999999` would ensure visibility.
**Mistake:** 
1. The badge wrapper in the DOM might not be the `nth-of-type(2)` element anymore (due to layout changes).
2. `right: -10px` might be pushing it off-screen or behind an adjacent sibling with higher stacking context.
3. Streamlit's `iframe` or shadow roots (if any) might be clipping.

## Analysis
- **Iter 5 vs 6:** Iter 5 verified generally okay but user claimed "got rid of little x's" (Iter 4?). In Iter 6 I tried to force visibility but failed completely for the user. My browser agent saw them, which suggests a browser-specific rendering difference OR resolution responsiveness issue.
- **Browser Agent vs User:** The browser agent (likely 1080p+ headless) saw them. User (likely typical or specific resolution) did not.

## Options Going Forward
1.  **In-Flow Button:** Return to the "Split Button" or "Sidecar" approach (separate column) but style it to *look* attached (negative margin). This is safer than absolute positioning out of a zero-width container.
2.  **Relative Positioning:** Place the badge *inside* the button text? (Not possible with standard `st.button`).
3.  **Refined Selector:** Use `div:has(> button)` if supported (it is in modern browsers).
4.  **Debug Mode:** Use a bright background color to find where the badge is rendering.

## Recommendation
Abandon the "Zero Width Wrapper" absolute positioning if it is unreliable. Revert to a separate small column (`col_ratios = [1, 0.2]`) and use negative margins to pull the badge leftwards over the button. This guarantees the element has layout space and isn't clipped by `overflow: hidden` on the parent.
