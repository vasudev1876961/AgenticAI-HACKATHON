"""
Document Researcher Agent
Searches textual and tabular files, extracts evidence records with exact page/row citations.
"""

from typing import List, Dict, Any, Optional
from .base_agent import BaseAgent
from ..retrieval.search import EvidenceSearchEngine
from ..ingestion.loader_manager import DocumentManager


class DocumentResearcherAgent(BaseAgent):
    """
    Agent 2: Document Researcher
    Responsible for evidence extraction, provenance tracking, and document querying.
    """

    def __init__(self, doc_manager: DocumentManager, search_engine: EvidenceSearchEngine):
        super().__init__(
            name="DocumentResearcher",
            role_description="Searches text, extracts relevant passages, and preserves exact source locations."
        )
        self.doc_manager = doc_manager
        self.search_engine = search_engine

    def investigate(self, query: str, top_k: int = 6) -> Dict[str, Any]:
        """
        Executes query retrieval across ingested documents.
        """
        self.log_step(
            receiver="AnalystOrchestrator",
            step_name="SearchEvidence",
            content=f"Searching evidence for query: '{query}' across indexed files.",
            metadata={"query": query, "top_k": top_k}
        )

        results = self.search_engine.search(query=query, top_k=top_k)

        # Fallback if specific financial terms need broad match
        if not results:
            expanded_query = "profit revenue expense marketing Q2 Q3"
            results = self.search_engine.search(query=expanded_query, top_k=top_k)

        self.log_step(
            receiver="AnalystOrchestrator",
            step_name="EvidenceRetrieved",
            content=f"Retrieved {len(results)} grounded evidence snippets.",
            metadata={"count": len(results), "evidence_ids": [r["evidence_id"] for r in results]}
        )

        return {
            "query": query,
            "evidence_count": len(results),
            "evidence": results
        }
