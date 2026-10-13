"""
Unit Tests for Verification Critic Checks and Audit Loop.
"""

import pytest
from src.verification.validate_report import VerificationCritic, AuditCheckStatus


def test_check_a_numerical_reconciliation_pass():
    critic = VerificationCritic()
    mock_bridge = {
        "p_start": 150.0,
        "p_end": 70.0,
        "total_delta_profit": -80.0,
        "is_reconciled": True,
        "reconciliation_discrepancy": 0.0,
        "impacts": {"revenue": -60.0, "cogs": 15.0, "marketing": -25.0, "other_opex": -10.0}
    }
    draft_claims = [
        {"claim": "Operating profit declined by ₹80k from Q2 to Q3.", "evidence_ids": ["EV-001"], "is_factual_claim": True}
    ]
    report = critic.audit_analysis(
        draft_claims=draft_claims,
        profit_bridge_result=mock_bridge,
        retrieved_evidence=[{"evidence_id": "EV-001", "text": "Operating profit was 70k"}]
    )
    assert report.check_a_status == AuditCheckStatus.PASSED


def test_check_a_numerical_reconciliation_fail():
    critic = VerificationCritic()
    mock_unreconciled_bridge = {
        "p_start": 150.0,
        "p_end": 70.0,
        "total_delta_profit": -80.0,
        "is_reconciled": False,
        "reconciliation_discrepancy": 15.0,
    }
    report = critic.audit_analysis(
        draft_claims=[],
        profit_bridge_result=mock_unreconciled_bridge,
        retrieved_evidence=[]
    )
    assert report.check_a_status == AuditCheckStatus.FAILED
    assert report.status == "NEEDS_CORRECTION"
    assert report.retry is True


def test_check_b_citation_validity():
    critic = VerificationCritic()
    critic.set_evidence_lookup({"EV-001": {"text": "Valid source"}})

    # Test hallucinated ID
    draft_claims = [
        {"claim": "Some financial statement", "evidence_ids": ["EV-NONEXISTENT"], "is_factual_claim": True}
    ]
    report = critic.audit_analysis(draft_claims=draft_claims)
    assert report.check_b_status == AuditCheckStatus.FAILED
    assert any("does not exist" in i.reason for i in report.issues)


def test_check_c_cross_source_contradiction():
    """Written document claims marketing reduced, but data shows increase."""
    critic = VerificationCritic()
    mock_bridge = {
        "is_reconciled": True,
        "raw_changes": {"marketing": 25.0}  # Increase of +25k
    }
    retrieved_evidence = [
        {
            "evidence_id": "EV-PDF-01",
            "file_name": "quarterly_review_inconsistent.pdf",
            "text": "Management noted that marketing was reduced by 25k to improve profits."
        }
    ]
    report = critic.audit_analysis(
        draft_claims=[],
        profit_bridge_result=mock_bridge,
        retrieved_evidence=retrieved_evidence
    )
    assert len(report.contradictions) > 0
    assert report.contradictions[0]["severity"] == "CONTRADICTION_FLAGGED"
