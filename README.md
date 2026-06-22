# AI Company Assessment App

A Streamlit web app for consultants to upload company documents and perform AI-assisted company assessments across procurement, ESG, UAE climate law compliance, contract management, and finance audit.

## Features

- Client profile form
- PDF, Word, Excel, TXT, and Markdown document upload
- Five separate assessment modules
- 10-criterion weighted scoring model for each module
- KPI framework with 10 KPIs per module and traffic-light status
- Evidence mapping matrix for each assessment criterion
- Procurement maturity radar chart with 10 dimensions
- Automatic gap remediation plan with risk, root cause, impact, owner, effort, priority, and target date
- Local RAG knowledge base for SCP toolkit reference documents
- SCP-grounded AI recommendations using retrieved toolkit passages
- OpenAI API assessment generation
- Demo Assessment Mode for local rule-based findings without OpenAI API calls
- Text and table extraction from PDF, DOCX, XLSX, and XLS files
- 0 to 5 criterion scoring with weighted 0 to 100 module score
- Gap analysis table
- Risk register table
- Recommended action plan
- Required evidence list
- Evidence confidence and compliance status
- Executive summary
- Combined Executive Summary export to Word format
- Combined Detailed Assessment Report export to Word format
- KPI dashboard across completed modules

## Folder Structure

```text
.
|-- app.py
|-- knowledge_base/
|   |-- Procurement/
|   |-- ESG/
|   |-- UAE_Climate_Law/
|   |-- Contract_Management/
|   `-- Finance_Audit/
|-- pages/
|   |-- 1_Procurement_Assessment.py
|   |-- 2_ESG_Assessment.py
|   |-- 3_UAE_Climate_Law_Compliance.py
|   |-- 4_Contract_Management_Assessment.py
|   |-- 5_Finance_Audit_Assessment.py
|   |-- 6_Knowledge_Base_Manager.py
|   `-- 7_KPI_Dashboard.py
|-- utils/
|   |-- assessment.py
|   |-- assessment_runner.py
|   |-- dashboard.py
|   |-- demo_assessment.py
|   |-- document_processing.py
|   |-- evidence_mapping.py
|   |-- gap_planning.py
|   |-- kpi.py
|   |-- openai_assessment.py
|   |-- page.py
|   |-- proposal.py
|   |-- radar.py
|   |-- rag.py
|   |-- report.py
|   `-- state.py
|-- requirements.txt
`-- README.md
```

## Local Setup

1. Create and activate a virtual environment.

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Run the app.

```bash
streamlit run app.py
```

## OpenAI Setup

Set your API key as an environment variable:

```bash
set OPENAI_API_KEY=your_api_key_here
```

Or enter the API key in the sidebar of any assessment page. The app does not write the key to project files.

## Demo Assessment Mode

If no OpenAI API key is available, assessment pages automatically run in **Demo Assessment Mode**. You can also turn Demo Mode on from the assessment sidebar to test workflows before incurring API costs.

Demo Mode still runs the local workflow:

- Retrieves SCP standards from the local RAG knowledge base
- Applies the weighted scoring model
- Builds the evidence mapping matrix
- Generates rule-based findings, gaps, actions, required evidence, and executive summary
- Stores results in session state
- Exports the Word assessment report

Demo Mode does not call OpenAI. For production AI-generated narratives, provide an API key and turn Demo Mode off.

## Local SCP Knowledge Base

Place SCP policy and toolkit files in the module folder that matches the assessment area:

- `knowledge_base/Procurement`
- `knowledge_base/ESG`
- `knowledge_base/UAE_Climate_Law`
- `knowledge_base/Contract_Management`
- `knowledge_base/Finance_Audit`

Supported local knowledge base file types:

- DOCX
- PDF
- XLSX
- XLS
- TXT
- MD

On the main page, open **SCP Knowledge Base** and click **Build / Refresh Local Knowledge Base**. During assessment, the app retrieves the relevant module standards and uses them as SCP advisory standards. AI assessment is blocked if no relevant knowledge base content is retrieved, which prevents generic recommendations.

## KPI Framework

Each module includes 10 KPIs with definition, formula, data source, target, frequency, owner, risk if not measured, improvement action, traffic-light status, and KPI score. KPI status is reported separately from the core compliance score and is visible in each module, the main KPI dashboard tab, the KPI Dashboard page, and Word exports.

## Notes

The app extracts readable content and tables from uploaded files, compares client documents against local SCP advisory standards, sends grounded context to OpenAI, and stores module results in Streamlit session state. All completed modules are consolidated into two Word exports: a portfolio-level Combined Executive Summary and a Combined Detailed Assessment Report with an integrated performance grid, cross-functional findings matrix, 30-60-90 day roadmap, and module detail chapters. Legacy `.doc` files should be converted to `.docx` for reliable extraction.

Assessment execution is centralized on the main **Run Assessment** tab. The single **Run Combined Assessment** button evaluates Procurement, Sustainability and Climate Compliance, Contract Management, and Finance Audit. Individual module pages display evidence, scoring, and completed results but do not run or export separate assessments.
