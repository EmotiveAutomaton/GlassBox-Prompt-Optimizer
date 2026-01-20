"""
Zone A: Task Input & Glass Box Visualization
Restructured into Card Boxes:
- Card 1: "INPUT: STARTING PROMPT AND DATA"
- Card 2: "GLASS BOX" (Schematic + Internal Log)
"""

import streamlit as st
from typing import Optional
from glassbox.core.optimizer_base import AbstractOptimizer

# SVG Icons (replacing emojis)
SVG_GEAR = '''<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1Z"/></svg>'''
SVG_PLAY = '''<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>'''
SVG_STOP = '''<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="6" width="12" height="12"/></svg>'''

def render_zone_a(optimizer: Optional[AbstractOptimizer] = None):
    """Render the Glass Box zone with card box layout."""
    
    # --- ROW 1: Two Card Boxes Side by Side ---
    col_input_card, col_glassbox_card = st.columns([1, 2])
    
    # === CARD 1: INPUT: STARTING PROMPT AND DATA ===
    with col_input_card:
        st.markdown('''
            <div class="boeing-card">
                <div class="boeing-card-header">INPUT: STARTING PROMPT AND DATA</div>
                <div class="boeing-card-content">
        ''', unsafe_allow_html=True)
        
        # Model Config (SVG icon instead of emoji)
        with st.popover("Model Settings", use_container_width=True):
            st.markdown("**Model Settings**")
            models = ["gpt-4o-mini", "gpt-4o", "gpt-4", "claude-3-5-sonnet"]
            st.selectbox("LLM Model", options=models, index=0, key="selected_model")
            st.slider("Temperature", 0.0, 1.0, 0.7, 0.1, key="temperature")
            st.slider("Generations/Step", 1, 10, 3, key="generations_per_step")
        
        # Seed Prompt
        st.text_area(
            "Seed Prompt",
            value=st.session_state.get("seed_prompt", "Write a clear, concise summary of the given text that captures the key points..."),
            height=120,
            key="seed_prompt_input",
            label_visibility="collapsed",
            placeholder="Enter your initial prompt here..."
        )
        
        # File Input
        st.file_uploader(
            "Input Data",
            type=["txt", "pdf", "md", "csv"],
            key="input_file_uploader",
            label_visibility="collapsed"
        )
        
        # RAG Config
        with st.popover("RAG Settings", use_container_width=True):
            st.markdown("**RAG Settings**")
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
        
        st.markdown('</div></div>', unsafe_allow_html=True)
    
    # === CARD 2: GLASS BOX (Schematic + Internal Log) ===
    with col_glassbox_card:
        st.markdown('''
            <div class="boeing-card">
                <div class="boeing-card-header">GLASS BOX</div>
                <div class="boeing-card-content">
        ''', unsafe_allow_html=True)
        
        col_schematic, col_log = st.columns([2, 1])
        
        with col_schematic:
            # Schematic visualization (expanded)
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
                        border-radius:4px; padding:12px; height:280px; 
                        overflow-y:auto; font-family:'JetBrains Mono', monospace; 
                        font-size:11px; color:#333; line-height:1.4;">
                {monologue}
            </div>
            """, unsafe_allow_html=True)
            
            status = st.session_state.get("optimizer_status", "idle")
            st.markdown(f"<div style='margin-top:5px; font-weight:500; color:#333;'>STATUS: <span style='color:#0D7CB1'>{status.upper()}</span></div>", unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)


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
