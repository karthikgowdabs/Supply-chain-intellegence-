import pytest
import pandas as pd
import os
from modules.data_collection import load_dataset, _extract_category

def test_extract_category():
    assert _extract_category("TV Model (Electronics)") == "Electronics"
    assert _extract_category("Simple Product") == "Unknown"
    assert _extract_category("Ambiguous (Type A) (Type B)") == "Type B" # Last one

def test_load_dataset_missing_file():
    with pytest.raises(FileNotFoundError):
        load_dataset("non_existent.csv")
