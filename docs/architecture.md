# System Architecture: Evidence-First Autonomous Document and Data Analyst

## 1. Architectural Philosophy
Generic document chatbots rely on generative LLMs to perform both information retrieval and arithmetic calculation. This introduces critical flaws:
1. **Mathematical Hallucination**: LLMs frequently make calculation errors when comparing financial periods or aggregating expenses.
2. **Citation Dissociation**: Chatbots generate plausible narratives that blend facts with unverified causal claims without preserving exact source provenance.
3. **Inability to Test Counterfactuals**: Chatbots cannot answer executive "What-If" questions with verified accounting guarantees.
4. **No Downside Risk & Leverage Modeling**: Chatbots cannot model stochastic uncertainty, Degree of Operating Leverage (DOL), or provide regulatory audit certification (SOX 404 / BCBS 239).

Our **Evidence-First Autonomous Document and Data Analyst** decouples qualitative understanding from deterministic computation, orchestrating 9 specialist agents coordinated via the **Neuro-SAN** framework:

```mermaid
graph TD
    User([User / Executive / REST Client]) --> Orchestrator[1. Analyst Orchestrator Agent]
    
    subgraph Multi-Agent Network [Neuro-SAN Multi-Agent Network]
        Orchestrator --> Researcher[2. Document Researcher Agent]
        Orchestrator --> Analyst[3. Data Analyst Agent]
        Orchestrator --> ScenarioAgent[4. Scenario Simulation Agent]
        Orchestrator --> ForensicsAgent[5. Document Forensics Agent]
        Orchestrator --> RiskAgent[6. Risk & Governance Agent]
        Researcher --> Investigator[7. Cross-Source Investigator Agent]
        Analyst --> Investigator
        Investigator --> Critic[8. Verification Critic Agent]
        Critic -- "APPROVED" --> Writer[9. Report Writer Agent]
        Critic -- "NEEDS_CORRECTION (Retry <= 2)" --> Orchestrator
    end
    
    subgraph Deterministic Coded Tools [Python Deterministic Coded Tools]
        Researcher --> IngestTool[IngestionTool: PyMuPDF / OpenPyXL / Docx]
        Researcher --> SearchTool[RetrievalTool: Hybrid BM25 + Dense RRF]
        Analyst --> SheetTool[SpreadsheetTool: OpenPyXL / Pandas Schema]
        Analyst --> CalcTool[CalculationTool: Deterministic Profit Bridge]
        ScenarioAgent --> SimTool[SimulationTool: Counterfactual & Sensitivity]
        ForensicsAgent --> ForensicsTool[ForensicsTool: Ratio Surge & Target Gap]
        RiskAgent --> MonteCarloTool[MonteCarloTool: Stochastic VaR 95/99]
        RiskAgent --> RiskGovTool[RiskGovernanceTool: DOL & Lineage DAG]
        Critic --> VerifyTool[VerificationTool: Checks A, B, C, D]
    end

    Writer --> FinalReport([Cited Executive Report, Waterfall Chart, HTML Voice Briefing & SOX Certificate])
```

---

## 2. Agent Responsibilities & Contracts

| Agent | Responsibility | Inputs | Outputs | Primary Tool Bindings |
| :--- | :--- | :--- | :--- | :--- |
| **1. Analyst Orchestrator** | Plans investigation, decomposes queries, routes sub-tasks, enforces retry limit | User question + Workspace Inventory | Investigation Plan & Specialist Routing | Agent invocation registry |
| **2. Document Researcher** | Searches textual documents, extracts grounded excerpts via Hybrid RRF | Question + File indexes | Evidence records with exact citations | `RetrievalTool`, `IngestionTool` |
| **3. Data Analyst** | Analyzes spreadsheets and computes deterministic variances | Financial metrics + Spreadsheet data | Reconciled profit bridge + Period deltas | `CalculationTool`, `SpreadsheetTool` |
| **4. Scenario Simulation Agent** | Evaluates What-If interventions, calculates profit recovery & sensitivity matrices | Baseline financials + Modifications | Reconciled counterfactual bridges + Recovery % | `SimulationTool` |
| **5. Document Forensics Agent** | Audits non-linear ratio surges, cost elasticity, and board target gaps | Multi-source datasets | Anomaly scorecard + Target reconciliation | `ForensicsTool` |
| **6. Risk & Governance Agent** | Simulates Monte Carlo VaR, DuPont operating leverage & SOX audit certification | Multi-period financials | Value-at-Risk, DOL (8.89x), Lineage DAG | `MonteCarloTool`, `RiskGovernanceTool` |
| **7. Cross-Source Investigator** | Reconciles numbers against written reports; isolates contradictions | Numerical metrics + Document excerpts | Classified findings (Facts vs Causal claims) | Cross-referencing logic |
| **8. Verification Critic** | Audits findings across Checks A–D, triggers bounded retries | Draft claims + Calculation results | Audit scorecard (`APPROVED` / `NEEDS_CORRECTION`) | `VerificationTool` |
| **9. Report Writer** | Formats final executive presentation from verified findings only | Verified findings + Audit report | Executive summary, tables, HTML/PDF reports | `ReportGenerator`, `ExecutiveBriefingHTML` |

---

## 3. Data Flow & Provenance Lifecycle

### Step 1: Ingestion & Provenance Tagging (`src/ingestion/`)
- Multi-format loader ingests PDF, XLSX, CSV, and DOCX files.
- Each extracted item receives a deterministic `evidence_id` (e.g. `EV-001`, `EV-002`) and preserves exact provenance metadata:
  - **PDF**: File name, page number, section header, text snippet.
  - **Excel**: File name, sheet name, row index, column headers, cell range, structured key-value pairs.
  - **CSV**: File name, row index, headers, structured data.
  - **DOCX**: File name, paragraph ID, section title, text.

### Step 2: Hybrid Search & Retrieval Indexing (`src/retrieval/`)
- Employs **Reciprocal Rank Fusion (RRF)** combining dense semantic vectors and `BM25Okapi` keyword matching.
- Preserves exact source location pointers across all retrieved chunks.

### Step 3: Deterministic Financial Analysis, Leverage & Risk (`src/analysis/`)
- Pure Python formulas guarantee 100% mathematical accuracy:
  $$P = R - C - M - O$$
  $$\Delta P = \Delta R - \Delta C - \Delta M - \Delta O$$
- Component impacts:
  - $\text{Impact}(R) = R_{\text{Q3}} - R_{\text{Q2}} = -60\text{k}$
  - $\text{Impact}(C) = -(C_{\text{Q3}} - C_{\text{Q2}}) = +15\text{k}$
  - $\text{Impact}(M) = -(M_{\text{Q3}} - M_{\text{Q2}}) = -25\text{k}$
  - $\text{Impact}(O) = -(O_{\text{Q3}} - O_{\text{Q2}}) = -10\text{k}$
  - Sum of Impacts $\equiv \Delta P = -80\text{k}$ ($100\%$ reconciled, $0.00$ discrepancy).
- **Counterfactual Engine**: Evaluates hypothetical management interventions and computes profit recovery deltas.
- **Monte Carlo Stochastic Risk Engine**: Runs 2,000 trials modeling operational uncertainty and calculating Value-at-Risk ($\text{VaR}_{95\%}$ & $\text{VaR}_{99\%}$) and Expected Shortfall ($\text{CVaR}_{95\%}$).
- **DuPont Operating Leverage Engine**: Calculates Degree of Operating Leverage ($\text{DOL} = 8.89\text{x}$) and Break-Even Revenue ($₹835.7\text{k}$).
- **Cryptographic Lineage DAG**: Generates SHA-256 hashes for all ingested files and certifies **SOX Section 404** / **BCBS 239** compliance.

### Step 4: Verification Critic Audit Loop (`src/verification/`)
Every draft claim passes four strict audit checks:
- **Check A (Numerical Reconciliation)**: Verifies that component variances sum exactly to $\Delta P$. Rejects claims where narrative contradicts calculation.
- **Check B (Citation Validity)**: Verifies that every cited `evidence_id` exists in the evidence store and supports the assertion.
- **Check C (Cross-Source Consistency)**: Scans for conflicts between textual claims (e.g., "marketing expenditure was reduced") and accounting records (e.g., marketing increased by +25k).
- **Check D (Evidence Sufficiency & Prompt Injection Defense)**: Identifies adversarial directives inside document text and flags unsupported causal statements.
- **Bounded Evaluation Loop**: If a critical issue is identified, the Critic returns remediation instructions and triggers a re-analysis (strictly capped at 2 retries).

---

## 4. Neuro-SAN Framework Integration
- **HOCON Manifest** (`registries/manifest.hocon`): Declares the agent network, entry agents, and metadata tags.
- **Network Configuration** (`registries/document_analyst.hocon`): Declares 9 agent roles, parent-child hierarchies, tool classes, and model parameters.
- **Coded Tools** (`coded_tools/document_analyst/`): Implements Python tool classes connected to the agents according to the Neuro-SAN specification (`SimulationTool`, `ForensicsTool`, `MonteCarloTool`, `RiskGovernanceTool`, `CalculationTool`, `RetrievalTool`, `IngestionTool`, `SpreadsheetTool`, `VerificationTool`).
