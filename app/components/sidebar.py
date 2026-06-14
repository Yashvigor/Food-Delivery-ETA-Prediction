import os
import streamlit as st

def render_sidebar():
    """Renders the custom sidebar with clean minimalist premium branding."""
    st.sidebar.markdown(
        """
        <div style="text-align: center; margin-top: 20px; margin-bottom: 20px;">
            <h1 style="background: linear-gradient(135deg, #ff8a5c 0%, #f4511e 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-family: 'Outfit', sans-serif; font-size: 1.75rem; font-weight: 800; margin-bottom: 3px; letter-spacing: -0.025em;">
                DeliverIQ
            </h1>
            <p style="color: #475569; font-family: 'Inter', sans-serif; font-size: 0.72rem; margin-top: 0; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase;">
                Predict. Optimize. Deliver.
            </p>
        </div>
        <hr style="border: 0; height: 1px; background: linear-gradient(to right, rgba(255,255,255,0), rgba(255,255,255,0.04), rgba(255,255,255,0)); margin: 15px 0;"/>
        """,
        unsafe_allow_html=True
    )
    
    # Footer branding
    st.sidebar.markdown(
        """
        <div style="margin-top: 60px; text-align: center; color: #334155; font-size: 0.7rem; font-family: 'Inter', sans-serif; font-weight: 500; letter-spacing: 0.025em;">
            DeliverIQ Ops Console v1.0.0 &bull; &copy; 2026
        </div>
        """,
        unsafe_allow_html=True
    )
