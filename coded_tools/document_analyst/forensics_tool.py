"""
Neuro-SAN Coded Tool: ForensicsTool
Wraps financial forensics, ratio surge detection, and target-vs-actual auditing.
"""

from typing import Dict, Any, Optional
from src.analysis.document_forensics import analyze_financial_forensics


class ForensicsTool:
    """
    Exposes document forensics and statistical anomaly auditing to Neuro-SAN agents.
    """

    def execute(
        self,
        operation: str = "audit",
        p1_data: Optional[Dict[str, Any]] = None,
        p2_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        p1 = p1_data or {"revenue": 1000.0, "cogs": 600.0, "marketing": 100.0, "other_opex": 150.0}
        p2 = p2_data or {"revenue": 940.0, "cogs": 585.0, "marketing": 125.0, "other_opex": 160.0}

        if operation == "audit":
            report = analyze_financial_forensics(p1, p2)
            return {"status": "success", "result": report.to_dict()}
        else:
            return {"status": "error", "message": f"Unknown operation: {operation}"}

    def __call__(self, **kwargs) -> Dict[str, Any]:
        return self.execute(**kwargs)
