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
st.markdown("<h1 style='color: #ffffff; margin-bottom: 20px; font-family: \"Outfit\";'>⚡ Smart ETA Prediction Engine</h1>", unsafe_allow_html=True)
st.write("Calculate accurate delivery times and delay probabilities using state-of-the-art Machine Learning and live mapping systems.")

# Get restaurants and couriers from database for dynamic selectboxes
try:
    restaurants = db_helper.execute_select("SELECT * FROM Restaurants")
    couriers = db_helper.execute_select("SELECT * FROM Couriers")
except Exception as e:
    restaurants = []
    couriers = []
    st.error(f"Failed to fetch database reference data: {e}")

# Form split
col_map, col_details = st.columns([1, 1.2], gap="large")

with col_map:
    st.markdown("### 🗺️ Location & External Integrations")
    
    # 1. Restaurant selection
    if restaurants:
        rest_options = {r["name"]: r for r in restaurants}
        selected_rest_name = st.selectbox("Select Restaurant", list(rest_options.keys()))
        selected_rest = rest_options[selected_rest_name]
        
        # Parse restaurant location (lat, lon)
        try:
            rest_lat, rest_lon = map(float, selected_rest["location"].split(","))
        except Exception:
            rest_lat, rest_lon = 45.7725, -122.6801  # Default fallback
    else:
        selected_rest_name = "Mock Burger Shop"
        selected_rest = {"restaurant_id": "R0001"}
        rest_lat, rest_lon = 45.7725, -122.6801
        
    st.caption(f"Restaurant Coords: {rest_lat:.5f}, {rest_lon:.5f}")
    
    # 2. Customer location coords
    st.markdown("**Customer Coordinates Offset**")
    cust_offset_lat = st.slider("Customer Lat Offset (from Restaurant)", -0.150, 0.150, 0.045, format="%.4f")
    cust_offset_lon = st.slider("Customer Lon Offset (from Restaurant)", -0.150, 0.150, -0.035, format="%.4f")
    
    cust_lat = rest_lat + cust_offset_lat
    cust_lon = rest_lon + cust_offset_lon
    
    st.caption(f"Customer Coords: {cust_lat:.5f}, {cust_lon:.5f}")
    
    # 3. Dynamic route computation
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    if st.button("🗺️ Compute OSRM Driving Route Details"):
        with st.spinner("Querying OpenStreetMap Router..."):
            distance, travel_time = utils.get_route_details(rest_lat, rest_lon, cust_lat, cust_lon)
            st.session_state["osm_distance"] = distance
            st.session_state["osm_travel_time"] = travel_time
            st.success(f"OSRM Routing complete: {distance} km (Estimated driving: {travel_time} mins)")
            
    # Default calculated distance
    default_distance = st.session_state.get("osm_distance", 4.8)
    distance_km = st.number_input("Calculated Distance (km)", min_value=0.1, max_value=50.0, value=default_distance, step=0.1)
    
    # 4. Weather integration
    st.write("---")
    st.markdown("**🌤️ Real-Time Weather Integration**")
    fetch_live = st.checkbox("Query weather dynamically at location coords")
    
    weather_cond = "Sunny"
    if fetch_live:
        with st.spinner("Fetching weather details..."):
            weather_data = utils.get_weather_details(rest_lat, rest_lon)
            weather_cond = weather_data["Weather_Condition"]
            st.info(f"Live Weather fetched: {weather_cond} ({weather_data['Temperature_C']}°C, Visibility: {weather_data['Visibility_km']}km)")
    else:
        weather_cond = st.selectbox("Select Weather Condition Override", ["Sunny", "Cloudy", "Rainy", "Storm"])

with col_details:
    st.markdown("### 🛵 Order & Courier Parameters")
    
    # 1. Courier details
    if couriers:
        courier_options = {c["name"]: c for c in couriers}
        selected_cour_name = st.selectbox("Select Courier", list(courier_options.keys()))
        selected_cour = courier_options[selected_cour_name]
    else:
        selected_cour_name = "Mock Courier Rider"
        selected_cour = {"courier_id": "C0001", "experience": 5, "rating": 4.5, "vehicle_type": "Scooter"}
        
    st.caption(f"Profile: Experience={selected_cour.get('experience')} yrs, Vehicle={selected_cour.get('vehicle_type')}, Rating=★{selected_cour.get('rating')}")
    
    # sliders/inputs
    prep_time = st.slider("Restaurant Preparation Time (Min)", 5, 60, 18, help="Time to prepare, cook, and pack the meal")
    traffic_level = st.selectbox("Traffic Severity Level", ["Low", "Medium", "High", "Jam"])
    
    # Allows overriding vehicle for comparison
    vehicle_type = st.selectbox("Vehicle Type override", ["Bike", "Scooter", "Cycle"], index=["Bike", "Scooter", "Cycle"].index(selected_cour.get("vehicle_type", "Scooter")))
    
    # Exp and Age overrides
    courier_exp = st.slider("Courier Experience Override (Years)", 1, 15, int(selected_cour.get("experience", 5)))
    courier_age = st.slider("Courier Age Override (Years)", 18, 55, 27)
    
    # Temporal variables
    time_of_day = st.selectbox("Time of Day", ["Morning", "Afternoon", "Night"])
    day_of_week = st.selectbox("Day of Week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    
    is_peak = st.selectbox("Is Peak Hour?", ["Yes", "No"], index=1)
    is_festival = st.selectbox("Festival Day?", ["Yes", "No"], index=1)
    is_holiday = st.selectbox("Holiday?", ["Yes", "No"], index=1)
    
    # Order particulars
    order_size = st.selectbox("Order Size", ["Small", "Medium", "Large"], index=1)
    location_type = st.selectbox("Customer Handoff Location Type", ["Residential", "Commercial"])
    restaurant_rating = st.slider("Restaurant Rating (Stars)", 1.0, 5.0, float(selected_rest.get("rating", 4.5)), step=0.1)

st.write("---")

# Prediction Trigger
if st.button("⚡ CALCULATE SMART ETA & LATE RISK"):
    # Build payload matching models feature structure
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
    
    with st.spinner("Running deep predictive networks..."):
        try:
            # 1. Run prediction
            results = predict.predict_single_delivery(payload, save_to_db=True)
            
            # 2. Display prediction card
            st.markdown("### 🏆 Prediction Outputs")
            render_prediction_card(results)
            
            # 3. Compare Delivery Methods
            st.markdown("### 🚲 Mode of Transit Speed Comparison")
            modes_col1, modes_col2, modes_col3 = st.columns(3)
            
            # Build fast alternatives prediction
            eta_base = results["ETA_Minutes"]
            
            with modes_col1:
                # Cycle speed (slower)
                cycle_eta = round(eta_base * 1.35 if vehicle_type != "Cycle" else eta_base, 1)
                st.metric("🚲 Bicycle ETA", f"{cycle_eta} mins", delta=f"+{round(cycle_eta - eta_base, 1)}m" if vehicle_type != "Cycle" else "Active Mode", delta_color="inverse")
            with modes_col2:
                # Scooter speed
                scooter_eta = round(eta_base * 1.0 if vehicle_type == "Scooter" else (eta_base * 0.75 if vehicle_type == "Cycle" else eta_base * 1.15), 1)
                st.metric("🛵 Electric Scooter ETA", f"{scooter_eta} mins", delta=f"{round(scooter_eta - eta_base, 1)}m" if vehicle_type != "Scooter" else "Active Mode", delta_color="inverse")
            with modes_col3:
                # Bike speed (fastest)
                bike_eta = round(eta_base * 1.0 if vehicle_type == "Bike" else (eta_base * 0.85 if vehicle_type == "Scooter" else eta_base * 0.65), 1)
                st.metric("🏍️ Fuel Motorbike ETA", f"{bike_eta} mins", delta=f"{round(bike_eta - eta_base, 1)}m" if vehicle_type != "Bike" else "Active Mode", delta_color="inverse")
                
            # 4. Explainable AI: Plot local SHAP Waterfall chart
            st.write("---")
            st.markdown("### 🧠 Explainable AI: SHAP Prediction Breakdown")
            st.write("Why was this prediction made? Check the exact feature contributions added or subtracted from the baseline expected transit time.")
            
            shap_contribs = results["SHAP_Contributions"]
            base_val = results["SHAP_Base_Value"]
            
            if shap_contribs:
                # Create horizontal bar plot representing waterfall structure
                features_names = list(shap_contribs.keys())
                contributions_values = list(shap_contribs.values())
                
                # Sort by absolute contribution magnitude
                sorted_indices = sorted(range(len(contributions_values)), key=lambda k: abs(contributions_values[k]))
                features_names = [features_names[i] for i in sorted_indices]
                contributions_values = [contributions_values[i] for i in sorted_indices]
                
                # Custom colors: green for negative contribution (speed up), red for positive (slow down)
                bar_colors = ["#ef4444" if val > 0 else "#10b981" for val in contributions_values]
                
                fig = go.Figure(go.Bar(
                    x=contributions_values,
                    y=features_names,
                    orientation='h',
                    marker=dict(
                        color=bar_colors,
                        line=dict(color="rgba(0,0,0,0)", width=0)
                    ),
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
                
                st.info(f"💡 **Interpretability**: The base average delivery standard starts at **{base_val} minutes**. Summing all contributing factors above equals your final predicted ETA of **{results['ETA_Minutes']} minutes**.")
            else:
                st.info("SHAP contributions analysis not initialized.")
                
        except Exception as e:
            st.error(f"Inference Engine error: {e}. Please ensure you have generated raw data and trained the models.")
