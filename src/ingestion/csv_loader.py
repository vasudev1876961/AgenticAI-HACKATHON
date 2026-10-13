"""
CSV Loader using pandas
Extracts tabular structure, column headers, row records, and text summaries with row numbers.
"""

import os
from typing import Dict, Any, List
import pandas as pd


def load_csv(file_path: str) -> Dict[str, Any]:
    """
    Extracts structured rows and summary text from a CSV file.
    Returns:
        - columns: list of str
        - num_rows: int
        - rows: list of row records with row_index (2-indexed, row 1 is header)
        - dataframe: pandas.DataFrame
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    df = pd.read_csv(file_path)
    file_name = os.path.basename(file_path)

    row_records = []
    for idx, row in df.iterrows():
        row_dict = row.to_dict()
        cleaned_dict = {k: (None if pd.isna(v) else v) for k, v in row_dict.items()}
        row_num = idx + 2
        row_text = f"File '{file_name}', Row {row_num}: " + ", ".join(f"{k}={v}" for k, v in cleaned_dict.items())
        row_records.append({
            "row_index": row_num,
            "data": cleaned_dict,
            "text": row_text
        })

    return {
        "columns": list(df.columns),
        "num_rows": len(df),
        "rows": row_records,
        "dataframe": df
    }
