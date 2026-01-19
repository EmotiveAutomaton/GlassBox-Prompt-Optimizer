"""
Zone A: The Glass Box Banner - Top Full-Width Visualization

Contains:
- Input & Control Area (seed prompt, action button)
- Schematic Visualization (engine-specific animated diagram)
- Internal Monologue Panel (shows active agent's system prompt)
"""

import streamlit as st
from typing import Optional

from glassbox.core.optimizer_base import AbstractOptimizer


def render_zone_a(optimizer: Optional[AbstractOptimizer] = None):
    """Render the Glass Box banner zone."""
    
    # Container for the banner
    st.markdown("""
    <style>
    .glass-box-banner {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #20C20E;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .monologue-panel {
        background-color: #0a0a0f;
        border: 1px solid #31333F;
        border-radius: 5px;
        padding: 10px;
        font-family: monospace;
        font-size: 12px;
        color: #20C20E;
        max-height: 200px;
        overflow-y: auto;
    }
    </style>
    """, unsafe_allow_html=True)

    # Three-column layout for the banner
    col_input, col_schematic, col_monologue = st.columns([1.2, 1.5, 1])

    with col_input:
        st.markdown("### 🎯 Task Input")
        
        # Seed prompt input
        seed_prompt = st.text_area(
            "Seed Prompt / Task Description",
            value=st.session_state.get("seed_prompt", "Write a clear, concise summary of the given text..."),
            height=120,
            key="seed_prompt_input",
            help="Enter your initial prompt or task description"
        )
        st.session_state["seed_prompt"] = seed_prompt

        # Action buttons
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            start_btn = st.button(
                "▶️ Initialize Optimization",
                type="primary",
                use_container_width=True,
                disabled=st.session_state.get("is_running", False)
            )
        with col_btn2:
            stop_btn = st.button(
                "⏹️ Stop",
                use_container_width=True,
                disabled=not st.session_state.get("is_running", False)
            )

        if start_btn:
            st.session_state["start_optimization"] = True
        if stop_btn:
            st.session_state["stop_optimization"] = True

    with col_schematic:
        st.markdown("### 🔄 Schematic Visualization")
        
        # Render engine-specific schematic
        if optimizer:
            try:
                graphviz_source = optimizer.generate_graphviz()
                st.graphviz_chart(graphviz_source, use_container_width=True)
            except Exception as e:
                st.warning(f"Schematic rendering: {e}")
                _render_placeholder_schematic()
        else:
            _render_placeholder_schematic()

    with col_monologue:
        st.markdown("### 💭 Internal Monologue")
        
        # Display the current agent's internal state
        monologue = ""
        if optimizer:
            monologue = optimizer.session.internal_monologue
        
        if not monologue:
            monologue = "[Idle] Waiting for optimization to start..."

        st.markdown(f"""
        <div class="monologue-panel">
            <pre>{monologue}</pre>
        </div>
        """, unsafe_allow_html=True)

        # Status indicator
        status = st.session_state.get("optimizer_status", "idle")
        status_colors = {
            "idle": "🔘",
            "running": "🟢",
            "paused": "🟡",
            "completed": "✅",
            "failed": "🔴",
            "stopped": "⏹️"
        }
        st.markdown(f"**Status:** {status_colors.get(status, '❓')} {status.title()}")


def _render_placeholder_schematic():
    """Render a placeholder when no optimizer is active."""
    placeholder_dot = """
    digraph Placeholder {
        rankdir=LR;
        bgcolor="#0E1117";
        node [style=filled, fillcolor="#31333F", fontcolor=white, fontname="Helvetica"];
        
        start [label="Start", shape=circle];
        process [label="Select\\nEngine", shape=box];
        end [label="Results", shape=circle];
        
        start -> process [color="#4A4A4A"];
        process -> end [color="#4A4A4A"];
    }
    """
    st.graphviz_chart(placeholder_dot, use_container_width=True)


def render_zone_a_compact():
    """Render a more compact version of Zone A for smaller screens."""
    st.markdown("### 🔮 Glass Box Optimizer")
    
    seed = st.text_area(
        "Seed Prompt",
        value=st.session_state.get("seed_prompt", ""),
        height=80,
        key="seed_prompt_compact"
    )
    st.session_state["seed_prompt"] = seed

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("▶️ Start", type="primary"):
            st.session_state["start_optimization"] = True
    with col2:
        if st.button("⏹️ Stop"):
            st.session_state["stop_optimization"] = True
    with col3:
        status = st.session_state.get("optimizer_status", "idle")
        st.markdown(f"**Status:** {status.title()}")
