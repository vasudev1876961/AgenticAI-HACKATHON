"""
Neuro-SAN Coded Tool: SimulationTool
Wraps deterministic counterfactual scenario simulation, sensitivity grids, and recovery playbooks.
"""

from typing import Dict, Any, Optional
from src.analysis.counterfactual_simulation import (
    simulate_counterfactual,
    generate_sensitivity_matrix,
    rank_recovery_levers
)


class SimulationTool:
    """
    Exposes counterfactual modeling and sensitivity matrices to Neuro-SAN agents.
    """

    def execute(
        self,
        operation: str = "simulate",
        p1_data: Optional[Dict[str, Any]] = None,
        p2_data: Optional[Dict[str, Any]] = None,
        modifications: Optional[Dict[str, Any]] = None,
        scenario_name: str = "Simulation",
        var1_name: str = "revenue",
        var2_name: str = "marketing"
    ) -> Dict[str, Any]:
        p1 = p1_data or {"revenue": 1000.0, "cogs": 600.0, "marketing": 100.0, "other_opex": 150.0}
        p2 = p2_data or {"revenue": 940.0, "cogs": 585.0, "marketing": 125.0, "other_opex": 160.0}

        if operation == "simulate":
            mods = modifications or {}
            res = simulate_counterfactual(p1, p2, mods, scenario_name=scenario_name)
            return {"status": "success", "result": res.to_dict()}
        elif operation == "sensitivity":
            grid = generate_sensitivity_matrix(p1, p2, var1_name=var1_name, var2_name=var2_name)
            return {"status": "success", "result": grid}
        elif operation == "playbooks":
            ranked = rank_recovery_levers(p1, p2)
            return {"status": "success", "result": ranked}
        else:
            return {"status": "error", "message": f"Unknown operation: {operation}"}

    def __call__(self, **kwargs) -> Dict[str, Any]:
        return self.execute(**kwargs)
