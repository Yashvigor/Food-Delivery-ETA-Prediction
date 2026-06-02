import streamlit as st

def render_prediction_card(pred_results: dict):
    """
    Renders an exceptionally beautiful, glassmorphic card displaying the predicted
    delivery ETA, delay risk, confidence, and speed categorization.
    """
    eta = pred_results.get("ETA_Minutes", 0)
    delay_prob = pred_results.get("Delay_Probability", 0)
    confidence = pred_results.get("Confidence_Score", 0)
    category = pred_results.get("Delivery_Category", "Normal")
    order_id = pred_results.get("Order_ID", "N/A")
    
    # Theme colors based on speed category
    if category == "Fast":
        cat_badge_bg = "linear-gradient(135deg, #10b981 0%, #059669 100%)"
        cat_color = "#10b981"
        cat_icon = "🚀"
    elif category == "Normal":
        cat_badge_bg = "linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)"
        cat_color = "#3b82f6"
        cat_icon = "🛵"
    else:  # Delayed
        cat_badge_bg = "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)"
        cat_color = "#ef4444"
        cat_icon = "⚠️"
        
    # Delay probability bar color
    if delay_prob < 30:
        bar_color = "#10b981"  # green
    elif delay_prob < 60:
        bar_color = "#ff9f43"  # orange
    else:
        bar_color = "#ef4444"  # red

    # Inline HTML for custom premium card
    st.markdown(
        f"""
        <style>
            .glass-card {{
                background: rgba(22, 28, 45, 0.45);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 20px;
                padding: 30px;
                margin-top: 15px;
                margin-bottom: 25px;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
                font-family: 'Inter', sans-serif;
            }}
            .eta-title {{
                color: #a0aec0;
                font-size: 0.9rem;
                text-transform: uppercase;
                letter-spacing: 2px;
                margin-bottom: 5px;
                font-weight: 600;
            }}
            .eta-value-container {{
                display: flex;
                align-items: baseline;
                gap: 10px;
            }}
            .eta-number {{
                font-family: 'Outfit', sans-serif;
                font-size: 5rem;
                font-weight: 700;
                color: #ffffff;
                line-height: 1;
                background: linear-gradient(135deg, #ffffff 0%, #a5b4fc 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 4px 20px rgba(165,180,252,0.15);
            }}
            .eta-unit {{
                font-size: 1.8rem;
                font-weight: 600;
                color: #a5b4fc;
            }}
            .metric-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-top: 25px;
                border-top: 1px solid rgba(255, 255, 255, 0.08);
                padding-top: 20px;
            }}
            .metric-label {{
                font-size: 0.85rem;
                color: #718096;
                margin-bottom: 4px;
            }}
            .metric-val {{
                font-size: 1.5rem;
                font-weight: 700;
                color: #ffffff;
            }}
            .badge {{
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 6px 16px;
                border-radius: 50px;
                font-size: 0.85rem;
                font-weight: 700;
                color: white;
                background: {cat_badge_bg};
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }}
            .meter-bg {{
                background: rgba(255, 255, 255, 0.05);
                height: 8px;
                border-radius: 4px;
                margin-top: 6px;
                overflow: hidden;
            }}
            .meter-fill {{
                background: {bar_color};
                width: {delay_prob}%;
                height: 100%;
                border-radius: 4px;
                box-shadow: 0 0 8px {bar_color};
                transition: width 1s ease-in-out;
            }}
        </style>
        
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
                <div>
                    <div class="eta-title">Estimated Delivery Time</div>
                    <div class="eta-value-container">
                        <span class="eta-number">{eta}</span>
                        <span class="eta-unit">mins</span>
                    </div>
                </div>
                <div class="badge">
                    <span>{cat_icon}</span>
                    <span>{category} Speed</span>
                </div>
            </div>
            
            <div style="margin-top: 20px;">
                <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #a0aec0;">
                    <span>Delay Risk Probability</span>
                    <span style="font-weight: 700; color: {cat_color};">{delay_prob}%</span>
                </div>
                <div class="meter-bg">
                    <div class="meter-fill"></div>
                </div>
            </div>
            
            <div class="metric-grid">
                <div>
                    <div class="metric-label">Confidence Score</div>
                    <div class="metric-val" style="color: #00f2fe;">{confidence}%</div>
                </div>
                <div>
                    <div class="metric-label">Logged Order ID</div>
                    <div class="metric-val" style="font-family: monospace; color: #facc15; font-size: 1.3rem; padding-top: 2px;">{order_id}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
