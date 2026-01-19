"""
Zone B: Control Sidebar - Configuration and Environmental Constraints

Contains:
- Engine Selector
- Model Selection
- Hyperparameters (temperature, generations, stop threshold)
- RAG Configuration (Barista Sim)
- Session Management (Import/Export)
"""

import streamlit as st
from typing import Optional
import json

from glassbox.models.session import OptimizerSession, SessionConfig
from glassbox.core import list_engines


def render_zone_b():
    """Render the control sidebar."""
    
    st.sidebar.markdown("# ⚙️ Configuration")
    st.sidebar.markdown("---")

    # Engine Selection
    st.sidebar.markdown("### 🚀 Engine")
    engine_names = list_engines()
    selected_engine = st.sidebar.selectbox(
        "Optimization Engine",
        options=engine_names,
        index=0,
        key="selected_engine",
        help="Select the optimization strategy"
    )

    # Engine descriptions
    engine_descriptions = {
        "OPro (Iterative)": "Iterative feedback loop optimization",
        "APE (Reverse Eng)": "Reverse-engineer prompts from examples",
        "Promptbreeder (Evolutionary)": "Evolve population of prompts",
        "S2A (Context Filter)": "Optimize context filtering for RAG"
    }
    st.sidebar.caption(engine_descriptions.get(selected_engine, ""))

    st.sidebar.markdown("---")

    # Model Selection
    st.sidebar.markdown("### 🤖 Model")
    models = ["gpt-4o-mini", "gpt-4o", "gpt-4", "claude-3-5-sonnet"]
    selected_model = st.sidebar.selectbox(
        "LLM Model",
        options=models,
        index=0,
        key="selected_model"
    )

    st.sidebar.markdown("---")

    # Hyperparameters
    st.sidebar.markdown("### 🎛️ Hyperparameters")
    
    st.sidebar.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        key="temperature",
        help="Higher = more creative, Lower = more deterministic"
    )

    st.sidebar.slider(
        "Generations per Step",
        min_value=1,
        max_value=10,
        value=3,
        key="generations_per_step",
        help="Number of variations to generate each step"
    )

    st.sidebar.number_input(
        "Stop Score Threshold",
        min_value=0.0,
        max_value=100.0,
        value=95.0,
        step=5.0,
        key="stop_threshold",
        help="Stop optimization when this score is reached"
    )

    st.sidebar.markdown("---")

    # RAG Configuration (Barista Sim)
    with st.sidebar.expander("🗃️ RAG Configuration"):
        st.markdown("**Barista Simulator**")
        
        st.text_input(
            "Vector Store Path",
            value="",
            key="vector_store_path",
            help="Path to ChromaDB directory"
        )

        st.slider(
            "Top K (Chunks)",
            min_value=1,
            max_value=10,
            value=5,
            key="top_k"
        )

        st.slider(
            "Noise Injection",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.1,
            key="noise_level",
            help="0% = Clean, 100% = High Noise"
        )

        st.caption("🟩 Green = Legitimate | 🟥 Red = Noise")

    st.sidebar.markdown("---")

    # Session Management
    st.sidebar.markdown("### 💾 Session")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("📤 Export", use_container_width=True, key="export_btn"):
            _export_session()
    
    with col2:
        if st.button("📥 Import", use_container_width=True, key="import_btn"):
            st.session_state["show_import_dialog"] = True

    # Import dialog
    if st.session_state.get("show_import_dialog", False):
        uploaded = st.sidebar.file_uploader(
            "Upload .opro file",
            type=["opro", "json"],
            key="file_uploader"
        )
        if uploaded:
            _import_session(uploaded)
            st.session_state["show_import_dialog"] = False
            st.rerun()


def _export_session():
    """Export current session to .opro file."""
    session: OptimizerSession = st.session_state.get("session")
    if session:
        json_data = session.to_json()
        st.sidebar.download_button(
            "⬇️ Download .opro",
            data=json_data,
            file_name="glassbox_session.opro",
            mime="application/json"
        )
    else:
        st.sidebar.warning("No active session to export")


def _import_session(uploaded_file):
    """Import session from .opro file."""
    try:
        content = uploaded_file.read().decode('utf-8')
        data = json.loads(content)
        session = OptimizerSession.load_from_dict(data) if hasattr(OptimizerSession, 'load_from_dict') else None
        if session:
            st.session_state["session"] = session
            st.sidebar.success("Session imported!")
        else:
            # Manual reconstruction
            st.session_state["seed_prompt"] = data.get("seed_prompt", "")
            st.sidebar.success("Session data loaded!")
    except Exception as e:
        st.sidebar.error(f"Import failed: {e}")


def get_session_config() -> SessionConfig:
    """Build SessionConfig from sidebar state."""
    return SessionConfig(
        model=st.session_state.get("selected_model", "gpt-4o-mini"),
        temperature=st.session_state.get("temperature", 0.7),
        generations_per_step=st.session_state.get("generations_per_step", 3),
        stop_score_threshold=st.session_state.get("stop_threshold", 95.0),
        noise_level=st.session_state.get("noise_level", 0.0),
        top_k=st.session_state.get("top_k", 5),
        vector_store_path=st.session_state.get("vector_store_path", "")
    )
