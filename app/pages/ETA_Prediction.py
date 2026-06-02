import os
import sys
import pandas as pd
import streamlit as st
import datetime
import plotly.graph_objects as go

# Add src to python path to import our modules easily
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src import db_helper, utils, predict
from app.components.sidebar import render_sidebar
from app.components.prediction_card import render_prediction_card

# Render Sidebar branding
render_sidebar()

# Title
st.markdown(
    """
    <div style="margin-bottom: 25px;">
        <h1 style='color: #ffffff; font-family: "Outfit"; font-size: 2.8rem; margin-bottom: 5px; text-shadow: 0 0 15px rgba(0, 242, 254, 0.2);'>
            ⚡ Predictive Dispatch & ETA Engine
        </h1>
        <p style='color: #a0aec0; font-size: 1.1rem; margin-top: 0;'>
            Select delivery endpoints, fetch real-world traffic patterns, and execute high-fidelity machine learning evaluations.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Get restaurants and couriers from database for dynamic selectboxes
try:
    restaurants = db_helper.execute_select("SELECT * FROM Restaurants")
    couriers = db_helper.execute_select("SELECT * FROM Couriers")
except Exception as e:
    restaurants = []
    couriers = []
    st.error(f"Failed to fetch database reference data: {e}")

# MAIN WORKSPACE STRUCTURE
st.markdown("### 🎛️ Configure Delivery Parameters")
st.write("Complete the three operational setup steps below to query dispatch nodes and predict travel outcomes.")

# Create clean, modern tabs for parameter categories
tab_geo, tab_fleet, tab_time = st.tabs([
    "📍 Step 1: Geography & Weather", 
    "🛵 Step 2: Courier & Vehicle Fleet", 
    "📅 Step 3: Logistics & Timing Context"
])

# Define default dictionary for inputs
if "payload" not in st.session_state:
    st.session_state["payload"] = {}

# --- TAB 1: GEOGRAPHY & WEATHER ---
with tab_geo:
    st.markdown("#### 🌍 Delivery Coordinate Endpoints & Routing API")
    st.write("Compute exact city road networks and driving distances dynamically.")
    
    geo_col1, geo_col2 = st.columns(2)
    
    with geo_col1:
        if restaurants:
            rest_options = {r["name"]: r for r in restaurants}
            selected_rest_name = st.selectbox("Select Dispatch Restaurant", list(rest_options.keys()))
            selected_rest = rest_options[selected_rest_name]
            try:
                rest_lat, rest_lon = map(float, selected_rest["location"].split(","))
            except Exception:
                rest_lat, rest_lon = 45.7725, -122.6801
        else:
            selected_rest_name = "The Burger Capital (Default)"
            selected_rest = {"restaurant_id": "R0001"}
            rest_lat, rest_lon = 45.7725, -122.6801
            
        st.markdown(
            f"""
            <div style="background: rgba(30, 41, 59, 0.35); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 12px 18px; margin-bottom: 15px;">
                <span style="font-size: 0.8rem; color: #718096; text-transform: uppercase;">Restaurant Node Coords</span><br/>
                <span style="font-family: monospace; color: #00f2fe; font-weight: 600; font-size: 1.05rem;">{rest_lat:.5f}, {rest_lon:.5f}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with geo_col2:
        st.markdown("<span style='font-size: 0.9rem; font-weight: 600; color: #ffffff;'>Customer Coordinate Offset</span>", unsafe_allow_html=True)
        cust_offset_lat = st.slider("Latitude Offset (Delta)", -0.150, 0.150, 0.045, format="%.4f", key="lat_offset_slider")
        cust_offset_lon = st.slider("Longitude Offset (Delta)", -0.150, 0.150, -0.035, format="%.4f", key="lon_offset_slider")
        
        cust_lat = rest_lat + cust_offset_lat
        cust_lon = rest_lon + cust_offset_lon
        
        st.markdown(
            f"""
            <div style="background: rgba(30, 41, 59, 0.35); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 12px 18px; margin-bottom: 15px;">
                <span style="font-size: 0.8rem; color: #718096; text-transform: uppercase;">Customer Endpoint Coords</span><br/>
                <span style="font-family: monospace; color: #a5b4fc; font-weight: 600; font-size: 1.05rem;">{cust_lat:.5f}, {cust_lon:.5f}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    st.write("---")
    
    route_col1, route_col2 = st.columns([1.2, 1])
    
    with route_col1:
        st.markdown("**⚡ Live OSRM Route Navigation**")
        st.write("Calculates real-world city road routes utilizing OpenStreetMap's route calculation nodes.")
        
        if st.button("🗺️ Compute OSRM Driving Distance & Time"):
            with st.spinner("Streaming OSRM nodes..."):
                distance, travel_time = utils.get_route_details(rest_lat, rest_lon, cust_lat, cust_lon)
                st.session_state["osm_distance"] = distance
                st.session_state["osm_travel_time"] = travel_time
                st.success(f"OSRM calculations complete! {distance} km driving route found.")
                
        default_distance = st.session_state.get("osm_distance", 4.8)
        distance_km = st.number_input("Final Route Distance (km)", min_value=0.1, max_value=50.0, value=default_distance, step=0.1)

    with route_col2:
        st.markdown("**🌤️ Real-Time Environment Metrics**")
        st.write("Fetches temperature, cloud matrices, and rain status dynamically via OpenWeatherMap APIs.")
        
        fetch_live = st.checkbox("Query weather live at Restaurant coordinates")
        
        if fetch_live:
            with st.spinner("Fetching coordinates weather..."):
                w_data = utils.get_weather_details(rest_lat, rest_lon)
                weather_cond = w_data["Weather_Condition"]
                st.success(f"Live Weather: {weather_cond} ({w_data['Temperature_C']}°C)")
        else:
            weather_cond = st.selectbox("Weather Condition Override", ["Sunny", "Cloudy", "Rainy", "Storm"])

# --- TAB 2: COURIER & FLEET LOGISTICS ---
with tab_fleet:
    st.markdown("#### 🛵 Dispatch Courier Profile & Vehicle Mode")
    st.write("Analyze rider demographics and transit capabilities.")
    
    fleet_col1, fleet_col2 = st.columns(2)
    
    with fleet_col1:
        if couriers:
            courier_options = {c["name"]: c for c in couriers}
            selected_cour_name = st.selectbox("Select Active Dispatch Courier", list(courier_options.keys()))
            selected_cour = courier_options[selected_cour_name]
        else:
            selected_cour_name = "Alex Mercer (Default)"
            selected_cour = {"courier_id": "C0001", "experience": 8, "rating": 4.8, "vehicle_type": "Bike"}
            
        st.markdown(
            f"""
            <div style="background: rgba(30, 41, 59, 0.45); border: 1px solid rgba(255,255,255,0.05); border-radius: 16px; padding: 20px;">
                <h5 style="margin-top:0; color: #ffffff; font-family: 'Outfit';">🛵 Courier Information Card</h5>
                <div style="display: flex; flex-direction: column; gap: 8px; font-size: 0.9rem; color: #a0aec0;">
                    <div>• Name: <b style="color:#ffffff;">{selected_cour_name}</b></div>
                    <div>• Registered Vehicle: <b style="color:#00f2fe;">{selected_cour.get('vehicle_type')}</b></div>
                    <div>• Industry Experience: <b style="color:#ffffff;">{selected_cour.get('experience')} Years</b></div>
                    <div>• Courier Quality Rating: <b style="color:#facc15;">★ {selected_cour.get('rating')} / 5.0</b></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with fleet_col2:
        vehicle_type = st.selectbox(
            "Override Fleet Vehicle Mode", 
            ["Bike", "Scooter", "Cycle"], 
            index=["Bike", "Scooter", "Cycle"].index(selected_cour.get("vehicle_type", "Scooter"))
        )
        courier_exp = st.slider("Override Courier Experience (Years)", 1, 15, int(selected_cour.get("experience", 5)))
        courier_age = st.slider("Override Courier Rider Age", 18, 55, 27)

# --- TAB 3: CONTEXT & TIMING ---
with tab_time:
    st.markdown("#### 📅 Operations Timeline & Order Context")
    st.write("Quantify orders timing variables and restaurant preparation estimates.")
    
    time_col1, time_col2 = st.columns(2)
    
    with time_col1:
        prep_time = st.slider("Restaurant Prep Time (Minutes)", 5, 60, 18, help="Expected time for kitchen food prep")
        traffic_level = st.selectbox("Current City Traffic Level", ["Low", "Medium", "High", "Jam"])
        time_of_day = st.selectbox("Dispatch Time of Day", ["Morning", "Afternoon", "Night"])
        day_of_week = st.selectbox("Dispatch Day of Week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        
    with time_col2:
        is_peak = st.selectbox("Is Peak Hour?", ["Yes", "No"], index=1)
        is_festival = st.selectbox("Festival Day?", ["Yes", "No"], index=1)
        is_holiday = st.selectbox("Official Public Holiday?", ["Yes", "No"], index=1)
        
        order_size = st.selectbox("Order Basket Size", ["Small", "Medium", "Large"], index=1)
        location_type = st.selectbox("Handoff Destination Type", ["Residential", "Commercial"])
        restaurant_rating = st.slider("Restaurant Standard Rating (Stars)", 1.0, 5.0, float(selected_rest.get("rating", 4.5)), step=0.1)

# Build parameter dictionary for execution
payload = {
    "Distance_km": distance_km,
    "Preparation_Time": prep_time,
    "Courier_Age": courier_age,
    "Courier_Experience": courier_exp,
    "Vehicle_Type": vehicle_type,
    "Weather": weather_cond,
    "Traffic_Level": traffic_level,
    "Time_of_Day": time_of_day,
    "Day_of_Week": day_of_week,
    "Festival_Day": is_festival,
    "Holiday": is_holiday,
    "Restaurant_Rating": restaurant_rating,
    "Order_Size": order_size,
    "Customer_Location_Type": location_type,
    "Peak_Hour": is_peak,
    "Restaurant_ID": selected_rest.get("restaurant_id", "R0001"),
    "Courier_ID": selected_cour.get("courier_id", "C0001")
}

st.write("---")

# Predict Button
st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)
if st.button("⚡ EXECUTE ML DISPATCH EVALUATION"):
    with st.spinner("Processing dual ML model estimates..."):
        try:
            # 1. Run predictions
            results = predict.predict_single_delivery(payload, save_to_db=True)
            
            # Save results in session state to remain stable
            st.session_state["latest_results"] = results
            st.success("Calculations complete! Outputs generated below.")
        except Exception as e:
            st.error(f"Inference Engine error: {e}. Please ensure you have generated raw data and trained the models.")

# --- DYNAMIC OUTPUT DASHBOARD HUD ---
if "latest_results" in st.session_state:
    results = st.session_state["latest_results"]
    
    st.markdown(
        """
        <div style="margin-top: 30px; border-left: 4px solid #00f2fe; padding-left: 15px; margin-bottom: 20px;">
            <h3 style="color: #ffffff; font-family: 'Outfit'; margin: 0;">📊 Predictive Dispatch Results HUD</h3>
            <p style="color: #718096; font-size: 0.9rem; margin: 3px 0 0 0;">Visualizing real-time calculations and feature risk weightings.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 1. Display glassmorphic prediction card
    render_prediction_card(results)
    
    # 2. Display vehicle mode comparisons
    st.markdown("#### 🏍️ Speed Mode Comparative Transit Analysis")
    modes_col1, modes_col2, modes_col3 = st.columns(3)
    eta_base = results["ETA_Minutes"]
    
    with modes_col1:
        cycle_eta = round(eta_base * 1.35 if vehicle_type != "Cycle" else eta_base, 1)
        st.metric("🚲 Bicycle Mode ETA", f"{cycle_eta}m", delta=f"+{round(cycle_eta - eta_base, 1)}m" if vehicle_type != "Cycle" else "Active Mode", delta_color="inverse")
    with modes_col2:
        scooter_eta = round(eta_base * 1.0 if vehicle_type == "Scooter" else (eta_base * 0.75 if vehicle_type == "Cycle" else eta_base * 1.15), 1)
        st.metric("🛵 Electric Scooter ETA", f"{scooter_eta}m", delta=f"{round(scooter_eta - eta_base, 1)}m" if vehicle_type != "Scooter" else "Active Mode", delta_color="inverse")
    with modes_col3:
        bike_eta = round(eta_base * 1.0 if vehicle_type == "Bike" else (eta_base * 0.85 if vehicle_type == "Scooter" else eta_base * 0.65), 1)
        st.metric("🏍️ Motorbike Mode ETA", f"{bike_eta}m", delta=f"{round(bike_eta - eta_base, 1)}m" if vehicle_type != "Bike" else "Active Mode", delta_color="inverse")
        
    st.write("---")
    
    # 3. Explainable AI waterfall
    st.markdown("#### 🧠 Explainable AI: SHAP Prediction Breakdown")
    st.write("This local SHAP waterfall diagram explains the exact quantity of minutes added or subtracted from standard averages.")
    
    shap_contribs = results["SHAP_Contributions"]
    base_val = results["SHAP_Base_Value"]
    
    if shap_contribs:
        features_names = list(shap_contribs.keys())
        contributions_values = list(shap_contribs.values())
        
        # Sort values by impact
        sorted_indices = sorted(range(len(contributions_values)), key=lambda k: abs(contributions_values[k]))
        features_names = [features_names[i] for i in sorted_indices]
        contributions_values = [contributions_values[i] for i in sorted_indices]
        
        bar_colors = ["#ef4444" if val > 0 else "#10b981" for val in contributions_values]
        
        fig = go.Figure(go.Bar(
            x=contributions_values,
            y=features_names,
            orientation='h',
            marker=dict(color=bar_colors),
            text=[f"+{v}m" if v > 0 else f"{v}m" for v in contributions_values],
            textposition='outside'
        ))
        
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#a0aec0",
            xaxis=dict(
                title="ETA Contribution (Minutes)",
                gridcolor="rgba(255,255,255,0.05)",
                zeroline=True,
                zerolinecolor="rgba(255,255,255,0.2)"
            ),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            margin=dict(l=150, r=40, t=20, b=20),
            height=max(200, len(features_names) * 35)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info(f"💡 **Interpretability Guide**: Operational baseline standard starts at **{base_val} minutes**. Combining all environmental and transit feature factors above results in the final predicted dispatch ETA of **{results['ETA_Minutes']} minutes**.")
    else:
        st.info("SHAP contributions analysis not initialized.")
else:
    # Warm user onboarding panel
    st.markdown(
        """
        <div style="background: rgba(30, 41, 59, 0.2); border: 1px dashed rgba(255, 255, 255, 0.08); border-radius: 20px; padding: 40px; text-align: center; margin-top: 30px;">
            <div style="font-size: 3rem; margin-bottom: 15px;">🔮</div>
            <h4 style="color: #ffffff; font-family: 'Outfit'; margin: 0 0 5px 0;">Awaiting Parameter Configurations</h4>
            <p style="color: #718096; font-size: 0.95rem; max-width: 500px; margin: 0 auto;">
                Adjust steps 1, 2, and 3 in the tab console above, then click the glow button to run machine learning predictions.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
