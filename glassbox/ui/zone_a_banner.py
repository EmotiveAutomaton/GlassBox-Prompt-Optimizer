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
    """Render the top row with INPUT and GLASS BOX cards.
    
    v0.0.6: Unified Zone A with internal Blue/Yellow HTML wrapper boxes.
    Uses explicit HTML divs with inline borders (CSS sibling selectors fail in Streamlit).
    """
    
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
    
    # === CARD 1: INITIAL PROMPT AND DATA (Unified Zone A) ===
    with col_input:
        with st.container(border=True):
            # Unified Header (no engine ID per v0.0.6 spec)
            st.markdown('<div class="card-header">INITIAL PROMPT AND DATA</div>', unsafe_allow_html=True)
            
            # --- BOX 1: Initial Prompt (Blue Border) - Using HTML wrapper ---
            st.markdown('''
                <div style="border: 2px solid #1A409F; border-radius: 6px; padding: 12px; margin-bottom: 12px; background: rgba(26, 64, 159, 0.03);">
                    <span style="color: #1A409F; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Initial Prompt</span>
                </div>
            ''', unsafe_allow_html=True)
            # Dynamic content based on engine (inside separate container due to Streamlit limitation)
            if engine_id == "opro":
                st.text_area("Seed Prompt", height=80, key="opro_seed_prompt", 
                           placeholder="Initial prompt to be optimized...", label_visibility="collapsed")
            elif engine_id == "ape":
                st.text_area("Ideal Output", height=60, key="ape_output_target",
                           placeholder="Ideal target output...", label_visibility="collapsed")
            elif engine_id == "promptbreeder":
                st.text_area("Seed Prompt", height=80, key="pb_seed_prompt",
                           placeholder="Base prompt for evolutionary optimization...", label_visibility="collapsed")
                st.slider("Population Size", 10, 100, 50, 10, key="pb_population")
            elif engine_id == "s2a":
                st.text_area("Starting Query", height=60, key="s2a_query",
                           placeholder="User query to answer...", label_visibility="collapsed")
            
            # --- BOX 2: Data (Yellow Border) - Using HTML wrapper ---
            st.markdown('''
                <div style="border: 2px solid #F5A623; border-radius: 6px; padding: 12px; margin-bottom: 12px; background: rgba(245, 166, 35, 0.03);">
                    <span style="color: #F5A623; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Data</span>
                </div>
            ''', unsafe_allow_html=True)
            # Dynamic content based on engine
            if engine_id == "opro":
                _render_tabbed_input(
                    label="Test Data",
                    state_prefix="opro_test",
                    height=150,
                    placeholder="Enter or upload test cases (one per line)..."
                )
            elif engine_id == "ape":
                _render_tabbed_input(
                    label="Input Data (Examples)",
                    state_prefix="ape_input",
                    height=100,
                    placeholder="Upload or paste input examples for reverse engineering..."
                )
            elif engine_id == "s2a":
                st.text_area("Raw Context", height=100, key="s2a_context",
                           placeholder="Retrieved context chunks...", label_visibility="collapsed")
            else:
                st.caption("Data management varies by engine.")

            # --- ACTION BUTTONS (Bottom of Zone A) ---
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            col_start, col_stop = st.columns(2)
            
            def _cb_start():
                print("DEBUG: Start Callback Triggered")
                st.session_state["start_optimization"] = True
            
            def _cb_stop():
                print("DEBUG: Stop Callback Triggered")
                st.session_state["stop_optimization"] = True

            with col_start:
                st.button("START OPTIMIZATION", type="primary", use_container_width=True, 
                         key="start_opt_btn", on_click=_cb_start)
            
            with col_stop:
                st.button("STOP OPTIMIZATION", use_container_width=True, 
                         key="stop_opt_btn", on_click=_cb_stop)

            # Iter 23: Marker for CSS Overflow Fix
            st.markdown('<div class="zone-a-left-marker" style="display:none;"></div>', unsafe_allow_html=True)

    
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
    suffix = active_tab.split(" ")[1] 
    
    # Data Keys
    data_key = f"{state_prefix}_data_{suffix}"         # The actual string text
    files_key = f"{state_prefix}_file_list_{suffix}"   # List of filenames/metadata
    upl_key_base = f"uploader_{state_prefix}_{suffix}" # Base key for uploader
    ctr_key = f"{state_prefix}_upl_ctr_{suffix}"       # Counter to clear uploader

    # Initialize
    if data_key not in st.session_state: st.session_state[data_key] = ""
    if files_key not in st.session_state: st.session_state[files_key] = []
    if ctr_key not in st.session_state: st.session_state[ctr_key] = 0

    # 2. File Uploader ("Drop Zone")
    # We use a dynamic key to "clear" the input after processing (Accumulator Pattern)
    current_upl_key = f"{upl_key_base}_{st.session_state[ctr_key]}"
    
    uploaded_files = st.file_uploader(
        "Drag and drop a set of test data here", 
        type=["txt", "md", "csv", "json"], 
        key=current_upl_key,
        accept_multiple_files=True, # Iter 19: Allow multiple
        label_visibility="visible"
    )
    
    # Process New Uploads
    if uploaded_files:
        for uf in uploaded_files:
            # Check duplicates by name?
            existing_names = [f['name'] for f in st.session_state[files_key]]
            if uf.name not in existing_names:
                content = uf.getvalue().decode("utf-8")
                st.session_state[files_key].append({
                    "name": uf.name,
                    "size": uf.size,
                    "content": content
                })
        
        # Update concatenated text data
        all_text = "\n\n".join([f['content'] for f in st.session_state[files_key]])
        st.session_state[data_key] = all_text
        
        # Clear uploader by incrementing key
        st.session_state[ctr_key] += 1
        st.rerun()

    # 3. Custom File List (Vertical, Scrollable, Compact)
    # Replaces old caption. "Preset area... viewing three files... scroll"
    file_list = st.session_state[files_key]
    
    # 3. File List Area (Always Persistent)
    # Height 68px ~ 2 lines (User Request) to prevent overlap with buttons below
    with st.container(height=68):
        # MARKER: Injected for CSS targeting (Iter 20 Fix)
        # Must be present even if empty so CSS applies correctly
        st.markdown('<div class="file-list-scrollbar-marker" style="display:none;"></div>', unsafe_allow_html=True)
        
        file_list = st.session_state[files_key]
        if file_list:
            for i, f_info in enumerate(file_list):
                 # Layout: [Name (0.9)] [Remove (0.1)]
                 c_name, c_rem = st.columns([0.9, 0.1])
                 with c_name:
                     st.text(f_info['name']) 
                 with c_rem:
                     if st.button("✕", key=f"rm_file_{state_prefix}_{suffix}_{i}_{f_info['name']}"):
                         st.session_state[files_key].pop(i)
                         all_text = "\n\n".join([f['content'] for f in st.session_state[files_key]])
                         st.session_state[data_key] = all_text
                         st.rerun()
        else:
             # Empty state - just empty space as requested
             pass

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
    # [Button (~0.4)] [Badge (~0.01)] [Spacer (~0.6)]
    # This reduces the visual width of the buttons as requested.
    
    # Updated Ratios: One column per dataset (0.05) + Plus button (0.1)
    # This removes "dead space" caused by extra badge columns.
    col_ratios = []
    
    for d_name in datasets:
        # Fixed relative weight (approx 15% of screen) per button.
        # This keeps size constant as N increases (until overflow).
        col_ratios.append(0.15) 
    
    col_ratios.append(0.08) # Plus Button
    
    # Calculate remaining space for Spacer
    current_sum = sum(col_ratios)
    spacer = max(0.01, 1.0 - current_sum)
    col_ratios.append(spacer)

    # Vertical alignment 'center' ensures the "+" button aligns with the text pills
    cols = st.columns(col_ratios, gap="small", vertical_alignment="center")
    col_idx = 0
    
    # v0.0.17: Lock Controls when Running
    is_running = st.session_state.get("is_running", False)
    
    # --- RENDER CONTROLS ---
    for d_name in datasets:
        with cols[col_idx]:
            # 0. Marker for CSS Targeting (Iter 12)
            st.markdown('<div data-type="dataset-column-marker" style="display:none;"></div>', unsafe_allow_html=True)

            # 1. Main Dataset Button
            is_active = (d_name == active_tab)
            btn_type = "primary" if is_active else "secondary"
            tooltip = f"Select {d_name}" if d_name != "Dataset 1" else "Permanent Dataset"
            
            # Helper for CSS hook
            # If we render two buttons in one column, we rely on nth-child CSS
            
            if st.button(d_name, key=f"sel_{state_prefix}_{d_name}", type=btn_type, help=tooltip, use_container_width=True):
                 st.session_state[tab_key] = d_name
                 st.rerun()
            
            # 2. Render Badge (Re-enabled for Iter 9 "Floating Icon")
            if d_name != "Dataset 1":
                # v0.0.17: Disable X button if running
                if st.button("✕", key=f"del_{state_prefix}_{d_name}", help=f"Remove {d_name}", disabled=is_running):
                    # Check for data existence
                    suffix = d_name.split(" ")[1]
                    d_key = f"{state_prefix}_data_{suffix}"
                    # Simple check - if data exists in memory
                    if st.session_state.get(d_key, ""):
                         confirm_delete_dialog(state_prefix, d_name, tab_key)
                    else:
                         _delete_dataset(state_prefix, d_name)
                         # If we deleted the active tab, switch to D1
                         if active_tab == d_name:
                             st.session_state[tab_key] = "Dataset 1"
                         st.rerun()

        col_idx += 1
            
    # 3. Add Button (Last Column)
    with cols[col_idx]:
         # v0.0.17: Disable Add button if running
         if st.button("＋", key=f"add_{state_prefix}", help="Add new dataset", disabled=is_running):
             new_idx = len(datasets) + 1
             # Find next available index
             while f"Dataset {new_idx}" in datasets:
                 new_idx += 1
             datasets.append(f"Dataset {new_idx}")
             # Auto-select new
             st.session_state[tab_key] = f"Dataset {new_idx}"
             st.rerun()

@st.dialog("Confirm Deletion")
def confirm_delete_dialog(state_prefix: str, d_name: str, tab_key: str):
    st.warning(f"Are you sure you want to delete '{d_name}'?")
    st.caption("This action cannot be undone and will remove all associated test data.")
    
    col_yes, col_no = st.columns([1, 1])
    if col_yes.button("Delete", type="primary", use_container_width=True):
        _delete_dataset(state_prefix, d_name)
        # Handle tab switch if we deleted the active one
        if st.session_state.get(tab_key) == d_name:
             st.session_state[tab_key] = "Dataset 1"
        st.rerun()
        
    if col_no.button("Cancel", use_container_width=True):
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
        st.session_state[data_key] = "" # v0.0.18: Explicitly clear content logic
        del st.session_state[data_key]  # Then remove key
        
    # v0.0.18: Also clean up related file lists so they don't zombie back
    files_key = f"{state_prefix}_file_list_{suffix}"
    if files_key in st.session_state:
        st.session_state[files_key] = []
        del st.session_state[files_key]
    
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
            cycle_count = st.session_state.get("cycle_count", 0)

            # --- MOCK CYCLE LOGIC FOR ALPHA DEMO ---
            if status == "running":
                # Auto-increment cycle for demo purposes if not handled by backend
                import time
                # Simple throttle to prevent rapid spinning
                cycle_count = st.session_state.get("cycle_count", 0)
                if cycle_count == 0:
                     st.session_state["cycle_count"] = 1
                     st.rerun() # Force refresh to show change immediately
            elif status == "idle":
                active_node = None 
                cycle_count = 0 # Force 0 if idle/stopped
            # ---------------------------------------
            
            # v0.0.6: Detect user input for animation trigger
            has_user_input = bool(st.session_state.get("opro_seed_prompt", "").strip())

            # Generate DOT
            try:
                dot_source = visualizer.get_engine_chart(engine_id, active_node, cycle_count, has_user_input)
                st.graphviz_chart(dot_source, use_container_width=True)
            except Exception as e:
                st.error(f"Viz Error: {e}")

        # 2. READOUT PANEL - Split View (v0.0.6 spec 8.3)
        with col_log:
            # Get content for both panels based on active node
            input_content, output_content = _get_split_readout_content(engine_id, active_node)
            
            # --- TOP: System Logic / Input ---
            st.markdown('''
                <div style="border-left: 3px solid #1A409F; padding-left: 8px; margin-bottom: 10px;">
                    <span style="color: #1A409F; font-size: 10px; font-weight: 600; text-transform: uppercase;">System Logic / Input</span>
                </div>
            ''', unsafe_allow_html=True)
            st.code(input_content, language="text", line_numbers=False)
            
            # --- BOTTOM: Result / Output ---
            st.markdown('''
                <div style="border-left: 3px solid #22c55e; padding-left: 8px; margin-bottom: 10px;">
                    <span style="color: #22c55e; font-size: 10px; font-weight: 600; text-transform: uppercase;">Result / Output</span>
                </div>
            ''', unsafe_allow_html=True)
            st.code(output_content, language="text", line_numbers=False)
            
            # Status Footer
            st.markdown(f"<div style='margin-top:5px; font-size:11px; font-weight:500; color:#666;'>STATUS: <span style='color:#0D7CB1'>{status.upper()}</span></div>", unsafe_allow_html=True)

        # Iter 23: Bottom Marker for CSS Height (Min Height)
        st.markdown('<div class="glassbox-height-marker" style="display:none;"></div>', unsafe_allow_html=True)


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


def _get_split_readout_content(engine: str, node: Optional[str]) -> tuple:
    """
    v0.0.6: Returns (input_content, output_content) for split panel view.
    Top panel shows system logic/input, bottom shows result/output.
    """
    if not node:
        return (
            "[System Idle]\nAwaiting optimization start...",
            "[No Output Yet]\nResults will appear here."
        )
    
    split_content = {
        "opro": {
            "START": (
                "Meta-Prompt:\n\"Optimize the following prompt for clarity.\"",
                "[Generating Variations...]\nCandidate 1: Pending"
            ),
            "TEST": (
                "Test Cases:\n- Input: 'Boeing 777'\n- Expected: Summary",
                "Running Evaluation...\nTest 1: PASS\nTest 2: PENDING"
            ),
            "RATE": (
                "Scoring Criteria:\n- Clarity (40%)\n- Accuracy (60%)",
                "Score: 87/100\nReasoning: Good precision, minor verbosity."
            ),
            "CHANGE": (
                "Mutation Operator:\n\"Make response more concise.\"",
                "New Candidate Generated:\n[Revised Prompt V2]"
            )
        },
        "ape": {
            "START": (
                "Input Examples Loaded:\n3 Input/Output pairs",
                "[Reverse Engineering...]\nAnalyzing patterns..."
            ),
            "TEST": (
                "Validation Set: 5 samples",
                "Match Rate: 80%"
            ),
            "RATE": (
                "Evaluation Metrics: BLEU, Exact Match",
                "BLEU: 0.72 | Exact: 4/5"
            ),
            "CHANGE": (
                "Resampling Strategy: Top-K",
                "New Instruction Candidate Generated"
            )
        }
    }
    
    engine_data = split_content.get(engine, {})
    return engine_data.get(node, (
        f"Processing {node}...\nExecuting logic.",
        f"[{node} Output]\nPending result..."
    ))

