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
                # Iter 35: Split Prompt (0.84) into Prompt (0.42) + Result (0.42)
                grid_ratios = [0.08, 0.08, 0.42, 0.42]
                h_score, h_iter, h_prompt, h_result = st.columns(grid_ratios, gap="small")

                # RENDER CLICKABLE HEADERS
                # Inject a marker to explicitly PROTECT these as "Headers" (Solid Button Style)
                # See styles.py: div[data-testid="stColumn"]:has(.zone-c-header) button
                HEADER_MARKER = '<div class="zone-c-header" style="display:none;"></div>'

                # Indicator logic
                def _arrow(c):
                    if st.session_state["zc_sort_col"] == c:
                        return " ▲" if st.session_state["zc_sort_asc"] else " ▼"
                    return ""

                with h_score:
                    st.markdown(HEADER_MARKER, unsafe_allow_html=True)
                    st.button(f"Score{_arrow('Score')}", key="h_btn_score", on_click=_sort_score, use_container_width=True)
                with h_iter:
                    st.markdown(HEADER_MARKER, unsafe_allow_html=True)
                    st.button(f"Iter{_arrow('Iter')}", key="h_btn_iter", on_click=_sort_iter, use_container_width=True)
                with h_prompt:
                    st.markdown(HEADER_MARKER, unsafe_allow_html=True)
                    st.button(f"Prompt Candidate{_arrow('Prompt')}", key="h_btn_prompt", on_click=_sort_prompt, use_container_width=True)
                with h_result:
                    # No Sort for result yet, or alias to prompt sort? Just static for now.
                    st.markdown(HEADER_MARKER, unsafe_allow_html=True)
                    st.button("Result", key="h_btn_result", disabled=True, use_container_width=True)
                
                # 3. Data Rows (Loop)
                # Selection State Management (Queue of max 2 items, storing UUIDs now)
                # 3. Data Rows (Loop)
                # Selection State Management (State Machine V2: Primary & Anchor)
                if "zc_primary_id" not in st.session_state:
                    st.session_state["zc_primary_id"] = None
                if "zc_anchor_id" not in st.session_state:
                    st.session_state["zc_anchor_id"] = None
                
                def _handle_selection_v2(clicked_id):
                    pid = st.session_state["zc_primary_id"]
                    aid = st.session_state["zc_anchor_id"]
                    
                    if pid == clicked_id:
                        # Click on Primary -> Clear Anchor (Single View)
                        st.session_state["zc_anchor_id"] = None
                    else:
                        # Click on New -> Old Primary becomes Anchor, New becomes Primary
                        st.session_state["zc_anchor_id"] = pid
                        st.session_state["zc_primary_id"] = clicked_id
                        
                    # Sync to global 'selected_candidates' list for Zone E compatibility
                    # We rebuild the list based on IDs
                    # This is populated at the START of the next render cycle typically, 
                    # but we can do it here if we want immediate reflected state if we weren't rerunning.
                    # Streamlit rerun handles the UI update.

                # Wrap in container
                with st.container():
                    # BUG-025: Scope marker to isolate row hover logic from parent container
                    st.markdown('<div class="zone-c-row-scope" style="display:none;"></div>', unsafe_allow_html=True)
                    
                    if not df_sorted.empty:
                        pid = st.session_state["zc_primary_id"]
                        aid = st.session_state["zc_anchor_id"]
                        
                        for i, row in df_sorted.iterrows():
                            # Create a specialized container for the row to hold the marker
                            # We use cols inside to layout the text
                            
                            # ID for logic (row 'id' from c.id)
                            c_id = str(row.get("id", ""))
                            
                            # Determine Selection State & Marker
                            marker_class = "ghost-col-marker" # Default (Transparent)
                            if c_id == pid:
                                marker_class = "ghost-marker-primary" # Dark Blue BG
                            elif c_id == aid:
                                marker_class = "ghost-marker-secondary" # Blue Halo
                            
                            marker_html = f'<div class="{marker_class}" style="display:none;"></div>'
                            
                            # Data Extraction
                            score_val = int(row.get("Score", 0))
                            iter_val = int(row.get("Iter", 0))
                            full_prompt = row.get("Prompt", "")
                            
                            # Retrieve Output
                            cand_obj = next((c for c in candidates if str(c.id) == c_id), None)
                            full_output = getattr(cand_obj, "output", "") if cand_obj else ""

                            snippet_p = (full_prompt[:40] + "...") if len(full_prompt) > 40 else full_prompt
                            snippet_r = (full_output[:40] + "...") if len(full_output) > 40 else full_output
                            
                            # Helper to render cell with specific marker
                            # We inject marker in EVERY col to ensure the parent 'stColumn' gets tagged
                            def _render_cell(col, content, key_suffix, clickable=True, help_text=None):
                                with col:
                                    st.markdown(marker_html, unsafe_allow_html=True)
                                    if clickable:
                                        # Use on_click for proper state update with UUID
                                        if st.button(content, key=f"{key_suffix}_{i}", help=help_text, on_click=_handle_selection_v2, args=(c_id,), use_container_width=True):
                                            pass
                                    else:
                                        st.button(content, key=f"{key_suffix}_{i}", disabled=True, use_container_width=True)

                            # Grid Layout
                            c_score, c_iter, c_prompt, c_result = st.columns(grid_ratios, gap="small")

                            # Render Cells
                            _render_cell(c_score, f"{score_val}", "score", clickable=True)
                            _render_cell(c_iter, f"{iter_val}", "iter", clickable=True)
                            _render_cell(c_prompt, snippet_p, "prompt", clickable=True, help_text=full_prompt)
                            _render_cell(c_result, snippet_r, "result", clickable=True, help_text=full_output)
                        
                        st.caption("Click new row to select. Click Primary again to clear comparison.")
                    
                    else:
                        st.info("No variations generated yet.")

    
    # === RIGHT COLUMN: RATINGS + FINAL OUTPUT ===
    with col_right:
        # === CARD: PROMPT RATINGS (Contains optimization progress graph - NOW LARGER) ===
        with st.container(border=True):
            st.markdown('<div class="card-header">PROMPT RATINGS</div>', unsafe_allow_html=True)
            
            # Render the optimization progress graph (larger now)
            _render_optimization_graph(trajectory, candidates)
        
        # === CARD: DETAIL INSPECTOR & DIFF (Replaces Final Output) ===
        # Iter 48: Integrated Zone E here for proper layout
        from glassbox.ui.zone_e_testbench import render_zone_e
        # Pass candidates so Zone E can resolve Primary/Anchor IDs
        render_zone_e(test_bench, candidates)
    
    # Close full-height container
    # End Bottom Row



def _render_optimization_graph(trajectory: List, candidates: List[UnifiedCandidate]):
    """
    Render detailed optimization graph.
    Refinements (Iter 36):
    - Color: Boeing Blue #0033A1.
    - Grid: Darker visible lines.
    - Labels: Larger.
    - Tooltip: Iter, Score (1 dec), Prompt: snippet, Result: snippet.
    - Selection: Dual states (Primary vs Secondary).
    """
    
    # Data Prep
    data_points = []
    
    # 2. Selection Sync Highlighting (Dual State) - V2 Logic (MOVED UP FOR SCOPE)
    pid = st.session_state.get("zc_primary_id")
    aid = st.session_state.get("zc_anchor_id")
    
    def _extract_res(c_id, c_list):
        # Helper to find result text
        return next((getattr(c, "output", "") for c in c_list if str(c.id) == str(c_id)), "")

    if trajectory:
        for entry in trajectory:
            s_val = entry.score if hasattr(entry, 'score') else 0
            i_val = entry.step if hasattr(entry, 'step') else 0
            p_text = entry.prompt if hasattr(entry, 'prompt') else ""
            c_id = entry.candidate_id if hasattr(entry, 'candidate_id') else ""
            r_text = _extract_res(c_id, candidates) # Attempt to fallback align
            data_points.append({"step": i_val, "score": s_val, "prompt": p_text, "result": r_text, "id": c_id})
    else:
        # Fallback to candidates
        sorted_candidates = sorted(candidates, key=lambda c: getattr(c, 'generation_index', 0))
        for c in sorted_candidates:
            s_val = getattr(c, 'score_aggregate', 0)
            i_val = getattr(c, 'generation_index', 0)
            p_text = getattr(c, 'display_text', "")
            r_text = getattr(c, 'output', "")
            c_id = str(c.id)
            data_points.append({"step": i_val, "score": s_val, "prompt": p_text, "result": r_text, "id": c_id})

    if not data_points:
        st.info("No data for graph.")
        return

    # Unpack for plotting
    x_vals = [d["step"] for d in data_points]
    y_vals = [d["score"] for d in data_points]
    
    # Tooltip Formatting
    hover_texts = []
    for d in data_points:
        p_snip = (d['prompt'][:60] + "...") if len(d['prompt']) > 60 else d['prompt']
        r_snip = (d['result'][:60] + "...") if len(d['result']) > 60 else d['result']
        
        # Format: Iter 2 -> Score: 95.0 -> Prompt: ... -> Result: ...
        txt = (
            f"<b>Iter: {d['step']}</b><br>"
            f"Score: {d['score']:.1f}<br>"
            f"<i>Prompt: {p_snip}</i><br>"
            f"<i>Result: {r_snip}</i>"
        )
        hover_texts.append(txt)
    
    # Dynamic Range
    min_score = min(y_vals)
    max_score = max(y_vals)
    y_range = [max(0, min_score - 5), min(105, max_score + 5)]

    fig = go.Figure()

    # 1. Main Trace (Line + Dots)
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode='lines+markers+text',
        name='Score',
        line=dict(color='#0033A1', width=3), # Official Boeing Blue
        marker=dict(
            size=12, 
            color='white',
            line=dict(color='#0033A1', width=2)
        ),
        text=[str(x) for x in x_vals], 
        textposition="top center",
        # Force Label Text Color to be visible
        textfont=dict(size=12, color="black", family="Arial Black"), 
        hovertemplate="%{hovertext}<extra></extra>",
        hovertext=hover_texts,
        # Iter 37: Embed ID for click handler
        customdata=[d["id"] for d in data_points] 
    ))

    # Determine Axis Ranges
    steps = [d["step"] for d in data_points]
    if len(steps) > 0:
        min_step, max_step = min(steps), max(steps)
        # v0.0.9: Reverted Left Rail padding (Back to standard tight layout)
        x_range = [min_step - 0.5, max_step + 0.5] if min_step == max_step else [min_step - 0.5, max_step + 0.5]
        
        scores = [d["score"] for d in data_points]
        min_score, max_score = min(scores), max(scores)
        y_buffer = (max_score - min_score) * 0.2 if max_score != min_score else 1.0
        y_range = [min_score - y_buffer, max_score + y_buffer]
    else:
        x_range = [-1, 5]
        y_range = [0, 100]

    # Layout Updates
    # Shapes for Tether
    shapes = []

    # 1. Selection Sync - Tether (Vertical Arrow Strategy)
    pid = st.session_state.get("zc_primary_id")
    aid = st.session_state.get("zc_anchor_id")
    
    if pid:
         prim_pt = next((d for d in data_points if str(d["id"]) == pid), None)
         if prim_pt:
             # v0.0.9: Vertical Drop with Arrow
             y_min = y_range[0]
             
             # The Line
             shapes.append(dict(
                 type="line",
                 x0=prim_pt["step"], y0=prim_pt["score"],
                 x1=prim_pt["step"], y1=y_min,
                 line=dict(color="#0033A1", width=2, dash="dot"),
                 layer="below"
             ))
             
             # The Arrow Head (at the bottom)
             # Use an Annotation because Shapes don't support arrowheads well
             fig.add_annotation(
                x=prim_pt["step"],
                y=y_min,
                ax=0,
                ay=-15, # Tail is 15px UP from the point (So arrow points DOWN)
                showarrow=True,
                arrowhead=2, # Crisp triangle
                arrowsize=1.5,
                arrowwidth=2,
                arrowcolor="#0033A1"
             )

    # Restore Layout Configuration (Accidentally deleted in v0.0.7)
    fig.update_layout(
        height=300,
        margin=dict(l=40, r=20, t=20, b=40),
        plot_bgcolor='#FDFDFE', # Match App BG
        paper_bgcolor='#FDFDFE',
        font=dict(color="black", size=11),
        xaxis_title='Iteration',
        yaxis_title='Score',
        yaxis=dict(
            range=y_range, 
            showgrid=True, 
            gridcolor='#BBBBBB', 
            zeroline=False,
            tickfont=dict(color="black"),
            title_font=dict(color="black")
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False, 
            title_font=dict(color="black")
        ),
        showlegend=False,
        shapes=shapes, 
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="sans-serif",
            font=dict(color="black") 
        )
    )

    if pid:
        # Primary (Newest)
        prim_pt = next((d for d in data_points if str(d["id"]) == pid), None)
        
        if prim_pt:
            fig.add_trace(go.Scatter(
                x=[prim_pt["step"]],
                y=[prim_pt["score"]],
                mode='markers',
                name='Selected (Primary)',
                marker=dict(
                    size=20, # Slightly larger
                    color='rgba(0,0,0,0)', # Transparent Fill (Ring)
                    # Restored: Thick Boeing Blue Halo
                    # User: "I have lost the primary halo... glowing blue donut"
                    line=dict(color='#0033A1', width=4) 
                ),
                hoverinfo='skip'
            ))

    if aid:
        # Secondary (Anchor)
        sec_pt = next((d for d in data_points if str(d["id"]) == aid), None)
        
    if aid:
        # Secondary (Anchor)
        sec_pt = next((d for d in data_points if str(d["id"]) == aid), None)
        
        if sec_pt:
            # v0.0.11: Match Zone C Secondary Highlight EXACTLY
            # Style from styles.py: background-color: rgba(26, 64, 159, 0.4);
            sec_color = "rgba(26, 64, 159, 0.4)" 
            sec_line_color = "rgba(26, 64, 159, 0.6)" # Slightly darker for line visibility
            
            # 2. Secondary Tether (Half-Drop)
            y_min = y_range[0]
            # Halfway point
            y_mid = (sec_pt["score"] + y_min) / 2
            
            # Tether Line (Halfway)
            fig.add_shape(
                 type="line",
                 x0=sec_pt["step"], y0=sec_pt["score"],
                 x1=sec_pt["step"], y1=y_mid,
                 line=dict(color=sec_line_color, width=2, dash="dot"),
                 layer="below"
            )
            # Arrow Head (At Middle)
            fig.add_annotation(
                x=sec_pt["step"],
                y=y_mid,
                ax=0,
                ay=-15,
                showarrow=True,
                arrowhead=2,
                arrowsize=1.5,
                arrowwidth=2,
                arrowcolor=sec_line_color
             )

            # v0.0.11: Secondary Halo - Solid Fill matching Zone C
            # User wants "light blue-white-blue mix... match shading... secondary selection in zone C"
            # In Zone C it's a BG color of rgba(26, 64, 159, 0.4).
            # So here we make the marker FILL that color, with maybe no border or thin border?
            fig.add_trace(go.Scatter(
                x=[sec_pt["step"]],
                y=[sec_pt["score"]],
                mode='markers',
                name='Selected (Secondary)',
                marker=dict(
                    size=22, 
                    color=sec_color, # Fill with the semi-transparent blue
                    line=dict(color=sec_line_color, width=0) # No border (or minimal)
                ),
                hoverinfo='skip'
            ))
    
    # Render with Click Handling (Iter 37)
    # Using on_select="rerun" to capture clicks
    event = st.plotly_chart(fig, use_container_width=True, key="ratings_graph_v3", on_select="rerun", selection_mode="points")
    
    # Event Handling Logic
    if event and "selection" in event and "points" in event["selection"]:
        points = event["selection"]["points"]
        if points:
            # We only care about the first point clicked
            pt = points[0]
            curve_idx = pt.get("curve_number", 0)
            point_idx = pt.get("point_index", 0)
            
            clicked_id = None
            
            # Map Curve+Index to ID
            # Logic: Trace 0 is ALWAYS the main data trace.
            if curve_idx == 0:
                if point_idx < len(data_points):
                    clicked_id = str(data_points[point_idx]["id"])
            elif curve_idx == 1:
                # Primary Highlight Trace - Clicked the Halo?
                if pid: clicked_id = pid
            elif curve_idx == 2:
                # Secondary Highlight Trace
                if aid: clicked_id = aid
            
            # Update State Machine if Valid & Different from current primary
            if clicked_id:
                current_pid = st.session_state.get("zc_primary_id")
                
                # De-bounce: if clicking the same point that is already primary, do nothing?
                # Spec says: "Click (Existing Primary): Clears Secondary."
                
                if clicked_id == current_pid:
                     st.session_state["zc_anchor_id"] = None # Clear anchor
                     st.rerun()
                else:
                    # New Primary
                    st.session_state["zc_anchor_id"] = current_pid
                    st.session_state["zc_primary_id"] = clicked_id
                    st.rerun()
