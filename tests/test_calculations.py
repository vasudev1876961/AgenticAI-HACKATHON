"""
Unit Tests for Deterministic Calculations and Financial Analysis.
"""

import pytest
from src.analysis.contribution_analysis import calculate_profit_bridge
from src.analysis.compare_periods import compare_periods, calculate_delta, calculate_pct_change
from src.analysis.cleaning import clean_numeric_value


def test_clean_numeric_value():
    assert clean_numeric_value(100) == 100.0
    assert clean_numeric_value("1,000") == 1000.0
    assert clean_numeric_value("₹1,50,000") == 150000.0
    assert clean_numeric_value("$25k") == 25000.0
    assert clean_numeric_value("(50)") == -50.0
    assert clean_numeric_value("-15") == -15.0
    assert clean_numeric_value("invalid_val") is None
    assert clean_numeric_value(None) is None


def test_compare_periods_normal():
    res = compare_periods("Revenue", "Q2", 1000, "Q3", 940)
    assert res["status"] == "success"
    assert res["delta"] == -60.0
    assert res["pct_change"] == -6.0
    assert res["direction"] == "decrease"


def test_compare_periods_zero_baseline():
    """Ensure zero division does not crash the system."""
    res = compare_periods("Metric", "Q1", 0, "Q2", 100)
    assert res["status"] == "success"
    assert res["delta"] == 100.0
    assert res["pct_change"] is None
    assert "Undefined" in res["pct_change_str"]


def test_calculate_profit_bridge_reconciliation():
    """Validates exact formula: Delta P = Delta R - Delta C - Delta M - Delta O."""
    q2 = {"revenue": 1000, "cogs": 600, "marketing": 100, "other_opex": 150}
    q3 = {"revenue": 940, "cogs": 585, "marketing": 125, "other_opex": 160}

    bridge = calculate_profit_bridge(q2, q3)

    assert bridge.p_start == 150.0
    assert bridge.p_end == 70.0
    assert bridge.total_delta_profit == -80.0
    assert bridge.is_reconciled is True
    assert bridge.reconciliation_discrepancy < 1e-4

    # Verify component impacts
    assert bridge.impacts["revenue"] == -60.0
    assert bridge.impacts["cogs"] == 15.0         # COGS down by 15 => +15 impact
    assert bridge.impacts["marketing"] == -25.0    # Marketing up by 25 => -25 impact
    assert bridge.impacts["other_opex"] == -10.0   # Other opex up by 10 => -10 impact

    # Verify ranked order: revenue (-60, abs 60), marketing (-25, abs 25), cogs (+15, abs 15), other_opex (-10, abs 10)
    assert bridge.ranked_contributors[0]["key"] == "revenue"
    assert bridge.ranked_contributors[1]["key"] == "marketing"
    assert bridge.ranked_contributors[2]["key"] == "cogs"
    assert bridge.ranked_contributors[3]["key"] == "other_opex"


def test_calculate_profit_bridge_validation():
    """Tests validation of missing keys and non-numeric fields."""
    with pytest.raises(ValueError):
        calculate_profit_bridge({"revenue": 100}, {"revenue": 90})

    with pytest.raises(TypeError):
        calculate_profit_bridge(
            {"revenue": "not_a_number", "cogs": 10, "marketing": 5, "other_opex": 5},
            {"revenue": 100, "cogs": 10, "marketing": 5, "other_opex": 5}
        )
