"""
Zone E: Detail Inspector & Diff Viewer (Bottom Right).

Purpose:
- Single Selection: View full prompt and response details.
- Dual Selection: Visual diff between two prompt versions.
"""

import streamlit as st
import difflib
from typing import Optional, List
from glassbox.models.session import TestBenchConfig
from glassbox.models.candidate import UnifiedCandidate

def render_zone_e(test_bench: TestBenchConfig, winner: Optional[UnifiedCandidate] = None):
    """
    Render the Inspection & Diff Zone.
    Uses 'selected_candidates' object list populated by Zone C.
    """
    # Wrap in Card Container standard
    with st.container(border=True):
        st.markdown('<div class="card-header">DETAIL INSPECTOR & DIFF</div>', unsafe_allow_html=True)
    
        # 1. Get Selection
        selection = st.session_state.get("selected_candidates", [])
        
        # Handle legacy 'winner' arg if passed (for compatibility), but rely on selection
        if not selection and winner:
            pass
    
        if not selection:
            st.info("Select a candidate in 'Potential Prompts' to inspect details.")
            return
    
        # 2. Render based on Count
        if len(selection) == 1:
            _render_single_view(selection[0])
        elif len(selection) >= 2:
            _render_diff_view(selection[0], selection[1])


def _render_single_view(candidate: UnifiedCandidate):
    """View details for a single candidate."""
    c = candidate
    
    # Header
    col_h1, col_h2 = st.columns([1, 1])
    with col_h1:
        st.metric("Score", f"{c.score_aggregate:.1f}")
    with col_h2:
        st.metric("Iteration", f"{c.generation_index}")
        
    st.markdown("---")
    
    # Content
    st.subheader("📝 Prompt Content")
    st.code(c.full_content, language="text")
    
    st.subheader("📤 Output / Response")
    # Show primary output or expand to tabs if multi-dataset
    outputs = getattr(c, "meta", {}).get("dataset_outputs", {})
    
    if outputs:
        # Create tabs for each dataset output
        tabs = st.tabs(list(outputs.keys()))
        for i, ds_key in enumerate(outputs.keys()):
            with tabs[i]:
                st.text_area(f"Response ({ds_key})", value=outputs[ds_key], height=200, disabled=True)
    else:
        # Fallback
        st.text_area("Response", value=c.output, height=200, disabled=True)


def _render_diff_view(c_new: UnifiedCandidate, c_old: UnifiedCandidate):
    """Render diff between two candidates."""
    
    st.caption(f"Comparing: **Iter {c_new.generation_index}** (New) vs **Iter {c_old.generation_index}** (Old)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(f"Iter {c_new.generation_index}", f"{c_new.score_aggregate:.1f}")
    with col2:
        st.metric(f"Iter {c_old.generation_index}", f"{c_old.score_aggregate:.1f}", 
                 delta=f"{c_old.score_aggregate - c_new.score_aggregate:.1f}", delta_color="inverse")

    st.markdown("#### 🔄 Prompt Mutation Diff")
    
    # Generate Diff
    diff = difflib.ndiff(
        c_old.full_content.splitlines(keepends=True),
        c_new.full_content.splitlines(keepends=True)
    )
    
    # Simple Color-Coded Markdown Logic
    diff_text = []
    for line in diff:
        if line.startswith("+ "):
            diff_text.append(f":green-background[{line.strip()}]")
        elif line.startswith("- "):
            diff_text.append(f":red-background[{line.strip()}]")
        elif line.startswith("? "):
            continue
        else:
            diff_text.append(line.strip())
            
    st.markdown("\n\n".join(diff_text))


def get_test_bench_config() -> TestBenchConfig:
    """
    Get current test bench configuration from session state.
    Note: Inputs are now rendered in Zone C (Test Bench Card), but accessed here for global session.
    """
    return TestBenchConfig(
        input_a=st.session_state.get("test_input_a", ""),
        input_b=st.session_state.get("test_input_b", ""),
        input_c=st.session_state.get("test_input_c", "")
    )

