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
            
            /* Move RIGHT (Dialed in Iter 15: 120px - 15px = 105px) */
            left: 105px !important; 
            
            /* Vertical: (Dialed in Iter 15: -10px + 22px = 12px) */
            /* Lowered by half-height of button */
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
        /* ITER 17: PLUS BUTTON REFINEMENT (Ghost, Small, Shifted)       */
        /* ------------------------------------------------------------- */
        div[data-testid="stColumn"] div[class*="st-key-add_"] button {
             /* 1. Style: Ghost Blue (White BG, Blue Borders) */
             background-color: #FFFFFF !important;
             color: var(--boeing-blue) !important;
             border: 1px solid var(--boeing-blue) !important;
             opacity: 0.5 !important;
             
             /* 2. Size: Shorter and Narrower */
             height: 24px !important;       /* ~50% of standard 48px */
             min-height: 24px !important;
             line-height: 1 !important;
             padding: 0px 8px !important;   /* Narrower padding */
             width: auto !important; 
             min-width: 32px !important;    /* ~2/3rds of previous 40-50px */
             font-size: 14px !important;    
             
             /* 3. Position: Shift Right */
             /* "Center of where dataset 3 would be" -> Shift approx half a column width */
             margin-left: 50px !important;  
             border-radius: 4px !important;
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

        </style>
    """, unsafe_allow_html=True)
