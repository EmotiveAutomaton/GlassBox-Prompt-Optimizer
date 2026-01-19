"""
Zone E: Test Bench - Bottom Right

Contains:
- Three distinct input areas (Golden Path, Edge Case, Adversarial)
- Traffic light indicators
- Free Play mode for winner testing
"""

import streamlit as st
from typing import Optional

from glassbox.models.session import TestBenchConfig, CandidateResult


def render_zone_e(test_bench: TestBenchConfig, winner: Optional[CandidateResult] = None):
    """Render the test bench zone."""
    
    # Mode toggle
    mode = st.radio(
        "Mode",
        options=["🧪 Test Bench", "🎮 Free Play"],
        horizontal=True,
        key="testbench_mode"
    )

    if mode == "🧪 Test Bench":
        _render_test_bench_mode(test_bench)
    else:
        _render_free_play_mode(winner)


def _render_test_bench_mode(test_bench: TestBenchConfig):
    """Render the tri-state test bench inputs."""
    st.markdown("### 🧪 Test Bench")
    st.caption("Define 3 test inputs to evaluate prompts against. Scores are averaged.")

    # Input A: Golden Path
    st.markdown("#### 🟢 Input A: Golden Path")
    st.caption("Standard, representative input")
    input_a = st.text_area(
        "Golden Path Input",
        value=test_bench.input_a or "Enter a standard test input...",
        height=80,
        key="test_input_a",
        label_visibility="collapsed"
    )
    score_a = st.session_state.get("score_a", None)
    if score_a is not None:
        _render_traffic_light(score_a, "a")

    # Input B: Edge Case
    st.markdown("#### 🟡 Input B: Edge Case")
    st.caption("Difficult or malformed input")
    input_b = st.text_area(
        "Edge Case Input",
        value=test_bench.input_b or "Enter an edge case...",
        height=80,
        key="test_input_b",
        label_visibility="collapsed"
    )
    score_b = st.session_state.get("score_b", None)
    if score_b is not None:
        _render_traffic_light(score_b, "b")

    # Input C: Adversarial
    st.markdown("#### 🔴 Input C: Adversarial/OOD")
    st.caption("Out-of-distribution or adversarial input")
    input_c = st.text_area(
        "Adversarial Input",
        value=test_bench.input_c or "Enter an adversarial input...",
        height=80,
        key="test_input_c",
        label_visibility="collapsed"
    )
    score_c = st.session_state.get("score_c", None)
    if score_c is not None:
        _render_traffic_light(score_c, "c")

    # Update test bench config
    test_bench.input_a = input_a
    test_bench.input_b = input_b
    test_bench.input_c = input_c

    # Store in session
    st.session_state["test_bench"] = test_bench


def _render_free_play_mode(winner: Optional[CandidateResult]):
    """Render free play mode for testing the winning prompt."""
    st.markdown("### 🎮 Free Play")
    
    if not winner:
        st.warning("No winner selected yet. Complete optimization first.")
        return

    st.markdown("**Winning Prompt:**")
    st.code(winner.prompt_text, language="text")
    st.metric("Final Score", f"{winner.global_score:.1f}")

    st.markdown("---")
    st.markdown("**Test with any input:**")
    
    free_input = st.text_area(
        "Custom Test Input",
        value="",
        height=100,
        key="free_play_input",
        placeholder="Enter any input to test the winning prompt..."
    )

    col1, col2 = st.columns([1, 3])
    
    with col1:
        run_test = st.button("▶️ Run Test", type="primary", key="run_free_play")
    
    with col2:
        compare_original = st.checkbox("Compare with original", value=True, key="compare_original")

    if run_test and free_input:
        with st.spinner("Generating response..."):
            # This would call the API - placeholder for now
            st.session_state["free_play_result"] = {
                "input": free_input,
                "response": "[Response would appear here after API call]"
            }

    # Display results
    result = st.session_state.get("free_play_result")
    if result:
        st.markdown("**Response:**")
        st.success(result.get("response", ""))

        if compare_original:
            st.markdown("**Original Seed Response (for comparison):**")
            st.info("[Original response would appear here]")

            st.markdown("**Qualitative Lift:**")
            st.caption("Compare the winning prompt's output against the original to see improvement.")


def _render_traffic_light(score: float, label: str):
    """Render a traffic light indicator for a test score."""
    threshold = 50  # Configurable pass threshold
    
    if score >= threshold:
        color = "#22c55e"
        status = "✅ Pass"
    else:
        color = "#ef4444"
        status = "❌ Fail"

    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
        <div style="width: 12px; height: 12px; border-radius: 50%; background-color: {color};"></div>
        <span style="color: {color}; font-size: 12px;">{status} ({score:.1f})</span>
    </div>
    """, unsafe_allow_html=True)


def get_test_bench_config() -> TestBenchConfig:
    """Get current test bench configuration from session state."""
    return TestBenchConfig(
        input_a=st.session_state.get("test_input_a", ""),
        input_b=st.session_state.get("test_input_b", ""),
        input_c=st.session_state.get("test_input_c", "")
    )
