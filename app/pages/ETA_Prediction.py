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
        <h1 style='color: #f8fafc; font-family: "Outfit"; font-size: 2.5rem; margin-bottom: 5px; text-shadow: 0 0 15px rgba(244, 81, 30, 0.15);'>
            ⚡ DeliverIQ ETA Engine
        </h1>
        <p style='color: #94a3b8; font-size: 1.05rem; margin-top: 0;'>
            Configure logistics telemetry parameters to predict delivery travel times and assess delays.
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

# Helper to format SHAP values in plain English
def get_factor_interpretations(shap_contribs: dict) -> list:
    interpretations = []
    if not shap_contribs:
        return interpretations
    sorted_features = sorted(shap_contribs.items(), key=lambda item: abs(item[1]), reverse=True)
    
    for feat, val in sorted_features[:3]:
        rounded_val = abs(round(val, 1))
        direction = "added" if val > 0 else "subtracted"
        direction_color = "#ef4444" if val > 0 else "#10b981"
        
        if feat == "Distance_km":
            interpretations.append(f"• **Delivery Distance** {direction} <strong style='color:{direction_color};'>{rounded_val} mins</strong> to transit.")
        elif feat == "Preparation_Time":
            interpretations.append(f"• **Kitchen preparation time** {direction} <strong style='color:{direction_color};'>{rounded_val} mins</strong> to preparation.")
        elif feat == "Traffic_Level":
            interpretations.append(f"• **Traffic congestion level** {direction} <strong style='color:{direction_color};'>{rounded_val} mins</strong> due to bottlenecks.")
        elif feat == "Weather":
            interpretations.append(f"• **Local weather conditions** {direction} <strong style='color:{direction_color};'>{rounded_val} mins</strong> to transit.")
        elif feat == "Courier_Experience":
            interpretations.append(f"• **Courier experience** {direction} <strong style='color:{direction_color};'>{rounded_val} mins</strong> due to rider proficiency.")
        elif feat == "Vehicle_Type":
            interpretations.append(f"• **Vehicle type select** {direction} <strong style='color:{direction_color};'>{rounded_val} mins</strong>.")
        elif feat == "Peak_Hour":
            interpretations.append(f"• **Peak hour operation** {direction} <strong style='color:{direction_color};'>{rounded_val} mins</strong>.")
        else:
            feat_name = feat.replace('_', ' ').capitalize()
            interpretations.append(f"• **{feat_name}** {direction} <strong style='color:{direction_color};'>{rounded_val} mins</strong>.")
            
    return interpretations

# MAIN WORKSPACE STRUCTURE
col_left, col_right = st.columns([1.0, 1.25], gap="large")

with col_left:
    st.markdown("### 🎛️ Parameter HUD")
    
    # 1. Delivery Information Container
    with st.container(border=True):
        st.markdown("#### 📍 1. Delivery Node Information")
        if restaurants:
            rest_options = {r["name"]: r for r in restaurants}
            selected_rest_name = st.selectbox("Select Restaurant", list(rest_options.keys()))
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
            <div style="background: rgba(17, 24, 39, 0.45); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 8px; padding: 10px 14px; margin-bottom: 15px;">
                <span style="font-size: 0.72rem; color: #64748b; text-transform: uppercase; font-weight: 600;">Restaurant Node Coordinates</span><br/>
                <span style="font-family: monospace; color: #ff7443; font-weight: 600; font-size: 0.95rem;">{rest_lat:.5f}, {rest_lon:.5f}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<span style='font-size: 0.82rem; font-weight: 600; color: #cbd5e1;'>Customer Coordinates Delta</span>", unsafe_allow_html=True)
        cust_offset_lat = st.slider("Latitude Offset", -0.150, 0.150, 0.045, step=0.001, format="%.4f", key="lat_offset_slider")
        cust_offset_lon = st.slider("Longitude Offset", -0.150, 0.150, -0.035, step=0.001, format="%.4f", key="lon_offset_slider")
        
        cust_lat = rest_lat + cust_offset_lat
        cust_lon = rest_lon + cust_offset_lon

        st.markdown(
            f"""
            <div style="background: rgba(17, 24, 39, 0.45); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 8px; padding: 10px 14px; margin-bottom: 12px;">
                <span style="font-size: 0.72rem; color: #64748b; text-transform: uppercase; font-weight: 600;">Customer Node Coordinates</span><br/>
                <span style="font-family: monospace; color: #38bdf8; font-weight: 600; font-size: 0.95rem;">{cust_lat:.5f}, {cust_lon:.5f}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("<span style='font-size: 0.82rem; font-weight: 600; color: #cbd5e1;'>Route Distance (km)</span>", unsafe_allow_html=True)
        r_calc1, r_calc2 = st.columns([1.5, 1])
        with r_calc1:
            if st.button("🗺️ Query Road Network (OSRM)", key="osrm_query"):
                with st.spinner("Calling OSRM Route API..."):
                    distance, travel_time = utils.get_route_details(rest_lat, rest_lon, cust_lat, cust_lon)
                    st.session_state["osm_distance"] = distance
                    st.session_state["osm_travel_time"] = travel_time
                    st.toast(f"Route Found: {distance} km via road network.", icon="🗺️")
        with r_calc2:
            default_distance = st.session_state.get("osm_distance", 4.8)
            distance_km = st.number_input("Distance km", min_value=0.1, max_value=50.0, value=default_distance, step=0.1, label_visibility="collapsed")
            
    # 2. Environmental Factors Container
    with st.container(border=True):
        st.markdown("#### 🌦️ 2. Environmental Factors")
        
        fetch_live = st.checkbox("Query Live Coordinates Weather", key="weather_fetch")
        if fetch_live:
            with st.spinner("Fetching weather parameters..."):
                w_data = utils.get_weather_details(rest_lat, rest_lon)
                weather_cond = w_data["Weather_Condition"]
                st.toast(f"Live Weather: {weather_cond} ({w_data['Temperature_C']}°C)", icon="🌦️")
        else:
            weather_cond = st.selectbox("Weather Condition Override", ["Sunny", "Cloudy", "Rainy", "Storm"])
            
        traffic_level = st.selectbox("Current Traffic Level", ["Low", "Medium", "High", "Jam"])
        time_of_day = st.selectbox("Time of Day", ["Morning", "Afternoon", "Night"])
        day_of_week = st.selectbox("Day of Week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        
    # 3. Courier Telemetry Container
    with st.container(border=True):
        st.markdown("#### 🛵 3. Courier Details")
        if couriers:
            courier_options = {c["name"]: c for c in couriers}
            selected_cour_name = st.selectbox("Select Courier Profile", list(courier_options.keys()))
            selected_cour = courier_options[selected_cour_name]
        else:
            selected_cour_name = "Alex Mercer (Default)"
            selected_cour = {"courier_id": "C0001", "experience": 8, "rating": 4.8, "vehicle_type": "Bike"}
            
        st.markdown(
            f"""
            <div style="background: rgba(17, 24, 39, 0.4); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 8px; padding: 12px 14px; margin-bottom: 12px;">
                <span style="font-size: 0.72rem; color: #64748b; text-transform: uppercase; font-weight: 600;">Courier Credentials</span>
                <div style="margin-top: 6px; font-size: 0.8rem; color: #cbd5e1; display: grid; grid-template-columns: 1fr 1fr; gap: 4px;">
                    <div>Class: <b>{selected_cour.get('vehicle_type')}</b></div>
                    <div>Rating: <b style="color:#facc15;">★ {selected_cour.get('rating')}</b></div>
                    <div>Experience: <b>{selected_cour.get('experience')} Yrs</b></div>
                    <div>ID: <b>{selected_cour.get('courier_id')}</b></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        vehicle_type = st.selectbox(
            "Override Fleet Vehicle Mode", 
            ["Bike", "Scooter", "Cycle"], 
            index=["Bike", "Scooter", "Cycle"].index(selected_cour.get("vehicle_type", "Scooter"))
        )
        courier_exp = st.slider("Override Rider Experience (Years)", 1, 15, int(selected_cour.get("experience", 5)))
        courier_age = st.slider("Override Rider Age (Years)", 18, 55, 27)

    # 4. Order Information Container
    with st.container(border=True):
        st.markdown("#### 📦 4. Order & Kitchen Parameters")
        prep_time = st.slider("Kitchen Prep Time (Minutes)", 5, 60, 18, help="Expected time for kitchen preparation")
        is_peak = st.selectbox("Peak Hours Operations?", ["Yes", "No"], index=1)
        is_festival = st.selectbox("Festival / High Demand Day?", ["Yes", "No"], index=1)
        is_holiday = st.selectbox("Public Holiday?", ["Yes", "No"], index=1)
        
        order_size = st.selectbox("Order Size", ["Small", "Medium", "Large"], index=1)
        location_type = st.selectbox("Delivery Destination Type", ["Residential", "Commercial"])
        restaurant_rating = st.slider("Restaurant Historical Rating", 1.0, 5.0, float(selected_rest.get("rating", 4.5)), step=0.1)

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

    st.write("")
    if st.button("⚡ EXECUTE ETA INFERENCE", use_container_width=True):
        with st.spinner("Processing dual regressor + classifier pipelines..."):
            try:
                results = predict.predict_single_delivery(payload, save_to_db=True)
                st.session_state["latest_results"] = results
                st.toast("Predictions calculated successfully!", icon="⚡")
            except Exception as e:
                st.error(f"Inference Engine error: {e}. Please ensure you have generated raw data and trained the models.")

with col_right:
    st.markdown("### 📊 Prediction HUD")
    
    if "latest_results" in st.session_state:
        results = st.session_state["latest_results"]
        
        # 1. Large ETA Card via custom component
        render_prediction_card(results)
        
        # Delay Risk and Arrival details
        delay_prob = results.get("Delay_Probability", 0)
        predicted_eta = results["ETA_Minutes"]
        
        current_time = datetime.datetime.now()
        arrival_time = current_time + datetime.timedelta(minutes=predicted_eta)
        arrival_str = arrival_time.strftime("%I:%M %p")
        
        if delay_prob < 30:
            risk_level = "Low Delay Risk"
            risk_color = "#10b981"
            risk_desc = "Fast, unobstructed delivery route expected."
        elif delay_prob < 60:
            risk_level = "Medium Delay Risk"
            risk_color = "#f59e0b"
            risk_desc = "Minor bottlenecks (traffic/prep) detected."
        else:
            risk_level = "High Delay Risk"
            risk_color = "#ef4444"
            risk_desc = "Severe delivery bottlenecks imminent."
            
        st.markdown(
            f"""
            <div style="background: rgba(18, 26, 42, 0.45); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                <h4 style="margin-top: 0; margin-bottom: 12px; font-family: 'Outfit'; color: #f8fafc;">📋 Delivery Diagnostics</h4>
                <div style="display: flex; flex-direction: column; gap: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.85rem; color: #64748b;">Estimated Arrival:</span>
                        <strong style="font-size: 1.1rem; color: #f8fafc; font-family: 'Outfit';">{arrival_str}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.85rem; color: #64748b;">Risk Status:</span>
                        <span style="background: rgba(255,255,255,0.02); border: 1px solid {risk_color}; color: {risk_color}; padding: 3px 10px; border-radius: 50px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">
                            {risk_level}
                        </span>
                    </div>
                    <div style="font-size: 0.78rem; color: #64748b; line-height: 1.3; border-top: 1px solid rgba(255,255,255,0.03); padding-top: 10px;">
                        💡 <b>Status Context</b>: {risk_desc}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # 2. XAI Explainability (SHAP Waterfall)
        st.markdown("#### 🧠 Local Explainability (SHAP Values)")
        st.write("Calculates the net impact (minutes added/subtracted) of each input detail on the baseline delivery time:")
        
        shap_contribs = results["SHAP_Contributions"]
        base_val = results["SHAP_Base_Value"]
        
        # Interpretations
        st.markdown("<span style='font-size:0.85rem; font-weight:600; color:#cbd5e1;'>Top Contributing Factors:</span>", unsafe_allow_html=True)
        interpretations = get_factor_interpretations(shap_contribs)
        if interpretations:
            bullet_html = "\n".join([f"<div style='font-size:0.82rem; color:#cbd5e1; margin-bottom:5px;'>{line}</div>" for line in interpretations])
            st.markdown(bullet_html, unsafe_allow_html=True)
        
        if shap_contribs:
            features_names = list(shap_contribs.keys())
            contributions_values = list(shap_contribs.values())
            
            # Sort values by impact
            sorted_indices = sorted(range(len(contributions_values)), key=lambda k: abs(contributions_values[k]))
            features_names = [features_names[i] for i in sorted_indices]
            contributions_values = [contributions_values[i] for i in sorted_indices]
            
            bar_colors = ["#ff5b2e" if val > 0 else "#10b981" for val in contributions_values]
            
            fig = go.Figure(go.Bar(
                x=contributions_values,
                y=[f.replace('_', ' ').title() for f in features_names],
                orientation='h',
                marker=dict(color=bar_colors),
                text=[f"+{v}m" if v > 0 else f"{v}m" for v in contributions_values],
                textposition='outside'
            ))
            
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#cbd5e1",
                font_family="'Inter', sans-serif",
                xaxis=dict(
                    title="ETA Contribution (Minutes)",
                    gridcolor="rgba(255,255,255,0.04)",
                    linecolor="rgba(255,255,255,0.08)",
                    zeroline=True,
                    zerolinecolor="rgba(255,255,255,0.15)"
                ),
                yaxis=dict(
                    gridcolor="rgba(255,255,255,0.04)",
                    linecolor="rgba(255,255,255,0.08)"
                ),
                margin=dict(l=100, r=40, t=10, b=10),
                height=max(200, len(features_names) * 32)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.info(f"💡 **Business Interpretation**: A standard baseline delivery takes about **{base_val} minutes**. Accumulating the positive and negative weights of your specific order details yields the final ETA prediction of **{results['ETA_Minutes']} minutes**.")
            
        # 3. Compare Other Ride Types
        st.markdown("#### 🚲 Alternative Dispatch Comparatives")
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
            
    else:
        st.markdown(
            """
            <div style="background: rgba(17, 24, 39, 0.25); border: 1px dashed rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 40px; text-align: center; margin-top: 30px; min-height: 300px; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                <div style="font-size: 3rem; margin-bottom: 15px;">🔮</div>
                <h4 style="color: #f8fafc; font-family: 'Outfit'; margin: 0 0 5px 0;">Awaiting Logistics Telemetry</h4>
                <p style="color: #64748b; font-size: 0.88rem; max-width: 380px; margin: 0 auto; line-height: 1.4;">
                    Configure delivery, weather, courier, and prep times in the left panel, then run prediction to launch the inference pipelines.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
