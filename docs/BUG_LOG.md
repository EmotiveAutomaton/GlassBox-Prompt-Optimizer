# GlassBox Prompt Optimizer - Bug Log

## Startup Issues (2026-01-19)

### BUG-001: Sidebar Navigation Buttons Not Full Width/Height
**Status:** Fixed  
**Severity:** High  
**Description:** Navigation buttons in the left sidebar do not extend to the full width and height of the panel. There is visible dead space around the buttons.  
**Expected:** Buttons should be flush with all four edges of the sidebar panel, with the top button aligned directly below the top bar.  
**Root Cause:** CSS selectors not targeting the correct Streamlit elements or padding/margin not fully removed.  
**Resolution:** Applied aggressive CSS targeting all nested divs in sidebar hierarchy with `!important` rules.

### BUG-002: Gear Icon Does Not Open Configuration Menu
**Status:** Fixed  
**Severity:** High  
**Description:** The gear icon in the top-right of the top bar does not open the configuration menu with import/export options.  
**Expected:** Clicking the gear icon should open the configuration popover containing import/export session functionality.  
**Root Cause:** JavaScript onclick handler has no corresponding Streamlit element to trigger.  
**Resolution:** Added "⚙️ Global Settings" popover to main content area with full import/export functionality.

### BUG-003: Card Borders Not Aligned Properly
**Status:** Fixed  
**Severity:** Medium  
**Description:** The card boxes have a header bar but the border does not run the entire length of the card content. Content appears outside the card boundaries.  
**Expected:** Each card should have a complete border around both the header and all content within.  
**Root Cause:** HTML structure has closing tags in wrong position or CSS not applying border correctly.  
**Resolution:** Simplified card structure to use dark header divs that visually group with Streamlit content below.

### BUG-004: Graph Missing from PROMPT RATINGS Card
**Status:** Fixed  
**Severity:** Medium  
**Description:** The PROMPT RATINGS card does not contain the optimization progress graph.  
**Expected:** The graph should be rendered inside the PROMPT RATINGS card with no separate header.  
**Root Cause:** Graph rendering code was removed during zone consolidation.  
**Resolution:** Added `_render_optimization_graph()` function inline in zone_c_results.py.

---

## Resolution Log

| Bug ID | Date Fixed | Commit | Notes |
|--------|------------|--------|-------|
| BUG-001 | 2026-01-19 | Pending | Aggressive CSS for sidebar |
| BUG-002 | 2026-01-19 | Pending | Global Settings popover in main area |
| BUG-003 | 2026-01-19 | Pending | Simplified card header structure |
| BUG-004 | 2026-01-19 | Pending | Restored optimization graph |
