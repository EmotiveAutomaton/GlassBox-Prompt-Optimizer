# BUG-011: Sidebar Buttons Not Flush Left or Top

**Status:** In Progress  
**Severity:** High  
**Created:** 2026-01-19  

## Description
Sidebar navigation buttons have visible dead space on the left side and are not flush with the blue top bar.

## Expected Behavior
All 4 engine buttons should be flush with:
- Left edge of sidebar (no gap)
- Bottom of blue top bar (no gap)

## Attempts

### Attempt 1: Aggressive CSS with !important
Applied padding/margin removal to all nested div levels.
**Result:** Partial success - left padding reduced but not eliminated.

### Attempt 2: Explicit 220px width
Set width: 220px on radio group and labels.
**Result:** Improved left alignment but gap remains.

### Attempt 3: Negative margin-top
Applied `margin-top: -10px` to radio group.
**Result:** Slight improvement but still visible gap at top.

### Attempt 4: Absolute positioning
Positioned radio group with `position: absolute; top: 0; left: 0`.
**Result:** Did not work as expected in Streamlit context.

### Attempt 5: Relative positioning with negative margin
Used `position: relative; margin-top: -16px` on .stRadio.
**Result:** Improved but still visible gap remains.

## Root Cause Analysis
Streamlit's internal component structure has multiple wrapper divs with default padding/gap that override CSS. The sidebar content area has internal spacing that cannot be fully removed with standard CSS selectors.
