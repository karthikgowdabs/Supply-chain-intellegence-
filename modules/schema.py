import pandas as pd

REQUIRED_COLUMNS = [
    "date",
    "sales",
    "price",
    "rating"
]

OPTIONAL_COLUMNS = [
    "returns"
]

def validate_schema(df):
    # Required columns check
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    # Handle optional columns
    for col in OPTIONAL_COLUMNS:
        if col not in df.columns:
            df[col] = 0  # default value

    # Date validation
    # try:
    #     df['date'] = pd.to_datetime(df['date'], errors='raise')
    # except:
    #     raise ValueError("Column 'date' must be valid datetime format")
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Detect bad rows
    invalid_dates = df['date'].isnull().sum()

    if invalid_dates > 0:
        raise ValueError(f"{invalid_dates} invalid date values found in dataset")
    # Numeric validation
    numeric_cols = ["sales", "price", "rating", "returns"]

    for col in numeric_cols:
        if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
            raise ValueError(f"Column '{col}' must be numeric")

    return df