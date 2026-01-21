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

## Resolution Plan
1.  **Color**: Use `div[data-testid="stButton"] > button` specificity to override Theme Primary Color.
2.  **Visibility**: Remove aggressive negative margins if they cause clipping. Try "Overlay" approach or revert to "Tight Sidecar" with zero gaps.
    *   *Decision*: User insisted on "Attached". Will try to make the sidecar physically closer and ensure `overflow: visible` is applied to parents.
3.  **Width**: Reduce column width ratios for buttons.
4.  **Drag/Drop**: Inspect CSS for `background-color` leaks.
