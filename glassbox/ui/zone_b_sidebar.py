"""
Zone B: Control Sidebar - Flush Navigation Only.
NO configuration button - config is accessed via gear icon in top bar only.
"""

import streamlit as st
from glassbox.models.session import SessionConfig


def render_zone_b():
    """Render the sidebar with flush navigation blocks only. No config popover here."""
    
    # === EXTREMELY AGGRESSIVE CSS FOR FLUSH BUTTONS ===
    st.sidebar.markdown("""
        <style>
            /* =========================================================
               SIDEBAR ROOT: Remove ALL padding at every level
               ========================================================= */
            section[data-testid="stSidebar"],
            section[data-testid="stSidebar"] > div,
            section[data-testid="stSidebar"] > div > div,
            section[data-testid="stSidebar"] > div > div > div,
            section[data-testid="stSidebar"] .stElementContainer,
            section[data-testid="stSidebar"] .element-container {
                padding: 0 !important;
                margin: 0 !important;
            }
            
            /* First div inside sidebar */
            section[data-testid="stSidebar"] > div:first-child {
                padding-top: 60px !important; /* Only pad for top bar */
                padding-left: 0 !important;
                padding-right: 0 !important;
                padding-bottom: 0 !important;
            }
            
            /* =========================================================
               RADIO GROUP: No gaps, full width
               ========================================================= */
            section[data-testid="stSidebar"] .stRadio {
                width: 100% !important;
                padding: 0 !important;
                margin: 0 !important;
            }
            
            section[data-testid="stSidebar"] .stRadio > div {
                width: 100% !important;
                padding: 0 !important;
                margin: 0 !important;
            }
            
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] {
                gap: 0 !important;
                width: 100% !important;
                padding: 0 !important;
                margin: 0 !important;
                display: flex !important;
                flex-direction: column !important;
            }
            
            /* =========================================================
               EACH NAV BUTTON: 100% width, no margins
               ========================================================= */
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label {
                display: flex !important;
                align-items: center !important;
                width: 100% !important;
                min-width: 220px !important;
                max-width: 220px !important;
                margin: 0 !important;
                padding: 18px 16px !important;
                border: none !important;
                border-bottom: 1px solid rgba(255,255,255,0.15) !important;
                border-radius: 0 !important;
                background-color: transparent !important;
                color: white !important;
                font-size: 13px !important;
                font-weight: 400 !important;
                cursor: pointer !important;
                box-sizing: border-box !important;
                transition: background-color 0.15s ease !important;
            }
            
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:first-child {
                border-top: none !important;
            }
            
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:hover {
                background-color: rgba(255,255,255,0.1) !important;
            }
            
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:has(input:checked) {
                background-color: #0D7CB1 !important;
            }
            
            /* Hide radio dots completely */
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label > div:first-child,
            section[data-testid="stSidebar"] .stRadio span[data-baseweb="radio"] {
                display: none !important;
                width: 0 !important;
                height: 0 !important;
                visibility: hidden !important;
            }
            
            /* Hide the text span that wraps radio label to control padding */
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label p {
                margin: 0 !important;
                padding: 0 !important;
            }
            
            /* =========================================================
               HIDE ANY POPOVERS IN SIDEBAR (Config moved to top bar)
               ========================================================= */
            section[data-testid="stSidebar"] .stPopover {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Navigation Blocks ONLY - no config
    view_options = [
        "OPro (Iterative)",
        "APE (Reverse Eng.)",
        "Promptbreeder (Evol.)",
        "S2A (Context Filter)"
    ]
    
    st.sidebar.radio(
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
