"""
Neuro-SAN Coded Tool: IngestionTool
Discovers, ingests, and extracts text/tables from PDF, XLSX, CSV, and DOCX files.
"""

import os
from typing import Dict, Any, List, Optional
from src.ingestion.loader_manager import DocumentManager


class IngestionTool:
    """
    Exposes document ingestion and metadata extraction capabilities to agents.
    """

    def __init__(self, workspace_path: Optional[str] = None):
        self.workspace_path = workspace_path or os.path.join(os.path.dirname(__file__), "..", "..", "data", "synthetic_demo")
        self.doc_manager = DocumentManager(self.workspace_path)
        if os.path.exists(self.workspace_path):
            self.doc_manager.ingest_directory(self.workspace_path)

    def execute(self, action: str = "list_files", file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Main execution endpoint for Neuro-SAN tool invocations.
        """
        if action == "list_files":
            return {
                "status": "success",
                "files": self.doc_manager.list_workspace_files()
            }
        elif action == "extract_document" and file_path:
            doc = self.doc_manager.ingest_file(file_path)
            return {
                "status": "success",
                "file_name": doc.file_name,
                "file_type": doc.file_type,
                "chunks_count": len(doc.chunks),
                "chunks_preview": [c.to_dict() for c in doc.chunks[:5]]
            }
        else:
            return {
                "status": "error",
                "message": f"Unsupported action '{action}' or missing file_path."
            }

    def __call__(self, **kwargs) -> Dict[str, Any]:
        return self.execute(**kwargs)
