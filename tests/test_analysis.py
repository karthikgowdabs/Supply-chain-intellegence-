import pandas as pd
import pytest
from modules.analysis import detect_declines, analyze_causes
from modules.features import compute_features

def test_detect_declines_simple():
    # Create synthetic data: Product A increases then drops 20% and stays there
    dates = pd.date_range(start='2023-01-01', periods=10, freq='MS')
    sales = [100, 110, 120, 120, 120, 90, 90, 90, 90, 90] # Peak 120. Drop to 90 is 25% drop (0.25 > 0.15)
    
    df = pd.DataFrame({
        'product_id': 'ProdA',
        'date': dates,
        'sales': sales,
        'price': 100.0,
        'rating': 4.5,
        'trend_index': 50.0
    })
    
    # We need compute_features to get sales_roll3
    # sales_roll3 for [.., 120, 120, 90] -> (120+120+90)/3 = 110. Peak roll might be (120+120+120)/3 = 120.
    # 90,90,90 -> 90. 90 is 25% less than 120.
    
    df = compute_features(df)
    
    # Run detection
    declines = detect_declines(df, threshold=0.15, sustain_months=3)
    
    assert not declines.empty
    assert declines.iloc[0]['product_id'] == 'ProdA'
    assert declines.iloc[0]['decline_confidence_score'] > 0
    
def test_cause_price_increase():
    # Setup: Price goes from 100 to 200 after peak
    dates = pd.date_range(start='2023-01-01', periods=10, freq='MS')
    sales = [100, 100, 100, 100, 100, 80, 80, 80, 80, 80] # Decline
    prices = [100, 100, 100, 100, 100, 200, 200, 200, 200, 200] # Price hike
    
    df = pd.DataFrame({
        'product_id': 'ProdB',
        'date': dates,
        'sales': sales,
        'price': prices,
        'rating': 4.5, # stable
        'trend_index': 50.0, # stable
        'competitor_launch': 0
    })
    
    df = compute_features(df)
    declines = detect_declines(df, threshold=0.15, sustain_months=3)
    
    causes_df = analyze_causes(df, declines)
    
    assert not causes_df.empty
    primary = causes_df.iloc[0]['primary_cause']
    assert "Price increased" in primary
