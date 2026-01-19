"""
Zone C: Results & Candidate Management - Bottom Left

Contains:
- Candidate List (ranked, color-coded scores)
- Detail Bucket (drill-down view)
- Visual Diff Engine
"""

import streamlit as st
from typing import List, Optional
import difflib

from glassbox.models.session import CandidateResult


def render_zone_c(candidates: List[CandidateResult], selected_ids: List[str] = None):
    """Render the results and candidate management zone."""
    
    st.markdown("### 📊 Candidates")
    
    if not candidates:
        st.info("No candidates yet. Start optimization to generate prompt variations.")
        return

    # Sort by global score
    sorted_candidates = sorted(candidates, key=lambda c: c.global_score, reverse=True)

    # Candidate list
    selected_candidate = None
    compare_candidates = []

    for i, candidate in enumerate(sorted_candidates[:20]):  # Limit display
        score = candidate.global_score
        
        # Color coding
        if score >= 80:
            color = "#22c55e"  # Green
            badge = "🟢"
        elif score >= 50:
            color = "#eab308"  # Yellow
            badge = "🟡"
        else:
            color = "#ef4444"  # Red
            badge = "🔴"

        # Traffic light status
        pass_a, pass_b, pass_c = candidate.pass_status
        traffic = f"{'🟢' if pass_a else '🔴'}{'🟢' if pass_b else '🔴'}{'🟢' if pass_c else '🔴'}"

        # Preview text
        preview = candidate.prompt_text[:60] + "..." if len(candidate.prompt_text) > 60 else candidate.prompt_text

        # Render row
        col_rank, col_score, col_traffic, col_preview, col_actions = st.columns([0.5, 0.8, 0.8, 3, 1])
        
        with col_rank:
            st.markdown(f"**#{i+1}**")
        
        with col_score:
            st.markdown(f"<span style='color:{color};font-weight:bold;'>{badge} {score:.1f}</span>", 
                       unsafe_allow_html=True)
        
        with col_traffic:
            st.markdown(traffic)
        
        with col_preview:
            st.caption(preview)
        
        with col_actions:
            col_view, col_compare = st.columns(2)
            with col_view:
                if st.button("👁️", key=f"view_{candidate.id}", help="View details"):
                    st.session_state["selected_candidate"] = candidate.id
            with col_compare:
                if st.checkbox("", key=f"compare_{candidate.id}", help="Select for comparison"):
                    compare_candidates.append(candidate)

        # Divider
        if i < len(sorted_candidates) - 1:
            st.markdown("<hr style='margin:5px 0;border-color:#31333F;'>", unsafe_allow_html=True)

    # Detail Bucket
    st.markdown("---")
    selected_id = st.session_state.get("selected_candidate")
    
    if selected_id:
        candidate = next((c for c in candidates if c.id == selected_id), None)
        if candidate:
            _render_detail_bucket(candidate)

    # Visual Diff
    if len(compare_candidates) >= 2:
        st.markdown("---")
        _render_diff_engine(compare_candidates[0], compare_candidates[1])


def _render_detail_bucket(candidate: CandidateResult):
    """Render detailed view of a single candidate."""
    st.markdown("### 🔍 Candidate Details")
    
    # Tabs for different views
    tab_prompt, tab_responses, tab_reasoning, tab_override = st.tabs([
        "📝 Prompt", "💬 Responses", "🧠 Reasoning", "✏️ Override"
    ])

    with tab_prompt:
        st.code(candidate.prompt_text, language="text")
        if st.button("📋 Copy", key="copy_prompt"):
            st.toast("Prompt copied to clipboard!")
            # Note: Actual clipboard requires JavaScript

    with tab_responses:
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.markdown("**Input A (Golden)**")
            st.markdown(f"Score: **{candidate.score_a:.1f}**")
            with st.expander("Response", expanded=False):
                st.text(candidate.response_a or "No response")

        with col_b:
            st.markdown("**Input B (Edge)**")
            st.markdown(f"Score: **{candidate.score_b:.1f}**")
            with st.expander("Response", expanded=False):
                st.text(candidate.response_b or "No response")

        with col_c:
            st.markdown("**Input C (Adversarial)**")
            st.markdown(f"Score: **{candidate.score_c:.1f}**")
            with st.expander("Response", expanded=False):
                st.text(candidate.response_c or "No response")

    with tab_reasoning:
        st.markdown("**Evaluator Reasoning:**")
        st.info(candidate.evaluator_reasoning_a or "No reasoning available")

        if candidate.mutation_operator:
            st.markdown("**Mutation Operator:**")
            st.caption(candidate.mutation_operator)

    with tab_override:
        st.markdown("**Human Score Override**")
        st.caption("Override the LLM judge's score with your own assessment.")
        
        current_override = candidate.human_override_score
        
        new_score = st.number_input(
            "Override Score",
            min_value=0.0,
            max_value=100.0,
            value=current_override if current_override is not None else candidate.global_score,
            step=5.0,
            key=f"override_score_{candidate.id}"
        )
        
        new_reasoning = st.text_area(
            "Override Reasoning",
            value=candidate.human_override_reasoning,
            key=f"override_reason_{candidate.id}"
        )
        
        if st.button("Apply Override", key=f"apply_override_{candidate.id}"):
            candidate.human_override_score = new_score
            candidate.human_override_reasoning = new_reasoning
            st.success(f"Score overridden to {new_score:.1f}")
            st.rerun()


def _render_diff_engine(candidate_a: CandidateResult, candidate_b: CandidateResult):
    """Render visual diff between two candidates."""
    st.markdown("### 📊 Visual Diff")
    st.caption(f"Comparing #{candidate_a.id} vs #{candidate_b.id}")

    # Generate HTML diff
    diff = difflib.HtmlDiff()
    
    lines_a = candidate_a.prompt_text.splitlines()
    lines_b = candidate_b.prompt_text.splitlines()
    
    html_diff = diff.make_table(
        lines_a, lines_b,
        fromdesc=f"Candidate {candidate_a.id} (Score: {candidate_a.global_score:.1f})",
        todesc=f"Candidate {candidate_b.id} (Score: {candidate_b.global_score:.1f})",
        context=True,
        numlines=3
    )

    # Style the diff table
    styled_html = f"""
    <style>
    .diff_header {{ background-color: #31333F; color: white; }}
    .diff_next {{ background-color: #1a1a2e; }}
    .diff_add {{ background-color: #22c55e22; color: #22c55e; font-weight: bold; }}
    .diff_chg {{ background-color: #eab30822; color: #eab308; }}
    .diff_sub {{ background-color: #ef444422; color: #ef4444; text-decoration: line-through; }}
    table.diff {{ font-family: monospace; font-size: 12px; width: 100%; border-collapse: collapse; }}
    table.diff td {{ padding: 4px 8px; border: 1px solid #31333F; }}
    </style>
    {html_diff}
    """

    st.markdown(styled_html, unsafe_allow_html=True)

    # Score comparison
    col1, col2 = st.columns(2)
    with col1:
        delta_a = candidate_a.global_score - candidate_b.global_score
        st.metric(
            f"Candidate {candidate_a.id}",
            f"{candidate_a.global_score:.1f}",
            delta=f"{delta_a:+.1f}" if delta_a != 0 else None
        )
    with col2:
        delta_b = candidate_b.global_score - candidate_a.global_score
        st.metric(
            f"Candidate {candidate_b.id}",
            f"{candidate_b.global_score:.1f}",
            delta=f"{delta_b:+.1f}" if delta_b != 0 else None
        )
