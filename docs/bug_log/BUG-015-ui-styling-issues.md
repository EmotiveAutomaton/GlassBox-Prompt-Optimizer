# Bug Log: Toggle/Delete Button Styling Issues

## Issue Description
User requires specific "Android-style" badge removal buttons for datasets, and specific "Boeing Blue" coloration.
Current state: Buttons are Red (default theme), X badge is invisible, and Drag/Drop area is darkened.

## Attempt History
1.  **Inline Radio**: Failed (Streaming `st.radio` doesn't support nested buttons).
2.  **Sidecar Buttons**: Implemented. User rejected ("Don't want detached X").
3.  **Corner Badge (CSS Hack)**: Implemented using negative margins.
    *   **Result**: "X icon not visible".
    *   **Root Cause**: Likely `overflow: hidden` on Streamlit column containers or z-index stacking context issues.
    *   **Side Effect**: Drag/Drop area darkened (Generic CSS selector collision?).
    *   **Side Effect**: Buttons remained Red (CSS Specificity lower than Streamlit default).

## Resolution (Fixed)
- **Column Logic**: Switched to `stColumn` CSS selectors and extremely narrow python column ratios (`0.08` vs `0.2`) to force the "Pill" look.
- **Badge Positioning**: Used `position: absolute` with `left: -12px` and `top: 0` on the *next* column's button to visually superimpose it on the previous column's button.
- **Transparency**: Added `opacity: 0.5` to the Add button.
- **Coloration**: Used `data-testid="stColumn"` structural selectors to reliably target buttons and apply Boeing Blue (`#1A409F`) to active states and White to inactive.
