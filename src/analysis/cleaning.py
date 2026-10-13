"""
Data cleaning and numeric sanitization utilities.
"""

import re
from typing import Any, Union, Optional
import pandas as pd


def clean_numeric_value(val: Any) -> Optional[float]:
    """
    Sanitizes string/numeric inputs into floats.
    Handles currency symbols (₹, $, €), commas (1,000 -> 1000), parenthesized negatives ((50) -> -50).
    """
    if val is None or pd.isna(val):
        return None
    if isinstance(val, (int, float)):
        return float(val)

    val_str = str(val).strip()
    if not val_str:
        return None

    # Handle negative notation like (100) or -100
    is_negative = False
    if val_str.startswith("(") and val_str.endswith(")"):
        is_negative = True
        val_str = val_str[1:-1].strip()
    elif val_str.startswith("-") or val_str.startswith("−"):
        is_negative = True
        val_str = val_str[1:].strip()

    # Remove currency symbols and formatting commas
    cleaned = re.sub(r'[₹\$€,\s]', '', val_str)
    
    # Handle 'k' or 'm' multipliers if present
    multiplier = 1.0
    if cleaned.lower().endswith('k'):
        multiplier = 1000.0
        cleaned = cleaned[:-1]
    elif cleaned.lower().endswith('m'):
        multiplier = 1000000.0
        cleaned = cleaned[:-1]

    try:
        num = float(cleaned) * multiplier
        return -num if is_negative else num
    except ValueError:
        return None


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Normalizes column names and converts numeric columns cleanly."""
    clean_df = df.copy()
    clean_df.columns = [str(c).strip().replace(" ", "_") for c in clean_df.columns]
    return clean_df
