# Archived Bug Log - Completed Issues

All bugs below have been successfully resolved.

---

## BUG-001: Sidebar Navigation Buttons Not Full Width/Height
**Status:** Fixed (2026-01-19)  
**Commit:** 88a8c30  
**Resolution:** Applied aggressive CSS targeting all nested divs in sidebar hierarchy.

## BUG-002: Gear Icon Does Not Open Configuration Menu
**Status:** Fixed (2026-01-19)  
**Commit:** 88a8c30  
**Resolution:** Added Global Settings popover to main content area.

## BUG-003: Card Borders Not Aligned Properly
**Status:** Fixed (2026-01-19)  
**Commit:** 88a8c30  
**Resolution:** Simplified card structure to use dark header divs.

## BUG-004: Graph Missing from PROMPT RATINGS Card
**Status:** Fixed (2026-01-19)  
**Commit:** 88a8c30  
**Resolution:** Added `_render_optimization_graph()` function inline in zone_c_results.py.

## BUG-008: Cards Need Visible Outlines
**Status:** Fixed (2026-01-19)  
**Commit:** 7cfa93b  
**Resolution:** Using `st.container(border=True)` for all cards.

## BUG-009: Global Settings Button in Wrong Location
**Status:** Fixed (2026-01-19)  
**Commit:** 7cfa93b  
**Resolution:** Removed popover from app.py main().

## BUG-010: Remove Free Play Mode
**Status:** Fixed (2026-01-19)  
**Commit:** 7cfa93b  
**Resolution:** Rewrote zone_c_results.py with horizontal test inputs.
