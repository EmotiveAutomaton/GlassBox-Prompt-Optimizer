# Bug: Plus Button Distortion (Tall/Narrow)

## Issue Description
"The plus button is incredibly tall and narrow... I want it shorter and centered... Small square."
User liked previous size ("less tall"). My changes made it stretch vertically.

## Attempted Fix (Failed)
**Strategy:** `vertical_alignment="center"` in `st.columns`.
**Assumption:** This would center the button vertically.
**Mistake:** 
1. `vertical_alignment="center"` stretches the *row* height to the tallest element (the dataset pills). If `st.button` is set to `use_container_width=True` (or by default in some contexts), it might stretch to fill the *aligned* container height? No, "center" usually keeps intrinsic height.
2. BUT, I might have inadvertently set `height: 100%` or similar in my "Global Button Fix" (`min-height: 48px`). The Plus button inherited `min-height: 48px` which made it "Tall". The narrowness comes from the column width `0.5` vs `1`.

## Analysis
- **Inheritance:** The global `div[data-testid="stColumn"] button { min-height: 48px; }` rule applied to the Plus button too.
- **Override Failure:** My specific override `div[data-testid="stColumn"]:nth-last-of-type(2) button` likely failed to match because of the DOM structure (maybe Spacer isn't last, or `stHorizontalBlock` nesting).

## Options Going Forward
1.  **Specific Key:** Use `key="add_dataset_btn"` in python and try to target by attribute? Streamlit doesn't emit keys to DOM.
2.  **Aria Label:** Use `help="Add Dataset"` and target `button[title="Add Dataset"]` (Streamlit maps help to title). PROVEN STRATEGY.
3.  **CSS Class:** Remove the global `min-height` on all buttons and be more specific for the Start/Stop buttons.

## Recommendation
Use `help="Add New Dataset"` on the Plus button. Target `button[title="Add New Dataset"]` in CSS to force `height: 32px; width: 32px;`.
Remove the global `min-height: 48px` which caused the regression.
