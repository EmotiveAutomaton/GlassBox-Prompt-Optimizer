# Bug: Stop Optimization Button Mismatch

## Issue Description
"Stop optimization button... doesn't... look like the start optimization button which has a very bubble look... Just looks like a square that is bigger."
User wants "Match Start Button" -> "Large Bubble".

## Attempted Fix (Failed)
**Strategy:** `min-height: 48px`. Changed text to "STOP OPTIMIZATION".
**Assumption:** Size was the only mismatch.
**Mistake:** 
1. **Shape:** Primary buttons (Start) have `border-radius: 1.5rem` (Pill/Bubble). Secondary buttons (Stop) have `border-radius: 0.25rem` (Rounded Rect).
2. **Padding:** Primary buttons often have larger internal padding.

## Analysis
- **Theme:** Streamlit's base theme styles Primary and Secondary differently beyond color.
- **Requirement:** "Same size... colored white". User essentially wants the Primary Button SHAPE but White COLOR.

## Options Going Forward
1.  **Change Type:** Set Stop button to `type="primary"` but override background color to White?
    *   *Issue:* Primary usually implies strict background color variables. Overriding might be fighting the framework.
2.  **CSS mimicry:** Target the Stop button and force `border-radius: 1.5rem` (or whatever the computed style of Primary is).
    *   *Selector:* Target by text `p:contains("STOP")` parent button? Or position.

## Recommendation
Apply `border-radius: 50px` (Pill shape) to the Stop button explicitly to match the "Bubble" look of the Start button.
Target: `div[data-testid="stColumn"] button:has(p:contains("STOP OPTIMIZATION"))` (if supported) or by column index/context.
Use `help="Stop Optimization"` to target `button[title="Stop Optimization"]` for robust styling.
