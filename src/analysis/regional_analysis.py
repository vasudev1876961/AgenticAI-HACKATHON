"""
Regional Contribution & Geographical Drill-Down Analysis
Computes geographical breakdowns, regional variances, and reconciles regional
contributors to total company performance.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
from .cleaning import clean_numeric_value
from .compare_periods import calculate_delta, calculate_pct_change


def analyze_regional_breakdown(df_regional: pd.DataFrame) -> Dict[str, Any]:
    """
    Performs deterministic variance analysis across geographical regions (e.g., North, South, East, West).
    Computes regional revenue and profit impact and reconciles against corporate totals.
    """
    if df_regional is None or df_regional.empty:
        return {"status": "error", "message": "Regional dataframe is empty or None."}

    df = df_regional.copy()
    df.columns = [str(c).strip().replace(" ", "_") for c in df.columns]

    regions = df["Region"].unique()
    regional_summary = []
    
    total_rev_q2 = 0.0
    total_rev_q3 = 0.0
    total_profit_q2 = 0.0
    total_profit_q3 = 0.0

    for reg in regions:
        reg_df = df[df["Region"] == reg]
        q2_row = reg_df[reg_df["Period"] == "Q2"]
        q3_row = reg_df[reg_df["Period"] == "Q3"]

        if q2_row.empty or q3_row.empty:
            continue

        q2_rev = clean_numeric_value(q2_row["Revenue"].values[0]) or 0.0
        q3_rev = clean_numeric_value(q3_row["Revenue"].values[0]) or 0.0
        q2_cogs = clean_numeric_value(q2_row["COGS"].values[0]) or 0.0
        q3_cogs = clean_numeric_value(q3_row["COGS"].values[0]) or 0.0
        q2_mkt = clean_numeric_value(q2_row["Marketing"].values[0]) or 0.0
        q3_mkt = clean_numeric_value(q3_row["Marketing"].values[0]) or 0.0
        q2_opex = clean_numeric_value(q2_row["Other_Opex"].values[0]) or 0.0
        q3_opex = clean_numeric_value(q3_row["Other_Opex"].values[0]) or 0.0

        p_q2 = q2_rev - q2_cogs - q2_mkt - q2_opex
        p_q3 = q3_rev - q3_cogs - q3_mkt - q3_opex

        rev_delta = calculate_delta(q2_rev, q3_rev)
        profit_delta = calculate_delta(p_q2, p_q3)
        rev_pct = calculate_pct_change(q2_rev, q3_rev)
        profit_pct = calculate_pct_change(p_q2, p_q3)

        total_rev_q2 += q2_rev
        total_rev_q3 += q3_rev
        total_profit_q2 += p_q2
        total_profit_q3 += p_q3

        regional_summary.append({
            "region": reg,
            "q2_revenue": q2_rev,
            "q3_revenue": q3_rev,
            "revenue_delta": rev_delta,
            "revenue_pct_change": rev_pct,
            "q2_profit": p_q2,
            "q3_profit": p_q3,
            "profit_delta": profit_delta,
            "profit_pct_change": profit_pct
        })

    total_rev_delta = calculate_delta(total_rev_q2, total_rev_q3)
    total_profit_delta = calculate_delta(total_profit_q2, total_profit_q3)

    # Compute share of total revenue contraction
    for item in regional_summary:
        if total_rev_delta != 0:
            share = (item["revenue_delta"] / total_rev_delta) * 100.0
            item["share_of_revenue_change_pct"] = round(share, 1)
        else:
            item["share_of_revenue_change_pct"] = 0.0

    # Rank regions by largest adverse revenue impact
    regional_summary.sort(key=lambda x: x["revenue_delta"])

    return {
        "status": "success",
        "regions": regional_summary,
        "total_revenue_q2": total_rev_q2,
        "total_revenue_q3": total_rev_q3,
        "total_revenue_delta": total_rev_delta,
        "total_profit_q2": total_profit_q2,
        "total_profit_q3": total_profit_q3,
        "total_profit_delta": total_profit_delta,
        "primary_revenue_drag_region": regional_summary[0]["region"] if regional_summary else None,
        "is_reconciled": abs(sum(r["revenue_delta"] for r in regional_summary) - total_rev_delta) < 1e-4
    }
