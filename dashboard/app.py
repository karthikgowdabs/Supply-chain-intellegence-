import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Ensure modules result in root (if running from root)
sys.path.append(os.getcwd())

from modules.pipeline import run_pipeline

st.set_page_config(page_title="Supply Chain Intelligence", layout="wide",page_icon="📊")

# Hide Streamlit Style Elements (Deploy Button, etc)
# st.markdown("""
#     <style>
#     /* Hide Deploy Button */
#     .stDeployButton, [data-testid="stDeployButton"] {
#         display: none !important;
#         visibility: hidden !important;
#     }
#     </style>
# """, unsafe_allow_html=True)

st.title("Supply Chain Intelligence")
st.caption("Predict • Detect • Decide")
# --- Sidebar ---
st.sidebar.title("Configuration")

# Data Source
# data_path = st.sidebar.text_input("Dataset Path", "data/raw_sales_500_electronics.csv")
st.subheader("Dataset Source")

uploaded_file = st.file_uploader("Upload CSV Dataset", type=["csv"])

use_default = st.checkbox("Use Default Dataset", value=True)

# Parameters
st.sidebar.subheader("Decline Detection Params")
threshold_pct = st.sidebar.slider("Decline Threshold (%)", 5, 50, 15) / 100.0
sustain_months = st.sidebar.slider("Sustain Months", 1, 12, 3)

# Load Data Button
if st.sidebar.button("Reload Data"):
    st.cache_data.clear()

# --- Data Loading (Cached) ---
# --- Data Loading (Cached) ---
from modules.pipeline import run_pipeline

@st.cache_data
def load_pipeline_data(data, thresh, sustain):
    return run_pipeline(data, thresh, sustain)


try:
    if uploaded_file is not None:
        df_input = pd.read_csv(uploaded_file)
        st.success("Custom dataset loaded")

    else:
        df_input = data_path  # default path

    results = load_pipeline_data(df_input, threshold_pct, sustain_months)

    df = results["data"]
    declines_df = results["declines"]
    causes_df = results["causes"]
    kpis_df = results["kpis"]

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

uploaded_file = st.file_uploader(
    "Upload CSV Dataset",
    type=["csv"],
    key="dataset_uploader"
)

# --- Main Tabs ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Overview", "Product Detail", "Comparison", "Diagnostics","Forecast","Report"])

# --- Tab 1: Overview ---
with tab1:
    st.title("System Overview")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Products Tracking", len(df['product_id'].unique()))
    col2.metric("Declined Products Detected", len(declines_df))
    avg_decline = declines_df['decline_confidence_score'].mean() if not declines_df.empty else 0
    col3.metric("Avg Decline Confidence", f"{avg_decline:.2f}")

    st.subheader("About Our Intelligence Platform")
    st.markdown(
        """
        ### Welcome to the Analytic Suite
        
        Our platform uses advanced signal processing to monitor your entire product portfolio in real-time. 
        We specialize in:
        - **Early Warning Detection**: Identifying sales slumps before they become critical.
        - **Root Cause Analysis**: Pinpointing whether price, rating, or competition is the driver.
        - **Lifecycle Management**: Assisting with inventory and promo decisions.
        
        For support or feature requests, visit our internal portal or contact the data science team.
        """
    )
    
    st.divider()

    st.subheader("Top Declined Products")
    if not declines_df.empty:
        # Merge with causes for better view
        display_df = declines_df.merge(causes_df[['product_id', 'primary_cause']], on='product_id', how='left')
        st.dataframe(display_df.sort_values('decline_confidence_score', ascending=False))
    else:
        st.info("No significant declines detected with current parameters.")

# --- Tab 2: Product Detail ---
with tab2:
    st.title("Deep Dive Analysis")
    
    products = sorted(df['product_id'].unique())
    selected_prod = st.selectbox("Select Product", products)
    
    if selected_prod:
        prod_data = df[df['product_id'] == selected_prod].sort_values('date')
        
        # Check if declined
        prod_decline = declines_df[declines_df['product_id'] == selected_prod]
        is_declined = not prod_decline.empty
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Sales Time Series")
            fig = px.line(prod_data, x='date', y='sales', title=f"Sales Trend: {selected_prod}", template="plotly_white")
            fig.update_traces(line_color='#2E86C1') # Custom Blue
            
            # Add rolling avg
            fig.add_scatter(x=prod_data['date'], y=prod_data['sales_roll3'], mode='lines', name='3-Month Rolling', line=dict(dash='dot', color='#E67E22'))

            anomalies = prod_data[prod_data['anomaly_flag'] == 1]

            fig.add_scatter(
                x=anomalies['date'],
                y=anomalies['sales'],
                mode='markers',
                name='Anomalies',
                marker=dict(color='red', size=8)
            )
            if is_declined:
                peak_date = prod_decline.iloc[0]['peak_date']
                start_date = prod_decline.iloc[0]['decline_start_date']
                
                fig.add_annotation(x=peak_date, y=prod_data.loc[prod_data['date'] == peak_date, 'sales'].values[0], text="Peak", showarrow=True)
                fig.add_vline(x=start_date.timestamp() * 1000, line_dash="dash", line_color="#E74C3C", annotation_text="Decline Start")
                
            st.plotly_chart(fig, use_container_width=True)
            
            # 3D Scatter for this product (Price vs Trend vs Sales)
            st.subheader("3D Feature Interaction")
            fig_3d = px.scatter_3d(prod_data, x='price', y='trend_index', z='sales', color='rating', title="Sales vs Price vs Trend", template="plotly_white", color_continuous_scale='Viridis')
            st.plotly_chart(fig_3d, use_container_width=True)

        with col2:
            st.subheader("Analysis Report")

            from modules.recommendation import generate_recommendation

            # 🔥 Define required data FIRST
            curr = prod_data.iloc[-1]

            kpi_row = kpis_df[kpis_df['product_id'] == selected_prod].iloc[0]

            if is_declined:
                cause_row = causes_df[causes_df['product_id'] == selected_prod].iloc[0]
                primary_cause = cause_row['primary_cause']
            else:
                primary_cause = "None"

            # 🔥 Recommendation
            recommendation = generate_recommendation(selected_prod, causes_df, kpis_df)

            st.subheader("Recommended Action")
            st.info(recommendation)

            # 🔥 Insight Summary
            st.markdown("### 🧠 Insight Summary")

            summary = f"""
            Product **{selected_prod}** is currently {'declining' if is_declined else 'stable'}.

            - Primary Issue: {primary_cause}
            - Sales Volatility: {kpi_row['sales_volatility']:.2f}
            - Avg Sales: {kpi_row['avg_sales']:.2f}

            Recommendation:
            {recommendation}
            """

            st.markdown(summary)

            # 🔥 Price Simulation
            st.subheader("Price Simulation")

            new_price = st.slider("Simulate New Price", 50, 2000, int(curr['price']))

            price_change = (new_price - curr['price']) / curr['price']

            elasticity = 0.7  # 🔥 better than fixed 0.5

            estimated_sales = curr['sales'] * (1 - elasticity * price_change)

            # 🔥 NEW: growth impact
            simulated_growth = (estimated_sales - curr['sales']) / curr['sales']

            st.metric("Estimated Sales Impact", f"{estimated_sales:.2f}")

            # 🔥 ADD THIS (IMPORTANT)
            st.metric("Sales Change %", f"{simulated_growth * 100:.2f}%")

            # 🔥 Risk Level
            st.markdown("### 🚨 Risk Assessment")

            risk_score = (
                    (1 if is_declined else 0) +
                    (1 if curr.get('anomaly_flag', 0) == 1 else 0) +
                    (1 if kpi_row['sales_volatility'] > kpi_row['avg_sales'] else 0)
            )

            #  (simulation impact)
            if simulated_growth < -0.1:
                risk_score += 1
            elif simulated_growth > 0.1:
                risk_score -= 1

            if risk_score >= 2:
                st.error("High Risk")
            elif risk_score == 1:
                st.warning("Moderate Risk")
            else:
                st.success("Low Risk")

            st.session_state["last_risk"] = risk_score


            # 🔥 Decline Details
            if is_declined:
                st.error("DETECTED DECLINE")

                st.write("**Primary Cause:**")
                st.info(primary_cause)

                st.write("**All Factors:**")
                for c in cause_row['causes']:
                    st.write(f"- {c}")
            else:
                st.success("Stable Lifecycle Phase")

            st.divider()

            st.session_state["last_product"] = selected_prod
            st.session_state["last_decline"] = is_declined
            # st.session_state["last_risk"] = risk_score
            st.session_state["last_recommendation"] = recommendation

            #  Current KPIs
            st.write("### 📊 Current KPIs")

            k1, k2, k3 = st.columns(3)

            with k1:
                st.metric("Price", f"${curr['price']:.2f}")

            with k2:
                st.metric("Rating", f"{curr['rating']:.2f}")

            with k3:
                st.metric("Inventory", f"{curr.get('inventory_level', 'N/A')}")

# --- Tab 3: Comparison ---
with tab3:
    st.title("Inter-Product Comparison")
    
    compare_prods = st.multiselect("Select Products to Compare", products, default=products[:2])

    st.session_state["compare_products"] = compare_prods

    if compare_prods:
        # Overlay Sales
        st.subheader("Sales Overlay")
        comp_data = df[df['product_id'].isin(compare_prods)]
        fig_comp = px.line(comp_data, x='date', y='sales', color='product_id', title="Comparative Sales Performance", template="plotly_white")
        st.plotly_chart(fig_comp, use_container_width=True)
        
        # KPI Table
        st.subheader("KPI Matrix")
        comp_kpis = kpis_df[kpis_df['product_id'].isin(compare_prods)]
        st.dataframe(comp_kpis)
        
        # 3D Market Position
        st.subheader("Market Position (3D Embed)")
        if len(compare_prods) > 0:
             # We plot aggregations
             fig_3d_comp = px.scatter_3d(
                 comp_kpis,
                 x='avg_sales',
                 y='price_volatility',
                 z='sales_growth',
                 color='product_id',
                 text='product_id',
                 title="Product Market Positioning"
             )
             st.plotly_chart(fig_3d_comp, use_container_width=True)

# --- Tab 4: Diagnostics ---
with tab4:
    st.title("Diagnostics")
    st.checkbox("Show Raw Data", key="show_raw")
    if st.session_state.show_raw:
        st.write("First 100 rows of processed data:")
        st.dataframe(df.head(100))
        
    st.subheader("Decline Detection Data")
    st.dataframe(declines_df)
    
    # Export
    csv = causes_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download Cause Analysis Report (CSV)",
        csv,
        "decline_causes.csv",
        "text/csv",
        key='download-csv'
    )

with tab5:
    st.title("Sales Forecast Intelligence")

    products = sorted(df['product_id'].unique())
    selected_prod = st.selectbox("Select Product", products, key="forecast_product")

    periods = st.slider("Forecast Days", 30, 180, 90)

    from modules.forecasting import forecast_sales

    prod_data = df[df['product_id'] == selected_prod].sort_values('date')

    if len(prod_data) < 5:
        st.warning("Not enough data to forecast")
    else:
        with st.spinner("Generating intelligent forecast..."):

            forecast_df = forecast_sales(df, selected_prod, periods)

        # 🔥 MAIN CHART
        fig = px.line(
            forecast_df,
            x='ds',
            y='yhat',
            title=f"Forecast: {selected_prod}",
            template="plotly_white"
        )
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            title_font=dict(size=18),
            font=dict(size=12)
        )
        # 🔥 Confidence band (PROPER WAY)
        fig.add_traces([
            dict(
                x=forecast_df['ds'],
                y=forecast_df['yhat_upper'],
                mode='lines',
                line=dict(width=0),
                showlegend=False
            ),
            dict(
                x=forecast_df['ds'],
                y=forecast_df['yhat_lower'],
                mode='lines',
                fill='tonexty',
                fillcolor='rgba(0,100,80,0.2)',
                line=dict(width=0),
                name='Confidence Interval'
            )
        ])

        # 🔥 Actual data
        fig.add_scatter(
            x=prod_data['date'],
            y=prod_data['sales'],
            mode='lines+markers',
            name='Actual Sales',
            line=dict(color='blue')
        )

        st.plotly_chart(fig, use_container_width=True)

        # 🔥 INTELLIGENCE PANEL (this is what makes it GOOD)

        st.subheader("Forecast Insights")

        short_term = forecast_df['yhat'].iloc[-7] - forecast_df['yhat'].iloc[0]
        long_term = forecast_df['yhat'].iloc[-1] - forecast_df['yhat'].iloc[0]

        st.session_state["last_forecast_product"] = selected_prod
        st.session_state["last_forecast_trend"] = long_term

        if long_term < 0:
            st.error("📉 Strong declining trend predicted")
        elif long_term > 0:
            st.success("📈 Growth trend expected")
        else:
            st.info("Stable performance expected")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("7-Day Trend", f"{short_term:.2f}")

        with col2:
            st.metric("90-Day Trend", f"{long_term:.2f}")

# with tab6:
#     st.title("Generate Product Report")
#
#     products = sorted(df['product_id'].unique())
#     selected_prod = st.selectbox("Select Product", products, key="report_product")
#
#     from modules.recommendation import generate_recommendation
#     from modules.report import generate_product_report
#
#     if selected_prod:
#         kpi_row = kpis_df[kpis_df['product_id'] == selected_prod].iloc[0]
#
#         recommendation = generate_recommendation(selected_prod, causes_df, kpis_df)
#
#         # 🔥 Risk calculation (reuse logic)
#         prod_data = df[df['product_id'] == selected_prod]
#         curr = prod_data.iloc[-1]
#
#         is_declined = not declines_df[declines_df['product_id'] == selected_prod].empty
#
#         risk_score = (
#             (1 if is_declined else 0) +
#             (1 if curr.get('anomaly_flag', 0) == 1 else 0) +
#             (1 if kpi_row['sales_volatility'] > kpi_row['avg_sales'] else 0)
#         )
#
#         if risk_score >= 2:
#             risk_level = "High"
#         elif risk_score == 1:
#             risk_level = "Moderate"
#         else:
#             risk_level = "Low"
#
#         if st.button("Generate Report"):
#             file_path = generate_product_report(
#                 selected_prod,
#                 kpi_row,
#                 recommendation,
#                 risk_level
#             )
#
#             with open(file_path, "rb") as f:
#                 st.download_button(
#                     label="Download Report",
#                     data=f,
#                     file_name=file_path,
#                     mime="application/pdf"
#                 )

with tab6:
    st.title("Smart Report Generator")

    from modules.report import generate_context_report

    if st.button("Generate Full Report"):
        file_path = generate_context_report(
            st.session_state,
            df,
            kpis_df
        )

        with open(file_path, "rb") as f:
            st.download_button(
                "Download Report",
                data=f,
                file_name="smart_report.pdf",
                mime="application/pdf"
            )