"""
Custom CSS Styles for GlassBox Prompt Optimizer

Premium dark theme with Boeing Console Green accents.
"""


def get_custom_css() -> str:
    """Return custom CSS for the application."""
    return """
    <style>
    /* =================================================================
       GLOBAL STYLES
       ================================================================= */
    
    /* Override Streamlit defaults */
    .stApp {
        background: linear-gradient(180deg, #0E1117 0%, #1a1a2e 100%);
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0E1117;
    }
    ::-webkit-scrollbar-thumb {
        background: #31333F;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #20C20E;
    }
    
    /* =================================================================
       GLASS BOX BANNER (Zone A)
       ================================================================= */
    
    .glass-box-container {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #1a1a2e 100%);
        border: 1px solid #20C20E;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 0 30px rgba(32, 194, 14, 0.1);
    }
    
    .glass-box-title {
        color: #20C20E;
        font-family: 'Consolas', monospace;
        font-size: 24px;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(32, 194, 14, 0.5);
        margin-bottom: 10px;
    }
    
    .monologue-panel {
        background: linear-gradient(180deg, #0a0a0f 0%, #0E1117 100%);
        border: 1px solid #31333F;
        border-left: 3px solid #20C20E;
        border-radius: 8px;
        padding: 15px;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 12px;
        color: #20C20E;
        max-height: 200px;
        overflow-y: auto;
        text-shadow: 0 0 5px rgba(32, 194, 14, 0.3);
    }
    
    /* =================================================================
       SIDEBAR (Zone B)
       ================================================================= */
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #16213e 0%, #0E1117 100%);
        border-right: 1px solid #31333F;
    }
    
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] .stNumberInput label {
        color: #FAFAFA !important;
        font-weight: 500;
    }
    
    /* =================================================================
       CANDIDATE CARDS (Zone C)
       ================================================================= */
    
    .candidate-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #31333F;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    
    .candidate-card:hover {
        border-color: #20C20E;
        box-shadow: 0 0 15px rgba(32, 194, 14, 0.2);
        transform: translateY(-2px);
    }
    
    .candidate-card.selected {
        border-color: #20C20E;
        box-shadow: 0 0 20px rgba(32, 194, 14, 0.3);
    }
    
    .candidate-rank {
        font-size: 18px;
        font-weight: bold;
        color: #888;
    }
    
    .candidate-score {
        font-size: 20px;
        font-weight: bold;
        padding: 4px 12px;
        border-radius: 20px;
    }
    
    .score-high {
        background: rgba(34, 197, 94, 0.2);
        color: #22c55e;
    }
    
    .score-medium {
        background: rgba(234, 179, 8, 0.2);
        color: #eab308;
    }
    
    .score-low {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
    }
    
    /* Traffic lights */
    .traffic-lights {
        display: inline-flex;
        gap: 3px;
        font-size: 10px;
    }
    
    .traffic-light {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
    }
    
    .traffic-light.pass {
        background: #22c55e;
        box-shadow: 0 0 5px #22c55e;
    }
    
    .traffic-light.fail {
        background: #ef4444;
        box-shadow: 0 0 5px #ef4444;
    }
    
    /* =================================================================
       TELEMETRY GRAPH (Zone D)
       ================================================================= */
    
    .telemetry-container {
        background: #0E1117;
        border: 1px solid #31333F;
        border-radius: 10px;
        padding: 10px;
    }
    
    /* =================================================================
       TEST BENCH (Zone E)
       ================================================================= */
    
    .test-input-golden {
        border-left: 3px solid #22c55e !important;
    }
    
    .test-input-edge {
        border-left: 3px solid #eab308 !important;
    }
    
    .test-input-adversarial {
        border-left: 3px solid #ef4444 !important;
    }
    
    /* =================================================================
       BUTTONS
       ================================================================= */
    
    .stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #20C20E 0%, #15a00c 100%);
        color: #0E1117;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        transition: all 0.3s ease;
    }
    
    .stButton > button[data-testid="baseButton-primary"]:hover {
        background: linear-gradient(135deg, #28e612 0%, #20C20E 100%);
        box-shadow: 0 0 20px rgba(32, 194, 14, 0.4);
        transform: translateY(-2px);
    }
    
    .stButton > button[data-testid="baseButton-secondary"] {
        background: transparent;
        color: #FAFAFA;
        border: 1px solid #31333F;
        border-radius: 8px;
    }
    
    .stButton > button[data-testid="baseButton-secondary"]:hover {
        border-color: #20C20E;
        color: #20C20E;
    }
    
    /* =================================================================
       METRICS
       ================================================================= */
    
    [data-testid="stMetricValue"] {
        color: #20C20E !important;
        font-weight: bold;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 14px;
    }
    
    /* =================================================================
       EXPANDERS
       ================================================================= */
    
    .streamlit-expanderHeader {
        background: #16213e;
        border-radius: 8px;
    }
    
    .streamlit-expanderContent {
        background: #1a1a2e;
        border-radius: 0 0 8px 8px;
    }
    
    /* =================================================================
       TAB STYLING
       ================================================================= */
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #16213e;
        border-radius: 8px;
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 6px;
        color: #888;
        padding: 8px 16px;
    }
    
    .stTabs [aria-selected="true"] {
        background: #20C20E !important;
        color: #0E1117 !important;
        font-weight: bold;
    }
    
    /* =================================================================
       CODE BLOCKS
       ================================================================= */
    
    .stCodeBlock {
        background: #0a0a0f !important;
        border: 1px solid #31333F;
        border-radius: 8px;
    }
    
    /* =================================================================
       STATUS INDICATORS
       ================================================================= */
    
    .status-running {
        color: #20C20E;
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    .status-idle {
        color: #666;
    }
    
    .status-completed {
        color: #22c55e;
    }
    
    .status-failed {
        color: #ef4444;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* =================================================================
       ANIMATIONS
       ================================================================= */
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.3s ease-out;
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 5px rgba(32, 194, 14, 0.3); }
        50% { box-shadow: 0 0 20px rgba(32, 194, 14, 0.6); }
    }
    
    .glow-effect {
        animation: glow 2s ease-in-out infinite;
    }
    
    /* =================================================================
       RESPONSIVE
       ================================================================= */
    
    @media (max-width: 768px) {
        .glass-box-container {
            padding: 10px;
        }
        
        .candidate-card {
            padding: 10px;
        }
    }
    </style>
    """


def inject_custom_css():
    """Inject custom CSS into Streamlit app."""
    import streamlit as st
    st.markdown(get_custom_css(), unsafe_allow_html=True)
