# 3-to-5 Minute Presentation & Live Demo Script

**Project Title:** Evidence-First Autonomous Document and Data Analyst  
**Presenter:** Hackathon Team  
**Duration:** ~4–5 Minutes  

---

## Part 1: The Problem (0:00 – 0:45)
- **Speaker:** "Hello judges. In modern enterprise settings, financial intelligence is trapped across dozens of fragmented files: quarterly reports in PDF, multi-tab financial spreadsheets in Excel, and marketing campaign logs in CSV.
- When an executive asks: *'Why did operating profit decline in Q3? Quantify the drivers and cite the evidence,'* conventional LLM chatbots fail. They make arithmetic mistakes, cannot reconcile financial statements, hallucinate page numbers, and blindly trust whatever text they read first.
- We built the **Evidence-First Autonomous Document and Data Analyst**, an enterprise agent network coordinated using **Neuro-SAN** that separates qualitative understanding from deterministic computation."

---

## Part 2: Architecture & Multi-Agent Network (0:45 – 1:30)
- **Speaker:** *(Open Tab: System Architecture on screen)*
- "Our solution coordinates 8 specialist agents:
  1. The **Analyst Orchestrator** creates the plan and directs tasks.
  2. The **Document Researcher** ingests PDFs, spreadsheets, and Word docs using Hybrid RRF search.
  3. The **Data Analyst** uses deterministic Python tools—not LLM arithmetic—to compute variances and profit bridges.
  4. The **Scenario Simulation Agent** evaluates What-If counterfactual decisions and generates sensitivity matrices.
  5. The **Document Forensics Agent** audits non-linear ratio surges and reconciles numbers against Board targets.
  6. The **Cross-Source Investigator** reconciles the data against written commentary.
  7. The **Verification Critic** acts as an independent auditor, enforcing four deterministic checks (Checks A through D).
  8. The **Report Writer** delivers executive presentations, PDF reports, and standalone interactive HTML briefings.
- All agent interactions and tool contracts are configured through Neuro-SAN HOCON specifications."

---

## Part 3: Live Query & Deterministic Calculation (1:30 – 2:30)
- **Speaker:** *(Switch to Tab: Live Investigation on `app.py`, click 'Launch Investigation')*
- "Let's run our core query on our synthetic corporate workspace:
- In seconds, the Orchestrator coordinates the team:
  - The Data Analyst calculates: Q2 Operating profit was **₹150,000**, Q3 fell to **₹70,000**—a net contraction of **-₹80,000** (-53.3%).
  - Look at the **Deterministic Profit Bridge Waterfall Chart**:
    - Lower revenue had an adverse impact of **-₹60,000**.
    - Cost of goods sold declined, providing a positive offset of **+₹15,000**.
    - Marketing expenditure expanded by **+₹25,000**, creating an adverse impact of **-₹25,000**.
    - Other operating expenses created a **-₹10,000** drag.
  - Notice our reconciliation badge: **100% RECONCILED**. Component variances mathematically sum to the exact ₹80,000 variance with 0.00 discrepancy."

---

## Part 4: What-If Simulation Sandbox & Forensics (2:30 – 3:30)
- **Speaker:** *(Switch to Tab: What-If Simulator)*
- "Now, what happens when an executive asks: *'What if we had held marketing flat at Q2 levels?'*
- In traditional RAG, the LLM hallucinates numbers. Here, our **Scenario Simulation Agent** recalculates the bridge:
  - Holding marketing flat at ₹100k recovers **+₹25,000 (31.25% of the drop)**.
  - You can see our **2D Sensitivity Grid** plotting Revenue variance against Marketing spend combinations.
- *(Switch to Tab: Financial Forensics)*
- Next, our **Document Forensics Agent** catches hidden operational anomalies:
  - Operating margin contracted by **-50.3%**.
  - Marketing intensity expanded by **+33.0%** despite top-line decline.
  - Reconciles realized numbers against Board targets in `quarterly_targets.docx`."

---

## Part 5: Deliverables & Verification Critic (3:30 – 4:30)
- **Speaker:** *(Show Download Buttons & Tab: Verification Critic)*
- "Finally, our deliverables:
  1. **Standalone HTML Executive Briefing:** A single, self-contained file with an embedded client-side What-If sandbox and interactive SVG waterfall.
  2. **Enterprise REST API:** A production FastAPI service (`api.py`) with full OpenAPI Swagger documentation at `/docs`.
  3. **Verification Critic Audit:** Checks A, B, C, and D passed with bounded retry defense.
  4. **Automated Testing:** All 42 unit, integration, and API tests pass, and all 12 benchmark evaluation scenarios pass with flying colors.
- Thank you, and we welcome your questions!"
