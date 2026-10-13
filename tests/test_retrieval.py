"""
Unit Tests for Document Ingestion and Evidence Retrieval.
"""

import os
import pytest
from src.ingestion.loader_manager import DocumentManager
from src.retrieval.search import EvidenceSearchEngine

DEMO_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "synthetic_demo")


@pytest.fixture
def doc_manager():
    mgr = DocumentManager()
    mgr.ingest_directory(DEMO_DIR)
    return mgr


def test_ingestion_multi_format(doc_manager):
    files = doc_manager.list_workspace_files()
    assert len(files) >= 5

    file_types = {f["file_type"] for f in files}
    assert "excel" in file_types
    assert "csv" in file_types
    assert "pdf" in file_types
    assert "docx" in file_types

    # Ensure chunks exist and have evidence IDs
    assert len(doc_manager.all_chunks) > 0
    first_chunk = doc_manager.all_chunks[0]
    assert first_chunk.evidence_id.startswith("EV-")
    assert first_chunk.file_name != ""


def test_search_evidence_relevance(doc_manager):
    engine = EvidenceSearchEngine(doc_manager.all_chunks)
    
    # Search for profit decline
    results = engine.search("operating profit decline Q3", top_k=5)
    assert len(results) > 0
    top_result = results[0]
    assert "evidence_id" in top_result
    assert top_result["relevance_score"] > 0

    # Test lookup by ID
    ev_id = top_result["evidence_id"]
    lookup = engine.get_evidence_by_id(ev_id)
    assert lookup is not None
    assert lookup["evidence_id"] == ev_id


def test_excel_provenance(doc_manager):
    """Ensures excel chunks preserve sheet name and row index."""
    excel_chunks = [c for c in doc_manager.all_chunks if c.source_type == "excel"]
    assert len(excel_chunks) > 0
    sample = excel_chunks[0]
    assert sample.sheet_name is not None
    assert sample.row_range is not None
    assert "Row" in sample.row_range
