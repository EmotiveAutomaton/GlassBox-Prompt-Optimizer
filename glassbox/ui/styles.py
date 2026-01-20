import streamlit as st

def inject_custom_css():
    """
    Injects Boeing Light Mode CSS with comprehensive styling.
    Fixes: flush sidebar, card outlines, no flash on navigation.
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
            --transition-fast: 0.15s ease;
            --transition-normal: 0.25s ease;
            --card-border: 1px solid #D0D0D0;
            --card-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }

        html, body, .stApp {
            background-color: var(--white) !important;
            color: var(--text-color) !important;
            font-family: 'Helvetica Neue', Arial, sans-serif !important;
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
        
        /* Gear Icon in Top Bar - Clickable */
        #top-bar-gear {
            background: transparent;
            border: none;
            cursor: pointer;
            padding: 8px;
            border-radius: 4px;
            transition: background-color var(--transition-fast);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        #top-bar-gear:hover {
            background-color: rgba(255,255,255,0.15);
        }

        .block-container {
            padding-top: 80px !important;
        }

        /* ========================================
           3. SIDEBAR - FIXED WIDTH, TRULY FLUSH
           ======================================== */
        section[data-testid="stSidebar"] {
            background-color: var(--slate-gray) !important;
            border-right: none;
            z-index: 999990;
            width: var(--sidebar-width) !important;
            min-width: var(--sidebar-width) !important;
            max-width: var(--sidebar-width) !important;
            padding-top: var(--topbar-height) !important; /* Flush with top bar */
            margin-top: 0 !important;
        }
        
        /* AGGRESSIVE: Remove ALL internal padding in sidebar */
        section[data-testid="stSidebar"] > div:first-child,
        section[data-testid="stSidebar"] > div:first-child > div:first-child,
        section[data-testid="stSidebar"] > div:first-child > div:first-child > div {
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Target the block wrapper specifically */
        section[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
        section[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
            padding: 0 !important;
            margin: 0 !important;
            gap: 0 !important;
        }
        
        /* HIDE ALL COLLAPSE/RESIZE CONTROLS */
        section[data-testid="stSidebar"] > div:first-child > button,
        button[data-testid="baseButton-headerNoPadding"],
        [data-testid="stSidebarCollapseButton"],
        section[data-testid="stSidebar"] [data-testid="stSidebarCollapsedControl"],
        div[data-testid="collapsedControl"] {
            display: none !important;
            visibility: hidden !important;
            pointer-events: none !important;
        }

        section[data-testid="stSidebar"] p, 
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] span {
            color: var(--text-white) !important;
        }

        /* ========================================
           4. CARD BOXES WITH HEADERS AND OUTLINES
           ======================================== */
        .card-header {
            background: var(--slate-gray);
            color: white;
            padding: 10px 16px;
            font-weight: 500;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin: 0;
            border-radius: 6px 6px 0 0;
        }
        
        /* Card outline container - targets Streamlit columns */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border: var(--card-border) !important;
            border-radius: 6px !important;
            box-shadow: var(--card-shadow) !important;
            background: #FFFFFF !important;
            margin-bottom: 16px !important;
            overflow: hidden;
        }

        /* ========================================
           5. BUTTONS WITH PRESS ANIMATION
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
            transform: translateY(-1px);
        }
        
        .stButton > button:active {
            transform: scale(0.98) translateY(0px);
        }
        
        .stButton > button[kind="primary"] {
            background-color: var(--boeing-blue) !important;
        }

        /* ========================================
           6. TEXT INPUTS
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
           7. PREVENT FLASH ON NAVIGATION
           ======================================== */
        /* Prevent background flash on rerun */
        .stApp, .main, .block-container {
            transition: none !important;
        }
        
        /* Keep sidebar stable during reruns */
        section[data-testid="stSidebar"] {
            transition: none !important;
        }

        /* ========================================
           8. HIDE STREAMLIT CHROME
           ======================================== */
        header[data-testid="stHeader"] { display: none; }
        footer { display: none; }
        div[data-testid="stToolbar"] { display: none !important; }

        </style>
    """, unsafe_allow_html=True)
