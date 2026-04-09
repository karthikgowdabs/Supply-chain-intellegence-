import pandas as pd
from sklearn.ensemble import IsolationForest


def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Select relevant features
    features = ['sales', 'price', 'rating']

    # Only keep existing columns
    features = [col for col in features if col in df.columns]

    model = IsolationForest(contamination=0.05, random_state=42)

    df['anomaly_flag'] = model.fit_predict(df[features])

    # Convert:
    # -1 → anomaly
    #  1 → normal
    df['anomaly_flag'] = df['anomaly_flag'].apply(lambda x: 1 if x == -1 else 0)

    return df