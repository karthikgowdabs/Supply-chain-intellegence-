# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
# from reportlab.lib.styles import getSampleStyleSheet
#
#
# def generate_product_report(product_id, kpi_row, recommendation, risk_level):
#     file_path = f"{product_id}_report.pdf"
#
#     doc = SimpleDocTemplate(file_path)
#     styles = getSampleStyleSheet()
#
#     content = []
#
#     # Title
#     content.append(Paragraph(f"Product Report: {product_id}", styles['Title']))
#     content.append(Spacer(1, 12))
#
#     # KPIs
#     content.append(Paragraph("Key Performance Indicators", styles['Heading2']))
#     content.append(Spacer(1, 8))
#
#     content.append(Paragraph(f"Average Sales: {kpi_row['avg_sales']:.2f}", styles['Normal']))
#     content.append(Paragraph(f"Sales Volatility: {kpi_row['sales_volatility']:.2f}", styles['Normal']))
#     content.append(Paragraph(f"Average Price: {kpi_row['avg_price']:.2f}", styles['Normal']))
#     content.append(Paragraph(f"Average Rating: {kpi_row['avg_rating']:.2f}", styles['Normal']))
#     content.append(Spacer(1, 12))
#
#     # Risk
#     content.append(Paragraph("Risk Assessment", styles['Heading2']))
#     content.append(Paragraph(f"Risk Level: {risk_level}", styles['Normal']))
#     content.append(Spacer(1, 12))
#
#     # Recommendation
#     content.append(Paragraph("Recommended Action", styles['Heading2']))
#     content.append(Paragraph(recommendation, styles['Normal']))
#
#     doc.build(content)
#
#     return file_path

import plotly.express as px


def create_sales_chart(prod_data):
    fig = px.line(prod_data, x='date', y='sales', title="Sales Trend")

    file_path = "temp_chart.png"
    fig.write_image(file_path)

    return file_path

def generate_summary(context):
    summary = "This report provides insights into product performance. "

    if "last_product" in context:
        summary += f"Product {context['last_product']} was analyzed. "

        if context.get("last_decline"):
            summary += "A decline has been detected. "

    if "last_forecast_trend" in context:
        if context["last_forecast_trend"] < 0:
            summary += "Future trend indicates decline. "
        else:
            summary += "Growth is expected. "

    if "last_risk" in context:
        summary += f"Risk level is {context['last_risk']}. "

    return summary

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

def generate_context_report(context, df, kpis_df):
    file_path = "analysis_report.pdf"
    styles = getSampleStyleSheet()

    doc = SimpleDocTemplate(file_path)
    content = []

    # Title
    content.append(Paragraph("Supply Chain Intelligence and Sales decline analysis Report", styles['Title']))
    content.append(Spacer(1, 12))

    # Summary
    summary = generate_summary(context)
    content.append(Paragraph(
        "<font size=12 color='black'><b>Executive Summary</b></font>",
        styles['Normal']
    ))
    content.append(Paragraph(summary, styles['Normal']))
    content.append(Spacer(1, 12))

    # Product Section
    if "last_product" in context:
        prod = context["last_product"]
        prod_data = df[df['product_id'] == prod]

        content.append(Paragraph(f"Product: {prod}", styles['Heading2']))

        chart = create_sales_chart(prod_data)
        content.append(Image(chart, width=400, height=200))

        kpi = kpis_df[kpis_df['product_id'] == prod].iloc[0]

        content.append(Paragraph(
            f"<b>Average Sales:</b> {kpi['avg_sales']:.2f}",
            styles['Normal']
        ))
        content.append(Paragraph(f"Volatility: {kpi['sales_volatility']:.2f}", styles['Normal']))
        content.append(Spacer(1, 10))

    # Comparison
    if "compare_products" in context:
        content.append(Paragraph("Comparison", styles['Heading2']))

        for p in context["compare_products"]:
            kpi = kpis_df[kpis_df['product_id'] == p].iloc[0]
            content.append(Paragraph(f"{p}: Avg Sales {kpi['avg_sales']:.2f}", styles['Normal']))

    # Forecast
    if "last_forecast_product" in context:
        content.append(Paragraph("Forecast", styles['Heading2']))

        trend = context["last_forecast_trend"]
        msg = "Decline expected" if trend < 0 else "Growth expected"

        content.append(Paragraph(msg, styles['Normal']))

    doc.build(content)
    return file_path