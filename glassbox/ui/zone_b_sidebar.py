"""
Zone B: Control Sidebar - Flush Navigation
No config button - config is in top bar gear icon
"""

import streamlit as st
from glassbox.models.session import SessionConfig

def render_zone_b():
    """Render the sidebar with flush navigation blocks only."""
    
    # Navigation Blocks - No title, no config button
    view_options = [
        "OPro (Iterative)",
        "APE (Reverse Eng.)",
        "Promptbreeder (Evol.)",
        "S2A (Context Filter)"
    ]
    
    # CSS to make nav items completely flush with sidebar edges and top bar
    st.sidebar.markdown("""
        <style>
            /* Remove all sidebar padding */
            section[data-testid="stSidebar"] > div:first-child {
                padding-top: 0 !important;
                padding-left: 0 !important;
                padding-right: 0 !important;
            }
            
            /* Radio group container - no gaps */
            .stRadio > div[role="radiogroup"] {
                gap: 0 !important;
                margin-top: 60px !important; /* Below top bar */
            }
            
            /* Each nav item - flush all edges */
            .stRadio > div[role="radiogroup"] > label {
                margin: 0 !important;
                padding: 18px 20px !important;
                width: 100% !important;
                border-bottom: 1px solid rgba(0,0,0,0.2);
                border-radius: 0 !important;
                background-color: transparent;
                transition: background-color 0.15s ease;
            }
            
            .stRadio > div[role="radiogroup"] > label:hover {
                background-color: rgba(255,255,255,0.08);
            }
            
            .stRadio > div[role="radiogroup"] > label:has(input:checked) {
                background-color: #0D7CB1 !important;
            }
            
            /* Hide radio dots */
            .stRadio > div[role="radiogroup"] > label > div:first-child {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    selected_engine = st.sidebar.radio(
        "Navigation",
        options=view_options,
        index=0,
        key="selected_engine",
        label_visibility="collapsed"
    )


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
