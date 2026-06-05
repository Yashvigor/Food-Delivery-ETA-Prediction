import streamlit as st

def render_prediction_card(pred_results: dict):
    """
    Renders an exceptionally beautiful, minimalistic SaaS card displaying the predicted
    delivery ETA, delay risk, confidence, and speed categorization.
    """
    eta = pred_results.get("ETA_Minutes", 0)
    delay_prob = pred_results.get("Delay_Probability", 0)
    confidence = pred_results.get("Confidence_Score", 0)
    category = pred_results.get("Delivery_Category", "Normal")
    order_id = pred_results.get("Order_ID", "N/A")
    
    # Theme colors based on speed category (Swiggy / Zomato Inspired)
    if category == "Fast":
        cat_badge_bg = "linear-gradient(135deg, #10b981 0%, #059669 100%)"
        cat_color = "#10b981"
        cat_icon = "🚀"
    elif category == "Normal":
        cat_badge_bg = "linear-gradient(135deg, #ff6b35 0%, #ff2b54 100%)"
        cat_color = "#ff6b35"
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
        bar_color = "#ef4444"

    # Inline HTML for custom premium card (SaaS Dark Glassmorphism Aesthetic)
    raw_html = f"""
        <style>
            .premium-results-card {{
                background: rgba(17, 24, 39, 0.7) !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                border-radius: 20px !important;
                padding: 30px !important;
                margin-top: 15px !important;
                margin-bottom: 25px !important;
                box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3) !important;
                font-family: 'Inter', sans-serif !important;
                position: relative !important;
                overflow: hidden !important;
                backdrop-filter: blur(12px) !important;
                -webkit-backdrop-filter: blur(12px) !important;
            }}
            .premium-results-card::before {{
                content: '' !important;
                position: absolute !important;
                top: 0 !important;
                left: 0 !important;
                right: 0 !important;
                height: 4px !important;
                background: {cat_badge_bg} !important;
                box-shadow: 0 2px 10px {cat_color} !important;
            }}
            .res-eta-title {{
                color: #94a3b8 !important;
                font-size: 0.85rem !important;
                text-transform: uppercase !important;
                letter-spacing: 2px !important;
                margin-bottom: 5px !important;
                font-weight: 600 !important;
            }}
            .res-eta-value-container {{
                display: flex !important;
                align-items: baseline !important;
                gap: 8px !important;
            }}
            .res-eta-number {{
                font-family: 'Outfit', sans-serif !important;
                font-size: 5.5rem !important;
                font-weight: 800 !important;
                line-height: 1 !important;
                background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%) !important;
                -webkit-background-clip: text !important;
                -webkit-text-fill-color: transparent !important;
                filter: drop-shadow(0 2px 10px rgba(255, 255, 255, 0.05)) !important;
            }}
            .res-eta-unit {{
                font-size: 1.8rem !important;
                font-weight: 700 !important;
                color: #ff6b35 !important;
                font-family: 'Outfit', sans-serif !important;
            }}
            .res-metric-grid {{
                display: grid !important;
                grid-template-columns: 1fr 1fr !important;
                gap: 20px !important;
                margin-top: 25px !important;
                border-top: 1px solid rgba(255, 255, 255, 0.05) !important;
                padding-top: 20px !important;
            }}
            .res-metric-label {{
                font-size: 0.85rem !important;
                color: #94a3b8 !important;
                margin-bottom: 4px !important;
                font-weight: 500 !important;
            }}
            .res-metric-val {{
                font-size: 1.5rem !important;
                font-weight: 700 !important;
                color: #f8fafc !important;
                font-family: 'Outfit', sans-serif !important;
            }}
            .res-badge {{
                display: inline-flex !important;
                align-items: center !important;
                gap: 6px !important;
                padding: 6px 16px !important;
                border-radius: 50px !important;
                font-size: 0.85rem !important;
                font-weight: 700 !important;
                color: white !important;
                background: {cat_badge_bg} !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
            }}
            .res-meter-bg {{
                background: rgba(255, 255, 255, 0.05) !important;
                height: 8px !important;
                border-radius: 4px !important;
                margin-top: 6px !important;
                overflow: hidden !important;
            }}
            .res-meter-fill {{
                background: {bar_color} !important;
                width: {delay_prob}% !important;
                height: 100% !important;
                border-radius: 4px !important;
                box-shadow: 0 0 8px {bar_color} !important;
            }}
        </style>
        
        <div class="premium-results-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
                <div>
                    <div class="res-eta-title">Estimated Delivery Time</div>
                    <div class="res-eta-value-container">
                        <span class="res-eta-number">{eta}</span>
                        <span class="res-eta-unit">mins</span>
                    </div>
                </div>
                <div class="res-badge">
                    <span>{cat_icon}</span>
                    <span>{category} Delivery</span>
                </div>
            </div>
            
            <div style="margin-top: 20px;">
                <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #94a3b8; font-weight: 500;">
                    <span>Probability of Delay</span>
                    <span style="font-weight: 700; color: {bar_color};">{delay_prob}%</span>
                </div>
                <div class="res-meter-bg">
                    <div class="res-meter-fill"></div>
                </div>
            </div>
            
            <div class="res-metric-grid">
                <div>
                    <div class="res-metric-label">Prediction Confidence</div>
                    <div class="res-metric-val" style="color: #ff6b35;">{confidence}%</div>
                </div>
                <div>
                    <div class="res-metric-label">Order ID</div>
                    <div class="res-metric-val" style="font-family: monospace; color: #00f2fe; font-size: 1.35rem; padding-top: 2px;">{order_id}</div>
                </div>
            </div>
        </div>
    """
    
    # Strip all leading/trailing whitespace from each line and remove empty lines to prevent Markdown from generating code blocks
    cleaned_html = "\n".join([line.strip() for line in raw_html.split("\n") if line.strip() != ""])
    st.markdown(cleaned_html, unsafe_allow_html=True)
