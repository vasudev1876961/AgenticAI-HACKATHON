"""
Evidence Search Engine
Provides BM25-based keyword and semantic retrieval across all ingested document chunks,
preserving provenance (evidence ID, file name, page, sheet, row, section).
"""

import re
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi

from ..ingestion.loader_manager import DocumentChunk


def tokenize(text: str) -> List[str]:
    """Basic lowercased alphanumeric tokenizer."""
    return re.findall(r'\b[a-zA-Z0-9_\u20B9\$]+\b', text.lower())


class EvidenceSearchEngine:
    """
    Search engine over Ingested Document Chunks.
    """

    def __init__(self, chunks: List[DocumentChunk]):
        self.chunks = chunks
        self.evidence_lookup: Dict[str, DocumentChunk] = {
            c.evidence_id: c for c in chunks
        }
        self.chunk_lookup: Dict[str, DocumentChunk] = {
            c.chunk_id: c for c in chunks
        }
        self._build_index()

    def _build_index(self):
        self.corpus = [tokenize(c.text) for c in self.chunks]
        if self.corpus and any(len(doc) > 0 for doc in self.corpus):
            self.bm25 = BM25Okapi(self.corpus)
        else:
            self.bm25 = None

    def search(
        self,
        query: str,
        top_k: int = 5,
        file_filters: Optional[List[str]] = None,
        source_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes BM25 search over evidence chunks, applying optional filters.
        """
        if not self.chunks or not self.bm25:
            return []

        tokenized_query = tokenize(query)
        if not tokenized_query:
            return []

        doc_scores = self.bm25.get_scores(tokenized_query)

        scored_chunks = []
        for idx, score in enumerate(doc_scores):
            chunk = self.chunks[idx]

            # Apply filters
            if file_filters and chunk.file_name not in file_filters and chunk.file_id not in file_filters:
                continue
            if source_types and chunk.source_type not in source_types:
                continue

            if score > 0.0:
                scored_chunks.append((chunk, float(score)))

        # Sort descending by score
        scored_chunks.sort(key=lambda x: x[1], reverse=True)

        results = []
        for chunk, score in scored_chunks[:top_k]:
            res = chunk.to_dict()
            res["relevance_score"] = round(score, 4)
            results.append(res)

        return results

    def get_evidence_by_id(self, evidence_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves exact evidence record by its unique ID."""
        chunk = self.evidence_lookup.get(evidence_id)
        return chunk.to_dict() if chunk else None

    def get_all_evidence(self) -> List[Dict[str, Any]]:
        """Returns all evidence items."""
        return [c.to_dict() for c in self.chunks]
