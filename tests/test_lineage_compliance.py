"""
Unit Tests for Audit Lineage DAG & Enterprise Compliance Engine (SOX 404 / BCBS 239)
Verifies cryptographic hashing, DAG connectivity, Mermaid generation, and SOX 404 controls.
"""

import os
import pytest
from src.ingestion.loader_manager import DocumentManager
from src.analysis.data_lineage import generate_audit_lineage, compute_file_sha256, AuditLineageReport
from src.agents.risk_governance_agent import RiskGovernanceAgent


@pytest.fixture
def doc_manager():
    mgr = DocumentManager()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    demo_path = os.path.join(base_dir, "data", "synthetic_demo")
    if os.path.exists(demo_path):
        mgr.ingest_directory(demo_path)
    return mgr


def test_sha256_cryptographic_digest(doc_manager):
    for doc in doc_manager.documents.values():
        path = doc.file_path
        digest = compute_file_sha256(path)
        assert len(digest) == 64
        assert all(c in "0123456789abcdef" for c in digest.lower())


def test_audit_lineage_dag_generation(doc_manager):
    report: AuditLineageReport = generate_audit_lineage(
        doc_manager=doc_manager,
        profit_bridge_result={"is_reconciled": True, "reconciliation_discrepancy": 0.0}
    )
    assert report.certificate_id.startswith("SOX404-BCBS239-")
    assert len(report.document_hashes) >= 4
    assert len(report.nodes) >= 8
    assert len(report.edges) >= 8

    # Verify Mermaid graph contains valid nodes
    assert "graph LR" in report.mermaid_graph
    assert "control_critic" in report.mermaid_graph


def test_sox_404_compliance_controls(doc_manager):
    report = generate_audit_lineage(
        doc_manager=doc_manager,
        profit_bridge_result={"is_reconciled": True, "reconciliation_discrepancy": 0.0}
    )
    sox = report.sox_404_compliance
    assert sox["certification_status"] == "CERTIFIED_COMPLIANT"

    # All individual controls must PASS
    controls = sox["audit_checks"]
    assert len(controls) == 5
    for c in controls:
        assert c["status"] == "PASS", f"Control {c['control_id']} failed"


def test_risk_governance_agent_execution(doc_manager):
    agent = RiskGovernanceAgent(doc_manager)
    risk_out = agent.evaluate_risk_profile("Q2", "Q3")
    assert "monte_carlo" in risk_out
    assert "dupont_leverage" in risk_out
    assert "audit_lineage" in risk_out
    assert "executive_risk_summary" in risk_out
    assert risk_out["executive_risk_summary"]["sox_certificate_id"].startswith("SOX404-BCBS239-")
