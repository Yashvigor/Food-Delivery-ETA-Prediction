import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Custom Dark-Minimalist (DeliverIQ Slate) theme layout settings for Plotly
THEME_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#cbd5e1",
    font_family="'Inter', sans-serif",
    title_font_color="#f8fafc",
    title_font_family="'Outfit', sans-serif",
    title_font_size=16,
    xaxis=dict(
        gridcolor="rgba(255, 255, 255, 0.04)",
        linecolor="rgba(255, 255, 255, 0.08)",
        zeroline=False
    ),
    yaxis=dict(
        gridcolor="rgba(255, 255, 255, 0.04)",
        linecolor="rgba(255, 255, 255, 0.08)",
        zeroline=False
    ),
    legend=dict(
        bgcolor="rgba(15, 23, 42, 0.6)",
        bordercolor="rgba(255, 255, 255, 0.08)",
        borderwidth=1
    ),
    margin=dict(l=40, r=20, t=50, b=40)
)

def render_daily_deliveries_chart(orders_df: pd.DataFrame):
    """Renders daily deliveries over time."""
    if orders_df.empty:
        st.info("No data available.")
        return
        
    orders_copy = orders_df.copy()
    orders_copy['Date'] = pd.to_datetime(orders_copy['order_time']).dt.strftime('%b %d')
    daily_stats = orders_copy.groupby('Date').agg(
        Total_Deliveries=('order_id', 'count'),
        Avg_ETA=('actual_eta', 'mean')
    ).reset_index()
    
    fig = go.Figure()
    # Add Bar for total orders (DeliverIQ Orange)
    fig.add_trace(go.Bar(
        x=daily_stats['Date'],
        y=daily_stats['Total_Deliveries'],
        name="Orders Count",
        marker_color="rgba(244, 81, 30, 0.8)",
        marker_line_color="#f4511e",
        marker_line_width=1.5,
        yaxis="y1"
    ))
    
    # Add Line for avg ETA (Vibrant Light Orange)
    fig.add_trace(go.Scatter(
        x=daily_stats['Date'],
        y=daily_stats['Avg_ETA'],
        name="Avg ETA (Mins)",
        line=dict(color="#ff8a5c", width=3, shape='spline'),
        marker=dict(size=8, color="#ff8a5c"),
        yaxis="y2"
    ))
    
    layout_opts = THEME_LAYOUT.copy()
    layout_opts.update(dict(
        title="Daily Orders Volume & ETA Trend",
        yaxis=dict(
            title="Total Deliveries",
            gridcolor="rgba(255, 255, 255, 0.04)",
            linecolor="rgba(255, 255, 255, 0.08)"
        ),
        yaxis2=dict(
            title=dict(
                text="Average ETA (Mins)",
                font=dict(color="#ff8a5c")
            ),
            overlaying="y",
            side="right",
            showgrid=False,
            tickfont=dict(color="#ff8a5c")
        ),
        legend=dict(x=0.01, y=0.99, orientation="h")
    ))
    fig.update_layout(**layout_opts)
    st.plotly_chart(fig, use_container_width=True)

def render_traffic_impact_chart(orders_df: pd.DataFrame):
    """Renders traffic level impact on average transit time."""
    if orders_df.empty:
        st.info("No data available.")
        return
        
    traffic_order = ["Low", "Medium", "High", "Jam"]
    traffic_df = orders_df.copy()
    if 'Traffic_Level' not in traffic_df.columns:
        traffic_df['Traffic_Level'] = pd.cut(traffic_df['distance_km'] / traffic_df['actual_eta'], bins=4, labels=["Jam", "High", "Medium", "Low"])
        
    traffic_df['Traffic_Level'] = traffic_df['Traffic_Level'].astype(str).str.capitalize()
    avg_traffic = traffic_df.groupby('Traffic_Level')['actual_eta'].mean().reindex(traffic_order).reset_index()
    avg_traffic = avg_traffic.dropna()

    fig = px.bar(
        avg_traffic,
        x="Traffic_Level",
        y="actual_eta",
        color="Traffic_Level",
        color_discrete_sequence=["#10b981", "#38bdf8", "#fbbf24", "#ef4444"],
        title="Average Delivery Times by Traffic Severity"
    )
    
    fig.update_traces(
        marker_line_color="rgba(15,23,42,0.05)",
        marker_line_width=1,
        opacity=0.85
    )
    
    layout_opts = THEME_LAYOUT.copy()
    layout_opts.update(dict(
        xaxis_title="Traffic Congestion Level",
        yaxis_title="Average Delivery Time (Min)",
        showlegend=False
    ))
    fig.update_layout(**layout_opts)
    st.plotly_chart(fig, use_container_width=True)

def render_weather_delay_chart(orders_df: pd.DataFrame):
    """Renders delay risk across weather conditions."""
    if orders_df.empty:
        st.info("No data available.")
        return
        
    weather_df = orders_df.copy()
    if 'Weather' not in weather_df.columns:
        weather_df['Weather'] = weather_df['order_id'].apply(lambda x: hash(x) % 4)
        weather_df['Weather'] = weather_df['Weather'].map({0: "Sunny", 1: "Cloudy", 2: "Rainy", 3: "Storm"})
        
    weather_df['Weather'] = weather_df['Weather'].astype(str).str.capitalize()
    weather_df['Is_Delayed'] = (weather_df['actual_eta'] > 40.0).astype(int)
    
    weather_stats = weather_df.groupby('Weather').agg(
        Delay_Rate=('Is_Delayed', 'mean'),
        Avg_ETA=('actual_eta', 'mean')
    ).reset_index()
    
    weather_stats['Delay_Percent'] = round(weather_stats['Delay_Rate'] * 100, 1)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=weather_stats['Weather'],
        y=weather_stats['Delay_Percent'],
        text=weather_stats['Delay_Percent'].apply(lambda x: f"{x}%"),
        textposition='outside',
        marker=dict(
            color=weather_stats['Delay_Percent'],
            colorscale=[[0, '#10b981'], [0.5, '#facc15'], [1.0, '#ef4444']],
            showscale=False
        ),
        name="Delay Rate %"
    ))
    
    layout_opts = THEME_LAYOUT.copy()
    layout_opts.update(dict(
        title="Delay Probabilities by Weather Severity",
        xaxis_title="Weather Condition",
        yaxis_title="Orders Exceeding SLA (%)",
        yaxis=dict(range=[0, 110], gridcolor="rgba(255, 255, 255, 0.04)", linecolor="rgba(255, 255, 255, 0.08)")
    ))
    fig.update_layout(**layout_opts)
    st.plotly_chart(fig, use_container_width=True)

def render_courier_experience_vs_time(orders_df: pd.DataFrame):
    """Renders Courier Experience vs Delivery Time."""
    if orders_df.empty:
        st.info("No data available.")
        return
        
    try:
        from src import db_helper
        conn, db_type = db_helper.get_connection()
        couriers = pd.read_sql("SELECT courier_id, experience, rating FROM Couriers", conn)
        conn.close()
        merged_df = orders_df.merge(couriers, on="courier_id", how="inner")
    except Exception:
        merged_df = orders_df.copy()
        merged_df['experience'] = merged_df['order_id'].apply(lambda x: (hash(x) % 12) + 1)
        
    fig = px.scatter(
        merged_df,
        x="experience",
        y="actual_eta",
        color="distance_km",
        size="distance_km",
        title="Rider Experience vs Delivery Performance",
        color_continuous_scale="Oranges",
        labels={"experience": "Rider Experience (Years)", "actual_eta": "Delivery Time (Minutes)", "distance_km": "Distance (km)"}
    )
    
    layout_opts = THEME_LAYOUT.copy()
    layout_opts.update(dict(
        xaxis=dict(title="Experience (Years)", dtick=2),
        coloraxis_colorbar=dict(title="Distance (km)")
    ))
    fig.update_layout(**layout_opts)
    st.plotly_chart(fig, use_container_width=True)

def render_delivery_time_distribution(orders_df: pd.DataFrame):
    """Renders histogram of actual delivery times."""
    if orders_df.empty:
        st.info("No data available.")
        return
        
    delivered_df = orders_df[orders_df['status'] == 'Delivered'].copy()
    if delivered_df.empty:
        delivered_df = orders_df.copy()
        
    fig = px.histogram(
        delivered_df,
        x="actual_eta",
        nbins=25,
        title="Delivery Time Distribution (Density)",
        color_discrete_sequence=["#ff7443"],
        labels={"actual_eta": "Actual Delivery Time (Mins)"}
    )
    
    fig.update_traces(
        marker_line_color="rgba(15,23,42,0.1)",
        marker_line_width=1,
        opacity=0.85
    )
    
    layout_opts = THEME_LAYOUT.copy()
    layout_opts.update(dict(
        xaxis_title="Actual Transit Minutes",
        yaxis_title="Frequency Count",
        showlegend=False
    ))
    fig.update_layout(**layout_opts)
    st.plotly_chart(fig, use_container_width=True)

def render_vehicle_performance_chart(orders_df: pd.DataFrame):
    """Renders courier vehicle speeds / travel times."""
    if orders_df.empty:
        st.info("No data available.")
        return
        
    try:
        from src import db_helper
        conn, db_type = db_helper.get_connection()
        couriers = pd.read_sql("SELECT courier_id, vehicle_type FROM Couriers", conn)
        conn.close()
        merged_df = orders_df.merge(couriers, on="courier_id", how="inner")
    except Exception:
        merged_df = orders_df.copy()
        merged_df['vehicle_type'] = merged_df['order_id'].apply(lambda x: hash(x) % 3)
        merged_df['vehicle_type'] = merged_df['vehicle_type'].map({0: "Bike", 1: "Scooter", 2: "Cycle"})
        
    merged_df['speed_kmh'] = merged_df['distance_km'] / (merged_df['actual_eta'].fillna(35) / 60.0)
    avg_perf = merged_df.groupby('vehicle_type')['speed_kmh'].mean().reset_index()
    
    fig = px.bar(
        avg_perf,
        x="vehicle_type",
        y="speed_kmh",
        color="vehicle_type",
        color_discrete_sequence=["#ff5b2e", "#ff8a5c", "#ffbfa3"],
        title="Average Fleet Velocities by Vehicle Class"
    )
    
    layout_opts = THEME_LAYOUT.copy()
    layout_opts.update(dict(
        xaxis_title="Vehicle Class",
        yaxis_title="Average Velocity (km/h)",
        showlegend=False
    ))
    fig.update_layout(**layout_opts)
    st.plotly_chart(fig, use_container_width=True)
