"""
Zone E: Detail Inspector & Diff Viewer (Bottom Right).

Purpose:
- Single Box UI for unified Inspection and Diffing.
- Left Rail: Dataset Selector.
- Main Stage: Prompt Inspector (Diff/Raw) + Result Inspector.
"""

import streamlit as st
from typing import Optional, List
from glassbox.models.session import TestBenchConfig
from glassbox.models.candidate import UnifiedCandidate

def render_zone_e(test_bench: TestBenchConfig, candidates: List[UnifiedCandidate] = []):
    """
    Render the Inspection & Diff Zone (Update 2 Specs).
    Architecture:
    - Inputs: Global Session State (zc_primary_id, zc_anchor_id).
    - Layout: Left Rail (Datasets) | Main Stage (Content).
    """
    # Wrap in Card Container strict
    with st.container(border=True):
        
        # 1. Resolve Data
        pid = st.session_state.get("zc_primary_id")
        aid = st.session_state.get("zc_anchor_id")
        
        # Resolve Objects
        primary_cand = next((c for c in candidates if str(c.id) == pid), None)
        anchor_cand = next((c for c in candidates if str(c.id) == aid), None) if aid else None
        
        # Header Logic
        title_html = '<div class="card-header">DETAIL INSPECTOR</div>'
        if primary_cand:
            p_idx = primary_cand.generation_index
            if anchor_cand:
                # Diff Mode Header with Halo Badge
                a_idx = anchor_cand.generation_index
                badge_html = f'''
                    <span style="
                        border: 2px solid #1A409F; 
                        border-radius: 12px; 
                        padding: 2px 8px; 
                        font-size: 11px; 
                        color: #1A409F; 
                        background: transparent;
                        margin-left: 10px;
                    ">
                        Diff vs Iter {a_idx}
                    </span>
                '''
                title_html = f'<div class="card-header">DETAILS: CANDIDATE {p_idx} {badge_html}</div>'
            else:
                title_html = f'<div class="card-header">DETAILS: CANDIDATE {p_idx}</div>'

        st.markdown(title_html, unsafe_allow_html=True)
    
        if not primary_cand:
            st.info("Select a candidate in 'Potential Prompts' to inspect.")
            return

        # 2. Main Layout: Rail vs Stage
        # Update 2 Spec: Left Rail (Dataset Selector) + Main Stage
        c_rail, c_main = st.columns([1, 4])
        
        # === LEFT RAIL (Datasets) ===
        with c_rail:
            # Active Dataset Pointer
            if "ze_active_dataset_idx" not in st.session_state:
                st.session_state["ze_active_dataset_idx"] = 0
            
            # Determine available datasets from TestBenchConfig
            # We assume TestBenchConfig has keys input_a, input_b, input_c... 
            # Actually, UnifiedCandidate stores 'test_results' dict keys.
            # Robust fallback: Use keys from the candidate's output dict if available, 
            # else standard D1/D2/D3 from config
            
            # For v0.0.5 we map input_a -> D1, input_b -> D2...
            # We will generate a list of available keys
            ds_keys = []
            if getattr(test_bench, "input_a", ""): ds_keys.append("input_a")
            if getattr(test_bench, "input_b", ""): ds_keys.append("input_b")
            if getattr(test_bench, "input_c", ""): ds_keys.append("input_c")
            
            if not ds_keys: ds_keys = ["input_a"] # Default fallback
            
            # Render Buttons
            for idx, k in enumerate(ds_keys):
                label = f"D{idx+1}"
                is_active = (st.session_state["ze_active_dataset_idx"] == idx)
                
                # Style class
                btn_key = f"ze_ds_btn_{idx}"
                custom_css_class = "zone-e-rail-btn-active" if is_active else "zone-e-rail-btn"
                
                # Injection to wrapper
                st.markdown(f'<div class="{custom_css_class}"></div>', unsafe_allow_html=True)
                
                if st.button(label, key=btn_key, use_container_width=True, help=f"View result for {k}"):
                    st.session_state["ze_active_dataset_idx"] = idx
                    st.rerun()

        # === MAIN STAGE ===
        with c_main:
            # A. PROMPT BLOCK (Diff Engine)
            st.caption("PROMPT INSPECTOR")
            
            if anchor_cand:
                # DIFF MODE
                # Use the backend method we added
                diff_html = primary_cand.get_diff(anchor_cand)
                
                # Render inside a pre-styled block
                st.markdown(
                    f'<div style="font-family: monospace; white-space: pre-wrap; background: #F8F9FA; padding: 10px; border-radius: 4px; border: 1px solid #EEE;">{diff_html}</div>', 
                    unsafe_allow_html=True
                )
            else:
                # RAW MODE
                st.code(primary_cand.full_content, language="text")
            
            st.divider()
            
            # B. RESULT CONTAINER
            active_ds_key = ds_keys[st.session_state["ze_active_dataset_idx"]] if st.session_state["ze_active_dataset_idx"] < len(ds_keys) else ds_keys[0]
            
            # Get output for this dataset
            # UnifiedCandidate.meta['dataset_outputs'] is where we likely store map
            outputs = getattr(primary_cand, "meta", {}).get("dataset_outputs", {})
            val = outputs.get(active_ds_key, primary_cand.output) # Fallback to main output
            
            st.caption(f"RESULT (Dataset {active_ds_key})")
            st.text_area("Result", value=val, height=150, disabled=True, label_visibility="collapsed")


def get_test_bench_config() -> TestBenchConfig:
    """
    Factory to compile current UI state into a TestBenchConfig object.
    Used by app.py to initialize/update the session.
    """
    cfg = TestBenchConfig()
    
    # Map OPRO Data (Default for v0.0.5)
    # In future this should switch based on engine type, but for now we look for known keys.
    if "opro_test_data_1" in st.session_state:
        cfg.input_a = st.session_state["opro_test_data_1"]
    if "opro_test_data_2" in st.session_state:
        cfg.input_b = st.session_state["opro_test_data_2"]
    if "opro_test_data_3" in st.session_state:
        cfg.input_c = st.session_state["opro_test_data_3"]
        
    return cfg
