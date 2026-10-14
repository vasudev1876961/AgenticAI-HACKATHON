"""
Scenario Simulation Agent
Autonomous specialist agent for counterfactual What-If modeling, sensitivity testing,
and strategic recovery playbook ranking.
"""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
from ..ingestion.loader_manager import DocumentManager
from ..analysis.counterfactual_simulation import (
    simulate_counterfactual,
    generate_sensitivity_matrix,
    rank_recovery_levers,
    CounterfactualScenarioResult
)
from ..analysis.cleaning import clean_numeric_value


class ScenarioSimulationAgent(BaseAgent):
    """
    Agent 7: Scenario Simulation Specialist
    Evaluates hypothetical financial interventions, models counterfactual waterfalls,
    and runs multi-dimensional sensitivity matrices.
    """

    def __init__(self, doc_manager: DocumentManager):
        super().__init__(
            name="ScenarioSimulationAgent",
            role_description="Executes counterfactual What-If financial simulations, sensitivity matrices, and recovery playbooks."
        )
        self.doc_manager = doc_manager

    def _extract_base_periods(self, p1_name: str = "Q2", p2_name: str = "Q3"):
        """Extracts P1 and P2 baseline dictionaries from loaded documents."""
        p1_data = {"revenue": 1000.0, "cogs": 600.0, "marketing": 100.0, "other_opex": 150.0}
        p2_data = {"revenue": 940.0, "cogs": 585.0, "marketing": 125.0, "other_opex": 160.0}

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
                break

        return p1_data, p2_data

    def simulate(
        self,
        modifications: Dict[str, Any],
        scenario_name: str = "Custom Counterfactual",
        description: str = "",
        p1_name: str = "Q2",
        p2_name: str = "Q3"
    ) -> Dict[str, Any]:
        """Runs a deterministic counterfactual simulation against the loaded baseline."""
        self.log_step(
            receiver="AnalystOrchestrator",
            step_name="SimulateCounterfactual",
            content=f"Running counterfactual scenario '{scenario_name}' with parameters {modifications}",
            metadata={"modifications": modifications}
        )

        p1_data, p2_data = self._extract_base_periods(p1_name, p2_name)
        result = simulate_counterfactual(
            p1=p1_data,
            p2=p2_data,
            modifications=modifications,
            scenario_name=scenario_name,
            description=description,
            p1_name=p1_name,
            p2_name=p2_name
        )

        self.log_step(
            receiver="AnalystOrchestrator",
            step_name="SimulationCompleted",
            content=f"Simulation '{scenario_name}' completed. Profit recovery: ₹{result.profit_recovery_amount:+g}k ({result.recovery_percentage:.1f}% of loss recovered).",
            metadata={"recovery": result.profit_recovery_amount, "reconciled": result.is_reconciled}
        )

        return result.to_dict()

    def run_sensitivity(
        self,
        var1_name: str = "revenue",
        var2_name: str = "marketing",
        p1_name: str = "Q2",
        p2_name: str = "Q3"
    ) -> Dict[str, Any]:
        """Computes a 2D sensitivity matrix across variations of two drivers."""
        p1_data, p2_data = self._extract_base_periods(p1_name, p2_name)
        return generate_sensitivity_matrix(
            p1=p1_data,
            p2=p2_data,
            var1_name=var1_name,
            var2_name=var2_name,
            p1_name=p1_name,
            p2_name=p2_name
        )

    def evaluate_playbooks(self, p1_name: str = "Q2", p2_name: str = "Q3") -> List[Dict[str, Any]]:
        """Evaluates standard strategic executive recovery playbooks."""
        p1_data, p2_data = self._extract_base_periods(p1_name, p2_name)
        return rank_recovery_levers(p1_data, p2_data, p1_name=p1_name, p2_name=p2_name)
