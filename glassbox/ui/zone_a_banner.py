"""
Zone A: Top Row Cards.
- Card 1: INITIAL PROMPT AND DATA (left) - Dynamic based on Engine.
- Card 2: GLASS BOX (right) - Visualization + Logic Readout.

Uses st.container(border=True) for visible card outlines.
"""

import streamlit as st
from typing import Optional
from glassbox.core.optimizer_base import AbstractOptimizer
from glassbox.core.visualizer import GraphVisualizer


def render_zone_a(optimizer: Optional[AbstractOptimizer] = None):
    """Render the top row with INPUT and GLASS BOX cards."""
    
    # Defaults
    raw_selection = st.session_state.get("selected_engine", "OPro (Iterative)")
    
    # Map friendly names to internal IDs
    engine_map = {
        "OPro (Iterative)": "opro",
        "APE (Reverse Eng.)": "ape",
        "Promptbreeder (Evol.)": "promptbreeder",
        "S2A (Context Filter)": "s2a"
    }
    engine_id = engine_map.get(raw_selection, "opro")
    
    # --- ROW 1: Two Card Boxes Side by Side ---
    col_input, col_glassbox = st.columns([1, 1.8])
    
    # === CARD 1: INITIAL PROMPT AND DATA (Dynamic based on Engine) ===
    with col_input:
        with st.container(border=True):
            st.markdown(f'<div class="card-header">INITIAL PROMPT AND DATA ({engine_id.upper()})</div>', unsafe_allow_html=True)
            
            # --- DYNAMIC INPUTS ---
            if engine_id == "opro":
                # OPro: Prompt (Text Only) + Test Data (File/Tabbed)
                st.text_area("Seed Prompt", height=80, key="opro_seed_prompt", 
                           placeholder="Initial prompt to be optimized...", label_visibility="collapsed")
                
                # Test Data with Tabs
                _render_tabbed_input(
                    label="Test Data",
                    state_prefix="opro_test",
                    height=150,
                    placeholder="Enter or upload test cases (one per line)..."
                )
            
            elif engine_id == "ape":
                # APE: Input Data (File/Tabbed) + Ideal Output (Text/File?) -> Spec said "Top box... Initial prompt and data area"
                # User Request: "APE... same thing with the top box... these test cases... driven by outside data sources"
                
                # APE Input Data (Tabbed)
                _render_tabbed_input(
                    label="Input Data (Examples)",
                    state_prefix="ape_input",
                    height=100,
                    placeholder="Upload or paste input examples for reverse engineering..."
                )
                
                # Ideally APE also needs Output data, but requirements focused on "Top box". 
                # We will keep Ideal Output as simple text for now to match strict instructions, 
                # or applying to both if "Initial prompt and area" implies the full pair.
                # Request says "replace the top box... initial prompt and data area". 
                # I will leave the second box (Ideal Output) as text for now to avoid over-engineering unless specified.
                st.text_area("Ideal Output [Target]", height=60, key="ape_output_target",
                           placeholder="Ideal target output...", label_visibility="collapsed")

            elif engine_id == "promptbreeder":
                # PromptBreeder: Prompt + Population
                st.text_area("Seed Prompt", height=80, key="pb_seed_prompt",
                           placeholder="Base prompt for evolutionary optimization...", label_visibility="collapsed")
                st.slider("Population Size", 10, 100, 50, 10, key="pb_population")
                st.caption("Evolutionary params managed by backend.")

            elif engine_id == "s2a":
                # S2A: Query + Raw Context
                st.text_area("Starting Query", height=60, key="s2a_query",
                           placeholder="User query to answer...", label_visibility="collapsed")
                st.text_area("Raw Context", height=100, key="s2a_context",
                           placeholder="Retrieved context chunks...", label_visibility="collapsed")

            # --- ACTION BUTTONS ---
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True) # Spacer
            col_start, col_stop = st.columns(2)
            with col_start:
                if st.button("START OPTIMIZATION", type="primary", use_container_width=True):
                    st.session_state["start_optimization"] = True
            with col_stop:
                if st.button("STOP", use_container_width=True):
                    st.session_state["stop_optimization"] = True
    
    # === CARD 2: GLASS BOX (Visualizer + Logic Readout) ===
    with col_glassbox:
        render_glassbox_card(engine_id)


def _render_tabbed_input(label: str, state_prefix: str, height: int = 100, placeholder: str = ""):
    """
    Renders a File Uploader + Tab Navigation combo.
    Text area is removed per requirements.
    Apps 'tabs' are radio buttons BELOW the uploader.
    """
    # 1. State Management
    tab_key = f"{state_prefix}_active_tab"
    if tab_key not in st.session_state:
        st.session_state[tab_key] = "Dataset 1"
    
    active_tab = st.session_state[tab_key]
    # Normalize tab name to index suffix (Set 1 -> 1)
    suffix = active_tab.split(" ")[1] 
    data_key = f"{state_prefix}_data_{suffix}"
    
    # Initialize data slot if missing
    if data_key not in st.session_state:
        st.session_state[data_key] = ""

    # 2. File Uploader (Top)
    # Label requested: "Drag and drop a set of test data here"
    # We maintain the unique key to reset on tab switch (standard Streamlit pattern)
    uploaded_file = st.file_uploader(
        "Drag and drop a set of test data here", 
        type=["txt", "md", "csv", "json"], 
        key=f"uploader_{state_prefix}_{suffix}", 
        label_visibility="visible"
    )
    
    if uploaded_file is not None:
        # Read and populate text area state
        string_data = uploaded_file.getvalue().decode("utf-8")
        st.session_state[data_key] = string_data
        
    # 3. Status Indicator (Since text area is gone)
    current_data = st.session_state[data_key]
    if current_data:
        # Show small confirmation so user knows this "Set" has data
        st.caption(f"✅ **{active_tab}**: Loaded {len(current_data)} chars.")
    else:
        st.caption(f"ℹ️ **{active_tab}**: Empty")

    # 4. Tabs & Management (Bottom - Inline Button Strip)
    # Layout: [Dataset 1]  [Dataset 2] [x]  [Dataset 3] [x]  [+]
    
    # helper for keys
    list_key = f"{state_prefix}_dataset_list"
    
    # Initialize list if missing
    if list_key not in st.session_state:
        st.session_state[list_key] = ["Dataset 1", "Dataset 2"]
    
    datasets = st.session_state[list_key]

    # Ensure active tab is valid
    if active_tab not in datasets:
        # Fallback to Dataset 1 if active was deleted
        active_tab = "Dataset 1"
        st.session_state[tab_key] = active_tab
        st.rerun()

    # --- DYNAMIC COLUMN GENERATION ---
    # Structure match: 
    # Dataset 1: [Button] (1 col)
    # Others:    [Button] [Sidecar X] (2 cols - tightly packed)
    # Final:     [+] (1 col)
    
    col_ratios = []
    
    for d_name in datasets:
        if d_name == "Dataset 1":
            col_ratios.append(1)
        else:
            col_ratios.append(1) # Main button
            col_ratios.append(0.25) # Sidecar X
    
    col_ratios.append(0.3) # For the [+] button
    
    cols = st.columns(col_ratios, gap="small")
    col_idx = 0
    
    # --- RENDER CONTROLS ---
    for d_name in datasets:
        # 1. Dataset Select Button
        is_active = (d_name == active_tab)
        btn_type = "primary" if is_active else "secondary"
        
        # Dataset 1
        if d_name == "Dataset 1":
            with cols[col_idx]:
                if st.button(d_name, key=f"sel_{state_prefix}_{d_name}", type=btn_type, help="Permanent Dataset", use_container_width=True):
                    st.session_state[tab_key] = d_name
                    st.rerun()
            col_idx += 1
            
        else:
            # Dataset N + Sidecar layout
            
            # Helper to determine correct CSS hook via tooltip
            select_help = f"Select {d_name}"
            
            # Main Select Button
            with cols[col_idx]:
                if st.button(d_name, key=f"sel_{state_prefix}_{d_name}", type=btn_type, help=select_help, use_container_width=True):
                    st.session_state[tab_key] = d_name
                    st.rerun()
            col_idx += 1
            
            # Sidecar X Button
            with cols[col_idx]:
                 # Use a distinct X character. 
                 if st.button("✕", key=f"del_{state_prefix}_{d_name}", help=f"Remove {d_name}"):
                    # Check for Data existence
                    suffix = d_name.split(" ")[1]
                    d_key = f"{state_prefix}_data_{suffix}"
                    if st.session_state.get(d_key, "").strip():
                         st.session_state[f"confirm_del_{state_prefix}"] = d_name
                    else:
                         _delete_dataset(state_prefix, d_name)
                         st.rerun()
            col_idx += 1

    # 3. Add Button (Last Column)
    with cols[col_idx]:
        if st.button("＋", key=f"add_{state_prefix}", help="Add new dataset"):
            new_idx = len(datasets) + 1
            while f"Dataset {new_idx}" in datasets:
                new_idx += 1
            datasets.append(f"Dataset {new_idx}")
            st.rerun()

    # --- CONFIRMATION DIALOG ---
    pending_del = st.session_state.get(f"confirm_del_{state_prefix}", None)
    if pending_del:
        st.warning(f"'{pending_del}' contains data. Delete anyway?")
        col_yes, col_no = st.columns([0.2, 0.8])
        if col_yes.button("Yes, Drop it", key=f"yes_del_{state_prefix}"):
            _delete_dataset(state_prefix, pending_del)
            st.session_state[f"confirm_del_{state_prefix}"] = None
            st.rerun()
        if col_no.button("Cancel", key=f"no_del_{state_prefix}"):
            st.session_state[f"confirm_del_{state_prefix}"] = None
            st.rerun()

def _delete_dataset(state_prefix, tab_name):
    """Helper to remove dataset from list and clear its data."""
    list_key = f"{state_prefix}_dataset_list"
    datasets = st.session_state[list_key]
    
    if tab_name in datasets:
        datasets.remove(tab_name)
    
    # Clear the data
    suffix = tab_name.split(" ")[1]
    data_key = f"{state_prefix}_data_{suffix}"
    if data_key in st.session_state:
        del st.session_state[data_key]
    
    # Reset specific keys if needed
    # (Streamlit widgets might hold onto state if key matches, but we usually rely on binding)

def _update_state(target_key, source_widget_key):
    """Callback to sync text widget back to main state variable"""
    st.session_state[target_key] = st.session_state[source_widget_key]

def render_glassbox_card(engine_id: str):
    with st.container(border=True):
        # Header - Full Width, No Checkbox
        st.markdown('<div class="card-header">GLASS BOX</div>', unsafe_allow_html=True)

        col_schematic, col_log = st.columns([2, 1.2])
        
        # 1. GRAPHVIZ SCHEMATIC
        with col_schematic:
            visualizer = GraphVisualizer()
            
            # Determine active node based on backend state (mocked for now if idle)
            active_node = st.session_state.get("active_node_id", "START" if engine_id in ["opro", "ape"] else "POOL")
            
            # Check for idle state override
            status = st.session_state.get("optimizer_status", "idle")
            if status == "idle":
                active_node = None 

            # Generate DOT
            try:
                dot_source = visualizer.get_engine_chart(engine_id, active_node)
                st.graphviz_chart(dot_source, use_container_width=True)
            except Exception as e:
                st.error(f"Viz Error: {e}")

        # 2. READOUT PANEL (Logic Inspection)
        with col_log:
            # Content depends on active node
            node_content = _get_readout_content(engine_id, active_node)
            
            st.markdown("**System Logic / Prompt**")
            st.code(node_content, language="text", line_numbers=False)
            
            # Status Footer
            st.markdown(f"<div style='margin-top:5px; font-size:11px; font-weight:500; color:#666;'>STATUS: <span style='color:#0D7CB1'>{status.upper()}</span></div>", unsafe_allow_html=True)


def _get_readout_content(engine: str, node: Optional[str]) -> str:
    """Helper to return mock system prompts for the alpha rollout."""
    if not node:
        return "[System Idle]\nSelect 'START' to begin optimization."
        
    prompts = {
        "opro": {
            "START": "USER: Optimize this prompt.\nSYSTEM: Generating variations...",
            "TEST": "Running test cases...\nEvaluating exact match...",
            "RATE": "Scoring Output: 85/100\nReasoning: Good clarity.",
            "CHANGE": "Applying meta-prompt:\n'Make it more professional.'"
        },
        "s2a": {
            "READ": "Ingesting 4k token context...",
            "FILTER": "Removing irrelevant sentences...\n(Noise Ratio: 40%)",
            "REFINE": "Rewriting context for clarity...",
            "ANSWER": "Generating final answer using refined context."
        }
    }
    
    # Fallback generic text
    engine_data = prompts.get(engine, {})
    return engine_data.get(node, f"Processing {node} state...\nExecuting internal logic.")
