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
            overflow-x: hidden;
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
           10. DATASET CONTROL STYLING (Split Buttons)
           ======================================== */
        
        /* 10.1 "Add" Button (Plus) */
        .stButton button[title="Add new dataset"] {
            background-color: #FFFFFF !important;
            color: var(--boeing-blue) !important;
            border: 1px solid var(--boeing-blue) !important;
            font-size: 16px !important;
            line-height: 1 !important;
            padding: 0px 10px !important;
        }
        .stButton button[title="Add new dataset"]:hover {
            background-color: #F0F5FA !important;
        }

        /* 10.2 Removable Dataset Main Button (Left half) */
        /* We hook onto 'Select Dataset X' tooltip */
        .stButton button[title^="Select Dataset"] {
            border-top-right-radius: 0 !important;
            border-bottom-right-radius: 0 !important;
            border-right: none !important; /* Merge seam */
            margin-right: -15px !important; /* Pull neighbor closer if possible, though container gap dominates */
            z-index: 0;
        }

        /* 10.3 "Remove" Sidecar Button (Right half - The X) */
        .stButton button[title^="Remove"] {
            background-color: #FFFFFF !important;
            color: var(--boeing-blue) !important; /* Blue X per request */
            border: 1px solid #D0D0D0 !important; /* Standard border */
            border-left: 1px solid #D0D0D0 !important; /* The vertical line separator */
            border-top-left-radius: 0 !important;
            border-bottom-left-radius: 0 !important;
            
            /* CRITICAL: Overcome Streamlit Column Gap */
            /* Streamlit st.columns(gap="small") is usually ~1rem range. We need negative margin to touch. */
            margin-left: -50px !important; /* Aggressive pull */
            position: relative;
            left: -10px; /* Fine tune */
            z-index: 1; /* Sit slightly above to ensure border clean */
            
            padding: 0 8px !important;
            min-width: 0 !important;
        }
        .stButton button[title^="Remove"]:hover {
            background-color: #FFF0F0 !important;
            color: #D32F2F !important;
            border-color: #D32F2F !important;
        }
        
        /* 10.4 Permanent Dataset (No X) - Keep Rounded */
        .stButton button[title="Permanent Dataset"] {
            border-radius: 4px !important;
            /* Ensure it looks distinct or same as others? Standard btn is fine. */
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
           9. HIDE STREAMLIT CHROME
           ======================================== */
        header[data-testid="stHeader"] { display: none; }
        footer { display: none; }
        div[data-testid="stToolbar"] { display: none !important; }

        </style>
    """, unsafe_allow_html=True)
