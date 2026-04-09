def run_pipeline(input_data, thresh, sustain):
    from modules.data_collection import load_dataset
    from modules.data_cleaning import clean_dataset
    from modules.features import compute_features, aggregate_product_kpis
    from modules.schema import validate_schema
    from modules.analysis import analyze_data
    from modules.forecasting import forecast_sales
    from modules.anomaly import detect_anomalies

    # 1. Load
    if isinstance(input_data, str):
        raw_df = load_dataset(input_data)
    else:
        raw_df = input_data.copy()

    # 2. Validate
    raw_df = validate_schema(raw_df)

    # 3. Clean
    clean_df = clean_dataset(raw_df)

    # 4. Features
    feat_df = compute_features(clean_df)
    # 5. anomaly
    feat_df = detect_anomalies(feat_df)


    # 6.. Analysis
    from modules.analysis import analyze_data

    analysis_results = analyze_data(feat_df, thresh, sustain)
    # 7. KPIs
    kpis = aggregate_product_kpis(feat_df)

    # forecast = forecast_sales(feat_df)

    return {
        "data": feat_df,
        "declines": analysis_results["declines"],
        "causes": analysis_results["causes"],
        "kpis": kpis,
        # "forecast": forecast  # NEW
    }