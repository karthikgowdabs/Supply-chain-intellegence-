import pandas as pd
import numpy as np

def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the dataset by sorting, processing duplicates, and imputing missing values.
    
    Args:
        df: Raw pandas DataFrame.
        
    Returns:
        pd.DataFrame: Cleaned DataFrame.
    """
    # Sort by product and date to ensure time-series order
    df = df.sort_values(by=['product_id', 'date']).reset_index(drop=True)
    
    # Handle duplicates: Keep last entry for same product-date
    if df.duplicated(subset=['product_id', 'date']).any():
        print(f"Removed {df.duplicated(subset=['product_id', 'date']).sum()} duplicate records.")
        df = df.drop_duplicates(subset=['product_id', 'date'], keep='last')
    
    # Impute missing values
    # Price: Forward fill (assume price holds until changed), then backward fill for starts
    df['price'] = df.groupby('product_id')['price'].ffill().bfill()
    
    # Rating: Fill with product's median, then global median
    df['rating'] = df.groupby('product_id')['rating'].transform(
        lambda x: x.fillna(x.median())
    )
    df['rating'] = df['rating'].fillna(df['rating'].median())
    
    # Trend Index: Fill with median (safe default)
    df['trend_index'] = df['trend_index'].fillna(50.0) # Assume neutral trend if missing
    
    # Sales: Fill with 0 (assuming no record means no sales, or use interpolation? 0 is safer for now)
    df['sales'] = df['sales'].fillna(0).astype(int)
    
    # Competitor Launch: Fill with 0 (assume no launch)
    df['competitor_launch'] = df['competitor_launch'].fillna(0).astype(int)
    
    return df
