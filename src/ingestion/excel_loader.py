"""
Excel Loader using pandas and openpyxl
Extracts all sheets, dimensions, headers, cell/row references, and tabular DataFrames.
"""

import os
from typing import Dict, Any, List
import pandas as pd
import openpyxl


def load_excel(file_path: str) -> Dict[str, Any]:
    """
    Extracts all sheets and structured row/cell information from an Excel workbook.
    Returns:
        - sheets: dict of sheet_name -> list of row records (with row_index, values, text summary)
        - dataframes: dict of sheet_name -> pandas.DataFrame
        - summary: list of metadata strings
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Excel file not found: {file_path}")

    wb = openpyxl.load_workbook(file_path, data_only=True)
    sheet_names = wb.sheetnames
    wb.close()

    sheets_data = {}
    dataframes = {}
    summary = []

    for name in sheet_names:
        df = pd.read_excel(file_path, sheet_name=name)
        dataframes[name] = df

        row_records = []
        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            # Clean NaN
            cleaned_dict = {k: (None if pd.isna(v) else v) for k, v in row_dict.items()}
            row_num = idx + 2  # 1-indexed, accounting for header row 1
            row_text = f"Sheet '{name}', Row {row_num}: " + ", ".join(f"{k}={v}" for k, v in cleaned_dict.items())
            row_records.append({
                "row_index": row_num,
                "data": cleaned_dict,
                "text": row_text,
                "sheet_name": name
            })

        sheets_data[name] = {
            "columns": list(df.columns),
            "num_rows": len(df),
            "rows": row_records
        }
        summary.append(f"Sheet '{name}' ({len(df)} rows, columns: {list(df.columns)})")

    return {
        "sheet_names": sheet_names,
        "sheets": sheets_data,
        "dataframes": dataframes,
        "summary": summary
    }
