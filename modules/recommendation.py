def generate_recommendation(product_id, causes_df, kpis_df):
    cause_row = causes_df[causes_df['product_id'] == product_id]
    kpi_row = kpis_df[kpis_df['product_id'] == product_id]

    if cause_row.empty or kpi_row.empty:
        return "Insufficient data to generate recommendation."

    cause = cause_row.iloc[0]['primary_cause']
    avg_sales = kpi_row.iloc[0]['avg_sales']
    volatility = kpi_row.iloc[0]['sales_volatility']

    # Rule-based logic (baseline)
    if "rating" in cause.lower():
        return "Sales decline is linked to rating drop. Improve product quality and customer feedback handling."

    elif "price" in cause.lower():
        return "Sales decline is linked to pricing issues. Consider price optimization or discounts."

    elif "stock" in cause.lower():
        return "Stockouts detected. Improve inventory management and supply chain."

    elif volatility > avg_sales:
        return "High volatility detected. Stabilize pricing and demand planning."

    else:
        return "Monitor performance. No critical action required yet."