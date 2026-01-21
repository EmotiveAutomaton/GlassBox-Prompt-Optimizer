"""
Zone F: Settings Popover
- Hidden in the main UI, triggered by the Top Bar Gear Icon via JS.
- Contains global settings: Model, Temperature, Dark Mode.
"""

import streamlit as st

def render_zone_f():
    """Render the hidden settings popover."""
    
    # CSS to position the popover transparently over the top-gear icon
    st.markdown("""
        <style>
        /* Position the popover container over the top-right gear icon */
        [data-testid="stPopover"] {
            position: fixed !important;
            top: 10px !important;
            right: 20px !important;
            z-index: 1000000 !important;
        }
        
        /* Make the button transparent but clickable */
        [data-testid="stPopover"] > button {
            width: 40px !important;
            height: 40px !important;
            background: transparent !important;
            border: none !important;
            color: transparent !important; /* Hide the emoji */
            padding: 0 !important;
            box-shadow: none !important;
        }
        
        /* Optional: Add hover effect to match the underlying icon's hover */
        [data-testid="stPopover"] > button:hover {
            background: rgba(255,255,255,0.1) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Render popover directly (no wrapper div needed for targeting if it's the unique popover)
    with st.popover("⚙️"):

            st.markdown("### Settings")
            
            # --- THEME SETTINGS ---
            st.markdown("#### Appearance")
            dark_mode = st.toggle("Dark Mode", value=st.session_state.get("dark_mode", False), key="dark_mode_toggle")
            if dark_mode != st.session_state.get("dark_mode", False):
                st.session_state["dark_mode"] = dark_mode
                st.rerun()

            st.divider()

            # --- MODEL SETTINGS ---
            st.markdown("#### Model Parameters")
            
            st.selectbox(
                "Model",
                options=["gpt-4o-mini", "gpt-4o", "gemini-1.5-pro", "gemini-1.5-flash"],
                index=0,
                key="selected_model"
            )
            
            st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=st.session_state.get("temperature", 0.7),
                step=0.1,
                key="temperature"
            )
            
            st.number_input(
                "Generations per Step",
                min_value=1,
                max_value=10,
                value=st.session_state.get("generations_per_step", 3),
                key="generations_per_step"
            )
            
            st.divider()
            
            # --- API CONFIG ---
            st.markdown("#### API Configuration")
            api_key = st.text_input("Boeing/Gemini API Key", type="password", key="api_key_input", help="Leave empty to use env vars")
            if api_key:
                st.session_state["api_key_override"] = api_key

            st.divider()

            # --- PERSISTENCE ---
            st.markdown("#### Session Management")
            
            # Export
            if "session" in st.session_state and st.session_state["session"]:
                session_json = st.session_state["session"].to_json()
                st.download_button(
                    label="💾 Export Session (.opro)",
                    data=session_json,
                    file_name=f"glassbox_session_{st.session_state['session'].metadata.session_id[:8]}.opro",
                    mime="application/json",
                    help="Save current session state to disk."
                )
            
            # Import
            from glassbox.models.session import OptimizerSession
            uploaded_file = st.file_uploader("📥 Import Session", type=["opro", "json"], key="session_uploader")
            if uploaded_file is not None:
                try:
                    # Read and load
                    json_str = uploaded_file.getvalue().decode("utf-8")
                    new_session = OptimizerSession.from_json(json_str)
                    
                    # Update state
                    st.session_state["session"] = new_session
                    st.success("Session loaded successfully!")
                    
                    # Force rerun to refresh UI
                    if st.button("Reload UI with New Session"):
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Failed to load session: {e}")


