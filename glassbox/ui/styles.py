import streamlit as st

def inject_custom_css():
    """
    Injects Boeing CSS with comprehensive styling.
    Supports Light/Dark mode via session state.
    """
    is_dark = st.session_state.get("dark_mode", False)
    
    # Define theme colors
    bg_color = "#0E1117" if is_dark else "#FDFDFE"
    text_color = "#FAFAFA" if is_dark else "#394957"
    card_bg = "#161b22" if is_dark else "#FFFFFF"
    card_border = "#30363d" if is_dark else "#D0D0D0"
    
    # === 1. DYNAMIC CSS (F-String) ===
    # Must use double braces {{ }} for CSS to escape f-string formatting
    st.markdown(f"""
        <style>
        :root {{
            /* Dynamic Colors */
            --white: {bg_color};
            --text-color: {text_color};
            --card-bg: {card_bg};
            --card-border-color: {card_border};
        }}
        </style>
    """, unsafe_allow_html=True)

    # === 2. STATIC CSS (Normal String) ===
    # Single braces { } are fine here
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        
        :root {
            --boeing-blue: #1A409F;
            --selected-blue: #0D7CB1;
            --slate-gray: #394957;
            --text-white: #FFFFFF;
            
            --sidebar-width: 220px;
            --topbar-height: 60px;
            --transition-fast: 0.1s ease;
            --card-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }

        html, body, .stApp {
            background-color: var(--white) !important;
            color: var(--text-color) !important;
            font-family: 'Helvetica Neue', Arial, sans-serif !important;
            font-family: 'Helvetica Neue', Arial, sans-serif !important;
            overflow-x: hidden;
        }
        
        /* Hide scrollbar for Chrome, Safari and Opera */
        ::-webkit-scrollbar {
            width: 0px;
            background: transparent;
        }

        /* ========================================
           2. GLOBAL FIXED TOP BAR
           ======================================== */
        #boeing-top-bar {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: var(--topbar-height);
            background: linear-gradient(180deg, var(--boeing-blue) 0%, #153580 100%);
            box-shadow: 0 4px 12px rgba(0,0,0,0.25);
            z-index: 999999;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 20px;
            font-family: 'Helvetica Neue', sans-serif;
            color: white;
        }

        #boeing-top-bar .top-bar-title {
            font-size: 16px;
            font-weight: 400;
            letter-spacing: 1px;
            white-space: nowrap;
        }

        #boeing-top-bar .top-bar-logo {
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            height: 32px;
        }

        .block-container {
            padding-top: 64px !important;
            padding-bottom: 20px !important;
            max-width: 100% !important;
        }

        /* Top Bar Gear Icon */
        #top-bar-gear {
            background: transparent !important;
            border: none !important;
            cursor: pointer !important;
            padding: 8px !important;
            border-radius: 50% !important;
            display: flex !important;
            align-items: center !important;
            justify_content: center !important;
            transition: background 0.2s ease !important;
        }
        #top-bar-gear:hover {
            background-color: rgba(255,255,255,0.1) !important;
        }

        /* ========================================
           3. SIDEBAR - FIXED, NO FLASH
           ======================================== */
        section[data-testid="stSidebar"] {
            background-color: var(--slate-gray) !important;
            border-right: none;
            z-index: 999990;
            width: var(--sidebar-width) !important;
            min-width: var(--sidebar-width) !important;
            max-width: var(--sidebar-width) !important;
            padding-top: var(--topbar-height) !important;
            margin-top: 0 !important;
            /* Prevent flash by ensuring bg is always set */
            transition: none !important;
        }
        
        /* Ensure all sidebar children have gray background to prevent flash */
        section[data-testid="stSidebar"] * {
            background-color: inherit;
        }
        
        section[data-testid="stSidebar"] > div:first-child,
        section[data-testid="stSidebar"] > div:first-child > div:first-child,
        section[data-testid="stSidebar"] > div:first-child > div:first-child > div {
            padding: 0 !important;
            margin: 0 !important;
            background-color: var(--slate-gray) !important;
        }
        
        section[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
        section[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
            padding: 0 !important;
            margin: 0 !important;
            gap: 0 !important;
            background-color: var(--slate-gray) !important;
        }
        
        /* HIDE ALL COLLAPSE/RESIZE CONTROLS */
        section[data-testid="stSidebar"] > div:first-child > button,
        button[data-testid="baseButton-headerNoPadding"],
        [data-testid="stSidebarCollapseButton"],
        section[data-testid="stSidebar"] [data-testid="stSidebarCollapsedControl"],
        div[data-testid="collapsedControl"] {
            display: none !important;
        }

        section[data-testid="stSidebar"] p, 
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] span {
            color: var(--text-white) !important;
        }

        /* ========================================
           4. CARD BOXES WITH OUTLINES & FLUSH HEADERS
           ======================================== */
        /* Reduce Gap between vertical blocks */
        [data-testid="stVerticalBlock"] {
            gap: 1rem !important;
        }

        /* 
           Target the Border Wrapper (st.container(border=True))
           We ensure it has a visible border and standard padding.
        */
        /* 
           Target the Border Wrapper (st.container(border=True))
           We ensure it has a visible border and standard padding.
        */
        /* 
           Target the Border Wrapper (st.container(border=True))
           We ensure it has a visible border and standard padding.
        */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            /* 
               NUCLEAR OPTION FOR BORDERS:
               Use a pseudo-element overlay with high z-index to draw the border 
               ON TOP of all content. This bypasses any internal clipping or stacking.
            */
            position: relative !important;
            background-color: var(--card-bg) !important;
            padding: 1rem !important;
            border-radius: 8px !important;
            border: none !important; /* Disable native border */
            box-shadow: var(--card-shadow) !important;
            overflow: visible !important; /* Allow overlay to sit cleanly */
        }

        div[data-testid="stVerticalBlockBorderWrapper"]::after {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 8px;
            border: 2px solid #555555 !important; /* Visible Gray */
            z-index: 999; /* Sit on top of everything inside the card */
            pointer-events: none; /* Let clicks pass through to content */
        }

        /* 
           Flush Header Trick:
           Use negative margins matching the container padding 
           to pull the header to the edges.
        */
        .card-header {
            background: var(--slate-gray);
            color: var(--text-white);
            padding: 10px 16px;
            font-weight: 500;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-radius: 6px 6px 0 0; /* Top corners match container */
            
            /* Negative margin to counteract container padding (1rem = ~16px) */
            margin-top: -1rem;
            margin-left: -1rem;
            margin-right: -1rem;
            margin-bottom: 1rem;
            
            /* Ensure it sits on top */
            position: relative;
            z-index: 1;
        }
        
        /* ========================================
           6. BUTTONS
           ======================================== */
        /* Default Button (Secondary) - Gray */
        .stButton > button {
            background-color: var(--slate-gray) !important;
            color: white !important;
            border-radius: 4px !important; 
            border: none !important;
            font-weight: 500 !important;
            text-transform: uppercase;
            font-size: 12px;
            transition: all var(--transition-fast);
        }
        
        /* Primary Button - Boeing Blue */
        /* Use specificity hack if needed, but [kind='primary'] is standard st */
        .stButton > button[kind="primary"] {
            background-color: var(--boeing-blue) !important;
            border: 1px solid var(--boeing-blue) !important;
            color: white !important;
        }
        
        .stButton > button:hover {
            background-color: var(--selected-blue) !important;
            border-color: var(--selected-blue) !important;
        }
        
        .stButton > button[kind="primary"]:hover {
            background-color: #153580 !important; /* Darker blue */
        }

        /* ========================================
           10. DATASET CONTROL STYLING (Corner Badge)
           ======================================== */
        
        /* 10.1 "Add" Button (Plus) - LAST COLUMN */

        
        /* 10.1 "Add" Button (Plus) - Targeted via Streamlit Key Class */
        /* Iter 16 SWAP: Revert to Standard Gray (Solid) */
        /* Targets any key starting with 'add_' (e.g. st-key-add_opro, st-key-add_ape) */

        
        /* 10.1.b "STOP OPTIMIZATION" Button (Iter 16: Ghost Style) */
        /* Targeted via explicit key: st-key-stop_opt_btn */
        .st-key-stop_opt_btn button {
            background-color: #FFFFFF !important;
            color: var(--boeing-blue) !important;
            border: 1px solid var(--boeing-blue) !important;
            border-radius: 4px !important;
            opacity: 0.5 !important;
            transition: all var(--transition-fast) !important;
        }

        .st-key-stop_opt_btn button:hover {
             background-color: var(--boeing-blue) !important;
             color: white !important;
             opacity: 1.0 !important;
        }

        /* 10.2 Standard Dataset Buttons */
        /* Dataset 1 (First Column) and Subsequent */
        div[data-testid="stColumn"] .stButton button {
            /* Layout Structure */
            border-radius: 20px !important;
            padding: 2px 15px !important;
            width: 100% !important; 
            min-width: 0 !important;
            min-height: 0px !important; 
            height: auto !important;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            
            /* Default Colors (Unselected/Secondary) */
            background-color: #FFFFFF !important;
            color: #555555 !important;
            border: 1px solid var(--boeing-blue) !important;
        }

        /* 10.2.1 ACTIVE State (Primary) - Force Blue */
        /* Must match specific columns to override the rule above */
        div[data-testid="stColumn"] .stButton button[kind="primary"] {
            background-color: var(--boeing-blue) !important;
            color: white !important;
            border-color: var(--boeing-blue) !important;
        }

        /* 10.3 "Floating Icon" BADGE (Iter 10 - Alignment Fix) */
        
        /* FORCE OVERFLOW VISIBLE on all layout containers */
        div[data-testid="stColumn"], 
        div[data-testid="stVerticalBlock"],
        div[data-testid="stHorizontalBlock"] {
            overflow: visible !important;
        }

        /* 1. WRAPPER CONTROL: Fix Vertical Alignment Issue (Raised Buttons) */
        /* The 2nd element (Badge Wrapper) was taking up space/flow. We crush it. */
        /* 1. WRAPPER CONTROL: Fix Vertical Alignment Issue (Raised Buttons) */
        /* 1. WRAPPER CONTROL: Fix Vertical Alignment Issue (Raised Buttons) */
        /* CRITICAL FIX (Iter 14): Anchor the Parent Block so Absolute Position works! */
        /* Otherwise top:0 goes to the page root (Header). */
        div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"]:has([data-type="dataset-column-marker"]) {
            position: relative !important;
            overflow: visible !important;
        }

        /* Target the Badge Wrapper (3rd element) inside the anchored block */
        div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"]:has([data-type="dataset-column-marker"]) > div:nth-of-type(3) {
             position: absolute !important;
             top: 0 !important;
             left: 0 !important;
             width: 0 !important;
             height: 0 !important;
             margin: 0 !important;
             padding: 0 !important;
             overflow: visible !important;
             z-index: 1000000 !important;
        }

        /* 2. BADGE BUTTON STYLING */
        /* Target the button inside the 3rd div */
        div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"]:has([data-type="dataset-column-marker"]) > div:nth-of-type(3) button {
            /* RESET STYLES */
            border: 1px solid #E0E0E0 !important;
            padding: 0 !important;
            margin: 0 !important;
            min-height: 0 !important;
            
            /* SHAPE & SIZE */
            width: 20px !important;
            height: 20px !important;
            min-width: 20px !important;
            border-radius: 50% !important;
            
            /* VISUALS */
            background-color: #FFFFFF !important;
            color: #666 !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.15) !important;
            
            /* TYPOGRAPHY */
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-size: 10px !important;
            line-height: 1 !important;
            
            /* POSITIONING relative to the Absolute Wrapper (Top-Left of Column) */
            position: absolute !important;
            
            /* Position: Right-Anchored (Fix for Zoom/Resize Adhesion) */
            right: 5px !important;
            left: auto !important;

            /* Vertical: Center optically (approx 12px from top) */
            top: 12px !important; 

            
            z-index: 1000001 !important; /* Higher than wrapper */
            pointer-events: auto !important;
        }
        
        /* HOVER STATE */
        div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"]:has([data-type="dataset-column-marker"]) > div:nth-of-type(3) button:hover {
             border-color: #FF4B4B !important;
             color: #FF4B4B !important;
             background-color: #FFFFFF !important;
             box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
             transform: scale(1.1);
        }
        
        /* ACTIVE/FOCUS STATE */
        div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"]:has([data-type="dataset-column-marker"]) > div:nth-of-type(3) button:focus:not(:active) {
            border-color: #E0E0E0 !important;
            color: #666 !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.15) !important;
        }
        
        /* CONTAINER OVERFLOW FIX */
        /* Ensure columns allow the badge to stick out */
        div[data-testid="column"] {
            overflow: visible !important;
        }
        div[data-testid="stVerticalBlock"] {
             overflow: visible !important;
        }




        /* ========================================
           7. TEXT INPUTS
           ======================================== */
        /* Standard Input Styling */
        .stTextInput > div > div > input, 
        .stTextArea > div > div > textarea, 
        .stSelectbox > div > div > div {
            background-color: #FFFFFF !important; 
            color: #333333 !important;
            border: 1px solid #CCC !important;
            border-radius: 4px !important;
        }

        /* FORCE VISIBLE PLACEHOLDERS */
        /* Webkit/Blink */
        .stTextInput input::-webkit-input-placeholder,
        .stTextArea textarea::-webkit-input-placeholder {
            color: #555555 !important;
            opacity: 1 !important;
            font-weight: 500;
        }
        /* Mozilla */
        .stTextInput input::-moz-placeholder,
        .stTextArea textarea::-moz-placeholder {
            color: #555555 !important;
            opacity: 1 !important;
            font-weight: 500;
        }
        /* Default */
        .stTextInput input::placeholder,
        .stTextArea textarea::placeholder {
            color: #555555 !important;
            opacity: 1 !important;
            font-weight: 500;
        }
        
        /* Dark mode overrides for inputs would be handled by var(--card-bg) if we wanted dynamic, 
           but user asked for 'the gray we are using', implying specific look. 
           We'll stick to a safe light-gray for now, or use a variable if defined. */

        /* ========================================
           8. RADIO BUTTONS (Custom Blue)
           ======================================== */
        /* Target the radio circle when selected */
        div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child {
            background-color: transparent !important; /* Outer ring default */
            border-color: #999 !important;
        }

        /* Checked State - The inner dot or fill */
        div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child[aria-checked="true"] {
            background-color: var(--selected-blue) !important;
            border-color: var(--selected-blue) !important;
        }
        
        /* If Streamlit uses a nested div for the fill */
        div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child[aria-checked="true"] > div {
             background-color: white !important;
        }

        /* ========================================
           9. SETTINGS POPOVER POSITIONING
           ======================================== */
        .settings-popover-container {
            position: fixed !important;
            top: 70px !important;
            right: 20px !important;
            left: auto !important;
            z-index: 999998 !important;
            width: auto !important;
        }
        
        .settings-popover-container > div {
            position: static !important;
        }
        
        .settings-popover-container button[data-testid="stPopoverButton"] {
            background: transparent !important;
            border: none !important;
            padding: 5px !important;
            font-size: 18px !important;
        }

        /* ========================================
           10. DRAG AND DROP FIX (Darker Gray)
           ======================================== */
        section[data-testid="stFileUploaderDropzone"] {
            background-color: var(--slate-gray) !important;
            border: 1px dashed #555 !important;
            color: white !important;
        }
        div[data-testid="stFileUploader"] section {
            background-color: var(--slate-gray) !important;
            border: 1px dashed #555 !important;
            color: white !important;
        }
        
        /* 10.1 "Browse files" Button */
        section[data-testid="stFileUploaderDropzone"] button,
        div[data-testid="stFileUploader"] section button {
             background-color: #2B3843 !important; /* Slightly darker than slate-gray */
             color: white !important;
             border: 1px solid #555 !important;
        }
        
        /* Fix text color inside dropzone */
        section[data-testid="stFileUploaderDropzone"] *, 
        div[data-testid="stFileUploader"] section * {
             color: white !important;
        }

        /* ========================================
           9. HIDE STREAMLIT CHROME
           ======================================== */
        header[data-testid="stHeader"] { display: none; }
        footer { display: none; }
        div[data-testid="stToolbar"] { display: none !important; }

        /* ------------------------------------------------------------- */
        /* ITER 19: MULTI-FILE LIST STYLING                              */
        /* ------------------------------------------------------------- */
        
        /* 1. HIDE Native Streamlit File List */
        div[data-testid="stFileUploader"] ul[data-testid="stUploadedFileList"] {
             display: none !important;
        }
        
        /* 2. Custom File List Container (The "Preset Area") */
        /* Border, BG, Radius */
        div[data-testid="stVerticalBlockBorderWrapper"] {
             border: 1px solid #E0E0E0 !important;
             background-color: #F8F9FA !important; 
             border-radius: 4px !important;
        }

        /* 3. Items inside the list */
        div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stText"],
        div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stMarkdown"] p {
             font-size: 13px !important;
             color: #333333 !important; /* Force Dark Gray */
             padding: 4px 0px !important;
             white-space: nowrap !important;
             overflow: hidden !important;
             text-overflow: ellipsis !important;
        }
        
        /* Remove Button (X) */
        div[class*="st-key-rm_file_"] button {
             border: none !important;
             background: transparent !important;
             color: #999 !important;
             padding: 0px !important;
             width: 20px !important;
             height: 20px !important;
             min-height: 0 !important;
             line-height: 1 !important;
        }
        div[class*="st-key-rm_file_"] button:hover {
             color: #FF4B4B !important;
             background: rgba(255, 75, 75, 0.1) !important;
             border-radius: 50% !important;
        }
        
        /* 4. Custom Scrollbar */
        div[data-testid="stVerticalBlockBorderWrapper"] ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] ::-webkit-scrollbar-track {
            background: transparent; 
        }
        div[data-testid="stVerticalBlockBorderWrapper"] ::-webkit-scrollbar-thumb {
            background-color: #CCC; 
            border-radius: 3px;
        }

        /* ------------------------------------------------------------- */
        /* ITER 18: PLUS BUTTON FINE-TUNING (Tiny, Shifted, Opaque)      */
        /* ------------------------------------------------------------- */
        div[data-testid="stColumn"] div[class*="st-key-add_"] button {
             /* 1. Style: Ghost Blue (White BG, Blue Borders) */
             background-color: #FFFFFF !important;
             color: var(--boeing-blue) !important;
             border: 1px solid var(--boeing-blue) !important;
             opacity: 0.7 !important; /* Increased from 0.5 */
             
             /* 2. Size: Reduced to ~60% of previous 24px -> ~15px */
             height: 15px !important;       
             min-height: 15px !important;
             line-height: 1 !important;
             padding: 0px !important;       /* Remove padding to fit icon */
             width: auto !important; 
             min-width: 24px !important;    /* Proportional width reduction */
             font-size: 12px !important;    
             
             /* 3. Position: Shift Down & Right */
             /* Down ~15px (35% of dataset btn). Right ~65px (50 + 15) */
             margin-top: 15px !important;
             margin-left: 65px !important;  
             border-radius: 4px !important;
             
             /* Flex alignment check */
             align-self: flex-start !important; 
        }

        div[data-testid="stColumn"] div[class*="st-key-add_"] button:hover {
             /* Hover: Solid Blue, Full Opacity */
             background-color: var(--boeing-blue) !important; 
             color: white !important;
             border-color: var(--boeing-blue) !important;
             opacity: 1.0 !important;
        }
        
        /* Specific fix to prevent horizontal scroll if shift pushes too far? */
        /* Checking... */

        /* ITER 20 FIX (RETRY 2): Robust Scroll via Marker */
        /* We use the injected marker class to safely target the container */
        div[data-testid="stVerticalBlock"]:has(.file-list-scrollbar-marker) {
             height: 100% !important;
             max-height: 100% !important; /* Ensure it respects parent height */
             overflow-y: auto !important;
             overflow-x: hidden !important;
             display: flex !important;
             flex-direction: column !important;
             /* Iter 22: Polish Whitespace (User Req: 3px) */
             padding-top: 3px !important;
             gap: 3px !important;
        }

        /* ITER 23 FIX: GlassBox Height Match (384px) */
        /* Target both wrapper and inner block to be safe */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.glassbox-height-marker),
        div[data-testid="stVerticalBlock"]:has(.glassbox-height-marker) {
             min-height: 400px !important;
             display: flex !important;
             flex-direction: column !important;
        }

        /* ITER 23 REVISION: Fix Header Cutoff (Overflow Visible) */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.zone-a-left-marker),
        div[data-testid="stVerticalBlock"]:has(.zone-a-left-marker) {
             overflow: visible !important;
             padding-top: 8px !important;
        }







        /* ITER 29: EXPLICIT HEADER FIX & MUTED SELECTION */
        
        /* HEADER OVERRIDE: Explicitly target Zone C Headers */
        /* Must have higher specificity/correct scope to win over generic defaults */
        div[data-testid="stColumn"]:has(.zone-c-header) button {
             background-color: #31333F !important; /* Standard Dark Button BG */
             color: white !important;
             border: 1px solid rgba(250, 250, 250, 0.2) !important;
             border-radius: 4px !important; /* Rectangle, slight radius */
             text-align: center !important;
             box-shadow: 0 1px 2px rgba(0,0,0,0.1) !important;
        }
        div[data-testid="stColumn"]:has(.zone-c-header) button:hover {
             border-color: #FF4B4B !important; /* Streamlit Primary Hover */
             color: #FF4B4B !important;
        }

        /* DATA ROWS: Base Ghost Style */
        /* Note: We exclude .zone-c-header to be safe, though usage in python handles it */
        div[data-testid="stColumn"]:has(.ghost-col-marker) button,
        div[data-testid="stColumn"]:has(.ghost-marker-primary) button,
        div[data-testid="stColumn"]:has(.ghost-marker-secondary) button {
            border: none !important;
            border-bottom: 2px solid #555 !important;
            border-radius: 0 !important;
            font-weight: 400 !important;
            text-align: left !important;
            justify-content: flex-start !important;
            padding-left: 8px !important;
            transition: all 0.15s ease !important;
            box-shadow: none !important;
        }

        /* 1. DEFAULT STATE (Transparent) */
        div[data-testid="stColumn"]:has(.ghost-col-marker) button {
            background-color: transparent !important;
            color: #31333F !important;
        }
        div[data-testid="stColumn"]:has(.ghost-col-marker) button:hover {
            background-color: rgba(0,0,0,0.05) !important;
            color: #000 !important;
        }

        /* 2. PRIMARY SELECTION (Boeing Blue - matches Hover) */
        /* BUG-026 FIX: Add exact same exclusion logic as hover to prevent parent matching */
        div[data-testid="stColumn"]:not(:has(div[data-testid="stColumn"])):has(.ghost-marker-primary) button {
            background-color: var(--boeing-blue) !important;
            color: white !important;
            border-bottom-color: #000000 !important;
            opacity: 1 !important;
        }
        div[data-testid="stColumn"]:not(:has(div[data-testid="stColumn"])):has(.ghost-marker-primary) button:hover {
             /* Maintain state on hover */
             background-color: var(--boeing-blue) !important;
             color: white !important;
        }

        /* 3. SECONDARY SELECTION (Lighter Blue - Previous Selection) */
        /* BUG-026 FIX: applied here too */
        div[data-testid="stColumn"]:not(:has(div[data-testid="stColumn"])):has(.ghost-marker-secondary) button {
            background-color: rgba(26, 64, 159, 0.4) !important; /* Lighter Boeing Blue */
            color: white !important; /* Keep text white for readability */
            border-bottom-color: #000000 !important;
            opacity: 1 !important;
        }
        div[data-testid="stColumn"]:not(:has(div[data-testid="stColumn"])):has(.ghost-marker-secondary) button:hover {
             /* On hover, bump to full Boeing Blue to show interactivity */
             background-color: var(--boeing-blue) !important;
        }

        /* ========================================
           11. ZONE C - LINKED ROW HOVER (BUG-025 FIX REFINED)
           ======================================== */
        /* 
           Selector Strategy:
           1. Target stHorizontalBlock that contains our markers (.ghost-col-marker, etc.).
           2. CRITICAL: Exclude any HorizontalBlock that CONTAINS another HorizontalBlock.
              This prevents the Outer Layout (Zone C Split) from matching, as it contains the Row blocks.
           3. Apply hover style to buttons inside.
        */
        div[data-testid="stHorizontalBlock"]:not(:has(div[data-testid="stHorizontalBlock"])):has(.ghost-col-marker):hover button,
        div[data-testid="stHorizontalBlock"]:not(:has(div[data-testid="stHorizontalBlock"])):has(.ghost-marker-primary):hover button,
        div[data-testid="stHorizontalBlock"]:not(:has(div[data-testid="stHorizontalBlock"])):has(.ghost-marker-secondary):hover button {
             background-color: var(--boeing-blue) !important;
             color: white !important;
             opacity: 1 !important;
             border-bottom-color: #000000 !important;
        }

        /* Force reset on individual button hover within that strictly scoped row */
        div[data-testid="stHorizontalBlock"]:not(:has(div[data-testid="stHorizontalBlock"])):has(.ghost-col-marker) button:hover,
        div[data-testid="stHorizontalBlock"]:not(:has(div[data-testid="stHorizontalBlock"])):has(.ghost-marker-primary) button:hover,
        div[data-testid="stHorizontalBlock"]:not(:has(div[data-testid="stHorizontalBlock"])):has(.ghost-marker-secondary) button:hover {
             background-color: var(--boeing-blue) !important;
             color: white !important;
             border-bottom-color: #000000 !important;
        }

        
        /* ========================================
           12. ZONE E - DIFF & INSPECTOR STYLES
           ======================================== */
        
        /* Diff Colors (Boeing Standard v0.0.7) */
        .diff-add {
            /* New Text: White on Dark Blue Highlight */
            background-color: #1A409F; 
            color: #FFFFFF;
            border-radius: 2px;
            padding: 0 2px; /* Slight padding for the block effect */
        }
        
        .diff-del {
            /* Deleted Text: Light Blue Text (No BG), Strikethrough */
            background-color: transparent; 
            text-decoration: line-through;
            color: #89CFF0; /* Light Sky Blue */
        }
        
        /* Zone E Left Rail Buttons */
        .zone-e-rail-btn button {
            text-align: left !important;
            justify-content: flex-start !important;
            border: none !important;
            border-left: 2px solid transparent !important; /* Marker */
            background: transparent !important;
            border-radius: 0 !important;
            color: #555 !important;
        }
        
        .zone-e-rail-btn button:hover {
            background-color: rgba(0,0,0,0.05) !important;
            color: #000 !important;
        }
        /* Active Rail Button */
        .zone-e-rail-btn-active button {
            background-color: rgba(26, 64, 159, 0.1) !important;
            color: var(--boeing-blue) !important;
            border-left: 3px solid var(--boeing-blue) !important;
            font-weight: 600 !important;
        }

        /* Logic for Zone C Row Styles is already set in Section 10/11 above. 
           We rely on .ghost-marker-primary (Dark Blue) and .ghost-marker-secondary.
           v0.0.6 Update: Secondary is now Solid Semi-Transparent Blue (No Halo Border).
        */
        
        div[data-testid="stColumn"]:not(:has(div[data-testid="stColumn"])):has(.ghost-marker-secondary) button {
             /* Solid Semi-Transparent Boeing Blue */
             background-color: rgba(26, 64, 159, 0.4) !important; 
             color: white !important; /* Keep white text */
             border: none !important;
             border-bottom: 2px solid #555 !important; /* Match default row border style */
             border-radius: 0 !important;
             box-shadow: none !important;
             opacity: 1 !important;
        }
        
        </style>
    """, unsafe_allow_html=True)
