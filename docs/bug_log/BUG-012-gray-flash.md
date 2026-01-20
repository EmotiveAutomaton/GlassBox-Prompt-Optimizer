# BUG-012: Gray Flash When Switching Engines

**Status:** In Progress  
**Severity:** Medium  
**Created:** 2026-01-19  

## Description
When clicking between different engine options in the sidebar, a gray flash appears at the intersection of the blue top bar and the gray sidebar.

## Expected Behavior
No visual artifacts or flashing during navigation between engines.

## Root Cause
Streamlit's rerun mechanism briefly removes/recreates DOM elements, causing the sidebar background to flash behind the top bar during the transition.

## Proposed Fix
1. Set explicit background-color on all sidebar elements
2. Disable CSS transitions on sidebar during reruns
3. Ensure z-index prevents any overlap issues
