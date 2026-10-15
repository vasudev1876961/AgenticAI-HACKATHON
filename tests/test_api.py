"""
Unit Tests for FastAPI REST Endpoints
Verifies health, document listing, investigation pipeline, simulation, and forensics endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)


def test_api_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "AnalystOrchestrator" in data["agents_available"]
    assert "ScenarioSimulationAgent" in data["agents_available"]
    assert "DocumentForensicsAgent" in data["agents_available"]


def test_api_list_documents():
    response = client.get("/api/v1/documents")
    assert response.status_code == 200
    data = response.json()
    assert data["total_documents"] >= 1
    assert data["total_chunks"] >= 1


def test_api_investigate_endpoint():
    response = client.post(
        "/api/v1/investigate",
        json={"query": "Why did operating profit decline in Q3? Quantify contributors.", "use_hybrid_search": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "profit_bridge" in data
    assert data["profit_bridge"]["is_reconciled"] is True
    assert len(data["citations"]) >= 1
    assert data["audit"]["status"] in ["APPROVED", "WARNING_ACCEPTED"]


def test_api_simulate_endpoint():
    response = client.post(
        "/api/v1/simulate",
        json={
            "scenario_name": "Flat Marketing API Test",
            "description": "Marketing at Q2 level (100k)",
            "modifications": {"marketing": 100.0}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    res = data["result"]
    assert res["profit_recovery_amount"] == 25.0
    assert res["is_reconciled"] is True


def test_api_sensitivity_endpoint():
    response = client.get("/api/v1/sensitivity?var1=revenue&var2=marketing")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "grid" in data["matrix"]


def test_api_forensics_endpoint():
    response = client.get("/api/v1/forensics")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "anomalies" in data["forensics"]


def test_api_monte_carlo_endpoint():
    response = client.post(
        "/api/v1/monte-carlo",
        json={"iterations": 500, "target_profit": 150.0, "random_seed": 42}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    res = data["result"]
    assert res["iterations"] == 500
    assert "var_95" in res
    assert "percentiles" in res
    assert len(res["histogram_bins"]) == 20


def test_api_dupont_endpoint():
    response = client.get("/api/v1/dupont")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    res = data["result"]
    assert res["degree_of_operating_leverage"] > 5.0  # ~8.89x
    assert res["break_even_revenue_q3"] > 0
    assert "operating_risk_verdict" in res


def test_api_lineage_endpoint():
    response = client.get("/api/v1/lineage")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    lineage = data["lineage"]
    assert lineage["nodes_count"] >= 5
    assert lineage["edges_count"] >= 5
    assert "graph LR" in lineage["mermaid_graph"]
    assert "quarterly_financials.xlsx" in lineage["document_hashes"]


def test_api_compliance_endpoint():
    response = client.get("/api/v1/compliance")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    cert = data["sox_404_certification"]
    assert cert["certification_status"] == "CERTIFIED_COMPLIANT"
    assert len(cert["audit_checks"]) >= 5
