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
        # v0.0.6: Boeing Blue Header Background + Right Aligned Badge
        
        # Base Style for Header Container (Flexbox for alignment)
        # Header Logic
        # v0.0.6: Boeing Blue Header Background + Right Aligned Badge
        
        # Base Style for Header Container (Flexbox for alignment)
        # Flattened CSS and added Negative Margins to match .card-header
        header_style = (
            "display: flex; align-items: center; justify-content: space-between; "
            "background-color: #0033A1; color: white; "
            "padding: 10px 16px; "
            "border-radius: 6px 6px 0 0; "
            "font-weight: 600; font-size: 14px; letter-spacing: 1px; "
            "margin-top: -1rem; margin-left: -1rem; margin-right: -1rem; margin-bottom: 1rem; "
            "position: relative; z-index: 1;"
        )
        
        title_text = f"DETAILS: CANDIDATE {primary_cand.generation_index}" if primary_cand else "DETAILS"
        badge_html = ""
        
        if primary_cand and anchor_cand:
            p_idx = primary_cand.generation_index
            a_idx = anchor_cand.generation_index
            
            # v0.0.6 Badge Style: White Text, Semi-Transparent Blue BG (Glassy look)
            # Flattened CSS
            badge_style = (
                "background-color: rgba(255, 255, 255, 0.2); "
                "border: 1px solid rgba(255, 255, 255, 0.4); "
                "color: white; border-radius: 12px; padding: 2px 10px; "
                "font-size: 11px; font-weight: 500;"
            )
            badge_html = f'<span style="{badge_style}">Diff vs Iter {a_idx}</span>'

        # Compose Full Header
        html = f"""
            <div style="{header_style}">
                <span>{title_text}</span>
                {badge_html}
            </div>
        """
        
        # We replace the standard 'card-header' class usage with this custom block
        # intended to sit inside the container. 
        # Note: st.container(border=True) adds padding/margin we might fight against,
        # but placing this div first works well enough as a "inner header".
        st.markdown(html, unsafe_allow_html=True)
    
        if not primary_cand:
            st.info("Select a candidate in 'Potential Prompts' to inspect.")
            return

        if not primary_cand:
            st.info("Select a candidate in 'Potential Prompts' to inspect.")
            return

        # 2. Main Layout (v0.0.7: Single Column, Horizontal Buttons)
        # Removed c_rail/c_main split. Full width content.
        
        # A. PROMPT BLOCK (Diff Engine)
        st.caption("PROMPT INSPECTOR")
        
        if anchor_cand:
            # DIFF MODE
            diff_html = primary_cand.get_diff(anchor_cand)
            # Render inside a pre-styled block
            st.markdown(
                f'<div style="font-family: monospace; white-space: pre-wrap; background: #F8F9FA; padding: 10px; border-radius: 4px; border: 1px solid #EEE;">{diff_html}</div>', 
                unsafe_allow_html=True
            )
        else:
            # RAW MODE (Single Selection)
            # User Req: "Normal white space, normal white box, or just no box... put it on white"
            # We use a simple div with no heavy background, just basic text styling.
            raw_text = primary_cand.full_content
            st.markdown(
                f'<div style="white-space: pre-wrap; font-family: monospace; color: #333; padding: 5px;">{raw_text}</div>', 
                unsafe_allow_html=True
            )
        
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True) # Spacer

        # B. DATASET SELECTOR (Horizontal Strip)
        # "Buttons needs to read dataset 1, dataset 2"
        
        # Active Pointer
        if "ze_active_dataset_idx" not in st.session_state:
            st.session_state["ze_active_dataset_idx"] = 0
            
        # Determine Datasets (Same logic as before)
        ds_keys = []
        if getattr(test_bench, "input_a", ""): ds_keys.append("input_a")
        if getattr(test_bench, "input_b", ""): ds_keys.append("input_b")
        if getattr(test_bench, "input_c", ""): ds_keys.append("input_c")
        if not ds_keys: ds_keys = ["input_a"]

        # Horizontal Layout: [Dataset 1] [Dataset 2] [Dataset 3]
        cols = st.columns(len(ds_keys) + 2) # Fewer spacers needed for wider buttons
        
        for idx, k in enumerate(ds_keys):
            # Render Check
            if idx < len(cols):
                with cols[idx]:
                    label = f"Dataset {idx+1}"
                    is_active = (st.session_state["ze_active_dataset_idx"] == idx)
                    
                    # Style: Using standard st.button
                    btn_type = "primary" if is_active else "secondary"
                    
                    if st.button(label, key=f"ze_ds_horiz_{idx}", type=btn_type, use_container_width=True):
                        st.session_state["ze_active_dataset_idx"] = idx
                        st.rerun()

        st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True) # Spacer

        # C. RESULT CONTAINER
        active_ds_key = ds_keys[st.session_state["ze_active_dataset_idx"]] if st.session_state["ze_active_dataset_idx"] < len(ds_keys) else ds_keys[0]
        
        # Get output
        # Debugging: Ensure we catch the output if it exists under fallback keys or direct attribute
        # v0.0.10: robust lookup including test_results attr
        outputs = getattr(primary_cand, "meta", {}).get("dataset_outputs", {})
        val = outputs.get(active_ds_key, None)
        
        if val is None:
            # Try looking in 'test_results' if it exists (standard location for multisample)
            tr = getattr(primary_cand, "test_results", {})
            val = tr.get(active_ds_key, None)

        # Fallback 1: If 'input_a' and no val, try 'primary_cand.output'
        if val is None and active_ds_key == "input_a":
            val = primary_cand.output
            
        # Fallback 2: Just show empty string
        if val is None: val = ""
        
        # v0.0.10: Simple Title "RESULT"
        st.caption("RESULT")
        # v0.0.8: Match Prompt Inspector style (No text area box)
        st.markdown(
            f'<div style="white-space: pre-wrap; font-family: monospace; color: #333; padding: 5px;">{val}</div>', 
            unsafe_allow_html=True
        )


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
