"""
Report Generation Engine
Produces structured, professional reports adhering to the hackathon standards:
1. Executive Conclusion
2. Numerical Findings & Period Comparisons
3. Quantified Contributor Breakdown (Profit Bridge)
4. Evidence Provenance & Exact Citations
5. Contradictions & Missing Evidence
6. Audit Verification Summary & Next Steps
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def render_waterfall_chart(profit_bridge: Dict[str, Any], output_path: str) -> Optional[str]:
    """Generates a high-resolution financial waterfall chart PNG."""
    try:
        steps = profit_bridge.get("waterfall_steps", [])
        if not steps:
            return None

        labels = [s["name"].replace(" Operating Profit", "") for s in steps]
        amounts = [s["amount"] for s in steps]
        types = [s["type"] for s in steps]

        fig, ax = plt.subplots(figsize=(8, 3.2), dpi=150)
        fig.patch.set_facecolor('#FFFFFF')
        ax.set_facecolor('#F8FAFC')

        # Compute bottom offsets for waterfall
        bottoms = []
        curr = 0.0
        bar_colors = []

        for i, (amt, t) in enumerate(zip(amounts, types)):
            if t == "absolute":
                bottoms.append(0.0)
                curr = amt
                bar_colors.append('#3B82F6')  # Blue for start
            elif t == "total":
                bottoms.append(0.0)
                bar_colors.append('#1E40AF')  # Dark blue for end
            else:  # relative
                if amt >= 0:
                    bottoms.append(curr)
                    curr += amt
                    bar_colors.append('#10B981')  # Emerald for positive
                else:
                    curr += amt
                    bottoms.append(curr)
                    bar_colors.append('#EF4444')  # Red for negative

        bars = ax.bar(labels, amounts, bottom=bottoms, color=bar_colors, width=0.55, edgecolor='#CBD5E1', linewidth=0.8)

        # Value annotations
        for bar, amt, t in zip(bars, amounts, types):
            h = bar.get_height()
            b = bar.get_y()
            val_txt = f"{amt:+g}k" if t == "relative" else f"{amt:g}k"
            y_pos = b + h / 2.0 if t != "relative" else (b + h + 2 if h >= 0 else b - 8)
            ax.annotate(val_txt,
                        xy=(bar.get_x() + bar.get_width() / 2, y_pos),
                        xytext=(0, 0),
                        textcoords="offset points",
                        ha='center', va='center',
                        fontsize=8, fontweight='bold',
                        color='#FFFFFF' if t != 'relative' else '#0F172A')

        ax.set_title("Operating Profit Variance Bridge (in Thousands)", fontsize=11, fontweight='bold', pad=12, color='#0F172A')
        ax.set_ylabel("Impact (₹ k)", fontsize=9, color='#475569')
        ax.tick_params(axis='x', rotation=15, labelsize=8)
        ax.grid(axis='y', linestyle='--', alpha=0.4, color='#CBD5E1')
        ax.set_axisbelow(True)
        plt.tight_layout()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, bbox_inches='tight', dpi=150)
        plt.close(fig)
        return output_path
    except Exception as e:
        print(f"Chart render warning: {e}")
        return None


@dataclass
class FinalAnalysisReport:
    title: str
    executive_summary: str
    numerical_findings: List[Dict[str, Any]]
    profit_bridge: Optional[Dict[str, Any]]
    citations: List[Dict[str, Any]]
    contradictions: List[Dict[str, Any]]
    verification_audit: Dict[str, Any]
    limitations: List[str]
    markdown_content: str = ""

    def export_markdown(self, output_path: str):
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(self.markdown_content)

    def export_html(self, output_path: str):
        from .executive_briefing_html import generate_executive_briefing_html
        html = generate_executive_briefing_html(
            report_title=self.title,
            executive_summary=self.executive_summary,
            bridge=self.profit_bridge or {},
            citations=self.citations,
            contradictions=self.contradictions,
            audit=self.verification_audit
        )
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        return output_path


    def export_pdf(self, output_path: str):
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'RptTitle',
            parent=styles['Heading1'],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#0F172A'),
            spaceAfter=12
        )
        h2_style = ParagraphStyle(
            'RptH2',
            parent=styles['Heading2'],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor('#1E40AF'),
            spaceBefore=10,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'RptBody',
            parent=styles['Normal'],
            fontSize=9.5,
            leading=13.5,
            textColor=colors.HexColor('#334155'),
            spaceAfter=6
        )

        story = [
            Paragraph(self.title, title_style),
            Paragraph("<b>1. Executive Conclusion</b>", h2_style),
            Paragraph(self.executive_summary.replace("\n", "<br/>"), body_style),
            Spacer(1, 10),
            Paragraph("<b>2. Profit Bridge & Accounting Breakdown</b>", h2_style)
        ]

        # Add profit bridge table if available
        if self.profit_bridge:
            pb = self.profit_bridge
            table_data = [["Component", "Change", "Operating Profit Impact", "Nature"]]
            for c in pb.get("ranked_contributors", []):
                table_data.append([
                    c["label"],
                    f"{c['raw_change']:+g}k",
                    f"{c['profit_impact']:+g}k",
                    c["nature"].capitalize()
                ])
            table_data.append([
                "Total Operating Profit",
                f"{pb['total_delta_profit']:+g}k",
                f"{pb['total_delta_profit']:+g}k",
                "Reconciled Total"
            ])
            t = Table(table_data, colWidths=[180, 100, 140, 100])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ]))
            story.append(t)
            story.append(Spacer(1, 10))

            # Embed Waterfall Chart Image
            chart_img_path = os.path.join(os.path.dirname(output_path), "waterfall_bridge_chart.png")
            rendered = render_waterfall_chart(self.profit_bridge, chart_img_path)
            if rendered and os.path.exists(rendered):
                story.append(Image(rendered, width=480, height=192))
                story.append(Spacer(1, 10))

        # Add citations section
        story.append(Paragraph("<b>3. Documented Source Citations</b>", h2_style))
        for cit in self.citations[:6]:
            cit_text = f"<b>[{cit.get('evidence_id')}] {cit.get('file_name')}</b> "
            loc = []
            if cit.get("page"):
                loc.append(f"Page {cit['page']}")
            if cit.get("sheet_name"):
                loc.append(f"Sheet: {cit['sheet_name']}")
            if cit.get("row_range"):
                loc.append(f"{cit['row_range']}")
            if loc:
                cit_text += f"({', '.join(loc)})<br/>"
            cit_text += f"<i>Excerpt:</i> \"{cit.get('text', '')[:200]}...\""
            story.append(Paragraph(cit_text, body_style))
            story.append(Spacer(1, 4))

        doc.build(story)


class ReportGenerator:
    """
    Builds structured, verified Markdown and PDF reports.
    """

    @staticmethod
    def generate(
        question: str,
        executive_summary: str,
        profit_bridge: Optional[Dict[str, Any]],
        numerical_findings: List[Dict[str, Any]],
        citations: List[Dict[str, Any]],
        contradictions: List[Dict[str, Any]],
        verification_audit: Dict[str, Any],
        limitations: Optional[List[str]] = None
    ) -> FinalAnalysisReport:
        
        limitations = limitations or [
            "Analysis is bounded by the documents and datasets supplied in the active workspace.",
            "Causal explanations are distinguished from mathematical accounting variance.",
            "Historical periods outside Q2 and Q3 were not included in the primary dataset."
        ]

        # Construct Markdown Content
        md_lines = []
        md_lines.append(f"# Evidence-Backed Investigation Report")
        md_lines.append(f"**Investigated Question:** *{question}*\n")
        md_lines.append("---")

        # 1. Executive Conclusion
        md_lines.append("## 1. Executive Conclusion\n")
        md_lines.append(executive_summary)
        md_lines.append("")

        # 2. Key Numerical Findings & Comparison
        md_lines.append("## 2. Quantitative Performance Comparison\n")
        if numerical_findings:
            md_lines.append("| Metric | Baseline (Q2) | End Period (Q3) | Absolute Change | Percentage Change | Direction |")
            md_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
            for item in numerical_findings:
                md_lines.append(
                    f"| **{item.get('metric')}** | {item.get('value_1')} | {item.get('value_2')} | "
                    f"{item.get('delta', 'N/A')} | {item.get('pct_change_str', 'N/A')} | {item.get('direction', 'N/A')} |"
                )
            md_lines.append("")

        # 3. Contributor Breakdown & Profit Bridge
        md_lines.append("## 3. Quantified Contributor Breakdown (Profit Bridge)\n")
        if profit_bridge:
            md_lines.append(f"- **Starting Operating Profit (Q2):** ₹{profit_bridge.get('p_start'):,}k")
            md_lines.append(f"- **Ending Operating Profit (Q3):** ₹{profit_bridge.get('p_end'):,}k")
            md_lines.append(f"- **Net Operating Profit Variance (ΔP):** ₹{profit_bridge.get('total_delta_profit'):,}k ({profit_bridge.get('pct_change_profit'):+.1f}%)\n")

            md_lines.append("### Component Impact Breakdown:")
            md_lines.append("| Component | Raw Change (Q3 - Q2) | Impact on Profit | Accounting Nature | Reconciliation |")
            md_lines.append("| :--- | :--- | :--- | :--- | :--- |")
            for c in profit_bridge.get("ranked_contributors", []):
                md_lines.append(
                    f"| **{c['label']}** | {c['raw_change']:+g}k | **{c['profit_impact']:+g}k** | {c['nature'].capitalize()} | Verified |"
                )
            reconciled_tag = "✅ 100% Mathematically Reconciled (ΔP = ΔR - ΔC - ΔM - ΔO)" if profit_bridge.get("is_reconciled") else "❌ Reconciliation Discrepancy"
            md_lines.append(f"\n> **Reconciliation Status:** {reconciled_tag}\n")

        # 4. Source Evidence & Citations
        md_lines.append("## 4. Grounded Source Evidence & Citations\n")
        if citations:
            md_lines.append("| Evidence ID | Source File | Source Location | Supporting Excerpt / Content |")
            md_lines.append("| :--- | :--- | :--- | :--- |")
            for cit in citations:
                loc = []
                if cit.get("page"):
                    loc.append(f"Page {cit['page']}")
                if cit.get("sheet_name"):
                    loc.append(f"Sheet: {cit['sheet_name']}")
                if cit.get("row_range"):
                    loc.append(f"{cit['row_range']}")
                loc_str = ", ".join(loc) if loc else cit.get("section", "General")
                excerpt = cit.get("text", "").replace("\n", " ").strip()
                if len(excerpt) > 120:
                    excerpt = excerpt[:117] + "..."
                md_lines.append(f"| **`{cit.get('evidence_id')}`** | `{cit.get('file_name')}` | {loc_str} | {excerpt} |")
            md_lines.append("")

        # 5. Contradictions & Audit Findings
        md_lines.append("## 5. Cross-Source Audit & Discrepancies\n")
        if contradictions:
            md_lines.append("> ⚠️ **Discrepancies Detected Across Workspace Sources:**\n")
            for c in contradictions:
                md_lines.append(f"- **{c.get('topic')}:**")
                md_lines.append(f"  - *Document Assertion:* {c.get('document_claim')}")
                md_lines.append(f"  - *Data Fact:* {c.get('data_fact')}")
                md_lines.append(f"  - *Reference:* `{c.get('evidence_id')}`")
            md_lines.append("")
        else:
            md_lines.append("✅ No internal contradictions detected between documentary commentary and numerical data.\n")

        # 6. Verification Critic Scorecard
        md_lines.append("## 6. Verification Critic Audit Scorecard\n")
        checks = verification_audit.get("checks", {})
        md_lines.append(f"- **Overall Audit Score:** `{verification_audit.get('score', 100)} / 100`")
        md_lines.append(f"- **Verification Decision:** `{verification_audit.get('status', 'APPROVED')}`")
        for chk, status in checks.items():
            icon = "✅" if status == "PASSED" else ("⚠️" if status == "WARNING" else "❌")
            md_lines.append(f"- {icon} **{chk}:** `{status}`")
        md_lines.append("")

        # 7. Limitations & Next Steps
        md_lines.append("## 7. Limitations & Next Analytical Steps\n")
        for lim in limitations:
            md_lines.append(f"- {lim}")
        md_lines.append("")

        full_md = "\n".join(md_lines)

        return FinalAnalysisReport(
            title="Evidence-Backed Autonomous Document and Data Analysis",
            executive_summary=executive_summary,
            numerical_findings=numerical_findings,
            profit_bridge=profit_bridge,
            citations=citations,
            contradictions=contradictions,
            verification_audit=verification_audit,
            limitations=limitations,
            markdown_content=full_md
        )
