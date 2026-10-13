"""
Document Manager & Orchestration
Coordinates multi-format ingestion, metadata tagging, and unified chunk creation.
"""

import os
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import pandas as pd

from .pdf_loader import load_pdf
from .excel_loader import load_excel
from .csv_loader import load_csv
from .docx_loader import load_docx


@dataclass
class DocumentChunk:
    chunk_id: str
    evidence_id: str
    file_id: str
    file_name: str
    source_type: str  # 'pdf', 'excel', 'csv', 'docx'
    text: str
    page: Optional[int] = None
    sheet_name: Optional[str] = None
    row_range: Optional[str] = None
    cell_range: Optional[str] = None
    section: str = "General"
    structured_data: Optional[Dict[str, Any]] = None
    relevance_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "chunk_id": self.chunk_id,
            "file_name": self.file_name,
            "source_type": self.source_type,
            "page": self.page,
            "sheet_name": self.sheet_name,
            "row_range": self.row_range,
            "cell_range": self.cell_range,
            "section": self.section,
            "text": self.text,
            "relevance_score": round(self.relevance_score, 4),
            "structured_data": self.structured_data
        }


@dataclass
class IngestedDocument:
    file_id: str
    file_name: str
    file_path: str
    file_type: str
    size_bytes: int
    chunks: List[DocumentChunk] = field(default_factory=list)
    raw_data: Any = None
    dataframes: Dict[str, pd.DataFrame] = field(default_factory=dict)


class DocumentManager:
    """
    Manages a workspace or collection of documents, providing ingestion,
    indexing, and structured evidence generation.
    """

    def __init__(self, workspace_path: Optional[str] = None):
        self.workspace_path = workspace_path
        self.documents: Dict[str, IngestedDocument] = {}
        self.all_chunks: List[DocumentChunk] = []
        self._evidence_counter = 0

    def _next_evidence_id(self) -> str:
        self._evidence_counter += 1
        return f"EV-{self._evidence_counter:03d}"

    def list_workspace_files(self) -> List[Dict[str, Any]]:
        """Lists all supported files in workspace or loaded memory."""
        files = []
        for file_id, doc in self.documents.items():
            files.append({
                "file_id": file_id,
                "file_name": doc.file_name,
                "file_type": doc.file_type,
                "size_bytes": doc.size_bytes,
                "chunks_count": len(doc.chunks),
                "sheets": list(doc.dataframes.keys()) if doc.dataframes else []
            })
        return files

    def ingest_file(self, file_path: str) -> IngestedDocument:
        """Ingests a single file and converts it into evidence chunks."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_name = os.path.basename(file_path)
        ext = os.path.splitext(file_name)[1].lower()
        file_id = f"doc_{file_name.replace('.', '_')}"
        size_bytes = os.path.getsize(file_path)

        chunks: List[DocumentChunk] = []
        dataframes: Dict[str, pd.DataFrame] = {}
        raw_data = None

        if ext == ".pdf":
            file_type = "pdf"
            pages = load_pdf(file_path)
            raw_data = pages
            for p in pages:
                # If page is long, break into paragraph chunks
                paragraphs = [par.strip() for par in p["text"].split("\n\n") if par.strip()]
                if not paragraphs:
                    paragraphs = [p["text"]] if p["text"].strip() else []

                for c_idx, par in enumerate(paragraphs):
                    ev_id = self._next_evidence_id()
                    chunk = DocumentChunk(
                        chunk_id=f"{file_id}_p{p['page']}_c{c_idx+1}",
                        evidence_id=ev_id,
                        file_id=file_id,
                        file_name=file_name,
                        source_type="pdf",
                        page=p["page"],
                        section=p["section"],
                        text=par
                    )
                    chunks.append(chunk)

        elif ext in [".xlsx", ".xls"]:
            file_type = "excel"
            excel_data = load_excel(file_path)
            raw_data = excel_data
            dataframes = excel_data["dataframes"]

            for sheet_name, sheet_info in excel_data["sheets"].items():
                for row_rec in sheet_info["rows"]:
                    ev_id = self._next_evidence_id()
                    row_idx = row_rec["row_index"]
                    chunk = DocumentChunk(
                        chunk_id=f"{file_id}_{sheet_name}_r{row_idx}",
                        evidence_id=ev_id,
                        file_id=file_id,
                        file_name=file_name,
                        source_type="excel",
                        sheet_name=sheet_name,
                        row_range=f"Row {row_idx}",
                        section=f"Sheet: {sheet_name}",
                        text=row_rec["text"],
                        structured_data=row_rec["data"]
                    )
                    chunks.append(chunk)

        elif ext == ".csv":
            file_type = "csv"
            csv_data = load_csv(file_path)
            raw_data = csv_data
            dataframes["default"] = csv_data["dataframe"]

            for row_rec in csv_data["rows"]:
                ev_id = self._next_evidence_id()
                row_idx = row_rec["row_index"]
                chunk = DocumentChunk(
                    chunk_id=f"{file_id}_r{row_idx}",
                    evidence_id=ev_id,
                    file_id=file_id,
                    file_name=file_name,
                    source_type="csv",
                    row_range=f"Row {row_idx}",
                    section="CSV Data",
                    text=row_rec["text"],
                    structured_data=row_rec["data"]
                )
                chunks.append(chunk)

        elif ext in [".docx", ".doc"]:
            file_type = "docx"
            docx_data = load_docx(file_path)
            raw_data = docx_data

            for rec in docx_data:
                ev_id = self._next_evidence_id()
                chunk = DocumentChunk(
                    chunk_id=f"{file_id}_p{rec['paragraph_id']}",
                    evidence_id=ev_id,
                    file_id=file_id,
                    file_name=file_name,
                    source_type="docx",
                    section=rec["section"],
                    text=rec["text"]
                )
                chunks.append(chunk)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

        doc = IngestedDocument(
            file_id=file_id,
            file_name=file_name,
            file_path=file_path,
            file_type=file_type,
            size_bytes=size_bytes,
            chunks=chunks,
            raw_data=raw_data,
            dataframes=dataframes
        )

        self.documents[file_id] = doc
        self.all_chunks.extend(chunks)
        return doc

    def ingest_directory(self, dir_path: str) -> List[IngestedDocument]:
        """Ingests all supported files in a directory."""
        supported_exts = {".pdf", ".xlsx", ".xls", ".csv", ".docx"}
        results = []
        for root, _, files in os.walk(dir_path):
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in supported_exts:
                    full_path = os.path.join(root, f)
                    try:
                        results.append(self.ingest_file(full_path))
                    except Exception as e:
                        print(f"Warning: Failed to ingest {full_path}: {e}")
        return results

    def get_dataframe(self, file_id: str, sheet_name: Optional[str] = None) -> Optional[pd.DataFrame]:
        """Retrieves a DataFrame from an ingested document."""
        if file_id not in self.documents:
            return None
        doc = self.documents[file_id]
        if sheet_name and sheet_name in doc.dataframes:
            return doc.dataframes[sheet_name]
        if "default" in doc.dataframes:
            return doc.dataframes["default"]
        if doc.dataframes:
            # Return first available
            return next(iter(doc.dataframes.values()))
        return None
