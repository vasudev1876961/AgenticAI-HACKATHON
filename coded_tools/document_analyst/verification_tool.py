"""
Neuro-SAN Coded Tool: VerificationTool
Audits draft claims against evidence IDs, validates mathematical reconciliation,
and detects cross-source contradictions.
"""

from typing import Dict, Any, List, Optional
from src.verification.validate_report import VerificationCritic


class VerificationTool:
    """
    Exposes verification and citation validation to Verification Critic Agent.
    """

    def __init__(self, critic: Optional[VerificationCritic] = None):
        self.critic = critic or VerificationCritic()

    def execute(
        self,
        draft_claims: List[Dict[str, Any]],
        profit_bridge_result: Optional[Dict[str, Any]] = None,
        retrieved_evidence: Optional[List[Dict[str, Any]]] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Executes audit checks returning verification report.
        """
        report = self.critic.audit_analysis(
            draft_claims=draft_claims,
            profit_bridge_result=profit_bridge_result,
            retrieved_evidence=retrieved_evidence,
            retry_count=retry_count
        )
        return report.to_dict()

    def __call__(self, **kwargs) -> Dict[str, Any]:
        return self.execute(**kwargs)
