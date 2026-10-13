"""
Unit Tests for System Advancements:
1. Hybrid Search (BM25 + Semantic Vector Space + RRF)
2. Regional Drill-Down Variance & Territorial Reconciliation
3. Visual Waterfall Chart Generator & Embedded PDF Export
"""

import os
import pytest
from src.ingestion.loader_manager import DocumentManager
from src.retrieval.hybrid_search import HybridSearchEngine
from src.analysis.regional_analysis import analyze_regional_breakdown
from src.reporting.generate_report import render_waterfall_chart

DEMO_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "synthetic_demo")


@pytest.fixture(scope="module")
def doc_manager():
    mgr = DocumentManager()
    mgr.ingest_directory(DEMO_DIR)
    return mgr


def test_hybrid_search_engine(doc_manager):
    """Tests HybridSearchEngine with RRF fusion."""
    engine = HybridSearchEngine(doc_manager.all_chunks)
    
    # 1. Exact match query
    res_hybrid = engine.search("operating profit decline", top_k=5, mode="hybrid")
    assert len(res_hybrid) > 0
    assert "evidence_id" in res_hybrid[0]
    assert "relevance_score" in res_hybrid[0]
    assert "bm25_score" in res_hybrid[0]
    assert "semantic_score" in res_hybrid[0]

    # 2. Conceptual query where semantic dense match shines
    res_dense = engine.search("headwinds and contraction", top_k=5, mode="semantic")
    assert len(res_dense) > 0


def test_regional_analysis_reconciliation(doc_manager):
    """Tests that regional variances reconcile 100% to corporate total."""
    target_doc = None
    for doc in doc_manager.documents.values():
        if "Regional Breakdown" in doc.dataframes:
            target_doc = doc
            break

    assert target_doc is not None
    df_regional = target_doc.dataframes["Regional Breakdown"]

    analysis = analyze_regional_breakdown(df_regional)
    assert analysis["status"] == "success"
    assert analysis["is_reconciled"] is True

    # Revenue delta should equal -60k: North (-30), East (-20), South (-10), West (0)
    assert analysis["total_revenue_delta"] == -60.0
    assert analysis["primary_revenue_drag_region"] == "North"

    regions_map = {r["region"]: r for r in analysis["regions"]}
    assert regions_map["North"]["revenue_delta"] == -30.0
    assert regions_map["North"]["share_of_revenue_change_pct"] == 50.0
    assert regions_map["East"]["revenue_delta"] == -20.0
    assert regions_map["East"]["share_of_revenue_change_pct"] == 33.3
    assert regions_map["South"]["revenue_delta"] == -10.0
    assert regions_map["South"]["share_of_revenue_change_pct"] == 16.7
    assert regions_map["West"]["revenue_delta"] == 0.0


def test_render_waterfall_chart():
    """Tests programmatic rendering of high-DPI waterfall PNG."""
    mock_bridge = {
        "waterfall_steps": [
            {"name": "Q2 Operating Profit", "amount": 150.0, "type": "absolute"},
            {"name": "Revenue Impact", "amount": -60.0, "type": "relative"},
            {"name": "COGS Variance", "amount": 15.0, "type": "relative"},
            {"name": "Marketing Variance", "amount": -25.0, "type": "relative"},
            {"name": "Other Opex Variance", "amount": -10.0, "type": "relative"},
            {"name": "Q3 Operating Profit", "amount": 70.0, "type": "total"}
        ]
    }
    output_png = os.path.join(os.path.dirname(__file__), "..", "outputs", "test_waterfall.png")
    rendered = render_waterfall_chart(mock_bridge, output_png)
    assert rendered is not None
    assert os.path.exists(output_png)
    assert os.path.getsize(output_png) > 1000
