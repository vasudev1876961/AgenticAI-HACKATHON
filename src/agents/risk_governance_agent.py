"""
Risk & Governance Specialist Agent
Autonomous agent for stochastic risk quantification (Monte Carlo VaR),
DuPont operational leverage analysis, and regulatory audit compliance (SOX 404 / BCBS 239).
"""

from typing import Dict, Any, Optional
from .base_agent import BaseAgent
from ..ingestion.loader_manager import DocumentManager
from ..analysis.monte_carlo_simulation import run_monte_carlo_simulation, MonteCarloRiskResult
from ..analysis.dupont_analysis import analyze_dupont_leverage, DuPontAnalysisResult
from ..analysis.data_lineage import generate_audit_lineage, AuditLineageReport
from ..analysis.cleaning import clean_numeric_value


class RiskGovernanceAgent(BaseAgent):
    """
    Agent 9: Risk & Governance Specialist
    Quantifies downside tail volatility, operational leverage sensitivity,
    and certifies audit lineage for regulatory governance.
    """

    def __init__(self, doc_manager: DocumentManager):
        super().__init__(
            name="RiskGovernanceAgent",
            role_description="Executes Monte Carlo VaR simulations, DuPont operating leverage modeling, and SOX 404 / BCBS 239 audit certification."
        )
        self.doc_manager = doc_manager

    def evaluate_risk_profile(
        self,
        p1_name: str = "Q2",
        p2_name: str = "Q3",
        iterations: int = 2000,
        target_profit: float = 150.0,
        profit_bridge_result: Optional[Dict[str, Any]] = None,
        critic_audit: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Runs the combined risk, leverage, and compliance assessment."""
        self.log_step(
            receiver="AnalystOrchestrator",
            step_name="RiskAssessmentStarted",
            content=f"Starting risk & governance evaluation for {p1_name} vs {p2_name}."
        )

        p1_data = {"revenue": 1000.0, "cogs": 600.0, "marketing": 100.0, "other_opex": 150.0}
        p2_data = {"revenue": 940.0, "cogs": 585.0, "marketing": 125.0, "other_opex": 160.0}

        # Extract real values from doc manager if available
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

        # 1. Monte Carlo Simulation
        monte_carlo_res: MonteCarloRiskResult = run_monte_carlo_simulation(
            base_data=p2_data,
            target_profit=target_profit,
            iterations=iterations,
            random_seed=42
        )

        # 2. DuPont Leverage Analysis
        dupont_res: DuPontAnalysisResult = analyze_dupont_leverage(
            p1=p1_data,
            p2=p2_data,
            p1_name=p1_name,
            p2_name=p2_name
        )

        # 3. Cryptographic Audit Lineage & SOX Certification
        lineage_report: AuditLineageReport = generate_audit_lineage(
            doc_manager=self.doc_manager,
            profit_bridge_result=profit_bridge_result,
            critic_audit=critic_audit
        )

        self.log_step(
            receiver="AnalystOrchestrator",
            step_name="RiskAssessmentCompleted",
            content=f"Risk evaluation complete. VaR(95%): {round(monte_carlo_res.var_95, 2)}k, DOL: {round(dupont_res.degree_of_operating_leverage, 2)}x, SOX Status: {lineage_report.sox_404_compliance['certification_status']}."
        )

        return {
            "monte_carlo": monte_carlo_res.to_dict(),
            "dupont_leverage": dupont_res.to_dict(),
            "audit_lineage": lineage_report.to_dict(),
            "executive_risk_summary": {
                "risk_tier": monte_carlo_res.simulated_scenarios_summary["risk_tier"],
                "var_95_amount": monte_carlo_res.var_95,
                "prob_target_achieved": monte_carlo_res.prob_target_achieved_pct,
                "degree_of_operating_leverage": dupont_res.degree_of_operating_leverage,
                "break_even_revenue": dupont_res.break_even_revenue_q3,
                "sox_certificate_id": lineage_report.certificate_id
            }
        }
