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
from src.reporting.executive_briefing_html import generate_executive_briefing_html

# Initialize FastAPI App
app = FastAPI(
    title="Evidence-First Autonomous Document and Data Analyst API",
    description="Enterprise Knowledge Agent REST API powered by Neuro-SAN Multi-Agent Network and Deterministic Calculations.",
    version="2.1.0",
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



# Endpoints
@app.get("/", tags=["General"])
def root():
    return {
        "name": "Evidence-First Autonomous Document and Data Analyst API",
        "status": "online",
        "version": "2.1.0",
        "docs": "/docs",
        "theme": "Enterprise Knowledge Agents / Neuro-SAN Multi-Agent Network"
    }


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
        forensics=res.get("forensics")
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
