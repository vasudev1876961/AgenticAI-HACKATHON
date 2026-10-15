"""
Neuro-SAN Coded Tool: MonteCarloTool
Wraps stochastic Monte Carlo risk simulation, Value at Risk (VaR), and target probability analysis.
"""

from typing import Dict, Any, Optional
from src.analysis.monte_carlo_simulation import run_monte_carlo_simulation


class MonteCarloTool:
    """
    Exposes stochastic simulation and VaR analysis to Neuro-SAN agents.
    """

    def execute(
        self,
        base_data: Optional[Dict[str, Any]] = None,
        target_profit: float = 150.0,
        iterations: int = 2000,
        revenue_volatility: float = 0.08,
        cogs_inflation_volatility: float = 0.04,
        marketing_shock_volatility: float = 0.12,
        fixed_opex_volatility: float = 0.03,
        random_seed: Optional[int] = 42
    ) -> Dict[str, Any]:
        data = base_data or {"revenue": 940.0, "cogs": 585.0, "marketing": 125.0, "other_opex": 160.0}
        res = run_monte_carlo_simulation(
            base_data=data,
            target_profit=target_profit,
            iterations=iterations,
            revenue_volatility=revenue_volatility,
            cogs_inflation_volatility=cogs_inflation_volatility,
            marketing_shock_volatility=marketing_shock_volatility,
            fixed_opex_volatility=fixed_opex_volatility,
            random_seed=random_seed
        )
        return {"status": "success", "result": res.to_dict()}

    def __call__(self, **kwargs) -> Dict[str, Any]:
        return self.execute(**kwargs)
