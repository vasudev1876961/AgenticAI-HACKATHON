"""
Document & Financial Forensics Agent
Autonomous specialist agent for statistical ratio surge detection,
cost elasticity auditing, and target realization analysis.
"""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
from ..ingestion.loader_manager import DocumentManager
from ..analysis.document_forensics import analyze_financial_forensics, FinancialForensicsReport
from ..analysis.cleaning import clean_numeric_value


class DocumentForensicsAgent(BaseAgent):
    """
    Agent 8: Document Forensics Specialist
    Uncovers silent accounting anomalies, ratio inversions, downside concentration,
    and target-vs-actual discrepancies across ingested documents.
    """

    def __init__(self, doc_manager: DocumentManager):
        super().__init__(
            name="DocumentForensicsAgent",
            role_description="Audits datasets for ratio surges, cost elasticity failures, and target reconciliation gaps."
        )
        self.doc_manager = doc_manager

    def audit(self, p1_name: str = "Q2", p2_name: str = "Q3") -> Dict[str, Any]:
        """Runs the forensic audit suite across loaded workspace datasets."""
        self.log_step(
            receiver="AnalystOrchestrator",
            step_name="ForensicAuditStarted",
            content=f"Initiating forensic analysis on {p1_name} vs {p2_name} operational metrics."
        )

        p1_data = {"revenue": 1000.0, "cogs": 600.0, "marketing": 100.0, "other_opex": 150.0}
        p2_data = {"revenue": 940.0, "cogs": 585.0, "marketing": 125.0, "other_opex": 160.0}
        regional_df = None
        marketing_df = None

        for doc in self.doc_manager.documents.values():
            if "Quarterly Summary" in doc.dataframes:
                df = doc.dataframes["Quarterly Summary"]
                col_metric = next((c for c in df.columns if "metric" in str(c).lower()), None)
                if col_metric and p1_name in df.columns and p2_name in df.columns:
                    for _, row in df.iterrows():
                        m_str = str(row[col_metric]).lower()
                        v1 = clean_numeric_value(row[p1_name])
                        v2 = clean_numeric_value(row[p2_name])
                        if v1 is not None and v2 is not None:
                            if "revenue" in m_str:
                                p1_data["revenue"], p2_data["revenue"] = v1, v2
                            elif "cost" in m_str or "cogs" in m_str:
                                p1_data["cogs"], p2_data["cogs"] = v1, v2
                            elif "marketing" in m_str:
                                p1_data["marketing"], p2_data["marketing"] = v1, v2
                            elif "other" in m_str or "opex" in m_str:
                                p1_data["other_opex"], p2_data["other_opex"] = v1, v2

            if "Regional Breakdown" in doc.dataframes:
                regional_df = doc.dataframes["Regional Breakdown"]

            if "marketing" in doc.file_name.lower() and doc.dataframes:
                marketing_df = next(iter(doc.dataframes.values()))

        report: FinancialForensicsReport = analyze_financial_forensics(
            p1=p1_data,
            p2=p2_data,
            p1_name=p1_name,
            p2_name=p2_name,
            regional_df=regional_df,
            marketing_df=marketing_df
        )

        self.log_step(
            receiver="AnalystOrchestrator",
            step_name="ForensicAuditCompleted",
            content=f"Forensic audit identified {len(report.anomalies)} anomalies. Overall Risk Score: {report.overall_risk_score}.",
            metadata={"anomaly_count": len(report.anomalies), "risk_score": report.overall_risk_score}
        )

        return report.to_dict()
