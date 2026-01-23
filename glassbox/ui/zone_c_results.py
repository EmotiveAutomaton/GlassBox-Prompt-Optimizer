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
                # Implementing Sort via Header Buttons
                
                # State for sorting (Defaults)
                if "zc_sort_col" not in st.session_state:
                    st.session_state["zc_sort_col"] = "Score"
                if "zc_sort_asc" not in st.session_state:
                    st.session_state["zc_sort_asc"] = False # Descending default

                # Callbacks for Headers
                def _sort_score():
                    if st.session_state["zc_sort_col"] == "Score":
                        st.session_state["zc_sort_asc"] = not st.session_state["zc_sort_asc"]
                    else:
                        st.session_state["zc_sort_col"] = "Score"
                        st.session_state["zc_sort_asc"] = False # Default desc for score

                def _sort_iter():
                    if st.session_state["zc_sort_col"] == "Iter":
                        st.session_state["zc_sort_asc"] = not st.session_state["zc_sort_asc"]
                    else:
                        st.session_state["zc_sort_col"] = "Iter"
                        st.session_state["zc_sort_asc"] = False

                def _sort_prompt():
                    if st.session_state["zc_sort_col"] == "Prompt":
                        st.session_state["zc_sort_asc"] = not st.session_state["zc_sort_asc"]
                    else:
                        st.session_state["zc_sort_col"] = "Prompt"
                        st.session_state["zc_sort_asc"] = True # Default asc for text
                
                # Apply Sorting to DF
                col = st.session_state["zc_sort_col"]
                asc = st.session_state["zc_sort_asc"]
                if not df.empty:
                    df_sorted = df.sort_values(by=col, ascending=asc)
                else:
                    df_sorted = df

                # 2. Header Row
                # User Req: "Increase width... 1.5x current size". 
                # Old: 0.05. New: 0.05 * 1.5 = 0.075 -> Round to 0.08.
                grid_ratios = [0.08, 0.08, 0.84]
                h_score, h_iter, h_prompt = st.columns(grid_ratios, gap="small")
                
                # RENDER CLICKABLE HEADERS
                # We use buttons with transparent/minimal styling if pos, or just standard buttons acting as headers
                # Indicator logic
                def _arrow(c):
                    if st.session_state["zc_sort_col"] == c:
                        return " ▲" if st.session_state["zc_sort_asc"] else " ▼"
                    return ""

                with h_score:
                    st.button(f"Score{_arrow('Score')}", key="h_btn_score", on_click=_sort_score, use_container_width=True)
                with h_iter:
                    st.button(f"Iter{_arrow('Iter')}", key="h_btn_iter", on_click=_sort_iter, use_container_width=True)
                with h_prompt:
                    st.button(f"Prompt Candidate{_arrow('Prompt')}", key="h_btn_prompt", on_click=_sort_prompt, use_container_width=True)
                
                # No Divider - Removed for less whitespace

                # 3. Data Rows (Loop)
                # 3. Data Rows (Loop)
                # Selection State Management (Queue of max 2 items)
                if "zc_selection_queue" not in st.session_state:
                    st.session_state["zc_selection_queue"] = [] # [newest_id, second_newest_id]
                
                def _handle_selection(row_id):
                    q = st.session_state["zc_selection_queue"]
                    # If already selected, maybe move to front? Or just ignore?
                    # User: "When I click one... it gets Blue-Grey... When I click a second... that second row gets a blue-grey... the first row transitions to off-white"
                    # This implies clicking a new item impacts the queue.
                    if row_id in q:
                        # If already in queue, move to front (become Primary)
                        q.remove(row_id)
                        q.insert(0, row_id)
                    else:
                        # Add to front, truncate to 2
                        q.insert(0, row_id)
                        if len(q) > 2:
                            q.pop() # Remove oldest
                    
                    st.session_state["zc_selection_queue"] = q
                    st.session_state["selected_candidate_id"] = row_id # Keep legacy pointer just in case

                # Wrap in container
                with st.container():
                    
                    if not df_sorted.empty:
                        q = st.session_state["zc_selection_queue"]
                        
                        for i, row in df_sorted.iterrows():
                            c_score, c_iter, c_prompt = st.columns(grid_ratios, gap="small")
                            
                            # Determine Selection State & Marker
                            marker_class = "ghost-col-marker" # Default (Transparent)
                            if len(q) > 0 and q[0] == i:
                                marker_class = "ghost-marker-primary" # 0: Primary (Blue-Grey)
                            elif len(q) > 1 and q[1] == i:
                                marker_class = "ghost-marker-secondary" # 1: Secondary (Off-White)
                            
                            marker_html = f'<div class="{marker_class}" style="display:none;"></div>'
                            
                            # Data Extraction
                            score_val = int(row.get("Score", 0))
                            iter_val = int(row.get("Iter", 0))
                            full_prompt = row.get("Prompt", "")
                            snippet = (full_prompt[:90] + "...") if len(full_prompt) > 90 else full_prompt
                            
                            # Helper to render cell with specific marker
                            def _render_cell(col, content, key_suffix, clickable=True, help_text=None):
                                with col:
                                    st.markdown(marker_html, unsafe_allow_html=True)
                                    if clickable:
                                        # Use on_click for proper state update
                                        if st.button(content, key=f"{key_suffix}_{i}", help=help_text, on_click=_handle_selection, args=(i,), use_container_width=True):
                                            pass
                                    else:
                                        st.button(content, key=f"{key_suffix}_{i}", disabled=True, use_container_width=True)

                            # --- RENDER CELLS [ISOLATED GHOST] ---
                            # Note: To make the *row* selectable by clicking Score/Iter, we could make them clickable too.
                            # User said "When I select...". Usually implies row selection. 
                            # Currently Score/Iter are disabled. I will keep them disabled as requested previously unless user asked otherwise.
                            # Actually user said "Select up to two different rows... when I click one of the rows". 
                            # Implies clicking ANYWHERE. I'll make Score/Iter clickable triggers too if simple.
                            # But standard pattern is left-to-right. I'll stick to Prompt being the trigger for now to avoid complexity, 
                            # or just make them all trigger `_handle_selection`. 
                            # "Make all rows... clickable". I'll make Score/Iter trigger selection too!
                            
                            # Score (Trigger Select)
                            _render_cell(c_score, f"{score_val}", "score", clickable=True)
                            
                            # Iteration (Trigger Select)
                            _render_cell(c_iter, f"{iter_val}", "iter", clickable=True)
                            
                            # Prompt (Trigger Select)
                            _render_cell(c_prompt, snippet, "prompt", clickable=True, help_text=full_prompt)

                        st.caption("Click any cell to select. Max 2 selections (Blue-Grey = Newest, Off-White = Previous).")
                    
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
