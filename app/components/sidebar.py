import os
import streamlit as st

def render_sidebar():
    """Renders the custom sidebar with simple premium branding."""
    st.sidebar.markdown(
        """
        <div style="text-align: center; margin-top: 15px; margin-bottom: 25px;">
            <h1 style="background: linear-gradient(135deg, #00f2fe 0%, #ff6b35 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-family: 'Outfit', sans-serif; font-size: 2.2rem; font-weight: 800; margin-bottom: 4px; filter: drop-shadow(0 2px 8px rgba(0, 242, 254, 0.15));">
                SwiftETA ⭐
            </h1>
            <p style="color: #64748b; font-family: 'Inter', sans-serif; font-size: 0.85rem; margin-top: 0; font-weight: 500; letter-spacing: 0.5px;">
                Predict. Optimize. Deliver.
            </p>
        </div>
        <hr style="border: 0; height: 1px; background: linear-gradient(to right, rgba(255,255,255,0), rgba(255,255,255,0.06), rgba(255,255,255,0)); margin: 20px 0;"/>
        """,
        unsafe_allow_html=True
    )
    
    # Footer branding
    st.sidebar.markdown(
        """
        <div style="margin-top: 80px; text-align: center; color: #475569; font-size: 0.72rem; font-family: 'Inter', sans-serif; font-weight: 500; line-height: 1.4;">
            SwiftETA ⭐ &copy; 2026
        </div>
        """,
        unsafe_allow_html=True
    )
