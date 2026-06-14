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
    
    # Theme colors based on speed category (Clean enterprise desaturated styles)
    if category == "Fast":
        cat_badge_bg = "rgba(16, 185, 129, 0.08)"
        cat_border = "rgba(16, 185, 129, 0.2)"
        cat_color = "#34d399"
        cat_icon = "🚀"
    elif category == "Normal":
        cat_badge_bg = "rgba(244, 81, 30, 0.08)"
        cat_border = "rgba(244, 81, 30, 0.2)"
        cat_color = "#ff7443"
        cat_icon = "🛵"
    else:  # Delayed
        cat_badge_bg = "rgba(239, 68, 68, 0.08)"
        cat_border = "rgba(239, 68, 68, 0.2)"
        cat_color = "#f87171"
        cat_icon = "⚠️"
        
    # Delay probability bar color
    if delay_prob < 30:
        bar_color = "#34d399"  # green
    elif delay_prob < 60:
        bar_color = "#f59e0b"  # warning amber
    else:
        bar_color = "#f87171"

    # Inline HTML for custom premium card (SaaS Dark Glassmorphism Aesthetic)
    raw_html = f"""
        <style>
            .premium-results-card {{
                background: rgba(20, 27, 45, 0.4) !important;
                border: 1px solid rgba(255, 255, 255, 0.05) !important;
                border-left: 4px solid {cat_color} !important;
                border-radius: 12px !important;
                padding: 24px !important;
                margin-top: 15px !important;
                margin-bottom: 25px !important;
                box-shadow: 0 4px 25px rgba(0, 0, 0, 0.15) !important;
                font-family: 'Inter', sans-serif !important;
                position: relative !important;
                overflow: hidden !important;
                backdrop-filter: blur(10px) !important;
                -webkit-backdrop-filter: blur(10px) !important;
            }}
            .res-eta-title {{
                color: #64748b !important;
                font-size: 0.72rem !important;
                text-transform: uppercase !important;
                letter-spacing: 0.05em !important;
                margin-bottom: 5px !important;
                font-weight: 700 !important;
            }}
            .res-eta-value-container {{
                display: flex !important;
                align-items: baseline !important;
                gap: 5px !important;
            }}
            .res-eta-number {{
                font-family: 'Outfit', sans-serif !important;
                font-size: 4.5rem !important;
                font-weight: 800 !important;
                line-height: 1 !important;
                color: #f8fafc !important;
                letter-spacing: -0.03em !important;
            }}
            .res-eta-unit {{
                font-size: 1.35rem !important;
                font-weight: 700 !important;
                color: {cat_color} !important;
                font-family: 'Outfit', sans-serif !important;
            }}
            .res-metric-grid {{
                display: grid !important;
                grid-template-columns: 1fr 1fr !important;
                gap: 20px !important;
                margin-top: 20px !important;
                border-top: 1px solid rgba(255, 255, 255, 0.04) !important;
                padding-top: 16px !important;
            }}
            .res-metric-label {{
                font-size: 0.75rem !important;
                color: #64748b !important;
                text-transform: uppercase !important;
                letter-spacing: 0.03em !important;
                margin-bottom: 4px !important;
                font-weight: 700 !important;
            }}
            .res-metric-val {{
                font-size: 1.35rem !important;
                font-weight: 700 !important;
                color: #f8fafc !important;
                font-family: 'Outfit', sans-serif !important;
            }}
            .res-badge {{
                display: inline-flex !important;
                align-items: center !important;
                gap: 5px !important;
                padding: 4px 12px !important;
                border-radius: 6px !important;
                font-size: 0.75rem !important;
                font-weight: 600 !important;
                color: {cat_color} !important;
                background: {cat_badge_bg} !important;
                border: 1px solid {cat_border} !important;
                align-self: flex-start !important;
            }}
            .res-meter-bg {{
                background: rgba(255, 255, 255, 0.04) !important;
                height: 5px !important;
                border-radius: 3px !important;
                margin-top: 8px !important;
                overflow: hidden !important;
            }}
            .res-meter-fill {{
                background: {bar_color} !important;
                width: {delay_prob}% !important;
                height: 100% !important;
                border-radius: 3px !important;
                box-shadow: 0 0 6px {bar_color} !important;
            }}
        </style>
        
        <div class="premium-results-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 5px;">
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
            
            <div style="margin-top: 15px;">
                <div style="display: flex; justify-content: space-between; font-size: 0.78rem; color: #64748b; font-weight: 500;">
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
                    <div class="res-metric-val" style="color: #ff7443;">{confidence}%</div>
                </div>
                <div>
                    <div class="res-metric-label">Order ID</div>
                    <div class="res-metric-val" style="font-family: monospace; color: #38bdf8; font-size: 1.15rem; padding-top: 2px;">{order_id}</div>
                </div>
            </div>
        </div>
    """
    
    # Strip all leading/trailing whitespace from each line and remove empty lines to prevent Markdown from generating code blocks
    cleaned_html = "\n".join([line.strip() for line in raw_html.split("\n") if line.strip() != ""])
    st.markdown(cleaned_html, unsafe_allow_html=True)
