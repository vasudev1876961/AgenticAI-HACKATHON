"""
Unit Tests for Monte Carlo Stochastic Risk & Value-at-Risk Engine
Verifies reproducibility, statistical consistency, VaR/CVaR bounds, and histogram integrity.
"""

import pytest
from src.analysis.monte_carlo_simulation import run_monte_carlo_simulation, MonteCarloRiskResult


def test_monte_carlo_reproducibility():
    base = {"revenue": 940.0, "cogs": 585.0, "marketing": 125.0, "other_opex": 160.0}
    res1 = run_monte_carlo_simulation(base, iterations=500, random_seed=42)
    res2 = run_monte_carlo_simulation(base, iterations=500, random_seed=42)
    assert res1.mean_profit == res2.mean_profit
    assert res1.var_95 == res2.var_95
    assert res1.prob_target_achieved_pct == res2.prob_target_achieved_pct


def test_monte_carlo_percentile_monotonicity():
    base = {"revenue": 940.0, "cogs": 585.0, "marketing": 125.0, "other_opex": 160.0}
    res = run_monte_carlo_simulation(base, iterations=1000, random_seed=99)
    p = res.percentiles
    assert p["p1"] <= p["p5"] <= p["p10"] <= p["p25"] <= p["p50"] <= p["p75"] <= p["p90"] <= p["p95"] <= p["p99"]


def test_monte_carlo_var_and_cvar():
    base = {"revenue": 940.0, "cogs": 585.0, "marketing": 125.0, "other_opex": 160.0}
    res = run_monte_carlo_simulation(base, iterations=1000, random_seed=123)
    assert res.var_95 >= 0.0
    assert res.var_99 >= res.var_95
    # CVaR (Expected Shortfall) is worst-case average, so it should be <= p5
    assert res.cvar_95 <= res.percentiles["p5"]


def test_monte_carlo_histogram_bins():
    base = {"revenue": 940.0, "cogs": 585.0, "marketing": 125.0, "other_opex": 160.0}
    iterations = 800
    res = run_monte_carlo_simulation(base, iterations=iterations, random_seed=77)
    assert len(res.histogram_bins) == 20
    total_binned = sum(b["count"] for b in res.histogram_bins)
    assert total_binned == iterations


def test_monte_carlo_probabilities_bounded():
    base = {"revenue": 940.0, "cogs": 585.0, "marketing": 125.0, "other_opex": 160.0}
    res = run_monte_carlo_simulation(base, target_profit=150.0, iterations=500, random_seed=42)
    assert 0.0 <= res.prob_target_achieved_pct <= 100.0
    assert 0.0 <= res.prob_loss_pct <= 100.0
