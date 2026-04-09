import pandas as pd
import numpy as np
from datetime import timedelta

def detect_declines(df: pd.DataFrame, threshold: float = 0.15, sustain_months: int = 3) -> pd.DataFrame:
    """
    Detects products with a significant decline in sales.
    
    Rule:
    1. Find peak sales month.
    2. Check if 3-month rolling average drops by >= threshold vs peak rolling average.
    3. Sustain for >= sustain_months.
    
    Returns:
        pd.DataFrame: Summary of declined products with dates and scores.
        Columns: product_id, peak_date, decline_start_date, decline_confidence_score, peak_sales_roll3
    """
    declines = []
    
    # Ensure relevant columns exist
    if 'sales_roll3' not in df.columns:
        raise ValueError("Feature 'sales_roll3' missing. Run compute_features first.")
        
    for product_id, group in df.groupby('product_id'):
        group = group.sort_values('date')
        if len(group) < sustain_months + 1:
            continue
            
        # 1. Find Peak (using rolling average to be robust to spikes)
        peak_idx = group['sales_roll3'].idxmax()
        peak_row = group.loc[peak_idx]
        peak_val = peak_row['sales_roll3']
        peak_date = peak_row['date']
        
        if peak_val == 0:
            continue
            
        # 2. Look at post-peak period
        post_peak = group[group['date'] > peak_date]
        if post_peak.empty:
            continue
            
        # Vectorized check for decline condition
        # masked is True where current <= peak * (1 - threshold)
        decline_mask = post_peak['sales_roll3'] <= (peak_val * (1 - threshold))
        
        # Find sustained sequence efficiently
        # We look for the first occurrence where the NEXT 'sustain_months' are all True
        
        decline_start = None
        
        # Convert mask to numpy for faster sliding window check
        mask_values = decline_mask.values
        dates = post_peak['date'].values
        
        n = len(mask_values)
        if n < sustain_months:
            continue
            
        for i in range(n - sustain_months + 1):
            if np.all(mask_values[i : i + sustain_months]):
                # Found it
                decline_start = dates[i]
                break
        
        if decline_start:
            # Calculate score: Magnitude of drop + duration factor
            # Get average drop in the sustained period
            sustained_period = post_peak[post_peak['date'] >= decline_start].head(sustain_months)
            avg_val = sustained_period['sales_roll3'].mean()
            drop_mag = (peak_val - avg_val) / peak_val
            
            # Simple confidence score logic
            confidence = min(1.0, drop_mag * 2) # normalize kinda
            
            declines.append({
                'product_id': product_id,
                'peak_date': peak_date,
                'decline_start_date': pd.Timestamp(decline_start),
                'decline_confidence_score': round(confidence, 2),
                'peak_sales_roll3': peak_val
            })
            
    return pd.DataFrame(declines)

def analyze_causes(df: pd.DataFrame, declines_df: pd.DataFrame) -> pd.DataFrame:
    """
    Identifies probable causes for each detected decline.
    """
    if declines_df.empty:
        return declines_df
        
    results = []
    
    df = df.sort_values(['product_id', 'date']).set_index('date')
    
    for _, row in declines_df.iterrows():
        pid = row['product_id']
        peak = row['peak_date']
        start = row['decline_start_date']
        
        # Get product data
        prod_data = df[df['product_id'] == pid]
        
        # Define windows
        # Pre-peak: 3 months leading up to and including peak
        pre_peak_window = prod_data.loc[:peak].tail(3)
        
        # Post-decline: Start of decline + 2 months (3 months total)
        post_decline_window = prod_data.loc[start:].head(3)
        
        if pre_peak_window.empty or post_decline_window.empty:
            continue
            
        # Compute averages map
        metrics = ['price', 'rating', 'trend_index', 'marketing_spend', 'inventory_level', 'stockouts', 'promo_flag']
        
        # Handle optional cols safely
        available_metrics = [m for m in metrics if m in prod_data.columns]
        
        pre_avgs = pre_peak_window[available_metrics].mean()
        post_avgs = post_decline_window[available_metrics].mean()
        
        causes = []
        
        # Rule 1: Price Increase
        if 'price' in pre_avgs:
            price_change = (post_avgs['price'] - pre_avgs['price']) / pre_avgs['price'] if pre_avgs['price'] > 0 else 0
            if price_change > 0.05:
                causes.append(f"Price increased by {price_change*100:.1f}%")
                
        # Rule 2: Satisfaction Drop
        if 'rating' in pre_avgs:
            rating_change = (post_avgs['rating'] - pre_avgs['rating']) / pre_avgs['rating'] if pre_avgs['rating'] > 0 else 0
            if rating_change < -0.05:
                causes.append(f"Rating dropped by {abs(rating_change)*100:.1f}% ({pre_avgs['rating']:.2f}->{post_avgs['rating']:.2f})")

        # Rule 3: Market Interest (Trend)
        if 'trend_index' in pre_avgs:
            trend_change = (post_avgs['trend_index'] - pre_avgs['trend_index']) / pre_avgs['trend_index'] if pre_avgs['trend_index'] > 0 else 0
            if trend_change < -0.10:
                causes.append(f"Market search interest fell by {abs(trend_change)*100:.1f}%")
                
        # Rule 4: Competitor Launch
        # Check window around decline start (+- 2 months)
        start_ts = pd.Timestamp(start)
        comp_window_start = start_ts - pd.DateOffset(months=2)
        comp_window_end = start_ts + pd.DateOffset(months=2)
        
        comp_launch_sum = prod_data.loc[comp_window_start:comp_window_end]['competitor_launch'].sum() if 'competitor_launch' in prod_data.columns else 0
        if comp_launch_sum > 0:
            causes.append(f"Competitor launch detected near decline start")
            
        # Rule 5: Supply Issue
        if 'stockouts' in pre_avgs:
             stockout_post = post_avgs['stockouts']
             if stockout_post > 0.1 and stockout_post > pre_avgs['stockouts']: # if >10% stockout rate
                 causes.append("Significant stockouts detected")
                 
        # Rule 6: Promo withdrawal
        if 'promo_flag' in pre_avgs and 'marketing_spend' in pre_avgs:
            if pre_avgs['promo_flag'] > 0.5 and post_avgs['promo_flag'] < 0.1:
                causes.append("Promotional period ended")
            elif pre_avgs['marketing_spend'] > post_avgs['marketing_spend'] * 1.5: # 50% drop
                causes.append("Marketing spend reduced significantly")
        
        if not causes:
            causes.append("Unknown / General Market Decline")
            
        # Add ranked causes summary
        results.append({
            'product_id': pid,
            'peak_date': peak,
            'decline_start_date': start,
            'causes': causes,
            'primary_cause': causes[0]
        })
        
    return pd.DataFrame(results)


def analyze_data(df, threshold, sustain_months):
    declines = detect_declines(df, threshold=threshold, sustain_months=sustain_months)

    causes = analyze_causes(df, declines)

    return {
        "declines": declines,
        "causes": causes
    }