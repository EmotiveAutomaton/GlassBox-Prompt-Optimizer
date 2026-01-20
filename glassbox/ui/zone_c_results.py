"""
Zone C: Bottom Row Cards
- Card: POTENTIAL PROMPTS (left, wide - majority of width)
- Card: PROMPT RATINGS (right top - graph, no extra header)
- Card: FINAL OUTPUT AND USER EVALUATION (right bottom - test bench content)
"""

import streamlit as st
from typing import List, Optional
import plotly.graph_objects as go

from glassbox.models.session import CandidateResult, TestBenchConfig


def render_zone_c(candidates: List[CandidateResult], test_bench: Optional[TestBenchConfig] = None):
    """Render the bottom row with three cards."""
    
    # --- BOTTOM ROW: Wide Left (POTENTIAL PROMPTS) | Right Column (RATINGS + FINAL OUTPUT) ---
    col_prompts, col_right = st.columns([2, 1.2])
    
    # === CARD: POTENTIAL PROMPTS (Wide, Left) ===
    with col_prompts:
        st.markdown('''
            <div class="boeing-card">
                <div class="boeing-card-header">POTENTIAL PROMPTS</div>
                <div class="boeing-card-content">
        ''', unsafe_allow_html=True)
        
        if not candidates:
            st.info("No candidates yet. Start optimization to generate prompt variations.")
        else:
            sorted_candidates = sorted(candidates, key=lambda c: c.global_score, reverse=True)
            
            # Compact table view
            for i, candidate in enumerate(sorted_candidates[:12]):
                score = candidate.global_score
                color = "#22c55e" if score >= 80 else "#eab308" if score >= 50 else "#ef4444"
                preview = candidate.prompt_text[:80] + "..." if len(candidate.prompt_text) > 80 else candidate.prompt_text
                
                col_rank, col_score, col_preview = st.columns([0.2, 0.3, 3])
                with col_rank:
                    st.markdown(f"**{i+1}**")
                with col_score:
                    st.markdown(f"<span style='color:{color};font-weight:bold;'>{score:.0f}</span>", unsafe_allow_html=True)
                with col_preview:
                    if st.button(preview[:60] + "...", key=f"select_{candidate.id}", use_container_width=True):
                        st.session_state["selected_candidate"] = candidate.id
                
                if i < min(len(sorted_candidates), 12) - 1:
                    st.markdown("<hr style='margin:2px 0;border-color:#E0E0E0;'>", unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
    
    # === RIGHT COLUMN: RATINGS + FINAL OUTPUT ===
    with col_right:
        # === CARD: PROMPT RATINGS (Graph, no extra header inside) ===
        st.markdown('''
            <div class="boeing-card">
                <div class="boeing-card-header">PROMPT RATINGS</div>
                <div class="boeing-card-content" style="padding: 8px;">
        ''', unsafe_allow_html=True)
        
        # Graph directly in card (no additional header)
        if candidates:
            top_5 = sorted(candidates, key=lambda c: c.global_score, reverse=True)[:5]
            fig = go.Figure(data=[
                go.Bar(
                    x=[f"#{i+1}" for i in range(len(top_5))],
                    y=[c.global_score for c in top_5],
                    marker_color='#0D7CB1'
                )
            ])
            fig.update_layout(
                height=150,
                margin=dict(l=10, r=10, t=10, b=30),
                plot_bgcolor='#FDFDFE',
                paper_bgcolor='#FDFDFE',
                yaxis=dict(range=[0, 105], showgrid=True, gridcolor='#E0E0E0'),
                xaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig, use_container_width=True, key="ratings_chart")
        else:
            st.markdown("<div style='height:100px;display:flex;align-items:center;justify-content:center;color:#999;'>No data</div>", unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
        
        # === CARD: FINAL OUTPUT AND USER EVALUATION ===
        st.markdown('''
            <div class="boeing-card">
                <div class="boeing-card-header">FINAL OUTPUT AND USER EVALUATION</div>
                <div class="boeing-card-content">
        ''', unsafe_allow_html=True)
        
        # Test Bench Mode Toggle
        mode = st.radio("Mode", options=["Test Bench", "Free Play"], horizontal=True, key="testbench_mode", label_visibility="collapsed")
        
        if mode == "Test Bench":
            # Compact test inputs A, B, C
            st.markdown("**Input A** (Golden Path)")
            input_a = st.text_area("A", value="Standard test input...", height=50, key="test_input_a", label_visibility="collapsed")
            
            st.markdown("**Input B** (Edge Case)")
            input_b = st.text_area("B", value="Edge case...", height=50, key="test_input_b", label_visibility="collapsed")
            
            st.markdown("**Input C** (Adversarial)")
            input_c = st.text_area("C", value="Adversarial...", height=50, key="test_input_c", label_visibility="collapsed")
        else:
            # Free Play mode
            selected_id = st.session_state.get("selected_candidate")
            if selected_id and candidates:
                candidate = next((c for c in candidates if c.id == selected_id), None)
                if candidate:
                    st.code(candidate.prompt_text[:200] + "...", language="text")
                    st.metric("Score", f"{candidate.global_score:.1f}")
            else:
                st.info("Select a prompt from POTENTIAL PROMPTS")
            
            free_input = st.text_area("Test Input", placeholder="Enter any input...", height=60, key="free_input")
            if st.button("Run Test", type="primary", use_container_width=True):
                st.success("Test completed!")
        
        st.markdown('</div></div>', unsafe_allow_html=True)
