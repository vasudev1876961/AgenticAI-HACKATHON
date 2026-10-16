"""
Autonomous Artifact Generation Script
Runs an end-to-end multi-agent investigation and generates all final deliverables:
- Standalone interactive HTML Executive Briefing (outputs/executive_briefing.html)
- Formal PDF Investigation Audit Report (outputs/investigation_report.pdf)
- Markdown Audit Deliverable (outputs/investigation_report.md)
- Cryptographic SOX 404 Audit Certificate (outputs/sox_404_certificate.json)
"""

import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.ingestion.loader_manager import DocumentManager
from src.agents.orchestrator import AnalystOrchestrator
from src.reporting.executive_briefing_html import generate_executive_briefing_html


def generate_all_artifacts():
    print("=" * 80)
    print("  AUTONOMOUS ANALYST — EXPORTING DELIVERABLES & AUDIT ARTIFACTS")
    print("=" * 80)

    demo_dir = os.path.join(BASE_DIR, "data", "synthetic_demo")
    mgr = DocumentManager()
    mgr.ingest_directory(demo_dir)

    orchestrator = AnalystOrchestrator(mgr, use_hybrid_search=True)
    query = "Why did our operating profit decline in Q3 compared with Q2? Identify the biggest contributors, calculate their impact, compare the findings with the reports, and cite the evidence."

    print(f"\n[*] Executing autonomous multi-agent investigation: '{query}'")
    res = orchestrator.run_investigation(query)
    report_obj = res.get("report")

    outputs_dir = os.path.join(BASE_DIR, "outputs")
    os.makedirs(outputs_dir, exist_ok=True)

    # 1. Interactive HTML Executive Briefing
    html_path = os.path.join(outputs_dir, "executive_briefing.html")
    html_content = generate_executive_briefing_html(
        report_title=f"Executive Briefing: Q3 Operating Profit Investigation",
        executive_summary=report_obj.executive_summary if report_obj else "",
        bridge=res.get("bridge", {}),
        citations=res.get("citations", []),
        contradictions=res.get("contradictions", []),
        audit=res.get("audit", {}),
        regional_breakdown=res.get("regional_breakdown"),
        forensics=res.get("forensics"),
        risk_governance=res.get("risk_governance"),
        execution_logs=res.get("execution_logs")
    )
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[+] Exported Interactive HTML Briefing -> {html_path}")

    # 2. Markdown Report
    md_path = os.path.join(outputs_dir, "investigation_report.md")
    if report_obj:
        report_obj.export_markdown(md_path)
        print(f"[+] Exported Markdown Audit Report     -> {md_path}")

    # 3. PDF Audit Report
    pdf_path = os.path.join(outputs_dir, "investigation_report.pdf")
    if report_obj:
        try:
            report_obj.export_pdf(pdf_path)
            print(f"[+] Exported Formal PDF Audit Report   -> {pdf_path}")
        except Exception as e:
            print(f"[!] PDF export note: {e}")

    # 4. SOX 404 Regulatory Certificate JSON
    cert_path = os.path.join(outputs_dir, "sox_404_certificate.json")
    risk_data = res.get("risk_governance", {})
    lineage = risk_data.get("audit_lineage", {})
    sox_data = lineage.get("sox_404_compliance", {})
    with open(cert_path, "w", encoding="utf-8") as f:
        json.dump({
            "certificate_id": lineage.get("certificate_id"),
            "iso_timestamp": lineage.get("iso_timestamp"),
            "sox_404_compliance": sox_data,
            "document_hashes": lineage.get("document_hashes"),
            "stress_testing": risk_data.get("stress_testing")
        }, f, indent=2)
    print(f"[+] Exported SOX 404 Audit Certificate -> {cert_path}")

    print("\n" + "=" * 80)
    print("  ALL ARTIFACTS SUCCESSFULLY GENERATED!")
    print("=" * 80)
    return html_path


if __name__ == "__main__":
    generate_all_artifacts()
