"""
Zone C: Bottom Row Cards.
- Card: POTENTIAL PROMPTS (left, wide).
- Card: PROMPT RATINGS (right top - contains optimization progress graph).
- Card: FINAL OUTPUT AND USER EVALUATION (right bottom - test bench).

Uses Streamlit containers with CSS for proper card borders.
"""

import streamlit as st
from typing import List, Optional
import plotly.graph_objects as go

from glassbox.models.session import CandidateResult, TestBenchConfig, TrajectoryEntry


def render_zone_c(candidates: List[CandidateResult], test_bench: Optional[TestBenchConfig] = None):
    """Render the bottom row with three cards."""
    
    # Get trajectory from session state for the graph
    trajectory = st.session_state.get("trajectory", [])
    
    # --- BOTTOM ROW: Wide Left (POTENTIAL PROMPTS) | Right Column (RATINGS + FINAL OUTPUT) ---
    col_prompts, col_right = st.columns([2, 1.2])
    
    # === CARD: POTENTIAL PROMPTS (Wide, Left) ===
    with col_prompts:
        st.markdown('<div class="card-header">POTENTIAL PROMPTS</div>', unsafe_allow_html=True)
        
        if not candidates:
            st.info("No candidates yet. Start optimization to generate prompt variations.")
        else:
            sorted_candidates = sorted(candidates, key=lambda c: c.global_score, reverse=True)
            
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
    
    # === RIGHT COLUMN: RATINGS + FINAL OUTPUT ===
    with col_right:
        # === CARD: PROMPT RATINGS (Contains optimization progress graph) ===
        st.markdown('<div class="card-header">PROMPT RATINGS</div>', unsafe_allow_html=True)
        
        # Render the optimization progress graph (from zone_d_telemetry)
        _render_optimization_graph(trajectory, candidates)
        
        st.markdown("---")
        
        # === CARD: FINAL OUTPUT AND USER EVALUATION ===
        st.markdown('<div class="card-header">FINAL OUTPUT AND USER EVALUATION</div>', unsafe_allow_html=True)
        
        # Test Bench Mode Toggle
        mode = st.radio("Mode", options=["Test Bench", "Free Play"], horizontal=True, key="testbench_mode_c", label_visibility="collapsed")
        
        if mode == "Test Bench":
            st.markdown("**Input A** (Golden Path)")
            st.text_area("A", value="Standard test input...", height=50, key="test_input_a", label_visibility="collapsed")
            
            st.markdown("**Input B** (Edge Case)")
            st.text_area("B", value="Edge case...", height=50, key="test_input_b", label_visibility="collapsed")
            
            st.markdown("**Input C** (Adversarial)")
            st.text_area("C", value="Adversarial...", height=50, key="test_input_c", label_visibility="collapsed")
        else:
            selected_id = st.session_state.get("selected_candidate")
            if selected_id and candidates:
                candidate = next((c for c in candidates if c.id == selected_id), None)
                if candidate:
                    st.code(candidate.prompt_text[:200] + "...", language="text")
                    st.metric("Score", f"{candidate.global_score:.1f}")
            else:
                st.info("Select a prompt from POTENTIAL PROMPTS.")
            
            st.text_area("Test Input", placeholder="Enter any input...", height=60, key="free_input")
            if st.button("Run Test", type="primary", use_container_width=True, key="run_test_btn"):
                st.success("Test completed!")


def _render_optimization_graph(trajectory: List, candidates: List[CandidateResult]):
    """Render the optimization progress graph inside PROMPT RATINGS card."""
    
    if not trajectory and not candidates:
        # Placeholder when no data
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[0, 1, 2, 3],
            y=[0, 0, 0, 0],
            mode='lines',
            line=dict(color='#CCC', width=1, dash='dot'),
            showlegend=False
        ))
        fig.update_layout(
            height=180,
            margin=dict(l=30, r=10, t=10, b=30),
            plot_bgcolor='#FDFDFE',
            paper_bgcolor='#FDFDFE',
            xaxis_title='Step',
            yaxis_title='Score',
            yaxis=dict(range=[0, 105]),
            font=dict(size=10),
            annotations=[
                dict(
                    text="Waiting for data...",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=12, color="#999")
                )
            ]
        )
        st.plotly_chart(fig, use_container_width=True, key="ratings_graph_placeholder")
        return
    
    # Build data from trajectory or candidates
    if trajectory:
        steps = [entry.step if hasattr(entry, 'step') else i for i, entry in enumerate(trajectory)]
        scores = [entry.score if hasattr(entry, 'score') else 0 for entry in trajectory]
    else:
        # Use candidate scores as fallback
        sorted_candidates = sorted(candidates, key=lambda c: c.global_score, reverse=True)[:10]
        steps = list(range(len(sorted_candidates)))
        scores = [c.global_score for c in sorted_candidates]
    
    # Calculate running average
    avg_scores = []
    for i, score in enumerate(scores):
        avg_scores.append(sum(scores[:i+1]) / (i+1))
    
    fig = go.Figure()
    
    # Average score line
    fig.add_trace(go.Scatter(
        x=steps,
        y=avg_scores,
        mode='lines+markers',
        name='Avg Score',
        line=dict(color='#0D7CB1', width=2),
        marker=dict(size=4)
    ))
    
    # Max score line
    max_scores = []
    running_max = 0
    for score in scores:
        running_max = max(running_max, score)
        max_scores.append(running_max)
    
    fig.add_trace(go.Scatter(
        x=steps,
        y=max_scores,
        mode='lines',
        name='Max Score',
        line=dict(color='#22c55e', width=2, dash='dash')
    ))
    
    fig.update_layout(
        height=180,
        margin=dict(l=30, r=10, t=10, b=30),
        plot_bgcolor='#FDFDFE',
        paper_bgcolor='#FDFDFE',
        xaxis_title='Step',
        yaxis_title='Score',
        yaxis=dict(range=[0, 105], showgrid=True, gridcolor='#E8E8E8'),
        xaxis=dict(showgrid=False),
        font=dict(size=10),
        legend=dict(orientation='h', yanchor='bottom', y=1, xanchor='right', x=1, font=dict(size=9)),
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True, key="ratings_graph")
