# BUG-027: Zone C Row Compression Failure

## Status: Active
**Date:** 2026-01-23
**Severity:** Medium (UI Polish)
**Component:** Styles (Zone C)

## Description
## Attempts
1.  **Iter 32 (CSS):** Padding/Margin overrides on `st.button` failed.
2.  **Iter 33 (Dataframe):** Switched to `st.dataframe`. **FAILED**.
    -   Reason: "Couldn't get columns to narrow properly."
    -   Result: Sparse UI, wasted space, not density.

## Analysis
Streamlit's `st.dataframe` and `st.data_editor` set column widths based on header length + content, and pixel-perfect shrinking (e.g., "Score" column being exactly 40px) is notoriously difficult or ignored.

## Proposed Solution (Iter 34)
**Formatted Multiline Buttons (`st.button` as Row)**
-   Instead of `st.columns` (which introduces gap) or `st.dataframe` (which introduces padding/width issues).
-   Use **ONE button per candidate**.
-   Format the label string to include data: `"[95] (It:12) Prompt..."`
-   Apply CSS to *this specific button* to align text left and monospace it?
-   Benefits:
    -   Single element (High density).
    -   Native interaction.
    -   No column gap issues.

## Proposed Solution (New)
-   **Abandon `st.button` for List:** The button component is too rigid.
-   **Switch to:** Custom HTML/JS Component for the list? Or `st.dataframe` with selection interaction?
-   **Or:** A clickable link structure using `st.markdown` with callback support (simulated).

## Potential Causes
-   **Streamlit Minimums:** Streamlit buttons (`st.button`) might have hardcoded `min-height` or internal padding that requires deeper CSS targeting (e.g., `div[data-testid="stMarkdownContainer"]` inside the button).
-   **Flex Gap:** The parent container gap might be overriding distinct row styles.
-   **Selector Specificity:** The CSS might not have been applying correctly (though we fixed the syntax error).

## Next Steps (Future Iteration)
-   Investigate Streamlit button internal DOM structure.
-   Consider using a custom component or HTML table for tighter control if `st.button` is too rigid.
