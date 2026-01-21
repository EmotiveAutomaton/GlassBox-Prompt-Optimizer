"""
Zone A: Top Row Cards.
- Card 1: INITIAL PROMPT AND DATA (left) - Dynamic based on Engine.
- Card 2: GLASS BOX (right) - Visualization + Logic Readout.

Uses st.container(border=True) for visible card outlines.
"""

import streamlit as st
from typing import Optional
from glassbox.core.optimizer_base import AbstractOptimizer
from glassbox.core.visualizer import GraphVisualizer


def render_zone_a(optimizer: Optional[AbstractOptimizer] = None):
    """Render the top row with INPUT and GLASS BOX cards."""
    
    # Defaults
    raw_selection = st.session_state.get("selected_engine", "OPro (Iterative)")
    
    # Map friendly names to internal IDs
    engine_map = {
        "OPro (Iterative)": "opro",
        "APE (Reverse Eng.)": "ape",
        "Promptbreeder (Evol.)": "promptbreeder",
        "S2A (Context Filter)": "s2a"
    }
    engine_id = engine_map.get(raw_selection, "opro")
    
    # --- ROW 1: Two Card Boxes Side by Side ---
    col_input, col_glassbox = st.columns([1, 1.8])
    
    # === CARD 1: INITIAL PROMPT AND DATA (Dynamic based on Engine) ===
    with col_input:
        with st.container(border=True):
            st.markdown(f'<div class="card-header">INITIAL PROMPT AND DATA ({engine_id.upper()})</div>', unsafe_allow_html=True)
            
            # --- SHARED SETTINGS POPOVER (Moved to Zone F) ---
            # Model configuration is now handled globally via the top bar gear icon.
            
            # --- DYNAMIC INPUTS ---
            if engine_id == "opro":
                # OPro: Prompt + Test Data
                st.text_area("Seed Prompt", height=80, key="seed_prompt", 
                           placeholder="Initial prompt to be optimized. This should be the raw prompt text you want to improve.", label_visibility="collapsed")
                st.text_area("Test Data", height=80, key="test_data",
                           placeholder="Test cases for evaluation (one per line). Provide input examples that the prompt should handle correctly.", label_visibility="collapsed")
            
            elif engine_id == "ape":
                # APE: Input/Ideal Output Pairs
                st.text_area("Input Data [Ex 1]", height=60, key="ape_input_1",
                           placeholder="Input example for reverse engineering. This is the user input that triggers the desired output.", label_visibility="collapsed")
                st.text_area("Ideal Output [Ex 1]", height=60, key="ape_output_1",
                           placeholder="Ideal target output. This is the exact response you want the model to generate for the given input.", label_visibility="collapsed")
                if st.button("[+] Add Example", key="ape_add_btn"):
                    st.info("Multi-example support coming in beta.")

            elif engine_id == "promptbreeder":
                # PromptBreeder: Prompt + Population
                st.text_area("Seed Prompt", height=80, key="seed_prompt",
                           placeholder="Base prompt for evolutionary optimization. This prompt will serve as the initial seed for mutation.", label_visibility="collapsed")
                st.slider("Population Size", 10, 100, 50, 10, key="pb_population")
                st.caption("Evolutionary params managed by backend.")

            elif engine_id == "s2a":
                # S2A: Query + Raw Context
                st.text_area("Starting Query", height=60, key="s2a_query",
                           placeholder="User query to answer. This is the question the model needs to answer using the provided context.", label_visibility="collapsed")
                st.text_area("Raw Context", height=100, key="s2a_context",
                           placeholder="Retrieved context chunks. Paste the raw text or JSON context here that needs to be filtered and refined.", label_visibility="collapsed")

            # --- ACTION BUTTONS ---
            col_start, col_stop = st.columns(2)
            with col_start:
                if st.button("START OPTIMIZATION", type="primary", use_container_width=True):
                    st.session_state["start_optimization"] = True
            with col_stop:
                if st.button("STOP", use_container_width=True):
                    st.session_state["stop_optimization"] = True
    
    # === CARD 2: GLASS BOX (Visualizer + Logic Readout) ===
    with col_glassbox:
        with st.container(border=True):
            # Header - Full Width, No Checkbox
            st.markdown('<div class="card-header">GLASS BOX</div>', unsafe_allow_html=True)

            col_schematic, col_log = st.columns([2, 1.2])
            
            # 1. GRAPHVIZ SCHEMATIC
            with col_schematic:
                visualizer = GraphVisualizer()
                
                # Determine active node based on backend state (mocked for now if idle)
                active_node = st.session_state.get("active_node_id", "START" if engine_id in ["opro", "ape"] else "POOL")
                
                # Check for idle state override
                status = st.session_state.get("optimizer_status", "idle")
                if status == "idle":
                    active_node = None 

                # Generate DOT
                try:
                    dot_source = visualizer.get_engine_chart(engine_id, active_node)
                    st.graphviz_chart(dot_source, use_container_width=True)
                except Exception as e:
                    st.error(f"Viz Error: {e}")

            # 2. READOUT PANEL (Logic Inspection)
            with col_log:
                # Content depends on active node
                node_content = _get_readout_content(engine_id, active_node)
                
                st.markdown("**System Logic / Prompt**")
                st.code(node_content, language="text", line_numbers=False)
                
                # Status Footer
                st.markdown(f"<div style='margin-top:5px; font-size:11px; font-weight:500; color:#666;'>STATUS: <span style='color:#0D7CB1'>{status.upper()}</span></div>", unsafe_allow_html=True)


def _get_readout_content(engine: str, node: Optional[str]) -> str:
    """Helper to return mock system prompts for the alpha rollout."""
    if not node:
        return "[System Idle]\nSelect 'START' to begin optimization."
        
    prompts = {
        "opro": {
            "START": "USER: Optimize this prompt.\nSYSTEM: Generating variations...",
            "TEST": "Running test cases...\nEvaluating exact match...",
            "RATE": "Scoring Output: 85/100\nReasoning: Good clarity.",
            "CHANGE": "Applying meta-prompt:\n'Make it more professional.'"
        },
        "s2a": {
            "READ": "Ingesting 4k token context...",
            "FILTER": "Removing irrelevant sentences...\n(Noise Ratio: 40%)",
            "REFINE": "Rewriting context for clarity...",
            "ANSWER": "Generating final answer using refined context."
        }
    }
    
    # Fallback generic text
    engine_data = prompts.get(engine, {})
    return engine_data.get(node, f"Processing {node} state...\nExecuting internal logic.")
