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
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');
        
        /* Apply fonts and baseline dark-mode colors */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: #cbd5e1;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
            color: #f8fafc !important;
            letter-spacing: -0.5px;
        }
        
        /* Main application background layout (Dark Slate HUD) */
        .stApp {
            background-color: #090d16;
            background-image: 
                radial-gradient(at 0% 0%, rgba(255, 107, 53, 0.08) 0, transparent 45%), 
                radial-gradient(at 100% 0%, rgba(0, 242, 254, 0.07) 0, transparent 45%),
                radial-gradient(at 50% 100%, rgba(15, 23, 42, 0.95) 0, transparent 60%);
            background-attachment: fixed;
        }
        
        /* Custom spacing system */
        div.block-container {
            padding-top: 2rem;
            padding-bottom: 2.5rem;
            max-width: 1250px;
        }
        
        /* Style high-contrast dashboard sidebar */
        section[data-testid="stSidebar"] {
            background-color: #070a10 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.04) !important;
            box-shadow: 4px 0 24px rgba(0,0,0,0.3) !important;
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
            background-color: rgba(17, 24, 39, 0.7) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 12px !important;
            color: #f1f5f9 !important;
            padding: 10px 14px !important;
            font-size: 0.95rem !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        }
        
        .stTextInput input:focus, .stNumberInput input:focus, div[data-baseweb="select"]:focus-within {
            border-color: #ff6b35 !important;
            box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.18) !important;
            outline: none !important;
        }
        
        /* Premium custom styling for tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px !important;
            background-color: rgba(17, 24, 39, 0.5) !important;
            padding: 6px !important;
            border-radius: 14px !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: auto !important;
            padding: 10px 20px !important;
            background-color: transparent !important;
            border-radius: 10px !important;
            border: none !important;
            color: #94a3b8 !important;
            font-family: 'Outfit', sans-serif !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            transition: all 0.2s ease !important;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            color: #f8fafc !important;
            background-color: rgba(255, 255, 255, 0.03) !important;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: rgba(255, 107, 53, 0.15) !important;
            color: #ff6b35 !important;
            box-shadow: 0 2px 8px rgba(255, 107, 53, 0.05) !important;
        }
        
        .stTabs [data-baseweb="tab-highlight-bar"] {
            display: none !important;
        }
        
        /* Slider Label text */
        .stSlider [data-testid="stWidgetLabel"] p {
            color: #f1f5f9 !important;
            font-weight: 500;
        }
        
        /* Custom horizontal radio selections styled as interactive SaaS Cards */
        div[role="radiogroup"] {
            display: flex !important;
            flex-direction: row !important;
            gap: 15px !important;
            margin-top: 5px !important;
            margin-bottom: 15px !important;
            flex-wrap: wrap !important;
        }
        
        div[role="radiogroup"] label {
            background: rgba(17, 24, 39, 0.6) !important;
            border: 1.5px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 14px !important;
            padding: 14px 22px !important;
            cursor: pointer !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
            flex: 1 !important;
            min-width: 120px !important;
            text-align: center !important;
            display: inline-block !important;
        }
        
        div[role="radiogroup"] label:hover {
            border-color: #ff6b35 !important;
            background: rgba(255, 107, 53, 0.05) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(255, 107, 53, 0.1) !important;
        }
        
        /* Highlight selected card */
        div[role="radiogroup"] label[data-baseweb="radio"]:has(input[checked]) {
            border-color: #ff6b35 !important;
            background: linear-gradient(135deg, rgba(255, 107, 53, 0.1) 0%, rgba(255, 43, 84, 0.1) 100%) !important;
            box-shadow: 0 4px 12px rgba(255, 107, 53, 0.18) !important;
        }
        
        /* Hide standard round radio indicator */
        div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child {
            display: none !important;
        }
        
        div[role="radiogroup"] label[data-baseweb="radio"] div {
            font-weight: 600 !important;
            color: #cbd5e1 !important;
        }
        
        div[role="radiogroup"] label[data-baseweb="radio"]:has(input[checked]) div {
            color: #ff6b35 !important;
        }
        
        /* Upgraded food-delivery gradient buttons */
        .stButton>button {
            background: linear-gradient(135deg, #ff6b35 0%, #ff2b54 100%) !important;
            color: #ffffff !important;
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 12px 28px !important;
            font-size: 1.05rem !important;
            box-shadow: 0 4px 15px rgba(255, 43, 84, 0.25) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            width: 100% !important;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 24px rgba(255, 43, 84, 0.4) !important;
        }
        
        .stButton>button:active {
            transform: translateY(1px) !important;
        }
        
        /* Customized Scrollbar styling */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #090d16;
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        /* Premium dashboard container cards */
        .premium-card {
            background: rgba(17, 24, 39, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 18px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            margin-bottom: 20px;
        }
        
        .premium-card:hover {
            transform: translateY(-3px);
            border-color: rgba(255, 107, 53, 0.2);
            box-shadow: 0 10px 30px rgba(255, 107, 53, 0.06);
        }

        /* Override Streamlit interactive dataframes */
        div[data-testid="stTable"] table, div[data-testid="stDataFrame"] {
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-radius: 12px !important;
            overflow: hidden !important;
        }

        /* Glassmorphic overlays for status notifications */
        div[data-testid="stNotification"] {
            background-color: rgba(17, 24, 39, 0.6) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-radius: 14px !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        }

        /* Hide default Streamlit Deploy button and make header blend in */
        .stAppDeployButton, div[data-testid="stAppDeployButton"] {
            display: none !important;
        }
        header[data-testid="stHeader"] {
            background: transparent !important;
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
