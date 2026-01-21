"""
Zone B: Control Sidebar - Flush Navigation Only.
Buttons are flush with all 4 edges of the sidebar using absolute positioning.
"""

import streamlit as st
from glassbox.models.session import SessionConfig


def render_zone_b():
    """Render the sidebar with flush navigation blocks only."""
    
    # === ABSOLUTE POSITIONING CSS FOR TRULY FLUSH BUTTONS ===
    st.sidebar.markdown("""
        <style>
            /* =========================================================
               SIDEBAR ROOT: Set up for absolute positioning of content
               ========================================================= */
            section[data-testid="stSidebar"] {
                padding-top: 60px !important;
                margin-top: 0 !important;
                background-color: #394957 !important;
                overflow: visible !important;
            }
            
            /* Remove all internal padding */
            section[data-testid="stSidebar"] > div:first-child {
                padding: 0 !important;
                margin: 0 !important;
                position: relative !important;
            }
            
            section[data-testid="stSidebar"] > div:first-child > div:first-child {
                padding: 0 !important;
                margin: 0 !important;
            }
            
            section[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
            section[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
                padding: 0 !important;
                margin: 0 !important;
                gap: 0 !important;
            }
            
            section[data-testid="stSidebar"] .stElementContainer,
            section[data-testid="stSidebar"] .element-container {
                padding: 0 !important;
                margin: 0 !important;
            }
            
            /* =========================================================
               RADIO GROUP: Position at very top, full width
               ========================================================= */
            section[data-testid="stSidebar"] .stRadio {
                position: relative !important;
                top: 0 !important;
                left: 0 !important;
                width: 220px !important;
                padding: 0 !important;
                margin: 0 !important;
                margin-top: -16px !important; /* Pull up to eliminate padding gap */
            }
            
            section[data-testid="stSidebar"] .stRadio > div {
                width: 220px !important;
                padding: 0 !important;
                margin: 0 !important;
            }
            
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] {
                gap: 0 !important;
                width: 220px !important;
                padding: 0 !important;
                margin: 0 !important;
                display: flex !important;
                flex-direction: column !important;
            }
            
            /* =========================================================
               EACH NAV BUTTON: Full width, no gaps
               ========================================================= */
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label {
                display: flex !important;
                align-items: center !important;
                width: 220px !important;
                min-width: 220px !important;
                max-width: 220px !important;
                margin: 0 !important;
                padding: 18px 16px !important;
                border: none !important;
                border-bottom: 1px solid rgba(255,255,255,0.15) !important;
                border-radius: 0 !important;
                background-color: #394957 !important;
                color: white !important;
                font-size: 13px !important;
                font-weight: 400 !important;
                cursor: pointer !important;
                box-sizing: border-box !important;
                transition: background-color 0.1s ease !important;
            }
            
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:hover {
                background-color: rgba(255,255,255,0.1) !important;
                color: white !important;
            }
            
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:hover * {
                background-color: transparent !important;
                color: white !important;
            }
            
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:has(input:checked) {
                background-color: #0D7CB1 !important;
            }
            
            /* Hide radio dots */
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label > div:first-child,
            section[data-testid="stSidebar"] .stRadio span[data-baseweb="radio"] {
                display: none !important;
            }
            
            section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label p {
                margin: 0 !important;
                padding: 0 !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Navigation Blocks ONLY
    mode_options = [
        "OPro (Iterative)",
        "APE (Reverse Eng.)",
        "Promptbreeder (Evol.)",
        "S2A (Context Filter)"
    ]
    
    selected_view = st.sidebar.radio(
        "Navigation",
        options=mode_options,
        label_visibility="collapsed",
        key="selected_engine"
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
