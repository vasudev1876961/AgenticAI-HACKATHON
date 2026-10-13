"""
Contribution & Profit Bridge Analysis
Calculates deterministic profit bridges, variance breakdowns, and full reconciliation:
Delta P = Delta R - Delta C - Delta M - Delta O
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from .cleaning import clean_numeric_value
from .compare_periods import calculate_pct_change


@dataclass
class ProfitBridgeResult:
    p_start: float
    p_end: float
    total_delta_profit: float
    pct_change_profit: Optional[float]
    impacts: Dict[str, float]
    raw_changes: Dict[str, float]
    is_reconciled: bool
    reconciliation_discrepancy: float
    ranked_contributors: List[Dict[str, Any]]
    waterfall_steps: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "p_start": self.p_start,
            "p_end": self.p_end,
            "total_delta_profit": self.total_delta_profit,
            "pct_change_profit": self.pct_change_profit,
            "impacts": self.impacts,
            "raw_changes": self.raw_changes,
            "is_reconciled": self.is_reconciled,
            "reconciliation_discrepancy": round(self.reconciliation_discrepancy, 6),
            "ranked_contributors": self.ranked_contributors,
            "waterfall_steps": self.waterfall_steps
        }


def calculate_profit_bridge(
    p1: Dict[str, Any],
    p2: Dict[str, Any],
    p1_name: str = "Q2",
    p2_name: str = "Q3"
) -> ProfitBridgeResult:
    """
    Computes deterministic profit bridge variance between two periods.
    Required keys in p1 and p2:
        - revenue
        - cogs
        - marketing
        - other_opex
    """
    required_keys = ["revenue", "cogs", "marketing", "other_opex"]

    # Validate presence
    for name, p in [(p1_name, p1), (p2_name, p2)]:
        missing = [k for k in required_keys if k not in p]
        if missing:
            raise ValueError(f"{name} is missing required fields: {missing}")

    clean_p1 = {}
    clean_p2 = {}
    for k in required_keys:
        v1 = clean_numeric_value(p1[k])
        v2 = clean_numeric_value(p2[k])
        if v1 is None:
            raise TypeError(f"{p1_name}.{k} ({p1[k]}) must be numeric.")
        if v2 is None:
            raise TypeError(f"{p2_name}.{k} ({p2[k]}) must be numeric.")
        clean_p1[k] = v1
        clean_p2[k] = v2

    # Calculate Operating Profit: P = R - C - M - O
    profit_p1 = clean_p1["revenue"] - clean_p1["cogs"] - clean_p1["marketing"] - clean_p1["other_opex"]
    profit_p2 = clean_p2["revenue"] - clean_p2["cogs"] - clean_p2["marketing"] - clean_p2["other_opex"]
    total_delta_profit = profit_p2 - profit_p1

    # Raw value changes: End - Start
    raw_changes = {
        "revenue": round(clean_p2["revenue"] - clean_p1["revenue"], 4),
        "cogs": round(clean_p2["cogs"] - clean_p1["cogs"], 4),
        "marketing": round(clean_p2["marketing"] - clean_p1["marketing"], 4),
        "other_opex": round(clean_p2["other_opex"] - clean_p1["other_opex"], 4),
    }

    # Accounting impacts on operating profit:
    # Delta P = Delta R - Delta C - Delta M - Delta O
    impacts = {
        "revenue": round(raw_changes["revenue"], 4),
        "cogs": round(-raw_changes["cogs"], 4),           # Lower COGS is positive impact
        "marketing": round(-raw_changes["marketing"], 4),   # Higher marketing is negative impact
        "other_opex": round(-raw_changes["other_opex"], 4) # Higher opex is negative impact
    }

    # Mathematical reconciliation check
    sum_of_impacts = sum(impacts.values())
    discrepancy = abs(sum_of_impacts - total_delta_profit)
    is_reconciled = discrepancy < 1e-4

    pct_profit_change = calculate_pct_change(profit_p1, profit_p2)

    # Rank contributors by absolute impact magnitude
    ranked_contributors = []
    labels = {
        "revenue": "Revenue Change",
        "cogs": "Cost of Goods Sold (COGS)",
        "marketing": "Marketing Expenditures",
        "other_opex": "Other Operating Expenses"
    }

    for key, impact in impacts.items():
        raw_delta = raw_changes[key]
        ranked_contributors.append({
            "key": key,
            "label": labels[key],
            "raw_change": raw_delta,
            "profit_impact": impact,
            "absolute_impact": abs(impact),
            "nature": "adverse" if impact < 0 else ("favorable" if impact > 0 else "neutral")
        })

    ranked_contributors.sort(key=lambda x: x["absolute_impact"], reverse=True)

    # Waterfall visualization steps
    waterfall_steps = [
        {"name": f"{p1_name} Operating Profit", "amount": profit_p1, "type": "absolute"},
        {"name": "Revenue Impact", "amount": impacts["revenue"], "type": "relative"},
        {"name": "COGS Variance", "amount": impacts["cogs"], "type": "relative"},
        {"name": "Marketing Variance", "amount": impacts["marketing"], "type": "relative"},
        {"name": "Other Opex Variance", "amount": impacts["other_opex"], "type": "relative"},
        {"name": f"{p2_name} Operating Profit", "amount": profit_p2, "type": "total"}
    ]

    return ProfitBridgeResult(
        p_start=round(profit_p1, 4),
        p_end=round(profit_p2, 4),
        total_delta_profit=round(total_delta_profit, 4),
        pct_change_profit=pct_profit_change,
        impacts=impacts,
        raw_changes=raw_changes,
        is_reconciled=is_reconciled,
        reconciliation_discrepancy=discrepancy,
        ranked_contributors=ranked_contributors,
        waterfall_steps=waterfall_steps
    )
