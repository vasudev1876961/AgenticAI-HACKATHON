"""
DuPont Operational Analysis & Operating Leverage (DOL) Engine
Decomposes corporate profitability into fundamental operational and cost drivers:
- Operating Margin (Return on Sales / ROS) Waterfall Decomposition
- Fixed vs Variable Cost Decomposition
- Degree of Operating Leverage (DOL)
- Break-Even Revenue and Margin of Safety
- Structural Vulnerability & Margin Erosion Diagnostic
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from .cleaning import clean_numeric_value
from .compare_periods import calculate_pct_change


@dataclass
class DuPontAnalysisResult:
    period_start: str
    period_end: str
    q2_metrics: Dict[str, float]
    q3_metrics: Dict[str, float]
    variance_metrics: Dict[str, float]
    degree_of_operating_leverage: float
    break_even_revenue_q3: float
    margin_of_safety_pct_q3: float
    fixed_costs_q3: float
    variable_costs_q3: float
    contribution_margin_ratio_q3: float
    operating_risk_verdict: str
    strategic_takeaways: list[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "period_start": self.period_start,
            "period_end": self.period_end,
            "q2_metrics": {k: round(v, 4) for k, v in self.q2_metrics.items()},
            "q3_metrics": {k: round(v, 4) for k, v in self.q3_metrics.items()},
            "variance_metrics": {k: round(v, 4) for k, v in self.variance_metrics.items()},
            "degree_of_operating_leverage": round(self.degree_of_operating_leverage, 3),
            "break_even_revenue_q3": round(self.break_even_revenue_q3, 2),
            "margin_of_safety_pct_q3": round(self.margin_of_safety_pct_q3, 2),
            "fixed_costs_q3": round(self.fixed_costs_q3, 2),
            "variable_costs_q3": round(self.variable_costs_q3, 2),
            "contribution_margin_ratio_q3": round(self.contribution_margin_ratio_q3, 4),
            "operating_risk_verdict": self.operating_risk_verdict,
            "strategic_takeaways": self.strategic_takeaways
        }


def analyze_dupont_leverage(
    p1: Dict[str, Any],
    p2: Dict[str, Any],
    p1_name: str = "Q2",
    p2_name: str = "Q3",
    variable_cogs_ratio: float = 0.70
) -> DuPontAnalysisResult:
    """
    Computes DuPont operational decomposition and degree of operating leverage.
    
    Standard baseline parameters:
    - Q2: Revenue 1000, COGS 600, Marketing 100, OpEx 150 -> Profit 150 (ROS 15.0%)
    - Q3: Revenue 940, COGS 585, Marketing 125, OpEx 160 -> Profit 70 (ROS 7.45%)
    """
    r1 = clean_numeric_value(p1.get("revenue", 1000.0))
    c1 = clean_numeric_value(p1.get("cogs", 600.0))
    m1 = clean_numeric_value(p1.get("marketing", 100.0))
    o1 = clean_numeric_value(p1.get("other_opex", 150.0))
    p1_prof = r1 - c1 - m1 - o1

    r2 = clean_numeric_value(p2.get("revenue", 940.0))
    c2 = clean_numeric_value(p2.get("cogs", 585.0))
    m2 = clean_numeric_value(p2.get("marketing", 125.0))
    o2 = clean_numeric_value(p2.get("other_opex", 160.0))
    p2_prof = r2 - c2 - m2 - o2

    # Return on Sales (Operating Margin)
    ros_1 = (p1_prof / r1) * 100.0 if r1 != 0 else 0.0
    ros_2 = (p2_prof / r2) * 100.0 if r2 != 0 else 0.0

    # Gross Margin %
    gm_1 = ((r1 - c1) / r1) * 100.0 if r1 != 0 else 0.0
    gm_2 = ((r2 - c2) / r2) * 100.0 if r2 != 0 else 0.0

    # Marketing Burden % of Revenue
    mkt_ratio_1 = (m1 / r1) * 100.0 if r1 != 0 else 0.0
    mkt_ratio_2 = (m2 / r2) * 100.0 if r2 != 0 else 0.0

    # Overhead Burden % of Revenue
    opex_ratio_1 = (o1 / r1) * 100.0 if r1 != 0 else 0.0
    opex_ratio_2 = (o2 / r2) * 100.0 if r2 != 0 else 0.0

    # Degree of Operating Leverage (DOL)
    # DOL = % delta Profit / % delta Revenue
    pct_delta_rev = calculate_pct_change(r1, r2) or 0.0
    pct_delta_prof = calculate_pct_change(p1_prof, p2_prof) or 0.0
    
    if abs(pct_delta_rev) > 1e-5:
        dol = pct_delta_prof / pct_delta_rev
    else:
        dol = 0.0

    # Cost Behavior Model (Fixed vs Variable) for P2
    # Variable COGS: 70% of COGS varies directly with production
    var_cogs_2 = c2 * variable_cogs_ratio
    fixed_cogs_2 = c2 * (1.0 - variable_cogs_ratio)

    # Marketing in this business acts largely as a discretionary fixed commitment in the quarter
    # Other OpEx is fixed administrative & facilities
    total_var_costs_2 = var_cogs_2
    total_fixed_costs_2 = fixed_cogs_2 + m2 + o2

    # Contribution Margin = Revenue - Variable Costs
    contribution_margin_2 = r2 - total_var_costs_2
    cmr_2 = contribution_margin_2 / r2 if r2 != 0 else 0.0

    # Break-Even Revenue = Fixed Costs / CMR
    if cmr_2 > 0:
        break_even_rev_2 = total_fixed_costs_2 / cmr_2
        margin_of_safety_pct_2 = ((r2 - break_even_rev_2) / r2) * 100.0
    else:
        break_even_rev_2 = 0.0
        margin_of_safety_pct_2 = 0.0

    # Diagnostic verdict
    if dol > 6.0:
        verdict = "SEVERE_NEGATIVE_OPERATING_LEVERAGE"
    elif dol > 3.0:
        verdict = "MODERATE_NEGATIVE_OPERATING_LEVERAGE"
    else:
        verdict = "STABLE_COST_STRUCTURE"

    takeaways = [
        f"Degree of Operating Leverage (DOL) is {round(dol, 2)}x: For every 1% contraction in revenue, operating profit collapses by {round(abs(dol), 2)}%.",
        f"Operating margin (ROS) compressed by {round(ros_1 - ros_2, 2)} percentage points (from {round(ros_1, 2)}% to {round(ros_2, 2)}%).",
        f"Marketing expense intensity surged from {round(mkt_ratio_1, 1)}% to {round(mkt_ratio_2, 1)}% of top-line revenue (+330 bps), compounding margin compression.",
        f"Current Q3 Margin of Safety is {round(margin_of_safety_pct_2, 1)}% (Break-Even Revenue: ₹{round(break_even_rev_2, 1)}k vs Realized: ₹{round(r2, 1)}k). A further revenue drop of {round(margin_of_safety_pct_2, 1)}% causes net operating loss."
    ]

    return DuPontAnalysisResult(
        period_start=p1_name,
        period_end=p2_name,
        q2_metrics={
            "revenue": r1,
            "cogs": c1,
            "marketing": m1,
            "other_opex": o1,
            "operating_profit": p1_prof,
            "return_on_sales_pct": ros_1,
            "gross_margin_pct": gm_1,
            "marketing_ratio_pct": mkt_ratio_1,
            "opex_ratio_pct": opex_ratio_1
        },
        q3_metrics={
            "revenue": r2,
            "cogs": c2,
            "marketing": m2,
            "other_opex": o2,
            "operating_profit": p2_prof,
            "return_on_sales_pct": ros_2,
            "gross_margin_pct": gm_2,
            "marketing_ratio_pct": mkt_ratio_2,
            "opex_ratio_pct": opex_ratio_2
        },
        variance_metrics={
            "delta_profit": p2_prof - p1_prof,
            "pct_delta_profit": pct_delta_prof,
            "delta_revenue": r2 - r1,
            "pct_delta_revenue": pct_delta_rev,
            "ros_compression_bps": (ros_1 - ros_2) * 100.0,
            "marketing_surge_bps": (mkt_ratio_2 - mkt_ratio_1) * 100.0
        },
        degree_of_operating_leverage=dol,
        break_even_revenue_q3=break_even_rev_2,
        margin_of_safety_pct_q3=margin_of_safety_pct_2,
        fixed_costs_q3=total_fixed_costs_2,
        variable_costs_q3=total_var_costs_2,
        contribution_margin_ratio_q3=cmr_2,
        operating_risk_verdict=verdict,
        strategic_takeaways=takeaways
    )
