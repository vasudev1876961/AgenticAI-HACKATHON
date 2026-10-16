"""
Macroeconomic Stress Testing & Black Swan Capital Resilience Engine
Simulates enterprise operating performance under multi-vector macroeconomic shocks:
Stagflation, CAC surge, supply-chain disruption, and regulatory overhead.
Calculates solvency thresholds, loss severity, and liquidity runway indices.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
import math


@dataclass
class ScenarioImpact:
    scenario_id: str
    name: str
    description: str
    revenue_shock_pct: float
    cogs_shock_pct: float
    marketing_shock_pct: float
    fixed_opex_shock_pct: float
    stressed_revenue: float
    stressed_cogs: float
    stressed_marketing: float
    stressed_opex: float
    stressed_profit: float
    stressed_margin_pct: float
    profit_delta_vs_baseline: float
    loss_severity_pct: float
    solvency_status: str  # "SOLVENT", "VULNERABLE", "DISTRESSED", "INSOLVENT"
    estimated_runway_months: float
    recommended_capital_buffer: float


@dataclass
class StressTestSummary:
    baseline_profit: float
    baseline_margin_pct: float
    num_scenarios_evaluated: int
    worst_case_scenario: str
    worst_case_profit: float
    max_capital_buffer_needed: float
    average_stressed_profit: float
    systemic_resilience_rating: str  # "AAA (High)", "BBB (Adequate)", "CCC (Vulnerable)", "D (Distressed)"
    scenarios: List[ScenarioImpact] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


PRESET_MACRO_SCENARIOS = [
    {
        "id": "STRESS-01",
        "name": "Stagflation Shock",
        "description": "Demand contraction coupled with COGS inflation and fixed overhead escalation.",
        "revenue_shock_pct": -0.15,
        "cogs_shock_pct": 0.12,
        "marketing_shock_pct": 0.05,
        "fixed_opex_shock_pct": 0.08,
    },
    {
        "id": "STRESS-02",
        "name": "CAC Hyper-Inflation & Market Saturation",
        "description": "Intensifying competitive advertising spend with diminishing customer acquisition return.",
        "revenue_shock_pct": -0.05,
        "cogs_shock_pct": 0.00,
        "marketing_shock_pct": 0.45,
        "fixed_opex_shock_pct": 0.05,
    },
    {
        "id": "STRESS-03",
        "name": "Supply Chain Fracture & Raw Material Spike",
        "description": "Logistics bottlenecks drive critical input costs up while order fulfillment delays dent sales.",
        "revenue_shock_pct": -0.08,
        "cogs_shock_pct": 0.20,
        "marketing_shock_pct": -0.10,
        "fixed_opex_shock_pct": 0.04,
    },
    {
        "id": "STRESS-04",
        "name": "Regulatory Compliance & Tech Migration Overhead",
        "description": "Unplanned compliance audit fees, legal provisions, and accelerated cloud migration expenses.",
        "revenue_shock_pct": 0.00,
        "cogs_shock_pct": 0.05,
        "marketing_shock_pct": 0.00,
        "fixed_opex_shock_pct": 0.25,
    }
]


def run_macro_stress_test(
    baseline_revenue: float = 940.0,
    baseline_cogs: float = 585.0,
    baseline_marketing: float = 125.0,
    baseline_fixed_opex: float = 160.0,
    initial_cash_reserve: float = 300.0,
    custom_scenarios: Optional[List[Dict[str, Any]]] = None
) -> StressTestSummary:
    """
    Simulates enterprise performance under adverse macroeconomic stress scenarios.
    """
    baseline_profit = baseline_revenue - baseline_cogs - baseline_marketing - baseline_fixed_opex
    baseline_margin = (baseline_profit / baseline_revenue * 100.0) if baseline_revenue > 0 else 0.0

    scenarios_to_run = custom_scenarios if custom_scenarios is not None else PRESET_MACRO_SCENARIOS
    evaluated: List[ScenarioImpact] = []

    worst_profit = baseline_profit
    worst_name = "Baseline"
    max_buffer = 0.0
    total_stressed_profit = 0.0

    for sc in scenarios_to_run:
        rev_shock = sc.get("revenue_shock_pct", 0.0)
        cogs_shock = sc.get("cogs_shock_pct", 0.0)
        mkt_shock = sc.get("marketing_shock_pct", 0.0)
        opex_shock = sc.get("fixed_opex_shock_pct", 0.0)

        s_rev = round(baseline_revenue * (1.0 + rev_shock), 2)
        s_cogs = round(baseline_cogs * (1.0 + cogs_shock), 2)
        s_mkt = round(baseline_marketing * (1.0 + mkt_shock), 2)
        s_opex = round(baseline_fixed_opex * (1.0 + opex_shock), 2)

        s_profit = round(s_rev - s_cogs - s_mkt - s_opex, 2)
        s_margin = round((s_profit / s_rev * 100.0), 2) if s_rev > 0 else 0.0

        delta_profit = round(s_profit - baseline_profit, 2)
        loss_severity = round((abs(delta_profit) / abs(baseline_profit) * 100.0), 2) if baseline_profit != 0 else 0.0

        # Solvency classification
        if s_profit >= (baseline_profit * 0.75):
            status = "SOLVENT"
        elif s_profit > 0:
            status = "VULNERABLE"
        elif s_profit >= -50.0:
            status = "DISTRESSED"
        else:
            status = "INSOLVENT"

        # Runway calculation: cash reserve / monthly burn
        # If quarterly profit is negative, quarterly burn = abs(s_profit), monthly burn = abs(s_profit) / 3.0
        if s_profit >= 0:
            runway_months = 36.0  # Profitable, runway indefinite
            needed_buffer = 0.0
        else:
            quarterly_burn = abs(s_profit)
            monthly_burn = quarterly_burn / 3.0
            runway_months = round(initial_cash_reserve / monthly_burn, 1) if monthly_burn > 0 else 36.0
            # Buffer needed to sustain 12 months (4 quarters) of loss
            annual_shortfall = quarterly_burn * 4.0
            needed_buffer = round(max(0.0, annual_shortfall - initial_cash_reserve), 2)

        if s_profit < worst_profit:
            worst_profit = s_profit
            worst_name = sc.get("name", sc.get("id"))

        if needed_buffer > max_buffer:
            max_buffer = needed_buffer

        total_stressed_profit += s_profit

        evaluated.append(ScenarioImpact(
            scenario_id=sc.get("id", "CUSTOM"),
            name=sc.get("name", "Custom Stress"),
            description=sc.get("description", ""),
            revenue_shock_pct=rev_shock,
            cogs_shock_pct=cogs_shock,
            marketing_shock_pct=mkt_shock,
            fixed_opex_shock_pct=opex_shock,
            stressed_revenue=s_rev,
            stressed_cogs=s_cogs,
            stressed_marketing=s_mkt,
            stressed_opex=s_opex,
            stressed_profit=s_profit,
            stressed_margin_pct=s_margin,
            profit_delta_vs_baseline=delta_profit,
            loss_severity_pct=loss_severity,
            solvency_status=status,
            estimated_runway_months=runway_months,
            recommended_capital_buffer=needed_buffer
        ))

    num_sc = len(evaluated)
    avg_profit = round(total_stressed_profit / num_sc, 2) if num_sc > 0 else baseline_profit

    # Systemic resilience score
    if worst_profit > 0 and avg_profit >= (baseline_profit * 0.5):
        rating = "AAA (High Resilience)"
    elif worst_profit >= -20.0:
        rating = "BBB (Adequate Resilience)"
    elif worst_profit >= -100.0:
        rating = "CCC (Vulnerable to Macro Shocks)"
    else:
        rating = "D (Distressed Under Stress)"

    return StressTestSummary(
        baseline_profit=round(baseline_profit, 2),
        baseline_margin_pct=round(baseline_margin, 2),
        num_scenarios_evaluated=num_sc,
        worst_case_scenario=worst_name,
        worst_case_profit=worst_profit,
        max_capital_buffer_needed=max_buffer,
        average_stressed_profit=avg_profit,
        systemic_resilience_rating=rating,
        scenarios=evaluated
    )
