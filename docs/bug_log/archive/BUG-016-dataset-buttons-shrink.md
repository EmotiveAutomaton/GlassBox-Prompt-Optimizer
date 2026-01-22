# Bug: Dataset Buttons Shrink to Unreadable Width (RESOLVED Iter 7)

## Issue Description
As new datasets are added, the buttons become narrower until text is unreadable ("barely see the first five letters").

## Attempted Fix (Failed)
**Strategy:** Used a "Spacer Column" with weight `15` vs `1` for buttons (`col_ratios = [1]*N + [0.5] + [15]`).
**Assumption:** The Spacer would take up the "excess" room, leaving fixed space (approx 6-7%) for buttons.
**Mistake:** 6% of the screen width is too small for the text "Dataset X". Streamlit's column logic subdivides the total width proportionally. `1/(N+15.5)` becomes tiny.

## Analysis
- **Root Cause:** Proportional weighting in `st.columns` forces elements to share width. Fixed pixel width is not natively supported in `st.columns` without extensive CSS or flexbox hacks.
- **Goal:** Fixed width "Pills" that wrap or scroll, OR simply fill available space intelligently without shrinking below readability.

## Options Going Forward
1.  **CSS Grid/Flexbox:** Abandon `st.columns` layout for the buttons and use a custom HTML container (`st.markdown`) with `display: flex; gap: 8px; flex-wrap: wrap;`. This allows pills to be "auto" width based on text.
    *   *Pros:* Perfect "Pill" sizing.
    *   *Cons:* Can't use native `st.button` easily. Need `st.button` logic or custom component. (Wait, styles can target `st.button` if they are in standard columns?). No, standard columns force width.
2.  **Scrollable Container:** Put buttons in a horizontal scroll container? Hard in Streamlit.
3.  **Adjust Ratios:** Use `col_ratios = [0.15] * N + [spacer]`. Ensure the sum doesn't exceed 1? No, logic is relative.
4.  **Revert to "Auto" (No Spacer):** Iteration 5 layout was working better? User said "buttons... get even narrower" in Iter 6. Iter 5 used `0.05` fixed? No, `0.05` is a ratio.

## Recommendation
Investigate if `st.button` can be rendered inside a custom `div` that ignores the column width constraints, or revert to the previous layout and accept some width variance?
**Best Bet:** Revisit the simple layout but use CSS `min-width` on the buttons to prevent shrinking below ~100px.
