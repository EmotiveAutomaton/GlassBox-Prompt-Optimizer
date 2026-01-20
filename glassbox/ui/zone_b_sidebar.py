"""
Zone B: Control Sidebar - Clean Navigation
Fixed width, transparent hover, SVG icons
"""

import streamlit as st
import os
from glassbox.core import list_engines
from glassbox.models.session import OptimizerSession, SessionConfig
import json

# SVG Icons (replacing emojis)
SVG_GEAR = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>'
SVG_UPLOAD = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>'
SVG_DOWNLOAD = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>'

def render_zone_b():
    """Render the Boeing Light Sidebar with Clean Navigation."""
    
    # Navigation Blocks (No Title/Caption)
    view_options = [
        "OPro (Iterative)",
        "APE (Reverse Eng.)",
        "Promptbreeder (Evol.)",
        "S2A (Context Filter)"
    ]
    
    selected_engine = st.sidebar.radio(
        "Navigation",
        options=view_options,
        index=0,
        key="selected_engine",
        label_visibility="collapsed"
    )
    
    # CSS for Config Button - Matches nav item style (transparent default)
    st.sidebar.markdown("""
        <style>
            /* Config Button - Transparent default, hover for light, blue on popover open */
            section[data-testid="stSidebar"] .stPopover > button,
            section[data-testid="stSidebar"] [data-testid="stPopover"] > button {
                background-color: transparent !important;
                color: white !important;
                border-radius: 0 !important;
                width: calc(100% + 2rem) !important;
                margin-left: -1rem !important;
                padding: 16px 20px !important;
                border: none !important;
                border-top: 2px solid rgba(0,0,0,0.3) !important;
                transition: background-color 0.15s ease;
                position: fixed !important;
                bottom: 0 !important;
                left: 0 !important;
                width: 220px !important;
            }
            
            section[data-testid="stSidebar"] .stPopover > button:hover {
                background-color: rgba(255,255,255,0.08) !important;
            }
            
            /* When popover is open */
            section[data-testid="stSidebar"] .stPopover[data-state="open"] > button {
                background-color: #0D7CB1 !important;
            }
            
            /* Make popover appear ABOVE button (flip arrow) */
            section[data-testid="stSidebar"] [data-testid="stPopoverContent"] {
                bottom: 60px !important;
                top: auto !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Config popover with SVG icons (at bottom)
    with st.sidebar.popover("Configuration", use_container_width=True):
        st.markdown("### Global Settings")
        st.caption("Manage application state and preferences.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Export Session", use_container_width=True):
                _export_session_logic()
        
        with col2:
            uploaded = st.file_uploader("Import", type=["opro", "json"], label_visibility="collapsed")
            if uploaded:
                _import_session(uploaded)

def _export_session_logic():
    session = st.session_state.get("session")
    if session:
        st.download_button(
            "Download .opro",
            data=session.to_json(),
            file_name="session.opro",
            mime="application/json",
            key="dl_btn_popover"
        )
    else:
        st.warning("No session active.")

def _import_session(uploaded_file):
    try:
        content = uploaded_file.read().decode('utf-8')
        data = json.loads(content)
        st.session_state["seed_prompt"] = data.get("seed_prompt", "")
        st.success("Imported!")
    except Exception as e:
        st.error(f"Error: {e}")

def get_session_config() -> SessionConfig:
    """Build SessionConfig from state."""
    return SessionConfig(
        model=st.session_state.get("selected_model", "gpt-4o-mini"),
        temperature=st.session_state.get("temperature", 0.7),
        generations_per_step=st.session_state.get("generations_per_step", 3),
        stop_score_threshold=st.session_state.get("stop_threshold", 95.0),
        noise_level=st.session_state.get("noise_level", 0.0),
        top_k=st.session_state.get("top_k", 5),
        vector_store_path=st.session_state.get("vector_store_path", "")
    )
