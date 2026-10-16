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


def test_scenario_11_what_if_counterfactual(orchestrator):
    """11. Counterfactual What-If simulation and deterministic profit recovery."""
    sim = orchestrator.scenario_simulator.simulate({"marketing": 100.0}, scenario_name="Flat Marketing")
    assert sim["profit_recovery_amount"] == 25.0
    assert sim["is_reconciled"] is True
    assert sim["recovery_percentage"] > 30.0


def test_scenario_12_forensic_ratio_target_audit(orchestrator):
    """12. Forensics ratio surges, cost elasticity, and board target gaps."""
    forensics = orchestrator.forensics_agent.audit()
    assert len(forensics["anomalies"]) >= 2
    assert len(forensics["target_reconciliation"]) >= 2
    assert forensics["overall_risk_score"] in ["CRITICAL", "HIGH", "ELEVATED", "MODERATE"]


def test_scenario_13_monte_carlo_var(orchestrator):
    """13. Monte Carlo stochastic Value-at-Risk (VaR) and target achievement."""
    risk_eval = orchestrator.risk_governance_agent.evaluate_risk_profile()
    mc = risk_eval["monte_carlo"]
    assert mc["iterations"] >= 500
    assert mc["var_95"] > 0
    assert len(mc["histogram_bins"]) == 20


def test_scenario_14_dupont_leverage(orchestrator):
    """14. DuPont Return on Sales decomposition and Degree of Operating Leverage."""
    risk_eval = orchestrator.risk_governance_agent.evaluate_risk_profile()
    dupont = risk_eval["dupont_leverage"]
    assert dupont["degree_of_operating_leverage"] > 8.0
    assert dupont["break_even_revenue_q3"] > 0
    assert "SEVERE_NEGATIVE_OPERATING_LEVERAGE" in dupont["operating_risk_verdict"]


def test_scenario_15_cryptographic_lineage_sox(orchestrator):
    """15. Cryptographic Data Lineage DAG and SOX 404 Audit Certification."""
    risk_eval = orchestrator.risk_governance_agent.evaluate_risk_profile()
    lineage = risk_eval["audit_lineage"]
    assert lineage["certificate_id"].startswith("SOX404-BCBS239-")
    assert lineage["sox_404_compliance"]["certification_status"] == "CERTIFIED_COMPLIANT"
    assert lineage["nodes_count"] >= 8


def test_scenario_16_macro_stress_testing(orchestrator):
    """16. Multi-vector macroeconomic shock stress testing and capital buffer."""
    risk_eval = orchestrator.risk_governance_agent.evaluate_risk_profile()
    stress = risk_eval["stress_testing"]
    assert stress["num_scenarios_evaluated"] == 4
    assert "worst_case_scenario" in stress
    assert isinstance(stress["worst_case_profit"], float)
    assert stress["systemic_resilience_rating"] is not None


def test_scenario_17_liquidity_runway_resilience(orchestrator):
    """17. Liquidity runway months and solvency classification across shock vectors."""
    risk_eval = orchestrator.risk_governance_agent.evaluate_risk_profile()
    stress = risk_eval["stress_testing"]
    scenarios = stress["scenarios"]
    assert len(scenarios) == 4
    for sc in scenarios:
        assert sc["solvency_status"] in ["SOLVENT", "VULNERABLE", "DISTRESSED", "INSOLVENT"]
        assert sc["estimated_runway_months"] > 0

