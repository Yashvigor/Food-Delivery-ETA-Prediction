import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Custom dark-theme layout settings for Plotly
THEME_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#a0aec0",
    font_family="'Inter', sans-serif",
    title_font_color="#ffffff",
    title_font_family="'Outfit', sans-serif",
    title_font_size=18,
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.05)",
        linecolor="rgba(255,255,255,0.1)",
        zeroline=False
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.05)",
        linecolor="rgba(255,255,255,0.1)",
        zeroline=False
    ),
    legend=dict(
        bgcolor="rgba(22, 28, 45, 0.6)",
        bordercolor="rgba(255,255,255,0.05)",
        borderwidth=1
    ),
    margin=dict(l=40, r=20, t=50, b=40)
)

def render_daily_deliveries_chart(orders_df: pd.DataFrame):
    """Renders daily deliveries over time."""
    if orders_df.empty:
        st.info("No data available.")
        return
        
    # Group by day
    orders_df['Date'] = pd.to_datetime(orders_df['order_time']).dt.strftime('%b %d')
    daily_stats = orders_df.groupby('Date').agg(
        Total_Deliveries=('order_id', 'count'),
        Avg_ETA=('actual_eta', 'mean')
    ).reset_index()
    
    fig = go.Figure()
    # Add Bar for total orders
    fig.add_trace(go.Bar(
        x=daily_stats['Date'],
        y=daily_stats['Total_Deliveries'],
        name="Orders Count",
        marker_color="rgba(79, 172, 254, 0.85)",
        marker_line_color="#00f2fe",
        marker_line_width=1.5,
        yaxis="y1"
    ))
    
    # Add Line for avg ETA
    fig.add_trace(go.Scatter(
        x=daily_stats['Date'],
        y=daily_stats['Avg_ETA'],
        name="Avg ETA (Mins)",
        line=dict(color="#facc15", width=3, shape='spline'),
        marker=dict(size=8, color="#facc15"),
        yaxis="y2"
    ))
    
    # Setup dual axis layout
    layout_opts = THEME_LAYOUT.copy()
    layout_opts.update(dict(
        title="Daily Delivery Volume & Average Transit Time",
        yaxis=dict(
            title="Total Orders",
            gridcolor="rgba(255,255,255,0.05)",
            linecolor="rgba(255,255,255,0.1)"
        ),
        yaxis2=dict(
            title="Average Transit (Mins)",
            overlaying="y",
            side="right",
            showgrid=False
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
        
    # Ensure traffic is ordered logically
    traffic_order = ["Low", "Medium", "High", "Jam"]
    
    # Group and average
    # Fallback to seed columns mapping if needed
    traffic_df = orders_df.copy()
    if 'Traffic_Level' not in traffic_df.columns:
        # Generate mockup traffic based on distance & actual eta if column is missing (e.g. from generic DB orders)
        traffic_df['Traffic_Level'] = pd.cut(traffic_df['distance_km'] / traffic_df['actual_eta'], bins=4, labels=["Jam", "High", "Medium", "Low"])
        
    # Standardize traffic casing
    traffic_df['Traffic_Level'] = traffic_df['Traffic_Level'].astype(str).str.capitalize()
    
    avg_traffic = traffic_df.groupby('Traffic_Level')['actual_eta'].mean().reindex(traffic_order).reset_index()
    avg_traffic = avg_traffic.dropna()

    fig = px.bar(
        avg_traffic,
        x="Traffic_Level",
        y="actual_eta",
        color="Traffic_Level",
        color_discrete_sequence=["#10b981", "#3b82f6", "#ff9f43", "#ef4444"],
        title="Impact of City Traffic on Actual Delivery Minutes"
    )
    
    fig.update_traces(
        marker_line_color="rgba(255,255,255,0.15)",
        marker_line_width=1,
        opacity=0.9
    )
    
    layout_opts = THEME_LAYOUT.copy()
    layout_opts.update(dict(
        xaxis_title="Traffic Level",
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
        # Mock weather
        weather_df['Weather'] = weather_df['order_id'].apply(lambda x: hash(x) % 4)
        weather_df['Weather'] = weather_df['Weather'].map({0: "Sunny", 1: "Cloudy", 2: "Rainy", 3: "Storm"})
        
    # Group weather
    weather_df['Weather'] = weather_df['Weather'].astype(str).str.capitalize()
    
    # Calculate late percentage (let's say actual ETA > 40 minutes or actual ETA > predicted + 5 mins is classified as delay)
    weather_df['Is_Delayed'] = (weather_df['actual_eta'] > 35.0).astype(int)
    
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
        title="Weather Influence on Delivery Delays",
        xaxis_title="Weather Condition",
        yaxis_title="Delay Probability (%)",
        yaxis=dict(range=[0, 110], gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)")
    ))
    fig.update_layout(**layout_opts)
    
    st.plotly_chart(fig, use_container_width=True)

def render_courier_experience_vs_time(orders_df: pd.DataFrame):
    """Renders Courier Experience vs Delivery Time."""
    if orders_df.empty:
        st.info("No data available.")
        return
        
    # Since sqlite generic seed orders don't store courier experience in orders directly,
    # we merge it with couriers list
    try:
        conn, db_type = db_helper.get_connection()
        couriers = pd.read_sql("SELECT courier_id, experience, rating FROM Couriers", conn)
        conn.close()
        
        merged_df = orders_df.merge(couriers, on="courier_id", how="inner")
    except Exception:
        # Fallback if DB query fails
        merged_df = orders_df.copy()
        merged_df['experience'] = merged_df['order_id'].apply(lambda x: (hash(x) % 12) + 1)
        
    fig = px.scatter(
        merged_df,
        x="experience",
        y="actual_eta",
        color="distance_km",
        size="distance_km",
        hover_data=["order_id", "courier_id"],
        title="Courier Experience vs Delivery Time",
        color_continuous_scale="Viridis",
        labels={"experience": "Courier Experience (Years)", "actual_eta": "Delivery Time (Minutes)", "distance_km": "Distance (km)"}
    )
    
    layout_opts = THEME_LAYOUT.copy()
    layout_opts.update(dict(
        xaxis=dict(title="Experience (Years)", dtick=2),
        coloraxis_colorbar=dict(title="Distance (km)")
    ))
    fig.update_layout(**layout_opts)
    
    st.plotly_chart(fig, use_container_width=True)
