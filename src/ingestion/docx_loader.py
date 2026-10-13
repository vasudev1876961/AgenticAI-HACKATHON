"""
DOCX Loader using python-docx
Extracts headings, paragraphs, and tables preserving paragraph indices and section context.
"""

import os
from typing import List, Dict, Any
from docx import Document


def load_docx(file_path: str) -> List[Dict[str, Any]]:
    """
    Extracts paragraphs and tables from a Word document (.docx).
    Returns list of items with:
        - paragraph_id: int
        - text: str
        - style: str
        - section: str
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"DOCX file not found: {file_path}")

    doc = Document(file_path)
    records = []
    current_section = "General"

    for idx, p in enumerate(doc.paragraphs):
        text = p.text.strip()
        if not text:
            continue
        
        style_name = p.style.name if p.style else "Normal"
        if "Heading" in style_name or "Title" in style_name:
            current_section = text

        records.append({
            "paragraph_id": idx + 1,
            "text": text,
            "style": style_name,
            "section": current_section
        })

    # Also extract tables if present
    for t_idx, table in enumerate(doc.tables):
        for r_idx, row in enumerate(table.rows):
            cells = [c.text.strip() for c in row.cells]
            table_text = f"Table {t_idx + 1}, Row {r_idx + 1}: " + " | ".join(cells)
            records.append({
                "paragraph_id": f"table_{t_idx + 1}_row_{r_idx + 1}",
                "text": table_text,
                "style": "Table",
                "section": current_section
            })

    return records
