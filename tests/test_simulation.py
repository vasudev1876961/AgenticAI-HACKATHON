"""
Unit Tests for Counterfactual Simulation Engine & ScenarioSimulationAgent
Verifies deterministic What-If calculation, mathematical reconciliation,
sensitivity matrix bounds, and strategic recovery ranking.
"""

import pytest
from src.analysis.counterfactual_simulation import (
    simulate_counterfactual,
    generate_sensitivity_matrix,
    rank_recovery_levers
)
from src.ingestion.loader_manager import DocumentManager
from src.agents.scenario_agent import ScenarioSimulationAgent


@pytest.fixture
def base_financials():
    p1 = {"revenue": 1000.0, "cogs": 600.0, "marketing": 100.0, "other_opex": 150.0}
    p2 = {"revenue": 940.0, "cogs": 585.0, "marketing": 125.0, "other_opex": 160.0}
    return p1, p2


def test_simulate_flat_marketing(base_financials):
    """Simulates holding marketing flat at Q2 level (100k)."""
    p1, p2 = base_financials
    sim = simulate_counterfactual(
        p1=p1,
        p2=p2,
        modifications={"marketing": 100.0},
        scenario_name="Flat Marketing"
    )

    # In baseline: profit fell from 150 to 70 (-80k)
    # With flat marketing: Q3 profit is 940 - 585 - 100 - 160 = 95k (delta -55k)
    # Recovery = -55 - (-80) = +25k
    assert sim.counterfactual_bridge.p_end == 95.0
    assert sim.counterfactual_profit_delta == -55.0
    assert sim.profit_recovery_amount == 25.0
    assert pytest.approx(sim.recovery_percentage, 0.01) == 31.25
    assert sim.is_reconciled is True
    assert sim.counterfactual_bridge.reconciliation_discrepancy < 1e-4


def test_simulate_relative_and_percentage_adjustments(base_financials):
    """Tests relative delta and percentage modifications."""
    p1, p2 = base_financials

    # Reduce other_opex by 10k via delta
    sim_delta = simulate_counterfactual(
        p1=p1,
        p2=p2,
        modifications={"other_opex_delta": -10.0}
    )
    assert sim_delta.counterfactual_bridge.p_end == 80.0
    assert sim_delta.profit_recovery_amount == 10.0
    assert sim_delta.is_reconciled is True

    # Adjust revenue by +5% via percentage
    sim_pct = simulate_counterfactual(
        p1=p1,
        p2=p2,
        modifications={"revenue_pct": 0.05}
    )
    expected_rev = 940.0 * 1.05  # 987.0
    assert pytest.approx(sim_pct.counterfactual_bridge.p_end, 0.1) == 987.0 - 585.0 - 125.0 - 160.0
    assert sim_pct.is_reconciled is True


def test_generate_sensitivity_matrix(base_financials):
    """Verifies that the sensitivity matrix creates a valid 2D grid."""
    p1, p2 = base_financials
    rev_mults = [-0.05, 0.0, 0.05]
    mkt_mults = [-0.10, 0.0, 0.10]

    matrix = generate_sensitivity_matrix(
        p1=p1,
        p2=p2,
        var1_name="revenue",
        var1_multipliers=rev_mults,
        var2_name="marketing",
        var2_multipliers=mkt_mults
    )

    assert len(matrix["grid"]) == 3
    for row in matrix["grid"]:
        assert len(row["columns"]) == 3
        for cell in row["columns"]:
            assert "resulting_profit" in cell
            assert "profit_delta" in cell


def test_rank_recovery_levers(base_financials):
    """Tests that recovery levers rank the highest profit recovery playbook first."""
    p1, p2 = base_financials
    levers = rank_recovery_levers(p1, p2)

    assert len(levers) >= 4
    # Highest recovery lever should be first
    for i in range(len(levers) - 1):
        assert levers[i]["recovery_amount"] >= levers[i + 1]["recovery_amount"]
    assert all(lever["is_reconciled"] is True for lever in levers)


def test_scenario_agent_execution():
    """Tests end-to-end execution of ScenarioSimulationAgent."""
    mgr = DocumentManager()
    agent = ScenarioSimulationAgent(mgr)

    sim = agent.simulate(modifications={"marketing": 100.0}, scenario_name="Flat Mkt")
    assert sim["profit_recovery_amount"] == 25.0
    assert sim["is_reconciled"] is True
    assert len(agent.execution_log) >= 2
