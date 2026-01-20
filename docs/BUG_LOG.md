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
| BUG-001 | 2026-01-19 | 88a8c30 | Aggressive CSS for sidebar |
| BUG-002 | 2026-01-19 | 88a8c30 | Global Settings popover in main area |
| BUG-003 | 2026-01-19 | 88a8c30 | Simplified card header structure |
| BUG-004 | 2026-01-19 | 88a8c30 | Restored optimization graph |

---

## New Issues (2026-01-19 17:13)

### BUG-005: Sidebar Buttons Not Flush Left or Top
**Status:** In Progress  
**Severity:** High  
**Description:** Sidebar buttons still have dead space on the left side and need to move up to be flush with the blue top bar.  
**Expected:** All 4 buttons flush with left edge and top edge of sidebar.

### BUG-006: Gray Flash When Switching Engines
**Status:** In Progress  
**Severity:** Low  
**Description:** The intersection between blue bar and gray sidebar flashes gray when clicking different engines.  
**Expected:** No visual flash during navigation.

### BUG-007: Gear Icon Does Not Open Config
**Status:** In Progress  
**Severity:** High  
**Description:** The gear icon in the top-right of the top bar still does not open the configuration menu.  
**Expected:** Clicking gear icon should open config popover with import/export.

### BUG-008: Cards Need Visible Outlines
**Status:** In Progress  
**Severity:** Medium  
**Description:** Card sections need visible outlines (shadow or border) to delineate each of the 5 sections.  
**Expected:** Each card should have a visible border or shadow.

### BUG-009: Global Settings Button in Wrong Location
**Status:** In Progress  
**Severity:** High  
**Description:** The Global Settings button appears at the top-left of the white content area. It should only be accessible via gear icon.  
**Expected:** Remove button from main area; config only via gear icon.

### BUG-010: Remove Free Play Mode
**Status:** In Progress  
**Severity:** Medium  
**Description:** Free Play mode should be removed. Only Test Bench with horizontal A/B/C inputs needed.  
**Expected:** Test inputs arranged horizontally, card made smaller.
