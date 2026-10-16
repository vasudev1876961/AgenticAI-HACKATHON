"""
Evidence-First Autonomous Document and Data Analyst
Enterprise REST API Server (FastAPI)
Exposes the complete Neuro-SAN Multi-Agent Network, deterministic calculation engine,
forensics suite, and counterfactual simulation sandbox via secure REST endpoints.
"""

import os
import sys
import time
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.ingestion.loader_manager import DocumentManager
from src.agents.orchestrator import AnalystOrchestrator
from src.analysis.counterfactual_simulation import simulate_counterfactual, generate_sensitivity_matrix, rank_recovery_levers
from src.analysis.document_forensics import analyze_financial_forensics
from src.analysis.monte_carlo_simulation import run_monte_carlo_simulation
from src.analysis.dupont_analysis import analyze_dupont_leverage
from src.analysis.data_lineage import generate_audit_lineage
from src.analysis.stress_testing import run_macro_stress_test
from src.reporting.executive_briefing_html import generate_executive_briefing_html

# Initialize FastAPI App
app = FastAPI(
    title="Evidence-First Autonomous Document and Data Analyst API",
    description="Enterprise Knowledge Agent REST API powered by Neuro-SAN Multi-Agent Network and Deterministic Calculations.",
    version="2.2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for enterprise frontend integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State: Ingestion Manager & Orchestrator
doc_manager = DocumentManager()
demo_data_path = os.path.join(BASE_DIR, "data", "synthetic_demo")
if os.path.exists(demo_data_path):
    doc_manager.ingest_directory(demo_data_path)

orchestrator = AnalystOrchestrator(doc_manager, use_hybrid_search=True)


# Request & Response Models
class InvestigationRequest(BaseModel):
    query: str = Field(..., json_schema_extra={"example": "Why did our operating profit decline in Q3 compared with Q2? Quantify contributors."})
    use_hybrid_search: bool = Field(True, description="Enable dense + BM25 Reciprocal Rank Fusion")


class SimulationRequest(BaseModel):
    scenario_name: str = Field("Custom Counterfactual", json_schema_extra={"example": "Flat Marketing Intervention"})
    description: str = Field("", json_schema_extra={"example": "Hold marketing expenditure at Q2 level (100k)"})
    modifications: Dict[str, Any] = Field(..., json_schema_extra={"example": {"marketing": 100.0}})


class MonteCarloRequest(BaseModel):
    iterations: int = Field(2000, ge=100, le=10000, json_schema_extra={"example": 2000})
    target_profit: float = Field(150.0, json_schema_extra={"example": 150.0})
    revenue_volatility: float = Field(0.08, ge=0.0, le=0.5, json_schema_extra={"example": 0.08})
    cogs_inflation_volatility: float = Field(0.04, ge=0.0, le=0.3, json_schema_extra={"example": 0.04})
    marketing_shock_volatility: float = Field(0.12, ge=0.0, le=0.5, json_schema_extra={"example": 0.12})
    fixed_opex_volatility: float = Field(0.03, ge=0.0, le=0.2, json_schema_extra={"example": 0.03})
    random_seed: Optional[int] = Field(42, json_schema_extra={"example": 42})


class StressTestRequest(BaseModel):
    baseline_revenue: float = Field(940.0, json_schema_extra={"example": 940.0})
    baseline_cogs: float = Field(585.0, json_schema_extra={"example": 585.0})
    baseline_marketing: float = Field(125.0, json_schema_extra={"example": 125.0})
    baseline_fixed_opex: float = Field(160.0, json_schema_extra={"example": 160.0})
    initial_cash_reserve: float = Field(300.0, json_schema_extra={"example": 300.0})
    custom_scenarios: Optional[List[Dict[str, Any]]] = None


# Endpoints
@app.get("/", tags=["General"])
def root():
    return {
        "name": "Evidence-First Autonomous Document and Data Analyst API",
        "status": "online",
        "version": "2.3.0",
        "docs": "/docs",
        "dashboard": "/dashboard",
        "report_html": "/api/v1/report/html",
        "theme": "Enterprise Knowledge Agents / Neuro-SAN Multi-Agent Network"
    }


@app.get("/dashboard", response_class=HTMLResponse, tags=["General"])
def get_executive_dashboard(query: str = "Why did our operating profit decline in Q3 compared with Q2?"):
    """Serves the interactive executive briefing dashboard directly at /dashboard."""
    res = orchestrator.run_investigation(query)
    report_obj = res.get("report")
    html = generate_executive_briefing_html(
        report_title=f"Executive Briefing: {query}",
        executive_summary=report_obj.executive_summary if report_obj else "",
        bridge=res.get("bridge", {}),
        citations=res.get("citations", []),
        contradictions=res.get("contradictions", []),
        audit=res.get("audit", {}),
        regional_breakdown=res.get("regional_breakdown"),
        forensics=res.get("forensics"),
        risk_governance=res.get("risk_governance")
    )
    return HTMLResponse(content=html)


@app.get("/health", tags=["General"])
def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "loaded_documents": len(doc_manager.documents),
        "indexed_chunks": len(doc_manager.all_chunks),
        "agents_available": [
            "AnalystOrchestrator",
            "DocumentResearcher",
            "DataAnalyst",
            "CrossSourceInvestigator",
            "VerificationCritic",
            "ScenarioSimulationAgent",
            "DocumentForensicsAgent",
            "RiskGovernanceAgent",
            "ReportWriter"
        ]
    }


@app.get("/api/v1/documents", tags=["Ingestion"])
def list_documents():
    """Returns metadata for all documents currently ingested in the workspace."""
    return {
        "total_documents": len(doc_manager.documents),
        "total_chunks": len(doc_manager.all_chunks),
        "files": doc_manager.list_workspace_files()
    }


@app.post("/api/v1/investigate", tags=["Multi-Agent Pipeline"])
def run_investigation(req: InvestigationRequest):
    """
    Executes an autonomous multi-agent investigation across ingested documents,
    performing deterministic calculations, citation verification, and critic audit loops.
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    if orchestrator.use_hybrid_search != req.use_hybrid_search:
        orchestrator.use_hybrid_search = req.use_hybrid_search
        orchestrator.update_engine()

    result = orchestrator.run_investigation(req.query)
    report_obj = result.get("report")

    return {
        "status": "success",
        "question": result["question"],
        "elapsed_seconds": result["elapsed_seconds"],
        "executive_summary": report_obj.executive_summary if report_obj else "",
        "profit_bridge": result["bridge"],
        "comparisons": result["comparisons"],
        "regional_breakdown": result.get("regional_breakdown"),
        "forensics": result.get("forensics"),
        "contradictions": result["contradictions"],
        "audit": result["audit"],
        "citations": result["citations"],
        "plan": result["plan"],
        "telemetry_count": len(result["execution_logs"])
    }


@app.post("/api/v1/simulate", tags=["Counterfactual Simulation"])
def simulate_scenario(req: SimulationRequest):
    """
    Simulates a counterfactual 'What-If' financial intervention, computing the
    reconciled profit bridge and profit recovery percentage.
    """
    p1_data, p2_data = orchestrator.scenario_simulator._extract_base_periods("Q2", "Q3")
    sim = simulate_counterfactual(
        p1=p1_data,
        p2=p2_data,
        modifications=req.modifications,
        scenario_name=req.scenario_name,
        description=req.description
    )
    return {
        "status": "success",
        "result": sim.to_dict()
    }


@app.get("/api/v1/sensitivity", tags=["Counterfactual Simulation"])
def get_sensitivity_matrix(
    var1: str = Query("revenue", description="First financial variable"),
    var2: str = Query("marketing", description="Second financial variable")
):
    """Generates a 2D sensitivity matrix across two financial drivers."""
    p1_data, p2_data = orchestrator.scenario_simulator._extract_base_periods("Q2", "Q3")
    matrix = generate_sensitivity_matrix(p1_data, p2_data, var1_name=var1, var2_name=var2)
    return {"status": "success", "matrix": matrix}


@app.get("/api/v1/playbooks", tags=["Counterfactual Simulation"])
def get_recovery_playbooks():
    """Ranks standard executive strategic interventions by profit recovery."""
    playbooks = orchestrator.scenario_simulator.evaluate_playbooks("Q2", "Q3")
    return {"status": "success", "playbooks": playbooks}


@app.get("/api/v1/forensics", tags=["Forensics & Anomaly"])
def get_forensics():
    """Runs a full statistical ratio surge and target-vs-actual forensic audit."""
    forensics = orchestrator.forensics_agent.audit("Q2", "Q3")
    return {"status": "success", "forensics": forensics}


@app.post("/api/v1/monte-carlo", tags=["Risk & Governance"])
def run_monte_carlo(req: MonteCarloRequest):
    """
    Executes a stochastic Monte Carlo simulation across financial operational distributions.
    Computes Value-at-Risk (VaR at 95% and 99%), Expected Shortfall (CVaR),
    and probability of achieving board targets.
    """
    p1_data, p2_data = orchestrator.scenario_simulator._extract_base_periods("Q2", "Q3")
    res = run_monte_carlo_simulation(
        base_data=p2_data,
        target_profit=req.target_profit,
        iterations=req.iterations,
        revenue_volatility=req.revenue_volatility,
        cogs_inflation_volatility=req.cogs_inflation_volatility,
        marketing_shock_volatility=req.marketing_shock_volatility,
        fixed_opex_volatility=req.fixed_opex_volatility,
        random_seed=req.random_seed
    )
    return {"status": "success", "result": res.to_dict()}


@app.get("/api/v1/dupont", tags=["Risk & Governance"])
def get_dupont_leverage():
    """
    Computes DuPont Return-on-Sales (ROS) decomposition, Degree of Operating
    Leverage (DOL), Break-Even Revenue, and Margin of Safety.
    """
    p1_data, p2_data = orchestrator.scenario_simulator._extract_base_periods("Q2", "Q3")
    res = analyze_dupont_leverage(p1_data, p2_data)
    return {"status": "success", "result": res.to_dict()}


@app.get("/api/v1/lineage", tags=["Risk & Governance"])
def get_data_lineage():
    """
    Retrieves the complete cryptographic audit lineage DAG (nodes, edges, SHA-256 hashes,
    and Mermaid flowchart) linking raw cells/pages to verified executive claims.
    """
    res = orchestrator.data_analyst.perform_quarterly_analysis("Q2", "Q3")
    lineage = generate_audit_lineage(doc_manager, profit_bridge_result=res.get("bridge"))
    return {"status": "success", "lineage": lineage.to_dict()}


@app.get("/api/v1/compliance", tags=["Risk & Governance"])
def get_sox_compliance():
    """
    Generates the regulatory compliance certification package for SOX Section 404,
    BCBS 239 risk data aggregation, and AICPA SOC 2 Type II auditability.
    """
    res = orchestrator.data_analyst.perform_quarterly_analysis("Q2", "Q3")
    lineage = generate_audit_lineage(doc_manager, profit_bridge_result=res.get("bridge"))
    return {
        "status": "success",
        "certificate_id": lineage.certificate_id,
        "sox_404_certification": lineage.sox_404_compliance
    }


@app.get("/api/v1/stress-test", tags=["Risk & Governance"])
def get_stress_test_report():
    """
    Executes preset macroeconomic stress testing scenarios: Stagflation, CAC Hyper-Inflation,
    Supply Chain Fracture, and Regulatory Overhead, returning solvency status and capital buffer.
    """
    res = run_macro_stress_test()
    return {"status": "success", "result": res.to_dict()}


@app.post("/api/v1/stress-test", tags=["Risk & Governance"])
def post_stress_test(req: StressTestRequest):
    """
    Simulates custom macroeconomic stress scenarios with custom financial baselines.
    """
    res = run_macro_stress_test(
        baseline_revenue=req.baseline_revenue,
        baseline_cogs=req.baseline_cogs,
        baseline_marketing=req.baseline_marketing,
        baseline_fixed_opex=req.baseline_fixed_opex,
        initial_cash_reserve=req.initial_cash_reserve,
        custom_scenarios=req.custom_scenarios
    )
    return {"status": "success", "result": res.to_dict()}


@app.get("/api/v1/report/html", response_class=HTMLResponse, tags=["Reporting"])
def get_html_report(query: str = "Why did operating profit decline in Q3?"):
    """Generates and serves a standalone interactive HTML executive briefing."""
    res = orchestrator.run_investigation(query)
    report_obj = res.get("report")
    html = generate_executive_briefing_html(
        report_title=f"Executive Briefing: {query}",
        executive_summary=report_obj.executive_summary if report_obj else "",
        bridge=res.get("bridge", {}),
        citations=res.get("citations", []),
        contradictions=res.get("contradictions", []),
        audit=res.get("audit", {}),
        regional_breakdown=res.get("regional_breakdown"),
        forensics=res.get("forensics"),
        risk_governance=res.get("risk_governance")
    )
    return HTMLResponse(content=html)


@app.get("/api/v1/report/pdf", tags=["Reporting"])
def get_pdf_report(query: str = "Why did operating profit decline in Q3?"):
    """Compiles and downloads a PDF audit report."""
    res = orchestrator.run_investigation(query)
    report_obj = res.get("report")
    output_pdf = os.path.join(BASE_DIR, "outputs", "api_generated_report.pdf")
    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
    if report_obj:
        report_obj.export_pdf(output_pdf)
        return FileResponse(output_pdf, media_type="application/pdf", filename="investigation_report.pdf")
    raise HTTPException(status_code=500, detail="Failed to compile PDF report.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=False)
