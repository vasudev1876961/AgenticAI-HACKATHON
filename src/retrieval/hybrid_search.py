"""
Hybrid Search Engine: BM25 + Semantic Dense Vector Space with Reciprocal Rank Fusion (RRF)
Combines keyword precision with semantic embeddings to handle conceptual queries
(e.g., matching 'why did earnings plunge' with 'operating profit contracted').
"""

import math
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi

from ..ingestion.loader_manager import DocumentChunk
from .search import tokenize


class HybridSearchEngine:
    """
    Advanced Hybrid Search combining:
    1. BM25 Okapi for exact keyword matching
    2. Sublinear TF-IDF + Cosine Vector Space for dense semantic matching
    3. Reciprocal Rank Fusion (RRF) to merge rankings without score calibration artifacts
    """

    def __init__(self, chunks: List[DocumentChunk], rrf_k: int = 60):
        self.chunks = chunks
        self.rrf_k = rrf_k
        self.evidence_lookup: Dict[str, DocumentChunk] = {c.evidence_id: c for c in chunks}
        self.chunk_lookup: Dict[str, DocumentChunk] = {c.chunk_id: c for c in chunks}
        
        self.bm25: Optional[BM25Okapi] = None
        self.tfidf_vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        
        self._build_indexes()

    def _build_indexes(self):
        if not self.chunks:
            return

        # 1. Build BM25
        corpus_tokens = [tokenize(c.text) for c in self.chunks]
        if any(len(doc) > 0 for doc in corpus_tokens):
            self.bm25 = BM25Okapi(corpus_tokens)

        # 2. Build Semantic Vector Space
        texts = [c.text for c in self.chunks]
        if texts and any(len(t.strip()) > 0 for t in texts):
            self.tfidf_vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),
                sublinear_tf=True,
                stop_words="english"
            )
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)

    def search(
        self,
        query: str,
        top_k: int = 6,
        mode: str = "hybrid",  # "hybrid", "bm25", "semantic"
        file_filters: Optional[List[str]] = None,
        source_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes query retrieval returning ranked evidence records.
        """
        if not self.chunks:
            return []

        num_docs = len(self.chunks)
        bm25_scores = np.zeros(num_docs)
        dense_scores = np.zeros(num_docs)

        # 1. BM25 Scoring
        if self.bm25:
            tokens = tokenize(query)
            if tokens:
                raw_bm25 = self.bm25.get_scores(tokens)
                bm25_scores = np.array(raw_bm25)

        # 2. Semantic Scoring
        if self.tfidf_vectorizer and self.tfidf_matrix is not None:
            try:
                q_vec = self.tfidf_vectorizer.transform([query])
                sims = cosine_similarity(q_vec, self.tfidf_matrix).flatten()
                dense_scores = np.nan_to_num(sims)
            except Exception:
                dense_scores = np.zeros(num_docs)

        # RRF Fusion: Rank both lists and compute RRF Score: 1 / (k + rank)
        rrf_scores = np.zeros(num_docs)

        if mode in ["hybrid", "bm25"]:
            bm25_ranked_indices = np.argsort(-bm25_scores)
            for rank, idx in enumerate(bm25_ranked_indices):
                if bm25_scores[idx] > 0:
                    rrf_scores[idx] += 1.0 / (self.rrf_k + rank + 1)

        if mode in ["hybrid", "semantic"]:
            dense_ranked_indices = np.argsort(-dense_scores)
            for rank, idx in enumerate(dense_ranked_indices):
                if dense_scores[idx] > 0:
                    rrf_scores[idx] += 1.0 / (self.rrf_k + rank + 1)

        final_indices = np.argsort(-rrf_scores)

        results = []
        for idx in final_indices:
            score = float(rrf_scores[idx])
            if score <= 0.0:
                continue

            chunk = self.chunks[idx]

            # Filters
            if file_filters and chunk.file_name not in file_filters and chunk.file_id not in file_filters:
                continue
            if source_types and chunk.source_type not in source_types:
                continue

            res = chunk.to_dict()
            res["relevance_score"] = round(score, 5)
            res["bm25_score"] = round(float(bm25_scores[idx]), 3)
            res["semantic_score"] = round(float(dense_scores[idx]), 3)
            results.append(res)

            if len(results) >= top_k:
                break

        # Fallback to pure BM25 if RRF didn't yield enough
        if not results and self.bm25:
            tokens = tokenize(query)
            if tokens:
                raw_bm25 = self.bm25.get_scores(tokens)
                top_indices = np.argsort(-raw_bm25)[:top_k]
                for idx in top_indices:
                    if raw_bm25[idx] > 0:
                        c = self.chunks[idx].to_dict()
                        c["relevance_score"] = round(float(raw_bm25[idx]), 4)
                        results.append(c)

        return results

    def get_evidence_by_id(self, evidence_id: str) -> Optional[Dict[str, Any]]:
        chunk = self.evidence_lookup.get(evidence_id)
        return chunk.to_dict() if chunk else None
