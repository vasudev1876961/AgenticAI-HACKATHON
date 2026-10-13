"""
Neuro-SAN Coded Tool: RetrievalTool
Searches evidence chunks across indexed documents with BM25 and keyword ranking.
"""

from typing import Dict, Any, List, Optional
from src.retrieval.search import EvidenceSearchEngine
from src.ingestion.loader_manager import DocumentManager


class RetrievalTool:
    """
    Exposes evidence search and citation extraction to Document Researcher.
    """

    def __init__(self, doc_manager: Optional[DocumentManager] = None):
        self.doc_manager = doc_manager
        if self.doc_manager:
            self.engine = EvidenceSearchEngine(self.doc_manager.all_chunks)
        else:
            self.engine = None

    def set_manager(self, doc_manager: DocumentManager):
        self.doc_manager = doc_manager
        self.engine = EvidenceSearchEngine(self.doc_manager.all_chunks)

    def execute(
        self,
        query: str,
        top_k: int = 5,
        file_filters: Optional[List[str]] = None,
        source_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Executes query retrieval returning ranked evidence records.
        """
        if not self.engine:
            return {"status": "error", "message": "Search engine not initialized with documents."}

        results = self.engine.search(
            query=query,
            top_k=top_k,
            file_filters=file_filters,
            source_types=source_types
        )

        return {
            "status": "success",
            "query": query,
            "total_matches": len(results),
            "evidence": results
        }

    def __call__(self, **kwargs) -> Dict[str, Any]:
        return self.execute(**kwargs)
