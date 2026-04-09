import pandas as pd
from prophet import Prophet

def forecast_sales(df: pd.DataFrame, product_id: str, periods=90):
    df = df.copy()

    periods = int(periods)

    # Filter product
    df = df[df['product_id'] == product_id]

    ts = df[['date', 'sales']].copy()
    ts = ts.rename(columns={'date': 'ds', 'sales': 'y'})
    ts = ts.sort_values('ds')

    if len(ts) < 5:
        raise ValueError("Not enough data")

    # 🔥 Normalize (VERY IMPORTANT)
    mean = ts['y'].mean()
    std = ts['y'].std() if ts['y'].std() != 0 else 1
    ts['y'] = (ts['y'] - mean) / std

    # 🔥 Better model
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        changepoint_prior_scale=0.5
    )

    model.fit(ts)

    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)

    # 🔥 Reverse scaling
    forecast['yhat'] = forecast['yhat'] * std + mean
    forecast['yhat_upper'] = forecast['yhat_upper'] * std + mean
    forecast['yhat_lower'] = forecast['yhat_lower'] * std + mean

    return forecast