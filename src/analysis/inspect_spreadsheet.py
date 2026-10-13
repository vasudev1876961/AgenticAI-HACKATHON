"""
Spreadsheet Inspection & Schema Discovery
Extracts column names, row counts, data types, and scans for financial metrics.
"""

from typing import Dict, Any, List, Optional
import pandas as pd


def inspect_dataframe(df: pd.DataFrame, max_preview_rows: int = 5) -> Dict[str, Any]:
    """
    Produces schema metadata and statistical summaries of a pandas DataFrame.
    """
    if df is None or df.empty:
        return {"error": "DataFrame is empty or None"}

    columns_info = []
    for col in df.columns:
        series = df[col]
        non_null_count = int(series.count())
        dtype_str = str(series.dtype)
        sample_vals = [v for v in series.dropna().head(3).tolist()]
        columns_info.append({
            "name": str(col),
            "dtype": dtype_str,
            "non_null_count": non_null_count,
            "samples": sample_vals
        })

    preview = df.head(max_preview_rows).to_dict(orient="records")

    return {
        "num_rows": len(df),
        "num_columns": len(df.columns),
        "columns": columns_info,
        "preview": preview
    }


def find_metric_in_df(df: pd.DataFrame, metric_keyword: str) -> Optional[Dict[str, Any]]:
    """
    Searches row-wise (e.g. Metric column contains 'revenue') or column-wise.
    """
    keyword_clean = metric_keyword.lower().strip()
    
    # Check if a column has metric names (e.g. 'Metric', 'Category', 'Item')
    for col in df.columns:
        if df[col].dtype == object or str(df[col].dtype) == "string":
            match_mask = df[col].astype(str).str.lower().str.contains(keyword_clean, na=False)
            if match_mask.any():
                matched_row = df[match_mask].iloc[0].to_dict()
                return {
                    "matched_in": "row",
                    "column": col,
                    "row_data": matched_row
                }

    # Check column names directly
    for col in df.columns:
        if keyword_clean in str(col).lower():
            return {
                "matched_in": "column",
                "column_name": col,
                "values": df[col].tolist()
            }

    return None
