"""
Analyst Orchestrator Agent
The central coordinating agent managing task planning, specialist routing,
the evaluation critic loop, and final presentation.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import time

from .base_agent import BaseAgent, AgentMessage
from .researcher import DocumentResearcherAgent
from .data_analyst import DataAnalystAgent
from .investigator import CrossSourceInvestigatorAgent
from .verifier import VerificationCriticAgent
from .report_writer import ReportWriterAgent
from ..ingestion.loader_manager import DocumentManager
from ..retrieval.search import EvidenceSearchEngine
from ..retrieval.hybrid_search import HybridSearchEngine
from ..reporting.generate_report import FinalAnalysisReport


@dataclass
class InvestigationPlan:
    question: str
    steps: List[str]
    assigned_agents: List[str]
    created_at: float = field(default_factory=time.time)


class AnalystOrchestrator(BaseAgent):
    """
    Agent 1: Analyst Orchestrator
    Entry point for user questions, coordinating the 5 specialist agents through
    a strict evaluation and verification loop.
    """

    def __init__(self, doc_manager: DocumentManager, max_retries: int = 2, use_hybrid_search: bool = True):
        super().__init__(
            name="AnalystOrchestrator",
            role_description="Decomposes research questions, routes sub-tasks to specialist agents, and oversees quality control."
        )
        self.doc_manager = doc_manager
        self.max_retries = max_retries
        self.use_hybrid_search = use_hybrid_search

        if use_hybrid_search:
            self.search_engine = HybridSearchEngine(doc_manager.all_chunks)
        else:
            self.search_engine = EvidenceSearchEngine(doc_manager.all_chunks)

        # Initialize specialists
        self.researcher = DocumentResearcherAgent(doc_manager, self.search_engine)
        self.data_analyst = DataAnalystAgent(doc_manager)
        self.investigator = CrossSourceInvestigatorAgent()
        self.verifier = VerificationCriticAgent(max_retries=max_retries)
        self.verifier.critic_engine.set_evidence_lookup(self.search_engine.evidence_lookup)
        self.report_writer = ReportWriterAgent()

    def update_engine(self):
        """Refreshes search index and critic lookups after new files are ingested."""
        if self.use_hybrid_search:
            self.search_engine = HybridSearchEngine(self.doc_manager.all_chunks)
        else:
            self.search_engine = EvidenceSearchEngine(self.doc_manager.all_chunks)
        self.researcher.search_engine = self.search_engine
        self.verifier.critic_engine.set_evidence_lookup(self.search_engine.evidence_lookup)

    def plan_investigation(self, question: str) -> InvestigationPlan:
        """Decomposes the user's question into structured sub-tasks."""
        steps = [
            "1. Inventory workspace documents and index evidence chunks.",
            "2. Retrieve relevant qualitative and quantitative excerpts from PDFs, spreadsheets, and reports.",
            "3. Execute deterministic Python calculations for Q2 vs Q3 variance and profit bridge.",
            "4. Perform cross-source investigation to reconcile narratives and isolate contradictions.",
            "5. Execute Verification Critic audit loop on calculations, citations, and evidence sufficiency.",
            "6. Compile and deliver final executive cited report."
        ]
        assigned_agents = [
            "DocumentResearcher",
            "DataAnalyst",
            "CrossSourceInvestigator",
            "VerificationCritic",
            "ReportWriter"
        ]
        return InvestigationPlan(
            question=question,
            steps=steps,
            assigned_agents=assigned_agents
        )

    def run_investigation(self, question: str) -> Dict[str, Any]:
        """
        Executes end-to-end investigation with evaluation critic loop.
        """
        start_time = time.time()
        self.update_engine()

        # Step 1: Planning
        plan = self.plan_investigation(question)
        self.log_step(
            receiver="AllSpecialists",
            step_name="TaskPlanning",
            content=f"Created investigation plan with {len(plan.steps)} steps for question: '{question}'",
            metadata={"plan_steps": plan.steps}
        )

        # Step 2: Evidence Retrieval via Document Researcher
        research_out = self.researcher.investigate(query=question, top_k=8)
        retrieved_evidence = research_out["evidence"]

        # Step 3: Structured Data Analysis via Data Analyst
        analysis_out = self.data_analyst.perform_quarterly_analysis(p1_name="Q2", p2_name="Q3")
        bridge_dict = analysis_out["bridge"]
        comparisons = analysis_out["comparisons"]

        # Step 4: Cross-Source Investigation
        investigation_out = self.investigator.investigate_findings(
            numerical_analysis=analysis_out,
            retrieved_evidence=retrieved_evidence
        )
        draft_claims = investigation_out["draft_claims"]
        contradictions = investigation_out["contradictions"]

        # Step 5: Verification Critic Audit & Evaluation Loop
        retry_count = 0
        audit_report = None
        while retry_count <= self.max_retries:
            audit_report = self.verifier.verify(
                draft_claims=draft_claims,
                profit_bridge_result=bridge_dict,
                retrieved_evidence=retrieved_evidence,
                retry_count=retry_count
            )

            if not audit_report.get("retry", False):
                # Passed or warning acceptable
                break

            # Handle remediation if retry triggered
            self.log_step(
                receiver="DataAnalyst/Researcher",
                step_name="CorrectionTriggered",
                content=f"Evaluation loop retry {retry_count + 1}: Resolving issues flagged by Verification Critic.",
                metadata={"issues": audit_report.get("issues", [])}
            )
            retry_count += 1

        # Step 6: Final Report Generation
        final_report: FinalAnalysisReport = self.report_writer.write_report(
            question=question,
            bridge_result=bridge_dict,
            comparisons=comparisons,
            citations=retrieved_evidence[:6],
            contradictions=contradictions,
            verification_audit=audit_report
        )

        elapsed = round(time.time() - start_time, 2)

        # Aggregate all agent telemetry logs in chronological order
        all_logs: List[AgentMessage] = []
        all_logs.extend(self.execution_log)
        all_logs.extend(self.researcher.execution_log)
        all_logs.extend(self.data_analyst.execution_log)
        all_logs.extend(self.investigator.execution_log)
        all_logs.extend(self.verifier.execution_log)
        all_logs.extend(self.report_writer.execution_log)
        all_logs.sort(key=lambda m: m.timestamp)

        return {
            "question": question,
            "elapsed_seconds": elapsed,
            "plan": plan.steps,
            "report": final_report,
            "bridge": bridge_dict,
            "comparisons": comparisons,
            "regional_breakdown": analysis_out.get("regional_breakdown"),
            "citations": retrieved_evidence[:6],
            "contradictions": contradictions,
            "audit": audit_report,
            "execution_logs": [m.to_dict() for m in all_logs]
        }
