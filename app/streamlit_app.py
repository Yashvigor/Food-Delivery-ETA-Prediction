import os
import streamlit as st

# Must be the very first Streamlit command
st.set_page_config(
    page_title="LogiPredict - Smart Delivery ETA & Logistics Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium CSS injection for beautiful dark mode
st.markdown(
    """
    <style>
        /* Import premium fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700;800&display=swap');
        
        /* Apply fonts */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: -0.5px;
        }
        
        /* Glassmorphic main panel background */
        .stApp {
            background-color: #0b0f19;
            background-image: 
                radial-gradient(at 0% 0%, rgba(79, 70, 229, 0.15) 0, transparent 50%), 
                radial-gradient(at 50% 0%, rgba(6, 182, 212, 0.1) 0, transparent 50%),
                radial-gradient(at 100% 100%, rgba(15, 23, 42, 0.95) 0, transparent 50%);
            background-attachment: fixed;
        }
        
        /* Premium custom containers */
        div.block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }
        
        /* Style Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #0f172a;
            border-right: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 4px 0 20px rgba(0,0,0,0.3);
        }
        
        /* Beautiful inputs */
        .stTextInput input, .stNumberInput input, .stSelectbox select, .stSlider {
            background-color: rgba(30, 41, 59, 0.5) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 10px !important;
            color: #ffffff !important;
            transition: all 0.3s ease;
        }
        
        .stTextInput input:focus, .stNumberInput input:focus {
            border-color: #00f2fe !important;
            box-shadow: 0 0 10px rgba(0, 242, 254, 0.2) !important;
        }
        
        /* Premium custom buttons */
        .stButton>button {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
            color: #ffffff !important;
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 12px 28px !important;
            font-size: 1.05rem !important;
            box-shadow: 0 4px 15px rgba(0, 242, 254, 0.35) !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(0, 242, 254, 0.5) !important;
        }
        
        .stButton>button:active {
            transform: translateY(1px) !important;
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #0f172a;
        }
        ::-webkit-scrollbar-thumb {
            background: #1e293b;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #334155;
        }
        
        /* Glowing badges */
        .glow-metric {
            background: rgba(22, 28, 45, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            transition: transform 0.3s ease;
        }
        .glow-metric:hover {
            transform: translateY(-3px);
            border-color: rgba(0, 242, 254, 0.2);
            box-shadow: 0 10px 25px rgba(0, 242, 254, 0.08);
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Define Programmatic Multipage Routing (Streamlit 1.35.0+)
# Make sure app sub-pages point to the exact absolute or relative script path
pages_dir = os.path.join(os.path.dirname(__file__), "pages")

home_page = st.Page(
    page=os.path.join(pages_dir, "Home.py"),
    title="Overview & Operations",
    icon="📊",
    default=True
)

eta_page = st.Page(
    page=os.path.join(pages_dir, "ETA_Prediction.py"),
    title="Smart ETA Predictor",
    icon="⚡"
)

analytics_page = st.Page(
    page=os.path.join(pages_dir, "Logistics_Analytics.py"),
    title="Logistics Insights",
    icon="📈"
)

insights_page = st.Page(
    page=os.path.join(pages_dir, "Model_Insights.py"),
    title="XAI Model Insights",
    icon="🧠"
)

# Run navigation
pg = st.navigation([home_page, eta_page, analytics_page, insights_page])
pg.run()
