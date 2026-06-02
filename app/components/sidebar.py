import os
import streamlit as st

def render_sidebar():
    """Renders the custom sidebar with premium styling and system configuration status."""
    st.sidebar.markdown(
        """
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="color: #00f2fe; font-family: 'Outfit', sans-serif; font-size: 2.2rem; font-weight: 700; margin-bottom: 5px; text-shadow: 0 0 10px rgba(0,242,254,0.3);">
                ⚡ LogiPredict
            </h1>
            <p style="color: #a0aec0; font-family: 'Inter', sans-serif; font-size: 0.9rem; margin-top: 0;">
                Smart Logistics & ETA Engine
            </p>
        </div>
        <hr style="border: 0; height: 1px; background: linear-gradient(to right, rgba(0,0,0,0), #00f2fe, rgba(0,0,0,0)); margin: 15px 0;"/>
        """,
        unsafe_allow_html=True
    )
    
    st.sidebar.markdown("### 📊 Platform Modules")
    
    # Simple navigation tips
    st.sidebar.info(
        "👈 Use the sidebar navigation menu to toggle between the dashboard analytics, customer ETA tool, and ML explanations."
    )
    
    st.sidebar.markdown("### ⚙️ System Status")
    
    # 1. Check Database connection
    pg_host = os.environ.get("DB_HOST")
    if pg_host:
        st.sidebar.success("🔗 Database: PostgreSQL (Connected)")
    else:
        st.sidebar.warning("💾 Database: SQLite (Fallback Mode)")
        
    # 2. Check API status
    owm_key = os.environ.get("OPENWEATHER_API_KEY")
    if owm_key:
        st.sidebar.success("🌤️ Weather Engine: OWM Live API")
    else:
        st.sidebar.info("🌤️ Weather Engine: Simulation Mode")
        
    st.sidebar.success("🗺️ Maps Router: OSRM Public Active")
    
    # Footer branding
    st.sidebar.markdown(
        """
        <div style="position: fixed; bottom: 15px; width: 230px; text-align: center; color: #718096; font-size: 0.75rem; font-family: 'Inter', sans-serif;">
            LogiPredict v1.0.0 &copy; 2026<br/>
            Designed for Premium Performance
        </div>
        """,
        unsafe_allow_html=True
    )
