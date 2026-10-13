"""
Verification / Critic Agent
Executes multi-point verification audits and enforces the bounded evaluation loop.
"""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
from ..verification.validate_report import VerificationCritic, VerificationReport


class VerificationCriticAgent(BaseAgent):
    """
    Agent 5: Verification / Critic Agent
    Reviews calculations, validates citations against evidence store, and enforces consistency.
    """

    def __init__(self, critic_engine: Optional[VerificationCritic] = None, max_retries: int = 2):
        super().__init__(
            name="VerificationCritic",
            role_description="Audits calculations, citations, and contradictions with strict retry limits."
        )
        self.critic_engine = critic_engine or VerificationCritic(max_retries=max_retries)

    def verify(
        self,
        draft_claims: List[Dict[str, Any]],
        profit_bridge_result: Optional[Dict[str, Any]],
        retrieved_evidence: List[Dict[str, Any]],
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Executes audit and returns structured evaluation verdict.
        """
        self.log_step(
            receiver="AnalystOrchestrator",
            step_name="AuditExecution",
            content=f"Initiating verification audit (Attempt {retry_count + 1}). Checking reconciliation, citations, and contradictions."
        )

        report: VerificationReport = self.critic_engine.audit_analysis(
            draft_claims=draft_claims,
            profit_bridge_result=profit_bridge_result,
            retrieved_evidence=retrieved_evidence,
            retry_count=retry_count
        )

        report_dict = report.to_dict()

        step_summary = (
            f"Audit finished with verdict: {report.status} (Score: {report.score}/100). "
            f"Issues found: {len(report.issues)}. Retry triggered: {report.retry}."
        )

        self.log_step(
            receiver="AnalystOrchestrator",
            step_name="AuditVerdict",
            content=step_summary,
            metadata=report_dict
        )

        return report_dict
