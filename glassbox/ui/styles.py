import streamlit as st

def inject_custom_css():
    """
    Injects Boeing Light Mode CSS with comprehensive styling.
    Fixes: flush sidebar, card outlines, no flash, full-height cards.
    """
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        
        /* ========================================
           1. CSS VARIABLES & GLOBAL RESET
           ======================================== */
        :root {
            --boeing-blue: #1A409F;
            --selected-blue: #0D7CB1;
            --slate-gray: #394957;
            --white: #FDFDFE;
            --text-color: #394957;
            --text-white: #FFFFFF;
            --sidebar-width: 220px;
            --topbar-height: 60px;
            --transition-fast: 0.1s ease;
            --card-border: 1px solid #D0D0D0;
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
            padding-top: 80px !important;
            min-height: calc(100vh - 80px);
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
           4. CARD BOXES WITH OUTLINES
           ======================================== */
        /* Card borders - visible outlines */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.card-header) {
            border: 1px solid #D0D0D0 !important;
            border-radius: 6px !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
            overflow: hidden !important;
            background: white !important;
        }
        
        .card-header {
            background: var(--slate-gray);
            color: white;
            padding: 10px 16px;
            font-weight: 500;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin: 0;
            border-radius: 0; /* No radius since parent wrapper has it */
        }
        
        /* Top row cards should be ~40% of viewport height */
        .top-row-cards {
            min-height: 40vh;
        }
        
        .top-row-cards div[data-testid="stVerticalBlockBorderWrapper"] {
            min-height: 38vh;
        }

        /* ========================================
           5. FULL-HEIGHT BOTTOM CARDS
           ======================================== */
        /* Make bottom row cards extend to near-bottom of screen */
        .bottom-card-container {
            min-height: calc(60vh - 80px);
            display: flex;
            flex-direction: column;
        }
        
        .bottom-card-container > div {
            flex: 1;
        }
        
        .bottom-card-container div[data-testid="stVerticalBlockBorderWrapper"] {
            min-height: calc(60vh - 100px);
        }

        /* ========================================
           6. BUTTONS
           ======================================== */
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
        
        .stButton > button:hover {
            background-color: var(--selected-blue) !important;
        }
        
        .stButton > button[kind="primary"] {
            background-color: var(--boeing-blue) !important;
        }

        /* ========================================
           7. TEXT INPUTS
           ======================================== */
        .stTextInput > div > div > input, 
        .stTextArea > div > div > textarea, 
        .stSelectbox > div > div > div {
            background-color: #FFFFFF !important;
            color: #333 !important;
            border: 1px solid #CCC !important;
            border-radius: 4px !important;
        }

        /* ========================================
           8. SETTINGS POPOVER POSITIONING
           ======================================== */
        /* Position settings popover trigger in top-right */
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
        
        /* Style the popover trigger button */
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
