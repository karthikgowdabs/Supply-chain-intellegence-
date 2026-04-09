import pandas as pd
import numpy as np

def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.sort_values(['product_id', 'date'])

    grouped = df.groupby('product_id')

    df['sales_roll3'] = grouped['sales'].transform(
        lambda x: x.shift(1).rolling(window=3, min_periods=1).mean()
    )

    df['sales_roll6'] = grouped['sales'].transform(
        lambda x: x.shift(1).rolling(window=6, min_periods=1).mean()
    )

    df['sales_pct_change'] = grouped['sales'].pct_change().fillna(0)
    df['price_pct_change'] = grouped['price'].pct_change().fillna(0)
    df['rating_pct_change'] = grouped['rating'].pct_change().fillna(0)

    if 'trend_index' in df.columns:
        df['trend_pct_change'] = grouped['trend_index'].pct_change().fillna(0)

    return df

import pandas as pd
import numpy as np

def aggregate_product_kpis(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Ensure proper sorting for growth calculation
    df = df.sort_values(['product_id', 'date'])

    grouped = df.groupby('product_id')

    kpis = grouped.agg(
        total_sales=('sales', 'sum'),
        avg_sales=('sales', 'mean'),
        sales_volatility=('sales', 'std'),

        avg_price=('price', 'mean'),
        price_volatility=('price', 'std'),

        avg_rating=('rating', 'mean'),
        rating_volatility=('rating', 'std')
    ).reset_index()

    # Handle optional columns safely
    if 'returns' in df.columns:
        return_rate = grouped['returns'].mean().reset_index(name='return_rate')
        kpis = kpis.merge(return_rate, on='product_id', how='left')
    else:
        kpis['return_rate'] = 0

    # Growth calculation (safe)
    def get_growth(x):
        if len(x) < 2:
            return 0
        first = x.iloc[0]
        last = x.iloc[-1]
        if first == 0:
            return 0
        return (last - first) / first

    growth = grouped['sales'].apply(get_growth).reset_index(name='sales_growth')

    kpis = kpis.merge(growth, on='product_id', how='left')

    # Fill NaN (important for std)
    kpis = kpis.fillna(0)

    return kpis
