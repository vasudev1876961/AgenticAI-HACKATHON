"""
Chunking utilities for text processing and semantic boundaries.
"""

from typing import List
import re


def create_text_chunks(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """
    Splits text into chunks of roughly `chunk_size` characters with `overlap`,
    attempting to split on sentence or paragraph boundaries.
    """
    if not text or len(text) <= chunk_size:
        return [text] if text else []

    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = []
    current_len = 0

    for sent in sentences:
        sent_len = len(sent)
        if current_len + sent_len > chunk_size and current_chunk:
            chunk_str = " ".join(current_chunk)
            chunks.append(chunk_str)
            # Handle overlap by keeping the last sentence
            current_chunk = [current_chunk[-1]] if len(current_chunk) > 1 else []
            current_len = sum(len(s) for s in current_chunk)

        current_chunk.append(sent)
        current_len += sent_len

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
