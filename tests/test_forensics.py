"""
Unit Tests for Document Forensics Engine & DocumentForensicsAgent
Verifies ratio surge detection, cost elasticity auditing, and target reconciliation.
"""

import pytest
import pandas as pd
from src.analysis.document_forensics import (
    calculate_financial_ratios,
    analyze_financial_forensics
)
from src.ingestion.loader_manager import DocumentManager
from src.agents.forensics_agent import DocumentForensicsAgent


def test_calculate_financial_ratios():
    data = {"revenue": 1000.0, "cogs": 600.0, "marketing": 100.0, "other_opex": 150.0}
    ratios = calculate_financial_ratios(data)

    assert ratios["gross_margin_pct"] == 40.0
    assert ratios["operating_margin_pct"] == 15.0
    assert ratios["marketing_intensity_pct"] == 10.0
    assert ratios["cogs_intensity_pct"] == 60.0


def test_detect_ratio_surges_and_anomalies():
    p1 = {"revenue": 1000.0, "cogs": 600.0, "marketing": 100.0, "other_opex": 150.0}
    p2 = {"revenue": 940.0, "cogs": 585.0, "marketing": 125.0, "other_opex": 160.0}

    report = analyze_financial_forensics(p1, p2)

    assert len(report.anomalies) >= 2
    categories = [a.category for a in report.anomalies]
    assert "RATIO_SURGE" in categories

    # Check for operating margin contraction flag
    margin_flag = next((a for a in report.anomalies if "Operating Margin" in a.metric), None)
    assert margin_flag is not None
    assert margin_flag.severity == "CRITICAL"


def test_target_reconciliation():
    p1 = {"revenue": 1000.0, "cogs": 600.0, "marketing": 100.0, "other_opex": 150.0}
    p2 = {"revenue": 940.0, "cogs": 585.0, "marketing": 125.0, "other_opex": 160.0}

    report = analyze_financial_forensics(p1, p2)

    assert len(report.target_reconciliation) >= 3
    targets_dict = {t["metric"]: t for t in report.target_reconciliation}

    # Revenue target was 950k, actual is 940k -> shortfall
    assert "Q3 Revenue" in targets_dict
    assert targets_dict["Q3 Revenue"]["status"] == "SHORTFALL"

    # COGS target was 590k ceiling, actual is 585k -> beat/favorable
    assert "Q3 COGS Ceiling" in targets_dict
    assert "FAVORABLE" in targets_dict["Q3 COGS Ceiling"]["status"]


def test_forensics_agent_audit():
    mgr = DocumentManager()
    agent = DocumentForensicsAgent(mgr)

    audit_res = agent.audit("Q2", "Q3")
    assert "anomalies" in audit_res
    assert "overall_risk_score" in audit_res
    assert audit_res["overall_risk_score"] in ["MODERATE", "ELEVATED", "CRITICAL"]
    assert len(agent.execution_log) >= 2
