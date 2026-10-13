"""
Neuro-SAN Coded Tool: CalculationTool
Performs deterministic calculations: profit bridges, variance analysis, and reconciliation.
"""

from typing import Dict, Any, Optional
from src.analysis.contribution_analysis import calculate_profit_bridge
from src.analysis.compare_periods import compare_periods


class CalculationTool:
    """
    Exposes deterministic calculation operations to the Data Analyst.
    """

    def execute(
        self,
        operation: str = "calculate_profit_bridge",
        p1_data: Optional[Dict[str, Any]] = None,
        p2_data: Optional[Dict[str, Any]] = None,
        p1_name: str = "Q2",
        p2_name: str = "Q3",
        metric_name: Optional[str] = None,
        val_1: Optional[Any] = None,
        val_2: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Executes either 'calculate_profit_bridge' or 'compare_periods'.
        """
        if operation == "calculate_profit_bridge":
            if not p1_data or not p2_data:
                return {
                    "status": "error",
                    "message": "p1_data and p2_data dictionaries with revenue, cogs, marketing, other_opex are required."
                }
            try:
                res = calculate_profit_bridge(p1_data, p2_data, p1_name, p2_name)
                return {
                    "status": "success",
                    "result": res.to_dict()
                }
            except Exception as e:
                return {"status": "error", "message": str(e)}

        elif operation == "compare_periods":
            if metric_name is None or val_1 is None or val_2 is None:
                return {
                    "status": "error",
                    "message": "metric_name, val_1, and val_2 are required for compare_periods."
                }
            comp = compare_periods(metric_name, p1_name, val_1, p2_name, val_2)
            return {
                "status": "success",
                "result": comp
            }
        else:
            return {"status": "error", "message": f"Unknown operation: {operation}"}

    def __call__(self, **kwargs) -> Dict[str, Any]:
        return self.execute(**kwargs)
