"""
Zone F: Settings Popover
- Hidden in the main UI, triggered by the Top Bar Gear Icon via JS.
- Contains global settings: Model, Temperature, Dark Mode.
"""

import streamlit as st

def render_zone_f():
    """Render the hidden settings popover."""
    
    # CSS to hide the trigger button visually but keep it clickable via JS
    st.markdown("""
        <style>
        #settings-trigger-container {
            position: fixed;
            top: -100px; /* Hide off-screen or make transparent */
            left: 0;
            opacity: 0;
            pointer-events: none; /* Prevent accidental clicks, though JS click() works */
            height: 0;
            width: 0;
            overflow: hidden;
        }
        /* Make the button clickable even if container is hidden/zero-size? 
           Actually, for JS click() to work, it shouldn't be display:none. 
           Opacity 0 is safer. */
        </style>
    """, unsafe_allow_html=True)

    # Wrap in a container to target with JS
    with st.container():
        st.markdown('<div id="settings-trigger-container">', unsafe_allow_html=True)
        
        with st.popover("⚙️"): # The label doesn't matter much if hidden
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

        st.markdown('</div>', unsafe_allow_html=True)
