import os
import sys
import pandas as pd
import streamlit as st
import datetime
import random

# Add src to python path to import our modules easily
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src import db_helper
from app.components.sidebar import render_sidebar
from app.components import charts

# Render Sidebar branding
render_sidebar()

# Title
st.markdown(
    """
    <div style="margin-bottom: 25px;">
        <h1 style='color: #f8fafc; font-family: "Outfit"; font-size: 2.8rem; margin-bottom: 5px; text-shadow: 0 0 15px rgba(255, 107, 53, 0.15);'>
            📈 Operations Logistics Analytics
        </h1>
        <p style='color: #94a3b8; font-size: 1.1rem; margin-top: 0;'>
            Aggregated insights on delivery volumes, weather delays, traffic bottlenecks, and courier transit efficiencies.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Fetch DB data
try:
    orders_data = db_helper.execute_select("SELECT * FROM Orders")
    df_orders = pd.DataFrame(orders_data)
except Exception as e:
    df_orders = pd.DataFrame()
    st.error(f"Failed to query orders database: {e}")

if df_orders.empty:
    st.info("No delivery analytics logged in database yet. Launch predictions or simulate operations below to populate graphs!")
else:
    # Operations KPIs Summary
    delivered_orders = df_orders[df_orders['status'] == 'Delivered']
    avg_speed = round(df_orders['distance_km'].mean() / (df_orders['actual_eta'].fillna(35).mean() / 60.0), 1) if not df_orders.empty else 18.5
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="premium-card">
                <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Total Operations Logged</div>
                <div style="font-size: 2.3rem; font-weight: 800; color: #f8fafc; font-family: 'Outfit'; margin: 5px 0;">{len(df_orders)}</div>
                <div style="font-size: 0.85rem; color: #10b981; font-weight: 600;">📊 In database log</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div class="premium-card">
                <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Average Fleet Speed</div>
                <div style="font-size: 2.3rem; font-weight: 800; color: #ff6b35; font-family: 'Outfit'; margin: 5px 0;">{avg_speed} <span style="font-size: 1.2rem; font-weight: 600;">km/h</span></div>
                <div style="font-size: 0.85rem; color: #ff8a5c; font-weight: 500;">⚡ Speed = distance / transit</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f"""
            <div class="premium-card">
                <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Delivered Orders Rate</div>
                <div style="font-size: 2.3rem; font-weight: 800; color: #ff2b54; font-family: 'Outfit'; margin: 5px 0;">{len(delivered_orders)} <span style="font-size: 1.2rem; font-weight: 600;">/ {len(df_orders)}</span></div>
                <div style="font-size: 0.85rem; color: #ff5273; font-weight: 600;">⏱️ SLA Complete Status</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    st.write("---")
    
    # 2x2 Charts Grid
    grid_row1_col1, grid_row1_col2 = st.columns(2)
    grid_row2_col1, grid_row2_col2 = st.columns(2)
    
    with grid_row1_col1:
        charts.render_daily_deliveries_chart(df_orders)
        
    with grid_row1_col2:
        charts.render_traffic_impact_chart(df_orders)
        
    with grid_row2_col1:
        charts.render_weather_delay_chart(df_orders)
        
    with grid_row2_col2:
        charts.render_courier_experience_vs_time(df_orders)

st.write("---")

# Operations Simulation Console
st.markdown("### 🎛️ Simulation Console")
st.write("Need more sample data to analyze? Use the simulator below to generate randomized historical delivery orders and save them to the database.")

sim_col1, sim_col2 = st.columns([1, 2])

with sim_col1:
    sim_count = st.number_input("Number of simulated orders to insert", min_value=5, max_value=200, value=25, step=5)
    
with sim_col2:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("🚀 Generate Simulated Orders"):
        with st.spinner("Creating orders and saving to database..."):
            try:
                conn, db_type = db_helper.get_connection()
                cur = conn.cursor()
                
                # Fetch courier ids and restaurant ids
                couriers = db_helper.execute_select("SELECT courier_id FROM Couriers")
                restaurants = db_helper.execute_select("SELECT restaurant_id FROM Restaurants")
                
                cour_ids = [c["courier_id"] for c in couriers] if couriers else ["C0001"]
                rest_ids = [r["restaurant_id"] for r in restaurants] if restaurants else ["R0001"]
                
                now = datetime.datetime.now()
                
                for i in range(int(sim_count)):
                    order_id = f"SIM{random.randint(1000, 9999)}"
                    cust_id = f"CUST{random.randint(100, 999)}"
                    rest_id = random.choice(rest_ids)
                    cour_id = random.choice(cour_ids)
                    dist = round(random.uniform(1.0, 15.0), 2)
                    
                    # Random order time in last 7 days
                    days_ago = random.randint(0, 7)
                    hours_ago = random.randint(1, 23)
                    order_time = now - datetime.timedelta(days=days_ago, hours=hours_ago)
                    
                    # Calculate actual ETA with standard noise
                    actual_eta = round(15.0 + (dist * 2.5) + random.uniform(-5.0, 12.0), 1)
                    actual_eta = max(actual_eta, 12.0)
                    
                    # Predict ETA roughly matching
                    pred_eta = round(actual_eta + random.uniform(-3.5, 3.5), 1)
                    delivery_time = order_time + datetime.timedelta(minutes=actual_eta)
                    
                    # Log Order
                    q_order = (
                        "INSERT INTO Orders (order_id, customer_id, restaurant_id, courier_id, distance_km, order_time, delivery_time, predicted_eta, actual_eta, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Delivered')" if db_type == "sqlite"
                        else "INSERT INTO Orders (order_id, customer_id, restaurant_id, courier_id, distance_km, order_time, delivery_time, predicted_eta, actual_eta, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Delivered')"
                    )
                    cur.execute(q_order, (order_id, cust_id, rest_id, cour_id, dist, order_time, delivery_time, pred_eta, actual_eta))
                    
                    # Log Prediction
                    q_pred = (
                        "INSERT INTO Predictions (order_id, predicted_time, confidence_score, prediction_timestamp) VALUES (?, ?, ?, ?)" if db_type == "sqlite"
                        else "INSERT INTO Predictions (order_id, predicted_time, confidence_score, prediction_timestamp) VALUES (%s, %s, %s, %s)"
                    )
                    cur.execute(q_pred, (order_id, pred_eta, round(random.uniform(82, 98), 1), order_time))
                    
                conn.commit()
                conn.close()
                st.success(f"Successfully streamed {sim_count} new delivered transactions into the {db_type.upper()} database! Refreshing dashboard...")
                st.rerun()
            except Exception as e:
                st.error(f"Simulation failed: {e}")
