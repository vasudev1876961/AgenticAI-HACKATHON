"""
Period comparison and variance metrics.
Calculates absolute change, percentage change, with explicit zero-baseline protection.
"""

from typing import Dict, Any, Optional
from .cleaning import clean_numeric_value


def calculate_delta(v1: float, v2: float) -> float:
    """Calculates absolute change: v2 - v1."""
    return round(v2 - v1, 4)


def calculate_pct_change(v1: float, v2: float) -> Optional[float]:
    """
    Calculates percentage change: ((v2 - v1) / v1) * 100.
    Returns None if base value v1 is 0.0 (undefined percentage change).
    """
    if v1 == 0.0:
        return None
    return round(((v2 - v1) / v1) * 100.0, 2)


def compare_periods(
    metric_name: str,
    period1_name: str,
    period1_val: Any,
    period2_name: str,
    period2_val: Any
) -> Dict[str, Any]:
    """
    Performs deterministic period comparison between two numeric points.
    """
    v1 = clean_numeric_value(period1_val)
    v2 = clean_numeric_value(period2_val)

    if v1 is None or v2 is None:
        return {
            "metric": metric_name,
            "period_1": period1_name,
            "value_1": period1_val,
            "period_2": period2_name,
            "value_2": period2_val,
            "delta": None,
            "pct_change": None,
            "status": "error",
            "message": f"Non-numeric values encountered: {period1_val}, {period2_val}"
        }

    delta = calculate_delta(v1, v2)
    pct = calculate_pct_change(v1, v2)

    pct_str = f"{pct:+.2f}%" if pct is not None else "Undefined (baseline is 0)"

    return {
        "metric": metric_name,
        "period_1": period1_name,
        "value_1": v1,
        "period_2": period2_name,
        "value_2": v2,
        "delta": delta,
        "pct_change": pct,
        "pct_change_str": pct_str,
        "status": "success",
        "direction": "increase" if delta > 0 else ("decrease" if delta < 0 else "neutral")
    }
