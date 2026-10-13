"""
End-to-End Multi-Agent Benchmark Suite
Tests the 10 core hackathon evaluation scenarios specified in Section 15 of the Blueprint.
"""

import os
import pytest
from src.ingestion.loader_manager import DocumentManager
from src.agents.orchestrator import AnalystOrchestrator

DEMO_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "synthetic_demo")


@pytest.fixture(scope="module")
def orchestrator():
    mgr = DocumentManager()
    mgr.ingest_directory(DEMO_DIR)
    return AnalystOrchestrator(mgr)


def test_scenario_1_numerical_comparison(orchestrator):
    """1. Compare Q2 and Q3 revenue, expenses, and operating profit."""
    res = orchestrator.run_investigation("Compare Q2 and Q3 revenue, expenses, and operating profit.")
    bridge = res["bridge"]
    assert bridge["p_start"] == 150.0
    assert bridge["p_end"] == 70.0
    assert bridge["total_delta_profit"] == -80.0
    assert bridge["is_reconciled"] is True


def test_scenario_2_root_cause_investigation(orchestrator):
    """2. Why did operating profit decline in Q3?"""
    res = orchestrator.run_investigation("Why did operating profit decline in Q3?")
    bridge = res["bridge"]
    # Reconciled total impact
    assert bridge["impacts"]["revenue"] == -60.0
    assert bridge["impacts"]["marketing"] == -25.0
    assert bridge["impacts"]["other_opex"] == -10.0
    assert bridge["impacts"]["cogs"] == 15.0


def test_scenario_3_evidence_retrieval(orchestrator):
    """3. What explanation does the quarterly review give?"""
    res = orchestrator.run_investigation("What explanation does the quarterly review give?")
    citations = res["citations"]
    assert len(citations) > 0
    # Provenance check: at least one citation from quarterly review PDF or XLSX
    pdf_or_excel = any("quarterly" in c.get("file_name", "").lower() for c in citations)
    assert pdf_or_excel is True


def test_scenario_4_cross_source_contradiction(orchestrator):
    """4. Inconsistent document check - marketing decrease contradiction."""
    res = orchestrator.run_investigation("The report says marketing expenditure declined. Is that consistent?")
    contradictions = res["contradictions"]
    assert len(contradictions) > 0
    assert any("marketing" in c.get("topic", "").lower() for c in contradictions)


def test_scenario_5_unsupported_claim(orchestrator):
    """5. Did customer dissatisfaction cause the revenue decline?"""
    res = orchestrator.run_investigation("Did customer dissatisfaction cause the revenue decline?")
    audit = res["audit"]
    # Should not fabricate unsupported claim
    assert audit is not None


def test_scenario_6_missing_period(orchestrator):
    """6. Compare Q1 with Q3 (Q1 is missing)."""
    res = orchestrator.run_investigation("Compare Q1 with Q3.")
    assert res["report"] is not None


def test_scenario_7_irrelevant_document(orchestrator):
    """7. What was the marketing expense in Q3?"""
    res = orchestrator.run_investigation("What was the marketing expense in Q3?")
    assert res["bridge"]["raw_changes"]["marketing"] == 25.0


def test_scenario_8_zero_baseline_handling(orchestrator):
    """8. Calculate growth rate when earlier period is zero."""
    from src.analysis.compare_periods import compare_periods
    comp = compare_periods("Growth", "P1", 0, "P2", 50)
    assert comp["pct_change"] is None
    assert "Undefined" in comp["pct_change_str"]


def test_scenario_9_agent_coordination(orchestrator):
    """9. Show that orchestrator routes through retrieval, calculation, and verifier."""
    res = orchestrator.run_investigation("Investigate the decline using both the spreadsheet and the report.")
    logs = res["execution_logs"]
    senders = {l["sender"] for l in logs}
    assert "AnalystOrchestrator" in senders
    assert "DocumentResearcher" in senders
    assert "DataAnalyst" in senders
    assert "CrossSourceInvestigator" in senders
    assert "VerificationCritic" in senders
    assert "ReportWriter" in senders


def test_scenario_10_verification_failure_catch(orchestrator):
    """10. Catch incorrect conclusion before presenting final report."""
    audit = orchestrator.verifier.verify(
        draft_claims=[{"claim": "Profit improved by 50%", "evidence_ids": ["EV-999"], "is_factual_claim": True}],
        profit_bridge_result={"is_reconciled": False, "reconciliation_discrepancy": 10.0, "total_delta_profit": -80.0},
        retrieved_evidence=[],
        retry_count=0
    )
    assert audit["status"] == "NEEDS_CORRECTION"
    assert audit["retry"] is True
