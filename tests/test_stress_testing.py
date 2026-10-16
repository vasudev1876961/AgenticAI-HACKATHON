"""
Unit Tests for Macroeconomic Stress Testing & Capital Resilience Engine
Validates multi-vector stress shocks, solvency classification, liquidity runway, and tool wrappers.
"""

import pytest
from src.analysis.stress_testing import (
    run_macro_stress_test,
    StressTestSummary,
    ScenarioImpact,
    PRESET_MACRO_SCENARIOS
)
from coded_tools.document_analyst.stress_test_tool import StressTestTool


def test_preset_macro_stress_testing_baseline():
    """Verify standard Q3 baseline under 4 preset macroeconomic scenarios."""
    summary: StressTestSummary = run_macro_stress_test(
        baseline_revenue=940.0,
        baseline_cogs=585.0,
        baseline_marketing=125.0,
        baseline_fixed_opex=160.0,
        initial_cash_reserve=300.0
    )

    assert summary.baseline_profit == 70.0
    assert summary.num_scenarios_evaluated == 4
    assert len(summary.scenarios) == 4
    assert summary.worst_case_profit < summary.baseline_profit
    assert summary.systemic_resilience_rating is not None

    # Check that each scenario has required impact metrics
    for sc in summary.scenarios:
        assert isinstance(sc.stressed_profit, float)
        assert sc.solvency_status in ["SOLVENT", "VULNERABLE", "DISTRESSED", "INSOLVENT"]
        assert sc.estimated_runway_months > 0.0


def test_stagflation_shock_mechanics():
    """Verify specific mathematical mechanics of the Stagflation scenario."""
    summary = run_macro_stress_test(
        baseline_revenue=1000.0,
        baseline_cogs=500.0,
        baseline_marketing=100.0,
        baseline_fixed_opex=100.0,
        initial_cash_reserve=200.0
    )

    stagflation = next(sc for sc in summary.scenarios if sc.scenario_id == "STRESS-01")
    # Revenue shock -15% -> 850
    assert stagflation.stressed_revenue == 850.0
    # COGS shock +12% -> 560
    assert stagflation.stressed_cogs == 560.0
    # Profit delta should be negative
    assert stagflation.profit_delta_vs_baseline < 0


def test_insolvency_and_runway_calculation():
    """Test when an extreme shock causes negative operating profit and computes runway/buffer."""
    extreme_custom = [
        {
            "id": "COLLAPSE-01",
            "name": "Catastrophic Demand Collapse",
            "description": "50% revenue crash",
            "revenue_shock_pct": -0.50,
            "cogs_shock_pct": 0.0,
            "marketing_shock_pct": 0.0,
            "fixed_opex_shock_pct": 0.0
        }
    ]

    summary = run_macro_stress_test(
        baseline_revenue=940.0,
        baseline_cogs=585.0,
        baseline_marketing=125.0,
        baseline_fixed_opex=160.0,
        initial_cash_reserve=100.0,
        custom_scenarios=extreme_custom
    )

    sc = summary.scenarios[0]
    assert sc.stressed_profit < 0  # Severe loss
    assert sc.solvency_status in ["DISTRESSED", "INSOLVENT"]
    assert sc.estimated_runway_months < 36.0  # Depleting cash
    assert sc.recommended_capital_buffer > 0.0  # Buffer needed for 12 mos


def test_stress_test_tool_execution():
    """Verify Neuro-SAN Coded Tool StressTestTool."""
    tool = StressTestTool()
    res = tool.execute(
        baseline_revenue=940.0,
        baseline_cogs=585.0,
        baseline_marketing=125.0,
        baseline_fixed_opex=160.0
    )

    assert res["status"] == "success"
    result_dict = res["result"]
    assert "baseline_profit" in result_dict
    assert "scenarios" in result_dict
    assert len(result_dict["scenarios"]) == 4


def test_zero_division_protection():
    """Test boundary conditions with zero revenue or zero baseline profit."""
    summary = run_macro_stress_test(
        baseline_revenue=0.0,
        baseline_cogs=0.0,
        baseline_marketing=0.0,
        baseline_fixed_opex=0.0
    )
    assert summary.baseline_profit == 0.0
    assert summary.baseline_margin_pct == 0.0
