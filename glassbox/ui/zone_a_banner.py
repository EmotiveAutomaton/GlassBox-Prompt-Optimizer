"""
Zone A: Top Row Cards.
- Card 1: INPUT STARTING PROMPT AND DATA (left).
- Card 2: GLASS BOX (right - diagram + internal log).

Uses st.container(border=True) for visible card outlines.
"""

import streamlit as st
from typing import Optional
from glassbox.core.optimizer_base import AbstractOptimizer


def render_zone_a(optimizer: Optional[AbstractOptimizer] = None):
    """Render the top row with INPUT and GLASS BOX cards."""
    
    # --- ROW 1: Two Card Boxes Side by Side (40% viewport height) ---
    
    # --- ROW 1: Two Card Boxes Side by Side ---

    
    col_input, col_glassbox = st.columns([1, 1.8])
    
    # === CARD 1: INITIAL PROMPT AND DATA ===
    with col_input:
        with st.container(border=True):
            st.markdown('<div class="card-header">INITIAL PROMPT AND DATA</div>', unsafe_allow_html=True)
            
            # Model Settings popover
            with st.popover("Model Settings", use_container_width=True):
                st.markdown("**Model Configuration**")
                models = ["gpt-4o-mini", "gpt-4o", "gpt-4", "claude-3-5-sonnet"]
                st.selectbox("LLM Model", options=models, index=0, key="selected_model")
                st.slider("Temperature", 0.0, 1.0, 0.7, 0.1, key="temperature")
                st.slider("Generations/Step", 1, 10, 3, key="generations_per_step")
            
            # Seed Prompt Text Area
            st.text_area(
                "Seed Prompt",
                value=st.session_state.get("seed_prompt", "Write a clear, concise summary of the given text that captures the key points..."),
                height=100,
                key="seed_prompt_input",
                label_visibility="collapsed",
                placeholder="Enter your initial prompt here..."
            )
            
            # File Upload
            st.file_uploader(
                "Input Data",
                type=["txt", "pdf", "md", "csv"],
                key="input_file_uploader",
                label_visibility="collapsed"
            )
            
            # RAG Settings popover
            with st.popover("RAG Settings", use_container_width=True):
                st.markdown("**RAG Configuration**")
                st.text_input("Vector Store Path", value="", key="vector_store_path")
                st.slider("Top K", 1, 10, 5, key="top_k")
                st.slider("Noise Injection", 0.0, 1.0, 0.0, 0.1, key="noise_level")
            
            # Action Buttons
            col_start, col_stop = st.columns(2)
            with col_start:
                if st.button("START OPTIMIZATION", type="primary", use_container_width=True):
                    st.session_state["start_optimization"] = True
            with col_stop:
                if st.button("STOP", use_container_width=True):
                    st.session_state["stop_optimization"] = True
    
    # === CARD 2: GLASS BOX (Schematic + Internal Log) ===
    with col_glassbox:
        with st.container(border=True):
            st.markdown('<div class="card-header">GLASS BOX</div>', unsafe_allow_html=True)
            
            col_schematic, col_log = st.columns([2, 1])
            
            with col_schematic:
                if optimizer:
                    try:
                        graphviz_source = optimizer.generate_graphviz()
                        st.graphviz_chart(graphviz_source, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Map error: {e}")
                        _render_placeholder_schematic()
                else:
                    _render_placeholder_schematic()
            
            with col_log:
                monologue = optimizer.session.internal_monologue if optimizer else "[Idle] System Ready..."
                st.markdown(f"""
                <div style="background:#F5F7FA; border:1px solid #E0E0E0; 
                            border-radius:4px; padding:12px; height:200px; 
                            overflow-y:auto; font-family:'JetBrains Mono', monospace; 
                            font-size:11px; color:#333; line-height:1.4;">
                    {monologue}
                </div>
                """, unsafe_allow_html=True)
                
                status = st.session_state.get("optimizer_status", "idle")
                st.markdown(f"<div style='margin-top:5px; font-weight:500; color:#333;'>STATUS: <span style='color:#0D7CB1'>{status.upper()}</span></div>", unsafe_allow_html=True)
    
    # Close top-row-cards wrapper
    # End Row 1



def _render_placeholder_schematic():
    """Render placeholder diagram."""
    st.graphviz_chart("""
    digraph G {
        rankdir=LR;
        bgcolor="transparent";
        node [style=filled, fillcolor="#1A409F", fontcolor=white, fontname="Inter", shape=box, style="rounded,filled"];
        edge [color="#394957", penwidth=2];
        
        Start [shape=circle];
        Optimizer [label="Engine\\nSelection"];
        Start -> Optimizer;
        Optimizer -> Results;
        Results [shape=circle, style=dashed];
    }
    """, use_container_width=True)
