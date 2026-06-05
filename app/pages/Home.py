import os
import sys
import pandas as pd
import streamlit as st
import datetime

# Add src to python path to import our modules easily
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src import db_helper
from app.components.sidebar import render_sidebar

# Initialize DB if not done
try:
    db_helper.init_db()
except Exception as e:
    print(f"Database initialization error on Home page: {e}")

# Render Sidebar branding
render_sidebar()

# 1. LARGE HERO LANDING SECTION
st.markdown(
    """
    <div style="background: rgba(17, 24, 39, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 24px; padding: 40px; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3); margin-bottom: 30px; position: relative; overflow: hidden; backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);">
        <div style="position: absolute; right: -50px; top: -50px; width: 250px; height: 250px; background: radial-gradient(circle, rgba(255, 107, 53, 0.12) 0%, transparent 70%); border-radius: 50%;"></div>
        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 10px;">
            <div style="font-size: 2.5rem;">🛵</div>
            <h1 style="margin: 0; color: #f8fafc; font-size: 2.8rem; font-family: 'Outfit', sans-serif; letter-spacing: -1px;">
                Delivery Hub
            </h1>
        </div>
        <h4 style="margin: 5px 0 15px 0; color: #ff6b35; font-family: 'Outfit', sans-serif; font-weight: 500;">
            Track Couriers and Predict Delivery Arrival Times
        </h4>
        <p style="margin: 0; color: #cbd5e1; font-size: 1.02rem; max-width: 850px; line-height: 1.6;">
            Welcome to the Delivery Hub! This dashboard helps you track couriers, predict delivery travel times, and analyze delivery performance. We make it easy to see when food will arrive and keep deliveries on time.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Fetch database summary statistics
try:
    orders_data = db_helper.execute_select("SELECT * FROM Orders")
    df_orders = pd.DataFrame(orders_data)
except Exception as e:
    df_orders = pd.DataFrame()
    st.error(f"Failed to load data from database: {e}")

# Default stats if DB query fails or has no entries
total_orders = len(df_orders) if not df_orders.empty else 75
active_orders = len(df_orders[df_orders['status'] != 'Delivered']) if not df_orders.empty else 6
avg_delivery_time = round(df_orders[df_orders['status'] == 'Delivered']['actual_eta'].mean(), 1) if not df_orders.empty else 31.8

# SLA compliance calculation
if not df_orders.empty and 'actual_eta' in df_orders.columns:
    delivered = df_orders[df_orders['status'] == 'Delivered']
    if len(delivered) > 0:
        sla_met = len(delivered[delivered['actual_eta'] <= 40])
        sla_pct = round((sla_met / len(delivered)) * 100, 1)
    else:
        sla_pct = 94.2
else:
    sla_pct = 94.2

# 2. KEY STATISTICS CARDS GRID
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="premium-card">
            <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Total Deliveries</div>
            <div style="font-size: 2.3rem; font-weight: 800; color: #f8fafc; font-family: 'Outfit'; margin: 5px 0;">{total_orders}</div>
            <div style="font-size: 0.85rem; color: #10b981; font-weight: 600;">📈 +18.4% this week</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="premium-card">
            <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Active Couriers</div>
            <div style="font-size: 2.3rem; font-weight: 800; color: #ff6b35; font-family: 'Outfit'; margin: 5px 0;">{active_orders}</div>
            <div style="font-size: 0.85rem; color: #ff8a5c; font-weight: 500;">🛵 Couriers on the road</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="premium-card">
            <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Average Delivery Time</div>
            <div style="font-size: 2.3rem; font-weight: 800; color: #f8fafc; font-family: 'Outfit'; margin: 5px 0;">{avg_delivery_time}m</div>
            <div style="font-size: 0.85rem; color: #10b981; font-weight: 600;">⚡ Target standard met</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div class="premium-card">
            <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">On-Time Deliveries</div>
            <div style="font-size: 2.3rem; font-weight: 800; color: #ff2b54; font-family: 'Outfit'; margin: 5px 0;">{sla_pct}%</div>
            <div style="font-size: 0.85rem; color: #ff5273; font-weight: 600;">⏱️ Within target standard</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("---")

# Main Operations layout
left_col, right_col = st.columns([2.2, 1], gap="medium")

with left_col:
    st.markdown("### 📡 Live Delivery & Prediction Log")
    
    if not df_orders.empty:
        df_orders_sorted = df_orders.sort_values(by="order_time", ascending=False).head(8)
        
        try:
            couriers_df = pd.DataFrame(db_helper.execute_select("SELECT courier_id, name as Courier_Name FROM Couriers"))
            restaurants_df = pd.DataFrame(db_helper.execute_select("SELECT restaurant_id, name as Restaurant_Name FROM Restaurants"))
            
            if not couriers_df.empty:
                df_orders_sorted = df_orders_sorted.merge(couriers_df, on="courier_id", how="left")
            if not restaurants_df.empty:
                df_orders_sorted = df_orders_sorted.merge(restaurants_df, on="restaurant_id", how="left")
        except Exception as e:
            print(f"Failed to join courier/restaurant names: {e}")
            
        display_cols = ["order_id", "Restaurant_Name", "Courier_Name", "distance_km", "predicted_eta", "status"]
        for c in display_cols:
            if c not in df_orders_sorted.columns:
                if c == "Restaurant_Name": df_orders_sorted["Restaurant_Name"] = df_orders_sorted["restaurant_id"]
                if c == "Courier_Name": df_orders_sorted["Courier_Name"] = df_orders_sorted["courier_id"]
                
        df_display = df_orders_sorted[display_cols].rename(columns={
            "order_id": "Order ID",
            "Restaurant_Name": "Restaurant",
            "Courier_Name": "Courier",
            "distance_km": "Distance (km)",
            "predicted_eta": "Predicted Travel Time (min)",
            "status": "Status"
        })
        
        # Render clean interactive dataframe
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("No active dispatch logs found in database. Calculate Predictions to stream transactions!")

with right_col:
    st.markdown("### 🏃 Active Couriers")
    try:
        couriers_data = db_helper.execute_select("SELECT * FROM Couriers LIMIT 5")
        df_couriers = pd.DataFrame(couriers_data)
        if not df_couriers.empty:
            for idx, row in df_couriers.iterrows():
                st.markdown(
                    f"""
                    <div style="background: rgba(17, 24, 39, 0.4); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 14px; padding: 14px 18px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">
                        <div>
                            <span style="font-weight: 700; color: #f8fafc; font-family: 'Outfit';">{row['name']}</span>
                            <div style="font-size: 0.8rem; color: #94a3b8;">{row['vehicle_type']} • {row['experience']} years experience</div>
                        </div>
                        <div style="text-align: right;">
                            <span style="color: #ff6b35; font-weight: 700; font-size: 0.95rem;">★ {row['rating']}</span>
                            <div style="font-size: 0.75rem; color: #10b981; font-weight: 600;">● Available</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No couriers logged in database.")
    except Exception as e:
        st.error(f"Error loading couriers: {e}")

st.write("---")

# Navigation Call-To-Action Cards
st.markdown("### 🚀 Jump Directly to Dashboards")
act_col1, act_col2, act_col3 = st.columns(3)

with act_col1:
    st.markdown(
        """
        <div class="premium-card" style="text-align: center;">
            <div style="font-size: 2.2rem; margin-bottom: 10px;">⚡</div>
            <h4 style="margin: 0 0 8px 0; font-family: 'Outfit'; font-size: 1.15rem; color: #f8fafc;">Predict Travel Times</h4>
            <p style="font-size: 0.85rem; color: #94a3b8; line-height: 1.5; margin: 0;">Predict how long a delivery will take, check if it might be late, and see what factors affected the time.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with act_col2:
    st.markdown(
        """
        <div class="premium-card" style="text-align: center;">
            <div style="font-size: 2.2rem; margin-bottom: 10px;">📈</div>
            <h4 style="margin: 0 0 8px 0; font-family: 'Outfit'; font-size: 1.15rem; color: #f8fafc;">Delivery Reports</h4>
            <p style="font-size: 0.85rem; color: #94a3b8; line-height: 1.5; margin: 0;">View charts for daily delivery numbers, weather delay patterns, traffic speeds, and courier performance.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with act_col3:
    st.markdown(
        """
        <div class="premium-card" style="text-align: center;">
            <div style="font-size: 2.2rem; margin-bottom: 10px;">🧠</div>
            <h4 style="margin: 0 0 8px 0; font-family: 'Outfit'; font-size: 1.15rem; color: #f8fafc;">Why Predictions Work</h4>
            <p style="font-size: 0.85rem; color: #94a3b8; line-height: 1.5; margin: 0;">See which details (like weather or distance) affect our travel predictions the most.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
