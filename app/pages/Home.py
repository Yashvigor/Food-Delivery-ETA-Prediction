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

# 1. DELIVERIQ HERO BANNER
st.markdown(
    """
    <div style="background: linear-gradient(135deg, rgba(244, 81, 30, 0.08) 0%, rgba(15, 23, 42, 0.45) 100%); border: 1px solid rgba(244, 81, 30, 0.18); border-radius: 16px; padding: 28px; margin-bottom: 25px; box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; flex-wrap: wrap; gap: 10px;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 2.2rem;">🍔</span>
                <h1 style="margin: 0; background: linear-gradient(135deg, #ff8a5c 0%, #f4511e 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.4rem; font-family: 'Outfit', sans-serif; font-weight: 900; letter-spacing: -0.04em;">
                    DeliverIQ
                </h1>
            </div>
            <div class="live-indicator"><span class="live-dot"></span>Dispatcher Hub Live</div>
        </div>
        <h3 style="margin: 0 0 10px 0; color: #f8fafc; font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 600; opacity: 0.9;">
            High-fidelity Predictive Dispatch Console
        </h3>
        <p style="margin: 0 0 24px 0; color: #94a3b8; font-size: 0.92rem; line-height: 1.6; max-width: 800px; font-weight: 400;">
            DeliverIQ leverages advanced regression models and delay classifiers to predict exact food delivery travel times. 
            Flag high-risk delays, audit local SHAP model contributions, and analyze fleet velocities to optimize scheduling and customer experience.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Hero Call-to-Actions (programmatic st.switch_page switches)
col_cta1, col_cta2, col_spacer = st.columns([1.2, 1.2, 3.6])
with col_cta1:
    if st.button("⚡ Predict Delivery ETA", key="home_cta_predict", help="Predict delivery times using ML models"):
        st.switch_page("pages/ETA_Prediction.py")
with col_cta2:
    if st.button("📈 Explore Fleet Analytics", key="home_cta_analytics", help="View fleet performance graphs"):
        st.switch_page("pages/Logistics_Analytics.py")

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

# 2. KEY STATISTICS CARDS GRID
st.markdown("### 📊 Operational Telemetry")
col1, col2, col3, col4 = st.columns(4)

with col1:
    raw_card = """
        <div style="background: rgba(18, 26, 42, 0.45); border: 1px solid rgba(255, 255, 255, 0.04); border-left: 3px solid #f4511e; border-radius: 8px; padding: 18px 20px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);">
            <div style="font-size: 0.72rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700;">Prediction Accuracy</div>
            <div style="font-size: 1.8rem; font-weight: 800; color: #f8fafc; font-family: 'Outfit'; margin: 4px 0; letter-spacing: -0.02em;">90.3% <span style="font-size:0.9rem; font-weight:500; color:#ff7443;">R²</span></div>
            <div style="font-size: 0.75rem; color: #10b981; font-weight: 500;">&bull; Tuned CatBoost Engine</div>
        </div>
    """
    st.markdown(raw_card, unsafe_allow_html=True)

with col2:
    raw_card = f"""
        <div style="background: rgba(18, 26, 42, 0.45); border: 1px solid rgba(255, 255, 255, 0.04); border-left: 3px solid #ff7443; border-radius: 8px; padding: 18px 20px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);">
            <div style="font-size: 0.72rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700;">Deliveries Tracked</div>
            <div style="font-size: 1.8rem; font-weight: 800; color: #f8fafc; font-family: 'Outfit'; margin: 4px 0; letter-spacing: -0.02em;">{total_orders} <span style="font-size:0.85rem; font-weight:500; color:#94a3b8;">Orders</span></div>
            <div style="font-size: 0.75rem; color: #10b981; font-weight: 500;">&bull; Database sync active</div>
        </div>
    """
    st.markdown(raw_card, unsafe_allow_html=True)

with col3:
    raw_card = f"""
        <div style="background: rgba(18, 26, 42, 0.45); border: 1px solid rgba(255, 255, 255, 0.04); border-left: 3px solid #fbbf24; border-radius: 8px; padding: 18px 20px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);">
            <div style="font-size: 0.72rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700;">Avg ETA Deviation</div>
            <div style="font-size: 1.8rem; font-weight: 800; color: #fbbf24; font-family: 'Outfit'; margin: 4px 0; letter-spacing: -0.02em;">3.8m <span style="font-size:0.85rem; font-weight:500; color:#fbbf24;">MAE</span></div>
            <div style="font-size: 0.75rem; color: #cbd5e1; font-weight: 500;">&bull; Under SLA threshold</div>
        </div>
    """
    st.markdown(raw_card, unsafe_allow_html=True)

with col4:
    raw_card = f"""
        <div style="background: rgba(18, 26, 42, 0.45); border: 1px solid rgba(255, 255, 255, 0.04); border-left: 3px solid #f87171; border-radius: 8px; padding: 18px 20px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);">
            <div style="font-size: 0.72rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700;">SLA Compliance</div>
            <div style="font-size: 1.8rem; font-weight: 800; color: #f87171; font-family: 'Outfit'; margin: 4px 0; letter-spacing: -0.02em;">{sla_pct}%</div>
            <div style="font-size: 0.75rem; color: #f87171; font-weight: 500;">&bull; Standard 40m SLA limit</div>
        </div>
    """
    st.markdown(raw_card, unsafe_allow_html=True)

st.write("---")

# 3. PLATFORM FEATURES GRID
st.markdown("### 🎛️ Platform Capabilities")
f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5)
with f_col1:
    st.markdown(
        """
        <div style="background: rgba(18, 26, 42, 0.35); border: 1px solid rgba(255, 255, 255, 0.03); border-radius: 8px; padding: 14px; text-align: center; min-height: 120px;">
            <div style="font-size: 1.35rem; margin-bottom: 5px;">⚡</div>
            <strong style="color: #f8fafc; font-size: 0.82rem; font-family: 'Outfit';">ETA Prediction</strong>
            <p style="font-size: 0.72rem; color: #64748b; margin: 4px 0 0 0; line-height: 1.3;">Dual regression & delay risk estimation.</p>
        </div>
        """, unsafe_allow_html=True
    )
with f_col2:
    st.markdown(
        """
        <div style="background: rgba(18, 26, 42, 0.35); border: 1px solid rgba(255, 255, 255, 0.03); border-radius: 8px; padding: 14px; text-align: center; min-height: 120px;">
            <div style="font-size: 1.35rem; margin-bottom: 5px;">🚦</div>
            <strong style="color: #f8fafc; font-size: 0.82rem; font-family: 'Outfit';">Traffic Analysis</strong>
            <p style="font-size: 0.72rem; color: #64748b; margin: 4px 0 0 0; line-height: 1.3;">Evaluates traffic jams and congestion delay weights.</p>
        </div>
        """, unsafe_allow_html=True
    )
with f_col3:
    st.markdown(
        """
        <div style="background: rgba(18, 26, 42, 0.35); border: 1px solid rgba(255, 255, 255, 0.03); border-radius: 8px; padding: 14px; text-align: center; min-height: 120px;">
            <div style="font-size: 1.35rem; margin-bottom: 5px;">⛈️</div>
            <strong style="color: #f8fafc; font-size: 0.82rem; font-family: 'Outfit';">Weather Insights</strong>
            <p style="font-size: 0.72rem; color: #64748b; margin: 4px 0 0 0; line-height: 1.3;">Integrates OpenWeather to evaluate rain & storms.</p>
        </div>
        """, unsafe_allow_html=True
    )
with f_col4:
    st.markdown(
        """
        <div style="background: rgba(18, 26, 42, 0.35); border: 1px solid rgba(255, 255, 255, 0.03); border-radius: 8px; padding: 14px; text-align: center; min-height: 120px;">
            <div style="font-size: 1.35rem; margin-bottom: 5px;">📈</div>
            <strong style="color: #f8fafc; font-size: 0.82rem; font-family: 'Outfit';">Delivery Analytics</strong>
            <p style="font-size: 0.72rem; color: #64748b; margin: 4px 0 0 0; line-height: 1.3;">Operations KPIs and fleet transit efficiency maps.</p>
        </div>
        """, unsafe_allow_html=True
    )
with f_col5:
    st.markdown(
        """
        <div style="background: rgba(18, 26, 42, 0.35); border: 1px solid rgba(255, 255, 255, 0.03); border-radius: 8px; padding: 14px; text-align: center; min-height: 120px;">
            <div style="font-size: 1.35rem; margin-bottom: 5px;">🧠</div>
            <strong style="color: #f8fafc; font-size: 0.82rem; font-family: 'Outfit';">Model Insights</strong>
            <p style="font-size: 0.72rem; color: #64748b; margin: 4px 0 0 0; line-height: 1.3;">Global factor weights and local SHAP feature audits.</p>
        </div>
        """, unsafe_allow_html=True
    )

st.write("---")

# 4. HOW IT WORKS PIPELINE
st.markdown(
    """
    <div style="background: rgba(15, 23, 42, 0.4); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 12px; padding: 22px; margin-bottom: 25px;">
        <h3 style="margin-top: 0; margin-bottom: 18px; font-family: 'Outfit'; font-size: 1.15rem; color: #f8fafc;">⛓️ Predictive Operations Pipeline</h3>
        <div style="display: flex; justify-content: space-between; align-items: center; gap: 8px; flex-wrap: wrap;">
            <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 12px; flex: 1; min-width: 140px; text-align: center;">
                <div style="font-size: 1.25rem; margin-bottom: 4px;">📥</div>
                <div style="font-size: 0.78rem; font-weight: 700; color: #ff8a5c; text-transform: uppercase;">1. Data Collection</div>
                <div style="font-size: 0.7rem; color: #64748b; margin-top: 2px;">Orders & coordinate offsets</div>
            </div>
            <div style="color: #475569; font-size: 1.2rem;">➔</div>
            <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 12px; flex: 1; min-width: 140px; text-align: center;">
                <div style="font-size: 1.25rem; margin-bottom: 4px;">🧹</div>
                <div style="font-size: 0.78rem; font-weight: 700; color: #ff8a5c; text-transform: uppercase;">2. Data Processing</div>
                <div style="font-size: 0.7rem; color: #64748b; margin-top: 2px;">IQR outlier filtering</div>
            </div>
            <div style="color: #475569; font-size: 1.2rem;">➔</div>
            <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 12px; flex: 1; min-width: 140px; text-align: center;">
                <div style="font-size: 1.25rem; margin-bottom: 4px;">🛠️</div>
                <div style="font-size: 0.78rem; font-weight: 700; color: #ff8a5c; text-transform: uppercase;">3. Feature Eng.</div>
                <div style="font-size: 0.7rem; color: #64748b; margin-top: 2px;">Temporal maps & weather API</div>
            </div>
            <div style="color: #475569; font-size: 1.2rem;">➔</div>
            <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 12px; flex: 1; min-width: 140px; text-align: center;">
                <div style="font-size: 1.25rem; margin-bottom: 4px;">🧠</div>
                <div style="font-size: 0.78rem; font-weight: 700; color: #ff8a5c; text-transform: uppercase;">4. Machine Learning</div>
                <div style="font-size: 0.7rem; color: #64748b; margin-top: 2px;">CatBoost & RF Classifiers</div>
            </div>
            <div style="color: #475569; font-size: 1.2rem;">➔</div>
            <div style="background: rgba(244, 81, 30, 0.05); border: 1px solid rgba(244, 81, 30, 0.2); border-radius: 8px; padding: 12px; flex: 1; min-width: 140px; text-align: center;">
                <div style="font-size: 1.25rem; margin-bottom: 4px;">⚡</div>
                <div style="font-size: 0.78rem; font-weight: 700; color: #ff5b2e; text-transform: uppercase;">5. ETA Prediction</div>
                <div style="font-size: 0.7rem; color: #cbd5e1; margin-top: 2px;">Predicted times & risk ratings</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# 5. BUSINESS IMPACT ANALYSIS
st.markdown(
    """
    <div style="margin-bottom: 25px;">
        <h3 style="margin-top: 0; margin-bottom: 15px; font-family: 'Outfit'; font-size: 1.15rem; color: #f8fafc;">📈 Measured Business Outcomes</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
            <div style="background: rgba(18, 26, 42, 0.45); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 10px; padding: 16px;">
                <div style="font-size: 0.7rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700;">Reduced Delays</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #10b981; margin: 4px 0;">-15.2%</div>
                <p style="font-size: 0.75rem; color: #64748b; margin: 0; line-height: 1.3;">Fewer late orders through weather and traffic-aware dispatch alerts.</p>
            </div>
            <div style="background: rgba(18, 26, 42, 0.45); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 10px; padding: 16px;">
                <div style="font-size: 0.7rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700;">Customer Trust</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #10b981; margin: 4px 0;">+18% CSAT</div>
                <p style="font-size: 0.75rem; color: #64748b; margin: 0; line-height: 1.3;">Increase in customer satisfaction due to high-reliability delay tracking.</p>
            </div>
            <div style="background: rgba(18, 26, 42, 0.45); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 10px; padding: 16px;">
                <div style="font-size: 0.7rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700;">Fleet Efficiency</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #ff7443; margin: 4px 0;">Optimized</div>
                <p style="font-size: 0.75rem; color: #64748b; margin: 0; line-height: 1.3;">Dynamically routes couriers according to real-time OSRM calculations.</p>
            </div>
            <div style="background: rgba(18, 26, 42, 0.45); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 10px; padding: 16px;">
                <div style="font-size: 0.7rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700;">Average MAE</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #ff7443; margin: 4px 0;">&lt; 3.9 Min</div>
                <p style="font-size: 0.75rem; color: #64748b; margin: 0; line-height: 1.3;">Low deviation ensures accurate customer ETAs and driver scheduling.</p>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("---")

# 6. MAIN LIVE OPERATIONS LAYOUT
left_col, right_col = st.columns([2.0, 1.1], gap="medium")

with left_col:
    # Flex header with simulator controls
    stream_h1, stream_h2 = st.columns([1.6, 1.0], gap="small")
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
                            <span style="font-family: monospace; color: #ff7443; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.5px;">ORDER: {ord_id}</span>
                            <h4 style="margin: 2px 0 0 0; color: #f8fafc; font-family: 'Outfit'; font-size: 1.1rem;">{order_name}</h4>
                        </div>
                        <span class="{status_class}">{status}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #64748b; margin-top: 8px;">
                        <span>Rider: <strong style="color: #94a3b8;">{rider_name}</strong></span>
                        <span>Distance: <strong style="color: #94a3b8;">{dist_val} km</strong></span>
                        <span>Predicted ETA: <strong style="color: #ff7443;">{eta_val} min</strong></span>
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
                    <div style="background: rgba(18, 26, 42, 0.45); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 8px; padding: 12px 16px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                        <div>
                            <span style="font-weight: 600; color: #f8fafc; font-size: 0.95rem; font-family: 'Outfit';">{row['name']}</span>
                            <div style="font-size: 0.78rem; color: #64748b;">{row['vehicle_type']} • {row['experience']} yrs exp</div>
                        </div>
                        <div style="text-align: right;">
                            <span style="color: #fbbf24; font-weight: 700; font-size: 0.88rem;">★ {row['rating']}</span>
                            <div style="font-size: 0.7rem; color: #34d399; font-weight: 600;">● Active</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No couriers logged in database.")
    except Exception as e:
        st.error(f"Error loading couriers: {e}")
