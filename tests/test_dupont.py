"""
Unit Tests for DuPont Analysis & Degree of Operating Leverage (DOL) Engine
Verifies operating margin decomposition, leverage ratios, break-even bounds, and edge cases.
"""

import pytest
from src.analysis.dupont_analysis import analyze_dupont_leverage, DuPontAnalysisResult


def test_dupont_q2_q3_baseline_calculation():
    p1 = {"revenue": 1000.0, "cogs": 600.0, "marketing": 100.0, "other_opex": 150.0}
    p2 = {"revenue": 940.0, "cogs": 585.0, "marketing": 125.0, "other_opex": 160.0}

    res: DuPontAnalysisResult = analyze_dupont_leverage(p1, p2)

    # Q2 Return on Sales = 150 / 1000 = 15.0%
    assert round(res.q2_metrics["return_on_sales_pct"], 2) == 15.0
    # Q3 Return on Sales = 70 / 940 = 7.45%
    assert round(res.q3_metrics["return_on_sales_pct"], 2) == 7.45

    # DOL: % change profit (-53.333%) / % change revenue (-6.0%) = 8.889
    assert 8.8 < res.degree_of_operating_leverage < 8.95
    assert res.operating_risk_verdict == "SEVERE_NEGATIVE_OPERATING_LEVERAGE"


def test_dupont_break_even_and_margin_of_safety():
    p1 = {"revenue": 1000.0, "cogs": 600.0, "marketing": 100.0, "other_opex": 150.0}
    p2 = {"revenue": 940.0, "cogs": 585.0, "marketing": 125.0, "other_opex": 160.0}

    res = analyze_dupont_leverage(p1, p2)

    # Break-even revenue should be positive and less than current revenue (since profit is +70k)
    assert 0 < res.break_even_revenue_q3 < 940.0
    # Margin of safety should be positive
    assert res.margin_of_safety_pct_q3 > 0.0


def test_dupont_flat_revenue_zero_division():
    # If revenue does not change, DOL should not crash with ZeroDivisionError
    p1 = {"revenue": 1000.0, "cogs": 600.0, "marketing": 100.0, "other_opex": 150.0}
    p2 = {"revenue": 1000.0, "cogs": 620.0, "marketing": 100.0, "other_opex": 150.0}

    res = analyze_dupont_leverage(p1, p2)
    assert res.degree_of_operating_leverage == 0.0
    assert res.variance_metrics["pct_delta_revenue"] == 0.0
