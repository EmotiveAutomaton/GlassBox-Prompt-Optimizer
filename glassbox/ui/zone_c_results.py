"""
Zone C: Bottom Row Cards.
- Card: POTENTIAL PROMPTS (left, wide).
- Card: PROMPT RATINGS (right top - contains optimization progress graph, now larger).
- Card: FINAL OUTPUT AND USER EVALUATION (right bottom - test bench only, inputs A/B/C horizontal).

Uses Streamlit containers with CSS for proper card borders.
Free Play mode removed. Only Test Bench with horizontal inputs.
"""

import streamlit as st
from typing import List, Optional
import plotly.graph_objects as go

from glassbox.models.session import TestBenchConfig
from glassbox.models.candidate import UnifiedCandidate


def render_zone_c(candidates: List[UnifiedCandidate], test_bench: Optional[TestBenchConfig] = None):
    """Render the bottom row with three cards."""
    
    # Get trajectory from session state for the graph
    trajectory = st.session_state.get("trajectory", [])
    
    # --- BOTTOM ROW: Full-Height Cards ---
    # Wrap in a container for CSS full-height styling
    # --- BOTTOM ROW: Full-Height Cards ---

    
    col_prompts, col_right = st.columns([2, 1.5])
    
    # === CARD: POTENTIAL PROMPTS (Wide, Left, Full Height) ===
    with col_prompts:
        with st.container(border=True):
            st.markdown('<div class="card-header">POTENTIAL PROMPTS</div>', unsafe_allow_html=True)
            
            if not candidates:
                st.info("No candidates yet. Start optimization to generate prompt variations.")
            else:
                sorted_candidates = sorted(candidates, key=lambda c: c.score_aggregate, reverse=True)
                
                for i, candidate in enumerate(sorted_candidates[:12]):
                    score = candidate.score_aggregate
                    color = "#22c55e" if score >= 80 else "#eab308" if score >= 50 else "#ef4444"
                    preview = candidate.display_text[:80] + "..." if len(candidate.display_text) > 80 else candidate.display_text
                    
                    col_rank, col_score, col_preview = st.columns([0.2, 0.3, 3])
                    with col_rank:
                        st.markdown(f"**{i+1}**")
                    with col_score:
                        st.markdown(f"<span style='color:{color};font-weight:bold;'>{score:.0f}</span>", unsafe_allow_html=True)
                    with col_preview:
                        if st.button(preview[:60] + "...", key=f"select_{candidate.id}", use_container_width=True):
                            st.session_state["selected_candidate"] = str(candidate.id)
                    
                    if i < min(len(sorted_candidates), 12) - 1:
                        st.markdown("<hr style='margin:2px 0;border-color:#E0E0E0;'>", unsafe_allow_html=True)
    
    # === RIGHT COLUMN: RATINGS + FINAL OUTPUT ===
    with col_right:
        # === CARD: PROMPT RATINGS (Contains optimization progress graph - NOW LARGER) ===
        with st.container(border=True):
            st.markdown('<div class="card-header">PROMPT RATINGS</div>', unsafe_allow_html=True)
            
            # Render the optimization progress graph (larger now)
            _render_optimization_graph(trajectory, candidates)
        
        # === CARD: FINAL OUTPUT AND USER EVALUATION (Test Bench Only, Horizontal Inputs) ===
        with st.container(border=True):
            st.markdown('<div class="card-header">FINAL OUTPUT AND USER EVALUATION</div>', unsafe_allow_html=True)
            
            # Test Bench Only - No mode toggle, no Free Play
            # Inputs A, B, C arranged horizontally
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.markdown("**A** (Golden)")
                st.text_area("A", value="Standard test...", height=60, key="test_input_a", label_visibility="collapsed")
            
            with col_b:
                st.markdown("**B** (Edge)")
                st.text_area("B", value="Edge case...", height=60, key="test_input_b", label_visibility="collapsed")
            
            with col_c:
                st.markdown("**C** (Adversarial)")
                st.text_area("C", value="Adversarial...", height=60, key="test_input_c", label_visibility="collapsed")
    
    # Close full-height container
    # End Bottom Row



def _render_optimization_graph(trajectory: List, candidates: List[UnifiedCandidate]):
    """Render the optimization progress graph inside PROMPT RATINGS card. Now larger."""
    
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
            height=250,  # Larger height
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
        sorted_candidates = sorted(candidates, key=lambda c: c.score_aggregate, reverse=True)[:10]
        steps = list(range(len(sorted_candidates)))
        scores = [c.score_aggregate for c in sorted_candidates]
    
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
        marker=dict(size=5)
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
        height=250,  # Larger height
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
