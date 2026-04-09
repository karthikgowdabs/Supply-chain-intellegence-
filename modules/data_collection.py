# import pandas as pd
# import os
# import re
#
# REQUIRED_COLUMNS = [
#     'product_id', 'date', 'sales', 'price',
#     'rating', 'trend_index', 'competitor_launch'
# ]
#
# OPTIONAL_COLUMNS = [
#     'category', 'inventory_level', 'stockouts', 'promo_flag',
#     'marketing_spend', 'returns_rate', 'lead_time_days',
#     'region', 'channel'
# ]
#
# def load_dataset(filepath: str) -> pd.DataFrame:
#     """
#     Loads the dataset from the specified path, validates columns,
#     and performs initial type conversion.
#
#     Args:
#         filepath (str): Path to the CSV file.
#
#     Returns:
#         pd.DataFrame: Loaded and validated dataframe.
#
#     Raises:
#         ValueError: If required columns are missing and cannot be inferred.
#         FileNotFoundError: If the file does not exist.
#     """
#     if not os.path.exists(filepath):
#         raise FileNotFoundError(f"Dataset not found at: {filepath}")
#
#     try:
#         df = pd.read_csv(filepath)
#     except Exception as e:
#         raise ValueError(f"Failed to read CSV file: {e}")
#
#     # Check for missing required columns
#     missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
#
#     if missing_cols:
#         raise ValueError(f"Missing required columns: {missing_cols}")
#
#     # Standardize Date
#     if 'date' in df.columns:
#         df['date'] = pd.to_datetime(df['date'], errors='coerce')
#         if df['date'].isnull().any():
#             print("Warning: Some dates could not be parsed and were set to NaT.")
#
#     # Smart Category Extraction if missing
#     if 'category' not in df.columns:
#         print("Notice: 'category' column missing. Attempting to extract from 'product_id'...")
#         df['category'] = df['product_id'].apply(_extract_category)
#
#     # Fill optional columns with sensible defaults if missing
#     for col in OPTIONAL_COLUMNS:
#         if col not in df.columns:
#             if col == 'category': continue # Already handled
#             df[col] = _get_default_value(col)
#
#     return df
#
# def _extract_category(product_id: str) -> str:
#     """
#     Extracts category from product_id string like 'Name (Category)'.
#     Returns 'Unknown' if pattern not found.
#     """
#     if not isinstance(product_id, str):
#         return "Unknown"
#
#     match = re.search(r'\((.*?)\)$', product_id)
#     if match:
#         return match.group(1).strip()
#     return "Unknown"
#
# def _get_default_value(col_name: str):
#     """Returns safe default values for optional columns."""
#     defaults = {
#         'inventory_level': 0,
#         'stockouts': 0,
#         'promo_flag': 0,
#         'marketing_spend': 0.0,
#         'returns_rate': 0.0,
#         'lead_time_days': 0,
#         'region': 'Global',
#         'channel': 'Omnichannel'
#     }
#     return defaults.get(col_name, None)

import pandas as pd
import os


def load_dataset(filepath: str) -> pd.DataFrame:
    """
    Loads the dataset from the specified path.

    Responsibilities:
    - ONLY load data
    - NO validation
    - NO cleaning
    - NO feature engineering

    Args:
        filepath (str): Path to the CSV file.

    Returns:
        pd.DataFrame: Raw loaded dataframe

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If CSV cannot be read
    """

    # Check file existence
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found at: {filepath}")

    # Load CSV
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        raise ValueError(f"Failed to read CSV file: {e}")

    return df