# BUG-023: Zone C Headers Styling Persistence

## Description
The headers in Zone C (Score, Iter, Prompt Candidate) fail to retain the solid button styling (like Zone A) and instead adopt the "Ghost" styling or a broken hybrid state, despite attempts to isolate the Ghost CSS to data rows.

## Symptoms
- Headers appear transparent or line-based instead of solid rectangles.
- Clicking them works for sorting, but visual feedback is wrong.

## Failed Attempts
1. **Container Isolation:** Moving `.zone-c-ghost-marker` to a data-row-only container.
2. **Column Isolation:** Moving `.ghost-col-marker` to data-row columns only.
   - Result: Headers still potentially affected if they share `st.columns` logic or if CSS selectors are too broad.
   - User reports: "That row has the same look as the rest of the rows."

## Suspected Cause
- `st.columns` in Streamlit might reuse DOM structures or classes that my CSS is targeting broadly (`div[data-testid="stColumn"]`).
- If Headers are in `st.columns` (they are) and Data Rows are in `st.columns` (they are), and I target `stColumn`, I rely on `:has(.ghost-col-marker)`.
- **Hypothesis:** The `.ghost-col-marker` might be leaking into the Header columns? Unlikely logic-wise.
- **Hypothesis 2:** The "Default" Ghost Style (`transparent`) might be applied *without* the marker if my selector is malformed?
- **Hypothesis 3:** The Headers *have* a marker? No.

## Proposed Fix Strategy
- **Explicit Header Class:** Inject a specific `.zone-c-header` marker into the Header columns.
- **CSS Override:** Force `background-color` and `border` for `:has(.zone-c-header)` to match standard buttons, overriding any potential ghost bleed.
- **Debug:** Check if Headers are accidentally receiving the ghost marker.

## Status
- logged
