"""
Counterfactual Simulation & Sensitivity Engine
Allows deterministic "What-If" analysis of enterprise financials:
- Simulates counterfactual interventions (e.g. flat marketing, price cushions, cost renegotiations)
- Recalculates operating profit and profit bridge deterministically
- Computes profit recovery deltas and % of loss recovered
- Generates 2D sensitivity matrices across varying operational variables
- Evaluates and ranks strategic recovery playbooks
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import copy
from .cleaning import clean_numeric_value
from .contribution_analysis import calculate_profit_bridge, ProfitBridgeResult


@dataclass
class CounterfactualScenarioResult:
    scenario_name: str
    description: str
    baseline_profit_delta: float
    counterfactual_profit_delta: float
    profit_recovery_amount: float
    recovery_percentage: Optional[float]
    counterfactual_bridge: ProfitBridgeResult
    modified_parameters: Dict[str, Any]
    is_reconciled: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_name": self.scenario_name,
            "description": self.description,
            "baseline_profit_delta": self.baseline_profit_delta,
            "counterfactual_profit_delta": self.counterfactual_profit_delta,
            "profit_recovery_amount": round(self.profit_recovery_amount, 4),
            "recovery_percentage": round(self.recovery_percentage, 2) if self.recovery_percentage is not None else None,
            "counterfactual_bridge": self.counterfactual_bridge.to_dict(),
            "modified_parameters": self.modified_parameters,
            "is_reconciled": self.is_reconciled
        }


def simulate_counterfactual(
    p1: Dict[str, Any],
    p2: Dict[str, Any],
    modifications: Dict[str, Any],
    scenario_name: str = "Custom Counterfactual",
    description: str = "",
    p1_name: str = "Q2",
    p2_name: str = "Q3"
) -> CounterfactualScenarioResult:
    """
    Deterministically simulates a counterfactual scenario by modifying P2 parameters.
    
    Supported modification keys:
    - Absolute overrides: 'revenue', 'cogs', 'marketing', 'other_opex'
    - Relative deltas: 'revenue_delta', 'cogs_delta', 'marketing_delta', 'other_opex_delta'
    - Percentage changes from baseline P2: 'revenue_pct', 'cogs_pct', 'marketing_pct', 'other_opex_pct'
    """
    # 1. Compute baseline profit bridge
    baseline_bridge = calculate_profit_bridge(p1, p2, p1_name=p1_name, p2_name=p2_name)
    baseline_delta_profit = baseline_bridge.total_delta_profit

    # 2. Create modified P2 dictionary
    sim_p2 = copy.deepcopy(p2)

    # Apply absolute overrides
    for key in ["revenue", "cogs", "marketing", "other_opex"]:
        if key in modifications and modifications[key] is not None:
            sim_p2[key] = clean_numeric_value(modifications[key])

    # Apply relative deltas (e.g. marketing_delta = -15 means reduce Q3 marketing by 15)
    for key in ["revenue", "cogs", "marketing", "other_opex"]:
        delta_key = f"{key}_delta"
        if delta_key in modifications and modifications[delta_key] is not None:
            curr_val = clean_numeric_value(sim_p2[key])
            sim_p2[key] = curr_val + clean_numeric_value(modifications[delta_key])

    # Apply percentage adjustments (e.g. marketing_pct = -0.20 means reduce by 20%)
    for key in ["revenue", "cogs", "marketing", "other_opex"]:
        pct_key = f"{key}_pct"
        if pct_key in modifications and modifications[pct_key] is not None:
            curr_val = clean_numeric_value(sim_p2[key])
            sim_p2[key] = curr_val * (1.0 + float(modifications[pct_key]))

    # 3. Compute counterfactual profit bridge
    cf_bridge = calculate_profit_bridge(p1, sim_p2, p1_name=p1_name, p2_name=p2_name)
    cf_delta_profit = cf_bridge.total_delta_profit

    # 4. Compute recovery metrics
    # If baseline profit fell by -80k and counterfactual falls by -55k, recovery = +25k
    profit_recovery = cf_delta_profit - baseline_delta_profit

    # Recovery percentage relative to the baseline loss
    if baseline_delta_profit < 0:
        recovery_pct = (profit_recovery / abs(baseline_delta_profit)) * 100.0
    elif baseline_delta_profit > 0:
        recovery_pct = (profit_recovery / baseline_delta_profit) * 100.0
    else:
        recovery_pct = 0.0

    return CounterfactualScenarioResult(
        scenario_name=scenario_name,
        description=description,
        baseline_profit_delta=baseline_delta_profit,
        counterfactual_profit_delta=cf_delta_profit,
        profit_recovery_amount=profit_recovery,
        recovery_percentage=recovery_pct,
        counterfactual_bridge=cf_bridge,
        modified_parameters=modifications,
        is_reconciled=cf_bridge.is_reconciled
    )


def generate_sensitivity_matrix(
    p1: Dict[str, Any],
    p2: Dict[str, Any],
    var1_name: str = "revenue",
    var1_multipliers: Optional[List[float]] = None,
    var2_name: str = "marketing",
    var2_multipliers: Optional[List[float]] = None,
    p1_name: str = "Q2",
    p2_name: str = "Q3"
) -> Dict[str, Any]:
    """
    Computes a 2D sensitivity grid evaluating combinations of two key cost/revenue drivers.
    Default: Revenue multipliers [-10%, -5%, 0%, +5%, +10%] vs Marketing multipliers [-20%, -10%, 0%, +10%, +20%].
    """
    if var1_multipliers is None:
        var1_multipliers = [-0.10, -0.05, 0.0, 0.05, 0.10]
    if var2_multipliers is None:
        var2_multipliers = [-0.20, -0.10, 0.0, 0.10, 0.20]

    base_v1 = clean_numeric_value(p2[var1_name])
    base_v2 = clean_numeric_value(p2[var2_name])

    matrix_rows = []
    for m1 in var1_multipliers:
        row_vals = []
        val1 = base_v1 * (1.0 + m1)
        for m2 in var2_multipliers:
            val2 = base_v2 * (1.0 + m2)
            sim_res = simulate_counterfactual(
                p1, p2,
                modifications={var1_name: val1, var2_name: val2},
                p1_name=p1_name,
                p2_name=p2_name
            )
            row_vals.append({
                "var1_pct": f"{m1 * 100:+.0f}%",
                "var2_pct": f"{m2 * 100:+.0f}%",
                "var1_val": round(val1, 1),
                "var2_val": round(val2, 1),
                "resulting_profit": round(sim_res.counterfactual_bridge.p_end, 1),
                "profit_delta": round(sim_res.counterfactual_profit_delta, 1),
                "recovery_amount": round(sim_res.profit_recovery_amount, 1)
            })
        matrix_rows.append({
            "var1_pct_label": f"{m1 * 100:+.0f}%",
            "var1_val": round(val1, 1),
            "columns": row_vals
        })

    return {
        "var1_name": var1_name,
        "var2_name": var2_name,
        "var1_labels": [f"{m * 100:+.0f}%" for m in var1_multipliers],
        "var2_labels": [f"{m * 100:+.0f}%" for m in var2_multipliers],
        "grid": matrix_rows
    }


def rank_recovery_levers(
    p1: Dict[str, Any],
    p2: Dict[str, Any],
    p1_name: str = "Q2",
    p2_name: str = "Q3"
) -> List[Dict[str, Any]]:
    """
    Simulates standard executive interventions and ranks them by profit recovery.
    """
    scenarios = [
        {
            "name": "Flat Marketing Policy",
            "desc": "Hold marketing expenses flat at Q2 level (₹100k) rather than allowing ₹25k surge.",
            "mods": {"marketing": clean_numeric_value(p1["marketing"])}
        },
        {
            "name": "50% Revenue Shock Cushion",
            "desc": "Preserve 50% of the lost revenue through targeted retention (Revenue at ₹970k instead of ₹940k).",
            "mods": {"revenue_delta": abs(clean_numeric_value(p2["revenue"]) - clean_numeric_value(p1["revenue"])) * 0.5}
        },
        {
            "name": "Aggressive COGS Supplier Renegotiation",
            "desc": "Deepen COGS savings by an additional ₹15k through supply chain optimization (COGS at ₹570k).",
            "mods": {"cogs_delta": -15.0}
        },
        {
            "name": "Strict Other Opex Freeze",
            "desc": "Freeze administrative and operational overhead at Q2 levels (₹150k instead of ₹160k).",
            "mods": {"other_opex": clean_numeric_value(p1["other_opex"])}
        },
        {
            "name": "Combined Disciplined Playbook",
            "desc": "Implement both Flat Marketing Policy (₹100k) and Other Opex Freeze (₹150k).",
            "mods": {
                "marketing": clean_numeric_value(p1["marketing"]),
                "other_opex": clean_numeric_value(p1["other_opex"])
            }
        }
    ]

    results = []
    for s in scenarios:
        sim = simulate_counterfactual(
            p1=p1,
            p2=p2,
            modifications=s["mods"],
            scenario_name=s["name"],
            description=s["desc"],
            p1_name=p1_name,
            p2_name=p2_name
        )
        results.append({
            "scenario_name": sim.scenario_name,
            "description": sim.description,
            "new_profit": sim.counterfactual_bridge.p_end,
            "new_profit_delta": sim.counterfactual_profit_delta,
            "recovery_amount": sim.profit_recovery_amount,
            "recovery_pct": sim.recovery_percentage,
            "is_reconciled": sim.is_reconciled
        })

    # Sort descending by recovery amount
    results.sort(key=lambda x: x["recovery_amount"], reverse=True)
    return results
