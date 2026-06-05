import os
import streamlit as st

# Must be the very first Streamlit command
st.set_page_config(
    page_title="SwiftETA ⭐ - Predict. Optimize. Deliver.",
    page_icon="🛵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Centralized Premium CSS Styling System (Obsidian Dark Slate / Glassmorphic Command Aesthetic)
st.markdown(
    """
    <style>
        /* Import Premium typography from Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800;900&display=swap');
        
        /* Apply fonts and baseline dark-mode colors */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: #94a3b8;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
            color: #f8fafc !important;
            letter-spacing: -0.03em !important;
        }
        
        /* Main application background layout (Dark Slate HUD) */
        .stApp {
            background-color: #0b0f19;
            background-image: 
                radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.05) 0, transparent 40%), 
                radial-gradient(at 100% 0%, rgba(14, 165, 233, 0.04) 0, transparent 45%),
                radial-gradient(at 50% 100%, rgba(15, 23, 42, 0.95) 0, transparent 60%);
            background-attachment: fixed;
        }
        
        /* Custom spacing system */
        div.block-container {
            padding-top: 2rem;
            padding-bottom: 2.5rem;
            max-width: 1200px;
        }
        
        /* Style high-contrast dashboard sidebar */
        section[data-testid="stSidebar"] {
            background-color: #070a11 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.03) !important;
            box-shadow: 4px 0 24px rgba(0,0,0,0.4) !important;
        }
        
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3, 
        section[data-testid="stSidebar"] h4,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] label {
            color: #f1f5f9 !important;
        }
        
        /* Upgraded premium inputs and sliders */
        .stTextInput input, .stNumberInput input, .stSelectbox select, div[data-baseweb="select"] > div {
            background-color: rgba(15, 23, 42, 0.75) !important;
            border: 1px solid rgba(255, 255, 255, 0.07) !important;
            border-radius: 8px !important;
            color: #f1f5f9 !important;
            padding: 8px 12px !important;
            font-size: 0.9rem !important;
            transition: all 0.2s ease;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
        }
        
        .stTextInput input:focus, .stNumberInput input:focus, div[data-baseweb="select"]:focus-within {
            border-color: #6366f1 !important;
            box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.15) !important;
            outline: none !important;
        }
        
        /* Premium custom styling for tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 6px !important;
            background-color: rgba(15, 23, 42, 0.6) !important;
            padding: 4px !important;
            border-radius: 10px !important;
            border: 1px solid rgba(255, 255, 255, 0.04) !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: auto !important;
            padding: 8px 16px !important;
            background-color: transparent !important;
            border-radius: 6px !important;
            border: none !important;
            color: #64748b !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 500 !important;
            font-size: 0.85rem !important;
            transition: all 0.15s ease !important;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            color: #cbd5e1 !important;
            background-color: rgba(255, 255, 255, 0.02) !important;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: rgba(99, 102, 241, 0.1) !important;
            color: #818cf8 !important;
            box-shadow: none !important;
            border: 1px solid rgba(99, 102, 241, 0.2) !important;
        }
        
        .stTabs [data-baseweb="tab-highlight-bar"] {
            display: none !important;
        }
        
        /* Slider Label text */
        .stSlider [data-testid="stWidgetLabel"] p {
            color: #cbd5e1 !important;
            font-size: 0.85rem;
            font-weight: 500;
        }
        
        /* Custom horizontal radio selections styled as interactive SaaS Cards */
        div[role="radiogroup"] {
            display: flex !important;
            flex-direction: row !important;
            gap: 12px !important;
            margin-top: 5px !important;
            margin-bottom: 15px !important;
            flex-wrap: wrap !important;
        }
        
        div[role="radiogroup"] label {
            background: rgba(15, 23, 42, 0.6) !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            border-radius: 10px !important;
            padding: 10px 18px !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
            flex: 1 !important;
            min-width: 100px !important;
            text-align: center !important;
            display: inline-block !important;
        }
        
        div[role="radiogroup"] label:hover {
            border-color: rgba(99, 102, 241, 0.4) !important;
            background: rgba(99, 102, 241, 0.03) !important;
        }
        
        /* Highlight selected card */
        div[role="radiogroup"] label[data-baseweb="radio"]:has(input[checked]) {
            border-color: #6366f1 !important;
            background: rgba(99, 102, 241, 0.08) !important;
            box-shadow: 0 0 0 1px #6366f1 !important;
        }
        
        /* Hide standard round radio indicator */
        div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child {
            display: none !important;
        }
        
        div[role="radiogroup"] label[data-baseweb="radio"] div {
            font-weight: 500 !important;
            color: #64748b !important;
            font-size: 0.85rem !important;
        }
        
        div[role="radiogroup"] label[data-baseweb="radio"]:has(input[checked]) div {
            color: #818cf8 !important;
        }
        
        /* Upgraded food-delivery gradient buttons to Senior Frontend Vercel styling */
        .stButton>button {
            background: linear-gradient(180deg, #6366f1 0%, #4f46e5 100%) !important;
            color: #ffffff !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 8px !important;
            padding: 8px 20px !important;
            font-size: 0.88rem !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05), 0 4px 12px rgba(99, 102, 241, 0.1) !important;
            transition: all 0.2s ease !important;
            width: 100% !important;
        }
        
        .stButton>button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.2) !important;
            border-color: rgba(255, 255, 255, 0.15) !important;
        }
        
        .stButton>button:active {
            transform: translateY(0) !important;
        }
        
        /* Customized Scrollbar styling */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #0b0f19;
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.08);
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.15);
        }
        
        /* Premium dashboard container cards */
        .premium-card {
            background: rgba(20, 27, 45, 0.5) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-radius: 12px !important;
            padding: 20px !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15) !important;
            transition: all 0.2s ease !important;
            margin-bottom: 15px;
        }
        
        .premium-card:hover {
            transform: translateY(-2px);
            border-color: rgba(99, 102, 241, 0.25) !important;
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.04) !important;
        }
        
        /* Override Streamlit interactive dataframes */
        div[data-testid="stTable"] table, div[data-testid="stDataFrame"] {
            border: 1px solid rgba(255, 255, 255, 0.04) !important;
            border-radius: 8px !important;
            overflow: hidden !important;
        }
        
        /* Glassmorphic overlays for status notifications */
        div[data-testid="stNotification"] {
            background-color: rgba(15, 23, 42, 0.7) !important;
            border: 1px solid rgba(255, 255, 255, 0.04) !important;
            border-radius: 10px !important;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1) !important;
        }
        
        /* Hide default Streamlit Deploy button and make header blend in */
        .stAppDeployButton, div[data-testid="stAppDeployButton"] {
            display: none !important;
        }
        header[data-testid="stHeader"] {
            background: transparent !important;
        }

        /* New premium timeline and badge styles for dispatch log */
        .timeline-card {
            background: rgba(18, 24, 38, 0.5) !important;
            border: 1px solid rgba(255, 255, 255, 0.04) !important;
            border-radius: 12px !important;
            padding: 16px 20px !important;
            margin-bottom: 12px !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
        }
        .timeline-card:hover {
            transform: translateY(-1px) !important;
            border-color: rgba(99, 102, 241, 0.3) !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
        }
        .status-badge {
            display: inline-flex !important;
            align-items: center !important;
            padding: 3px 10px !important;
            border-radius: 6px !important;
            font-size: 0.72rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.025em !important;
            border: 1px solid transparent !important;
        }
        .status-preparing {
            background: rgba(245, 158, 11, 0.06) !important;
            color: #fbbf24 !important;
            border-color: rgba(245, 158, 11, 0.15) !important;
        }
        .status-transit {
            background: rgba(14, 165, 233, 0.06) !important;
            color: #38bdf8 !important;
            border-color: rgba(14, 165, 233, 0.15) !important;
        }
        .status-delivered {
            background: rgba(16, 185, 129, 0.06) !important;
            color: #34d399 !important;
            border-color: rgba(16, 185, 129, 0.15) !important;
        }
        .timeline-bar-bg {
            background: rgba(255, 255, 255, 0.04) !important;
            height: 4px !important;
            border-radius: 2px !important;
            margin-top: 10px !important;
            overflow: hidden !important;
            width: 100% !important;
        }
        .timeline-bar-fill {
            height: 100% !important;
            border-radius: 2px !important;
            box-shadow: 0 0 6px rgba(99, 102, 241, 0.3) !important;
            background: linear-gradient(90deg, #6366f1 0%, #38bdf8 100%) !important;
        }
        .live-indicator {
            display: inline-flex !important;
            align-items: center !important;
            gap: 6px !important;
            font-weight: 600 !important;
            color: #f87171 !important;
            font-size: 0.75rem !important;
            letter-spacing: 0.05em !important;
        }
        .live-dot {
            width: 6px !important;
            height: 6px !important;
            background-color: #ef4444 !important;
            border-radius: 50% !important;
            animation: pulse-live 1.8s infinite ease-in-out !important;
        }
        @keyframes pulse-live {
            0% { transform: scale(0.95); opacity: 0.7; }
            50% { transform: scale(1.15); opacity: 1; }
            100% { transform: scale(0.95); opacity: 0.7; }
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Setup multipage pages directory
pages_dir = os.path.join(os.path.dirname(__file__), "pages")

home_page = st.Page(
    page=os.path.join(pages_dir, "Home.py"),
    title="Dispatch Hub",
    icon="🛵",
    default=True
)

eta_page = st.Page(
    page=os.path.join(pages_dir, "ETA_Prediction.py"),
    title="Predict ETA",
    icon="⚡",
    url_path="ETA_Prediction"
)

analytics_page = st.Page(
    page=os.path.join(pages_dir, "Logistics_Analytics.py"),
    title="Fleet Insights",
    icon="📈",
    url_path="Logistics_Analytics"
)

insights_page = st.Page(
    page=os.path.join(pages_dir, "Model_Insights.py"),
    title="AI Interpretability",
    icon="🧠",
    url_path="Model_Insights"
)

# Run navigation
pg = st.navigation([home_page, eta_page, analytics_page, insights_page])
pg.run()
