"""
Neuro-SAN Coded Tool: SpreadsheetTool
Inspects spreadsheet columns, structures, schemas, and cell ranges.
"""

from typing import Dict, Any, Optional
from src.ingestion.loader_manager import DocumentManager
from src.analysis.inspect_spreadsheet import inspect_dataframe


class SpreadsheetTool:
    """
    Exposes spreadsheet inspection to Data Analyst.
    """

    def __init__(self, doc_manager: Optional[DocumentManager] = None):
        self.doc_manager = doc_manager

    def set_manager(self, doc_manager: DocumentManager):
        self.doc_manager = doc_manager

    def execute(self, file_name: str, sheet_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Inspects schema, columns, and previews rows of a requested spreadsheet.
        """
        if not self.doc_manager:
            return {"status": "error", "message": "Document manager not connected."}

        target_doc = None
        for doc in self.doc_manager.documents.values():
            if file_name.lower() in doc.file_name.lower():
                target_doc = doc
                break

        if not target_doc:
            return {"status": "error", "message": f"Spreadsheet '{file_name}' not found."}

        df = target_doc.dataframes.get(sheet_name) if sheet_name else next(iter(target_doc.dataframes.values()), None)

        if df is None:
            return {"status": "error", "message": f"Sheet '{sheet_name}' not found in {file_name}."}

        inspection = inspect_dataframe(df)
        return {
            "status": "success",
            "file_name": target_doc.file_name,
            "sheet_name": sheet_name or "default",
            "schema": inspection
        }

    def __call__(self, **kwargs) -> Dict[str, Any]:
        return self.execute(**kwargs)
