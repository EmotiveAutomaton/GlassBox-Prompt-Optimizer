"""
GlassBox Prompt Optimizer v2.0

Main Streamlit application entry point.
Implements the 5-zone layout per Boeing Living Specs.

Usage:
    streamlit run glassbox/app.py
"""

import streamlit as st
import time
import threading
from typing import Optional

# Page config must be first Streamlit command
import base64

# Page config must be first Streamlit command
st.set_page_config(
    page_title="GlassBox Prompt Optimizer",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Now import our modules
# ... (standard imports follow)
from glassbox.core import (
    BoeingAPIClient,
    APIConfig,
    GeminiAPIClient,
    get_api_client,
    HumanOverrideEvaluator,
    OProEngine,
    APEEngine,
    PromptbreederEngine,
    S2AEngine,
    get_engine_class,
    list_engines
)
from glassbox.models import OptimizerSession, TestBenchConfig
from glassbox.ui import (
    render_zone_a,
    render_zone_b,
    get_session_config,
    render_zone_c,
    render_zone_d,
    render_zone_e,
    get_test_bench_config
)
from glassbox.ui.styles import inject_custom_css
from glassbox.rag import BaristaSimulator

# --- LOAD ASSETS ---
def get_image_base64(path_to_image):
    try:
        with open(path_to_image, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return ""

# Use the CORRECT white-on-transparent logo from main assets folder
logo_b64 = get_image_base64("glassbox/assets/BoeingWhiteOnTransparentLogo.png")

# Inject custom CSS
inject_custom_css()

# --- INJECT GLOBAL TOP BAR ---
# Layout: Title Left | Logo Centered | Gear Icon Right
# Gear icon clicks the hidden settings popover trigger
st.markdown(f"""
    <div id="boeing-top-bar">
        <span class="top-bar-title">GLASSBOX PROMPT OPTIMIZER</span>
        <img src="data:image/png;base64,{logo_b64}" alt="Boeing Logo" class="top-bar-logo">
        <button id="top-bar-gear" onclick="document.querySelector('#settings-trigger-container button').click()">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                <circle cx="12" cy="12" r="3"></circle>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
            </svg>
        </button>
    </div>
""", unsafe_allow_html=True)


# =============================================================================
# INITIALIZATION
# =============================================================================

def init_session_state():
    """Initialize session state variables."""
    defaults = {
        "session": None,
        "optimizer": None,
        "api_client": None,
        "evaluator": None,
        "is_running": False,
        "optimizer_status": "idle",
        "seed_prompt": "Write a clear, concise summary of the given text that captures the key points...",
        "selected_engine": "OPro (Iterative)",
        "selected_model": "gpt-4o-mini",
        "temperature": 0.7,
        "generations_per_step": 3,
        "stop_threshold": 95.0,
        "start_optimization": False,
        "stop_optimization": False,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_or_create_session() -> OptimizerSession:
    """Get existing session or create new one."""
    if st.session_state["session"] is None:
        session = OptimizerSession()
        session.seed_prompt = st.session_state.get("seed_prompt", "")
        session.config = get_session_config()
        session.test_bench = get_test_bench_config()
        st.session_state["session"] = session
    return st.session_state["session"]


def get_or_create_api_client():
    """
    Get existing API client or create new one.
    
    Auto-detects: Uses Gemini if GEMINI_API_KEY is set, else Boeing API.
    """
    if st.session_state["api_client"] is None:
        # Use factory function for auto-detection
        st.session_state["api_client"] = get_api_client()
        
        # Display which API is being used
        health = st.session_state["api_client"].health_check()
        if hasattr(st.session_state["api_client"], 'config') and hasattr(st.session_state["api_client"].config, 'model'):
            model = st.session_state["api_client"].config.model
            st.sidebar.caption(f"🔌 API: {model}")
    
    return st.session_state["api_client"]


def get_or_create_evaluator() -> HumanOverrideEvaluator:
    """Get existing evaluator or create new one."""
    if st.session_state["evaluator"] is None:
        api_client = get_or_create_api_client()
        st.session_state["evaluator"] = HumanOverrideEvaluator(api_client)
    return st.session_state["evaluator"]


def create_optimizer(engine_name: str):
    """Create optimizer instance for selected engine."""
    session = get_or_create_session()
    api_client = get_or_create_api_client()
    evaluator = get_or_create_evaluator()
    
    # Update session with current config
    session.seed_prompt = st.session_state.get("seed_prompt", "")
    session.config = get_session_config()
    session.test_bench = get_test_bench_config()
    session.metadata.engine_used = engine_name
    
    # Get engine class and instantiate
    EngineClass = get_engine_class(engine_name)
    if EngineClass:
        optimizer = EngineClass(api_client, evaluator, session)
        st.session_state["optimizer"] = optimizer
        return optimizer
    
    # Fallback to OPro
    return OProEngine(api_client, evaluator, session)


# =============================================================================
# OPTIMIZATION CONTROL
# =============================================================================

def start_optimization():
    """Start the optimization loop."""
    engine_name = st.session_state.get("selected_engine", "OPro (Iterative)")
    optimizer = create_optimizer(engine_name)
    
    st.session_state["is_running"] = True
    st.session_state["optimizer_status"] = "running"
    
    # Set up callbacks
    def on_step_complete(result):
        st.session_state["optimizer_status"] = "running"
    
    def on_status_change(status):
        st.session_state["optimizer_status"] = status.value
        if status.value in ["completed", "failed", "stopped"]:
            st.session_state["is_running"] = False
    
    optimizer.set_callbacks(on_step_complete, on_status_change)
    
    # Run in background thread
    optimizer.run_async(max_steps=50)


def stop_optimization():
    """Stop the current optimization."""
    optimizer = st.session_state.get("optimizer")
    if optimizer:
        optimizer.request_stop()
    st.session_state["is_running"] = False
    st.session_state["optimizer_status"] = "stopped"


# =============================================================================
# MAIN LAYOUT
# =============================================================================

def main():
    """Main application entry point."""
    init_session_state()
    
    # Handle start/stop actions
    if st.session_state.get("start_optimization"):
        st.session_state["start_optimization"] = False
        start_optimization()
        st.rerun()
    
    if st.session_state.get("stop_optimization"):
        st.session_state["stop_optimization"] = False
        stop_optimization()
        st.rerun()
    
    # === ZONE B: Sidebar (Flush Navigation Only) ===
    render_zone_b()
    
    # === Main Content Area ===
    
    # === TOP ROW: INPUT + GLASS BOX Cards ===
    optimizer = st.session_state.get("optimizer")
    render_zone_a(optimizer)
    
    # === BOTTOM ROW: POTENTIAL PROMPTS + PROMPT RATINGS + FINAL OUTPUT Cards ===
    session = get_or_create_session()
    render_zone_c(session.candidates, session.test_bench)
    
    # === SETTINGS POPOVER (at end, positioned over gear icon via CSS) ===
    # Put at end so it's easier to target with CSS
    st.markdown('''
        <style>
        /* Position the LAST element container with a popover trigger */
        .main .block-container > div:last-child {
            position: fixed !important;
            top: 10px !important;
            right: 10px !important;
            z-index: 999999 !important;
            width: 40px !important;
            height: 40px !important;
        }
        .main .block-container > div:last-child button[data-testid="stPopoverButton"] {
            background: transparent !important;
            border: none !important;
            color: transparent !important;
            width: 40px !important;
            height: 40px !important;
            padding: 0 !important;
            min-height: 40px !important;
        }
        .main .block-container > div:last-child p {
            display: none !important;
        }
        </style>
    ''', unsafe_allow_html=True)
    
    with st.popover("⚙️", use_container_width=False):
        st.markdown("### Settings")
        
        # Light/Dark Mode Toggle (disabled for now)
        st.markdown("**Theme**")
        theme = st.radio(
            "Theme Mode",
            options=["Light Mode", "Dark Mode"],
            index=0,
            key="theme_mode",
            disabled=True,
            label_visibility="collapsed"
        )
        st.caption("*Dark mode coming soon*")
        
        st.divider()
        
        # Import/Export
        st.markdown("**Session Management**")
        
        # Export
        session = get_or_create_session()
        import json
        session_json = json.dumps(session.to_dict(), indent=2)
        st.download_button(
            "📤 Export Session",
            data=session_json,
            file_name="glassbox_session.opro",
            mime="application/json",
            use_container_width=True
        )
        
        # Import
        uploaded = st.file_uploader("📥 Import Session", type=["opro", "json"], key="import_session_file", label_visibility="collapsed")
        if uploaded:
            try:
                data = json.load(uploaded)
                imported = OptimizerSession.from_dict(data)
                st.session_state["session"] = imported
                st.success("Session imported!")
                st.rerun()
            except Exception as e:
                st.error(f"Import failed: {e}")
    
    # === Auto-refresh during optimization ===
    if st.session_state.get("is_running", False):
        time.sleep(2)  # Poll every 2 seconds
        st.rerun()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()
