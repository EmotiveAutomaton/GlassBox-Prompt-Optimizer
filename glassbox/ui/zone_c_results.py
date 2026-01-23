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
                import pandas as pd
                
                # Prepare data for DataFrame
                data = []
                for i, c in enumerate(candidates):
                    # Use guaranteed attributes from UnifiedCandidate
                    step = c.generation_index
                    score = c.score_aggregate
                    
                    data.append({
                        "id": str(c.id), 
                        "Score": score,
                        "Iter": step, # Shortened name
                        "Prompt": c.display_text
                    })
                
                df = pd.DataFrame(data)
                
                # Configure Columns
                column_config = {
                    "id": None, # Hide ID
                    "Score": st.column_config.NumberColumn(
                        "Score",
                        help="Aggregate Score (0-100)",
                        format="%d",
                        width=80 # Fixed pixel width (tight)
                    ),
                    "Iter": st.column_config.NumberColumn(
                        "Iter",
                        help="Generation Step",
                        format="%d",
                        width=60 # Fixed pixel width (very tight)
                    ),
                    "Prompt": st.column_config.TextColumn(
                        "Prompt Snippet",
                        help="Full prompt text (hover to expand)",
                        width="medium" # Let it fill remaining space
                    )
                }

                # === CUSTOM GRID LAYOUT (HTML PIVOT) ===
                # Implementing Sort & Selection Controls explicitly
                
                # 1. Sorting Controls
                col_sort, col_spacer = st.columns([0.3, 0.7])
                with col_sort:
                    sort_metric = st.selectbox("Sort by:", ["Score", "Iteration"], key="zc_sort_metric")
                
                # Apply Sorting
                if not df.empty:
                    if sort_metric == "Score":
                        df_sorted = df.sort_values(by="Score", ascending=False)
                    else:
                        df_sorted = df.sort_values(by="Iter", ascending=False)
                else:
                    df_sorted = df

                # 2. Header Row (Strict Ratios: 1:1:8)
                # Using 0.08 for Score/Iter (approx 50-60px on 700px width)
                h_score, h_iter, h_prompt = st.columns([0.1, 0.1, 0.7], gap="small")
                with h_score:
                    st.markdown("**Score**")
                with h_iter:
                    st.markdown("**Iter**")
                with h_prompt:
                    st.markdown("**Prompt Candidate**")
                
                # Divider
                st.divider()

                # 3. Data Rows (Loop)
                if not df_sorted.empty:
                    for i, row in df_sorted.iterrows():
                        c_score, c_iter, c_prompt = st.columns([0.1, 0.1, 0.7], gap="small")
                        
                        # Data Extraction
                        score_val = int(row.get("Score", 0))
                        iter_val = int(row.get("Iter", 0))
                        full_prompt = row.get("Prompt", "")
                        snippet = (full_prompt[:75] + "...") if len(full_prompt) > 75 else full_prompt
                        
                        # --- RENDER CELLS ---
                        # Score
                        c_score.button(f"{score_val}", key=f"score_{i}", disabled=True, use_container_width=True)
                        
                        # Iteration
                        c_iter.button(f"{iter_val}", key=f"iter_{i}", disabled=True, use_container_width=True)
                        
                        # Prompt (Clickable for Selection + Native Hover)
                        if c_prompt.button(snippet, key=f"prompt_{i}", help=full_prompt, use_container_width=True):
                            # Handle Selection
                            # We can't easily highlight the row without state reload, but we can set the 'selected' state
                            # For now, just logging or relying on the 'View Details' card (not implemented yet)
                            # Or we can write to a session state var:
                            st.session_state["selected_candidate_id"] = i
                            # Optional: Rerun to show selection UI elsewhere?
                            # st.rerun()

                    st.caption("Hover over prompt text to view full content. Click to select.")
                
                else:
                    st.info("No variations generated yet.")

    
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
                st.text_area("A", value="", placeholder="Standard representative input scenario...", height=60, key="test_input_a", label_visibility="collapsed")
            
            with col_b:
                st.markdown("**B** (Edge)")
                st.text_area("B", value="", placeholder="Edge case or difficult input logic...", height=60, key="test_input_b", label_visibility="collapsed")
            
            with col_c:
                st.markdown("**C** (Adversarial)")
                st.text_area("C", value="", placeholder="Adversarial input or out-of-domain test...", height=60, key="test_input_c", label_visibility="collapsed")
    
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
