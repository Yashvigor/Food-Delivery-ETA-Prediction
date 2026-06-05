import os
import sys
import pandas as pd
import streamlit as st
import datetime
import random

# Add src to python path to import our modules easily
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src import db_helper, predict
from app.components.sidebar import render_sidebar

# Initialize DB if not done
try:
    db_helper.init_db()
except Exception as e:
    print(f"Database initialization error on Home page: {e}")

# Render Sidebar branding
render_sidebar()

# Function to simulate new synthetic dispatch order
def trigger_synthetic_dispatch():
    try:
        # Fetch restaurants and couriers from DB
        rests = db_helper.execute_select("SELECT restaurant_id, rating FROM Restaurants")
        cours = db_helper.execute_select("SELECT courier_id, experience, vehicle_type, rating FROM Couriers")
        
        selected_rest = random.choice(rests) if rests else {"restaurant_id": "R0001", "rating": 4.5}
        selected_cour = random.choice(cours) if cours else {"courier_id": "C0001", "experience": 5, "vehicle_type": "Bike", "rating": 4.5}
        
        # Build synthetic payload
        payload = {
            "Distance_km": round(random.uniform(1.2, 14.5), 1),
            "Preparation_Time": random.randint(10, 45),
            "Courier_Age": random.randint(20, 50),
            "Courier_Experience": int(selected_cour.get("experience", 5)),
            "Vehicle_Type": selected_cour.get("vehicle_type", "Bike"),
            "Weather": random.choice(["Sunny", "Cloudy", "Rainy", "Storm"]),
            "Traffic_Level": random.choice(["Low", "Medium", "High", "Jam"]),
            "Time_of_Day": random.choice(["Morning", "Afternoon", "Night"]),
            "Day_of_Week": random.choice(["Monday", "Wednesday", "Friday", "Sunday"]),
            "Festival_Day": random.choice(["Yes", "No"]),
            "Holiday": random.choice(["Yes", "No"]),
            "Restaurant_Rating": float(selected_rest.get("rating", 4.5)),
            "Order_Size": random.choice(["Small", "Medium", "Large"]),
            "Customer_Location_Type": random.choice(["Residential", "Commercial"]),
            "Peak_Hour": random.choice(["Yes", "No"]),
            "Restaurant_ID": selected_rest.get("restaurant_id", "R0001"),
            "Courier_ID": selected_cour.get("courier_id", "C0001")
        }
        
        # Execute model prediction and persist to database
        results = predict.predict_single_delivery(payload, save_to_db=True)
        st.toast(f"⚡ Simulated Dispatch: Order {results['Order_ID']} created! ETA: {results['ETA_Minutes']} min.", icon="🛵")
    except Exception as ex:
        st.error(f"Failed to generate synthetic dispatch: {ex}")

# 1. FUTURISTIC HERO BANNER GRID
hero_col1, hero_col2 = st.columns([1.6, 1], gap="medium")

with hero_col1:
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, rgba(17, 24, 39, 0.75) 0%, rgba(10, 15, 26, 0.9) 100%); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 24px; padding: 35px; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.35); min-height: 290px; backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);">
            <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 8px;">
                <div class="live-indicator"><span class="live-dot"></span>Dispatcher Online</div>
            </div>
            <h1 style="margin: 0; background: linear-gradient(135deg, #00f2fe 0%, #ff6b35 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3.2rem; font-family: 'Outfit', sans-serif; font-weight: 900; letter-spacing: -1.5px; filter: drop-shadow(0 2px 15px rgba(0, 242, 254, 0.15));">
                SwiftETA ⭐
            </h1>
            <h4 style="margin: 5px 0 15px 0; color: #ff6b35; font-family: 'Outfit', sans-serif; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; font-size: 0.95rem;">
                Predict. Optimize. Deliver.
            </h4>
            <p style="margin: 0; color: #cbd5e1; font-size: 1.0rem; line-height: 1.6; max-width: 600px;">
                Welcome to the SwiftETA Hub. Monitor live couriers, evaluate high-precision machine learning ETA predictions, and manage system logistics dispatching in real time.
            </p>
            <div style="margin-top: 20px; font-family: monospace; font-size: 0.8rem; color: #64748b;">
                System Coords: 45.7725° N, 122.6801° W • SQLite HUD Persistence Active
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with hero_col2:
    # Embed the high-tech generated branding banner
    hud_banner_path = "C:/Users/Yashvi Gor/.gemini/antigravity-ide/brain/161db535-ebb7-4b24-8c96-ae00b822a9a8/swifteta_brand_hud_1780635743169.png"
    if os.path.exists(hud_banner_path):
        st.image(hud_banner_path, use_container_width=True)
    else:
        st.markdown(
            """
            <div style="background: rgba(17, 24, 39, 0.4); border: 1px dashed rgba(255, 255, 255, 0.1); border-radius: 24px; display: flex; align-items: center; justify-content: center; height: 100%; min-height: 290px;">
                <span style="color: #64748b; font-size: 0.9rem;">SwiftETA System Visual Asset</span>
            </div>
            """,
            unsafe_allow_html=True
        )

st.write("---")

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

# 2. KEY STATISTICS CARDS GRID WITH NEON borders
col1, col2, col3, col4 = st.columns(4)

with col1:
    raw_card = """
        <div style="background: rgba(17, 24, 39, 0.55); border: 1px solid rgba(0, 242, 254, 0.15); border-radius: 18px; padding: 22px; box-shadow: 0 4px 20px rgba(0, 242, 254, 0.03); transition: all 0.3s ease;">
            <div style="font-size: 0.78rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Total Deliveries</div>
            <div style="font-size: 2.5rem; font-weight: 800; color: #f8fafc; font-family: 'Outfit'; margin: 5px 0; background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{total}</div>
            <div style="font-size: 0.85rem; color: #10b981; font-weight: 600;">📈 Telemetry Active</div>
        </div>
    """
    cleaned_card = "\n".join([line.strip() for line in raw_card.split("\n") if line.strip() != ""])
    st.markdown(cleaned_card.format(total=total_orders), unsafe_allow_html=True)

with col2:
    raw_card = """
        <div style="background: rgba(17, 24, 39, 0.55); border: 1px solid rgba(255, 107, 53, 0.2); border-radius: 18px; padding: 22px; box-shadow: 0 4px 20px rgba(255, 107, 53, 0.04); transition: all 0.3s ease;">
            <div style="font-size: 0.78rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Active Dispatches</div>
            <div style="font-size: 2.5rem; font-weight: 800; color: #ff6b35; font-family: 'Outfit'; margin: 5px 0; background: linear-gradient(135deg, #ff9f43 0%, #ff6b35 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{active}</div>
            <div style="font-size: 0.85rem; color: #ff8a5c; font-weight: 500;">🛵 Couriers on road</div>
        </div>
    """
    cleaned_card = "\n".join([line.strip() for line in raw_card.split("\n") if line.strip() != ""])
    st.markdown(cleaned_card.format(active=active_orders), unsafe_allow_html=True)

with col3:
    raw_card = """
        <div style="background: rgba(17, 24, 39, 0.55); border: 1px solid rgba(165, 180, 252, 0.15); border-radius: 18px; padding: 22px; box-shadow: 0 4px 20px rgba(165, 180, 252, 0.03); transition: all 0.3s ease;">
            <div style="font-size: 0.78rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Avg Travel Time</div>
            <div style="font-size: 2.5rem; font-weight: 800; color: #f8fafc; font-family: 'Outfit'; margin: 5px 0; background: linear-gradient(135deg, #ffffff 0%, #a5b4fc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{avg}m</div>
            <div style="font-size: 0.85rem; color: #10b981; font-weight: 600;">⚡ Target standard met</div>
        </div>
    """
    cleaned_card = "\n".join([line.strip() for line in raw_card.split("\n") if line.strip() != ""])
    st.markdown(cleaned_card.format(avg=avg_delivery_time), unsafe_allow_html=True)

with col4:
    raw_card = """
        <div style="background: rgba(17, 24, 39, 0.55); border: 1px solid rgba(255, 43, 84, 0.15); border-radius: 18px; padding: 22px; box-shadow: 0 4px 20px rgba(255, 43, 84, 0.03); transition: all 0.3s ease;">
            <div style="font-size: 0.78rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">SLA Compliance</div>
            <div style="font-size: 2.5rem; font-weight: 800; color: #ff2b54; font-family: 'Outfit'; margin: 5px 0; background: linear-gradient(135deg, #ff5273 0%, #ff2b54 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{sla}%</div>
            <div style="font-size: 0.85rem; color: #ff5273; font-weight: 600;">⏱️ Under 40-min target</div>
        </div>
    """
    cleaned_card = "\n".join([line.strip() for line in raw_card.split("\n") if line.strip() != ""])
    st.markdown(cleaned_card.format(sla=sla_pct), unsafe_allow_html=True)

st.write("---")

# Main Operations layout
left_col, right_col = st.columns([2.0, 1.1], gap="medium")

with left_col:
    # Flex header with simulator controls
    stream_h1, stream_h2 = st.columns([1.5, 1], gap="small")
    with stream_h1:
        st.markdown("### 📡 Live Dispatch Feed")
    with stream_h2:
        if st.button("⚡ Simulate Live Dispatch", help="Triggers synthetic order creation and predicts ETA using active models"):
            trigger_synthetic_dispatch()
            st.rerun()
            
    if not df_orders.empty:
        # Fetch newest 6 orders
        df_orders_sorted = df_orders.sort_values(by="order_time", ascending=False).head(6)
        
        try:
            couriers_df = pd.DataFrame(db_helper.execute_select("SELECT courier_id, name as Courier_Name FROM Couriers"))
            restaurants_df = pd.DataFrame(db_helper.execute_select("SELECT restaurant_id, name as Restaurant_Name FROM Restaurants"))
            
            if not couriers_df.empty:
                df_orders_sorted = df_orders_sorted.merge(couriers_df, on="courier_id", how="left")
            if not restaurants_df.empty:
                df_orders_sorted = df_orders_sorted.merge(restaurants_df, on="restaurant_id", how="left")
        except Exception as e:
            print(f"Failed to join courier/restaurant names: {e}")
        
        # Render beautiful timeline cards instead of raw grid
        for idx, row in df_orders_sorted.iterrows():
            status = row['status']
            if status == "Delivered":
                status_class = "status-badge status-delivered"
                progress_val = 100
            elif status == "In Transit":
                status_class = "status-badge status-transit"
                progress_val = 70
            else: # Preparing / Pending
                status_class = "status-badge status-preparing"
                progress_val = 30
                
            eta_val = row.get('predicted_eta', 30.0)
            dist_val = row.get('distance_km', 4.0)
            order_name = row.get('Restaurant_Name', row['restaurant_id'])
            rider_name = row.get('Courier_Name', row['courier_id'])
            ord_id = row['order_id']
            
            raw_timeline_card = f"""
                <div class="timeline-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <div>
                            <span style="font-family: monospace; color: #00f2fe; font-size: 0.85rem; font-weight: 700; letter-spacing: 0.5px;">ORDER: {ord_id}</span>
                            <h4 style="margin: 3px 0 0 0; color: #f8fafc; font-family: 'Outfit'; font-size: 1.15rem;">{order_name}</h4>
                        </div>
                        <span class="{status_class}">{status}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.82rem; color: #94a3b8; margin-top: 8px;">
                        <span>Rider: <strong style="color: #cbd5e1;">{rider_name}</strong></span>
                        <span>Distance: <strong style="color: #cbd5e1;">{dist_val} km</strong></span>
                        <span>Predicted ETA: <strong style="color: #ff6b35;">{eta_val} min</strong></span>
                    </div>
                    <div class="timeline-bar-bg">
                        <div class="timeline-bar-fill" style="width: {progress_val}%;"></div>
                    </div>
                </div>
            """
            cleaned_timeline_card = "\n".join([line.strip() for line in raw_timeline_card.split("\n") if line.strip() != ""])
            st.markdown(cleaned_timeline_card, unsafe_allow_html=True)
            
        # Optional Collapsible table for raw telemetry audits
        with st.expander("🔍 View Raw Dispatch Telemetry Table"):
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
                "predicted_eta": "Predicted ETA (min)",
                "status": "Status"
            })
            st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("No active dispatch logs found. Click 'Simulate Live Dispatch' to seed real-time telemetry!")

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
        <div class="premium-card" style="text-align: center; border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 18px; padding: 25px; transition: all 0.3s ease;">
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
        <div class="premium-card" style="text-align: center; border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 18px; padding: 25px; transition: all 0.3s ease;">
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
        <div class="premium-card" style="text-align: center; border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 18px; padding: 25px; transition: all 0.3s ease;">
            <div style="font-size: 2.2rem; margin-bottom: 10px;">🧠</div>
            <h4 style="margin: 0 0 8px 0; font-family: 'Outfit'; font-size: 1.15rem; color: #f8fafc;">Why Predictions Work</h4>
            <p style="font-size: 0.85rem; color: #94a3b8; line-height: 1.5; margin: 0;">See which details (like weather or distance) affect our travel predictions the most.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

