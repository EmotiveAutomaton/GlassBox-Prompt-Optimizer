import streamlit as st

def inject_custom_css():
    """
    Injects Boeing Light Mode CSS with comprehensive styling.
    Color Palette (Strict 4-Color):
    - Background: #FDFDFE (Near White)
    - Panel Base: #394957 (Slate Gray - Sidebar & Headers)
    - Top Bar: #1A409F (Boeing Blue)
    - Accent: #0D7CB1 (Selected Blue - Active State)
    """
    st.markdown("""
        <style>
        /* Font Import */
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
            font-weight: 400; /* NOT BOLD */
            letter-spacing: 1px;
            white-space: nowrap;
        }

        #boeing-top-bar .top-bar-logo {
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            height: 32px;
        }
        
        #boeing-top-bar .top-bar-spacer {
            width: 200px;
        }

        .block-container {
            padding-top: 80px !important;
        }

        /* ========================================
           3. SIDEBAR - FIXED WIDTH, NO RESIZE
           ======================================== */
        section[data-testid="stSidebar"] {
            background-color: var(--slate-gray) !important;
            border-right: none;
            padding-top: var(--topbar-height);
            z-index: 999990;
            width: var(--sidebar-width) !important;
            min-width: var(--sidebar-width) !important;
            max-width: var(--sidebar-width) !important;
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
        
        /* Hide resize handle */
        section[data-testid="stSidebar"]::after,
        section[data-testid="stSidebar"] > div[style*="cursor: col-resize"] {
            display: none !important;
        }

        /* Sidebar Text Color */
        section[data-testid="stSidebar"] p, 
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] span {
            color: var(--text-white) !important;
        }

        /* ========================================
           4. NAVIGATION BLOCKS - FULL WIDTH
           ======================================== */
        .stRadio > div[role="radiogroup"] > label > div:first-child {
            display: none !important;
        }

        .stRadio > div[role="radiogroup"] {
            gap: 0px;
        }

        .stRadio > div[role="radiogroup"] > label {
            background-color: transparent;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            border-radius: 0px !important;
            padding: 16px 20px !important;
            margin: 0 -1rem !important;
            width: calc(100% + 2rem) !important;
            transition: background-color var(--transition-fast);
            color: white !important;
            cursor: pointer;
        }

        .stRadio > div[role="radiogroup"] > label:hover {
            background-color: rgba(255,255,255,0.08);
        }
        
        .stRadio > div[role="radiogroup"] > label:has(input:checked) {
            background-color: var(--selected-blue) !important;
        }

        /* ========================================
           5. CONFIG BUTTON - FLUSH BOTTOM
           ======================================== */
        section[data-testid="stSidebar"] .stPopover > button,
        section[data-testid="stSidebar"] [data-testid="stPopover"] > button {
            background-color: transparent !important;
            color: white !important;
            border-radius: 0 !important;
            width: calc(100% + 2rem) !important;
            margin-left: -1rem !important;
            padding: 16px 20px !important;
            border: none !important;
            border-top: 2px solid rgba(0,0,0,0.3) !important;
            transition: background-color var(--transition-fast);
            position: fixed !important;
            bottom: 0 !important;
            left: 0 !important;
            width: var(--sidebar-width) !important;
        }
        
        section[data-testid="stSidebar"] .stPopover > button:hover,
        section[data-testid="stSidebar"] [data-testid="stPopover"] > button:hover {
            background-color: rgba(255,255,255,0.08) !important;
        }

        /* ========================================
           6. CARD BOXES WITH HEADERS
           ======================================== */
        .boeing-card {
            background: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 6px;
            margin-bottom: 16px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.04);
            transition: box-shadow var(--transition-normal), transform var(--transition-fast);
            overflow: hidden;
        }
        
        .boeing-card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            transform: translateY(-1px);
        }

        .boeing-card-header {
            background: var(--slate-gray);
            color: white;
            padding: 10px 16px;
            font-weight: 500;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .boeing-card-content {
            padding: 16px;
        }

        /* Legacy panel header support */
        .boeing-panel-header {
            background: var(--slate-gray);
            color: white;
            padding: 10px 15px;
            font-weight: 500;
            font-size: 13px;
            border-radius: 4px 4px 0 0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .boeing-panel-content {
            padding: 15px;
            color: var(--text-color);
        }

        /* ========================================
           7. BUTTONS WITH PRESS ANIMATION
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
           8. TEXT INPUTS
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
           9. ANIMATIONS - FADE IN ON ENGINE SWITCH
           ======================================== */
        .main .block-container {
            animation: fadeIn var(--transition-normal);
        }
        
        @keyframes fadeIn {
            from { opacity: 0.7; }
            to { opacity: 1; }
        }

        /* ========================================
           10. HIDE STREAMLIT CHROME
           ======================================== */
        header[data-testid="stHeader"] { display: none; }
        footer { display: none; }
        
        /* Hide bottom export/menu bar if visible */
        .stApp > footer,
        div[data-testid="stToolbar"] {
            display: none !important;
        }

        </style>
    """, unsafe_allow_html=True)
