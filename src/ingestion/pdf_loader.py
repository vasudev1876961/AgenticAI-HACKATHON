"""
PDF Loader using PyMuPDF (fitz)
Extracts page-by-page text, detects sections, and preserves exact source page references.
"""

import os
from typing import List, Dict, Any
import fitz  # PyMuPDF


def load_pdf(file_path: str) -> List[Dict[str, Any]]:
    """
    Extracts text and metadata from a PDF file page by page.
    Returns a list of page records with:
        - page: 1-indexed page number
        - text: extracted text
        - section: detected section header or 'General'
        - total_pages: int
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    records = []
    doc = fitz.open(file_path)
    total_pages = len(doc)

    for page_idx in range(total_pages):
        page = doc[page_idx]
        page_num = page_idx + 1
        text = page.get_text("text").strip()

        # Simple section detection heuristic from text lines
        section = "General"
        for line in text.split("\n"):
            line_str = line.strip()
            if "Section:" in line_str or line_str.isupper() and len(line_str) > 3:
                section = line_str.replace("Section:", "").strip()
                break

        records.append({
            "page": page_num,
            "text": text,
            "section": section,
            "total_pages": total_pages
        })

    doc.close()
    return records
