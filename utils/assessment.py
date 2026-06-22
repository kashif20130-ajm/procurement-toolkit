from __future__ import annotations

import pandas as pd


MODULE_CONFIG = {
    "Procurement Assessment": {
        "model_name": "Procurement maturity",
        "focus": "supplier strategy, sourcing controls, procurement governance, spend visibility, and supplier performance",
        "criteria": [
            {
                "criterion": "Procurement strategy and operating model",
                "weightage": 10,
                "evidence_required": "Approved procurement strategy, operating model, role descriptions, and governance calendar.",
                "improvement_action": "Define a procurement strategy aligned to business priorities with clear ownership and governance cadence.",
            },
            {
                "criterion": "Procurement policy and procedures",
                "weightage": 10,
                "evidence_required": "Current procurement policy, SOPs, delegation of authority, and approval workflow evidence.",
                "improvement_action": "Refresh policies and SOPs, publish approval thresholds, and train process users.",
            },
            {
                "criterion": "Spend visibility and analytics",
                "weightage": 10,
                "evidence_required": "Spend cube, category reports, supplier spend reports, and savings dashboards.",
                "improvement_action": "Create a recurring spend analytics process with category, supplier, and compliance reporting.",
            },
            {
                "criterion": "Category management",
                "weightage": 10,
                "evidence_required": "Category plans, demand forecasts, sourcing calendars, and stakeholder sign-offs.",
                "improvement_action": "Prioritize strategic categories and create category plans with savings, risk, and demand levers.",
            },
            {
                "criterion": "Strategic sourcing and tender controls",
                "weightage": 10,
                "evidence_required": "Tender packs, evaluation matrices, negotiation records, award approvals, and audit trail.",
                "improvement_action": "Standardize sourcing templates, evaluation rules, negotiation logs, and award governance.",
            },
            {
                "criterion": "Supplier due diligence and onboarding",
                "weightage": 10,
                "evidence_required": "Supplier onboarding checklist, KYC documents, sanctions checks, ESG checks, and approval records.",
                "improvement_action": "Implement risk-based supplier onboarding with required due diligence before vendor activation.",
            },
            {
                "criterion": "Purchase-to-pay controls",
                "weightage": 10,
                "evidence_required": "Purchase orders, three-way match records, invoice approvals, exceptions, and payment controls.",
                "improvement_action": "Strengthen no-PO-no-pay controls, approval segregation, and exception monitoring.",
            },
            {
                "criterion": "Supplier performance management",
                "weightage": 10,
                "evidence_required": "Supplier scorecards, SLA/KPI reports, review meeting minutes, and corrective action logs.",
                "improvement_action": "Introduce supplier scorecards and periodic business reviews for strategic and high-risk suppliers.",
            },
            {
                "criterion": "Procurement risk and compliance monitoring",
                "weightage": 10,
                "evidence_required": "Procurement risk register, policy compliance reports, audit findings, and remediation tracking.",
                "improvement_action": "Create compliance dashboards and track procurement risks through an accountable risk register.",
            },
            {
                "criterion": "Procurement technology and automation",
                "weightage": 10,
                "evidence_required": "ERP/e-procurement workflows, system access matrix, automation roadmap, and usage reports.",
                "improvement_action": "Automate requisition, sourcing, approval, contract, and supplier performance workflows where feasible.",
            },
        ],
    },
    "ESG Assessment": {
        "model_name": "ESG readiness",
        "focus": "environmental, social, and governance practices across operations and supply chain",
        "criteria": [
            {
                "criterion": "ESG strategy and materiality",
                "weightage": 10,
                "evidence_required": "ESG strategy, materiality assessment, stakeholder mapping, and board approval.",
                "improvement_action": "Complete a materiality assessment and define measurable ESG priorities linked to business strategy.",
            },
            {
                "criterion": "ESG governance and accountability",
                "weightage": 10,
                "evidence_required": "Committee terms of reference, accountability matrix, ESG KPIs, and meeting minutes.",
                "improvement_action": "Assign ESG governance roles and embed ESG KPIs into management reporting.",
            },
            {
                "criterion": "Environmental management",
                "weightage": 10,
                "evidence_required": "Environmental policy, permits, resource consumption data, waste records, and improvement plans.",
                "improvement_action": "Implement environmental management controls for energy, water, waste, and pollution prevention.",
            },
            {
                "criterion": "GHG emissions measurement",
                "weightage": 10,
                "evidence_required": "Scope 1, Scope 2, and relevant Scope 3 inventory, calculation methodology, and source data.",
                "improvement_action": "Build a verified emissions baseline and define a repeatable data collection process.",
            },
            {
                "criterion": "Social and workforce practices",
                "weightage": 10,
                "evidence_required": "HR policies, workforce metrics, health and safety records, training records, and grievance logs.",
                "improvement_action": "Strengthen labor, health and safety, diversity, training, and grievance management controls.",
            },
            {
                "criterion": "Human rights and supplier ESG",
                "weightage": 10,
                "evidence_required": "Supplier code of conduct, ESG questionnaires, audit reports, and corrective action plans.",
                "improvement_action": "Introduce supplier ESG risk screening and corrective action tracking for priority suppliers.",
            },
            {
                "criterion": "Ethics and anti-corruption",
                "weightage": 10,
                "evidence_required": "Code of conduct, anti-bribery policy, gifts register, whistleblowing records, and training logs.",
                "improvement_action": "Update ethics controls and run periodic anti-corruption and whistleblowing awareness activities.",
            },
            {
                "criterion": "Data quality and ESG controls",
                "weightage": 10,
                "evidence_required": "ESG data owners, source systems, control checks, data definitions, and review sign-offs.",
                "improvement_action": "Create data ownership, control checks, and review procedures for ESG metrics.",
            },
            {
                "criterion": "ESG reporting and disclosure",
                "weightage": 10,
                "evidence_required": "ESG report, disclosure index, framework mapping, and management approvals.",
                "improvement_action": "Map disclosures to a selected framework and prepare a controlled ESG reporting calendar.",
            },
            {
                "criterion": "ESG targets and improvement roadmap",
                "weightage": 10,
                "evidence_required": "ESG targets, action roadmap, budget, owners, and progress reports.",
                "improvement_action": "Set time-bound ESG targets with funded initiatives, owners, and progress tracking.",
            },
        ],
    },
    "UAE Climate Law Compliance Assessment": {
        "model_name": "UAE Climate Law compliance",
        "focus": "climate governance, emissions management, UAE regulatory readiness, and disclosure practices",
        "criteria": [
            {
                "criterion": "Climate governance and accountability",
                "weightage": 10,
                "evidence_required": "Board or executive climate oversight records, accountability matrix, and climate risk agenda.",
                "improvement_action": "Assign climate compliance ownership and include climate matters in governance forums.",
            },
            {
                "criterion": "Applicability and regulatory obligations mapping",
                "weightage": 10,
                "evidence_required": "UAE climate obligation register, applicability assessment, and compliance calendar.",
                "improvement_action": "Create an obligation register covering applicable UAE climate-related laws, rules, and reporting duties.",
            },
            {
                "criterion": "GHG emissions baseline",
                "weightage": 10,
                "evidence_required": "GHG inventory, calculation files, emissions factors, activity data, and organizational boundary.",
                "improvement_action": "Establish a documented GHG baseline with approved boundaries and calculation methodology.",
            },
            {
                "criterion": "Climate data management and controls",
                "weightage": 10,
                "evidence_required": "Data collection templates, source evidence, owner sign-offs, validation checks, and retention rules.",
                "improvement_action": "Implement controlled climate data collection with validation, approval, and document retention.",
            },
            {
                "criterion": "Climate risk and opportunity assessment",
                "weightage": 10,
                "evidence_required": "Physical and transition risk assessment, scenario analysis, and risk register entries.",
                "improvement_action": "Assess climate risks and opportunities and integrate them into enterprise risk management.",
            },
            {
                "criterion": "Emissions reduction targets",
                "weightage": 10,
                "evidence_required": "Reduction targets, baseline year, target boundaries, approval records, and progress tracking.",
                "improvement_action": "Define approved reduction targets aligned to the emissions baseline and business plan.",
            },
            {
                "criterion": "Transition plan and decarbonization initiatives",
                "weightage": 10,
                "evidence_required": "Transition plan, decarbonization projects, capex/opex estimates, owners, and milestones.",
                "improvement_action": "Develop a transition plan with practical initiatives, budgets, timelines, and accountable owners.",
            },
            {
                "criterion": "Climate reporting and disclosure readiness",
                "weightage": 10,
                "evidence_required": "Climate report drafts, disclosure mapping, management approvals, and reporting timetable.",
                "improvement_action": "Prepare reporting templates and disclosure controls for required climate submissions.",
            },
            {
                "criterion": "Assurance and audit readiness",
                "weightage": 10,
                "evidence_required": "Evidence library, audit trail, assurance readiness review, and remediation plan.",
                "improvement_action": "Build an evidence library and remediate data/control gaps before assurance or regulatory review.",
            },
            {
                "criterion": "Training and change management",
                "weightage": 10,
                "evidence_required": "Training materials, attendance logs, role-based guidance, and communications.",
                "improvement_action": "Train data owners, compliance teams, and leadership on UAE climate compliance responsibilities.",
            },
        ],
    },
    "Contract Management Assessment": {
        "model_name": "Contract management maturity",
        "focus": "contract lifecycle governance, obligations, risks, renewals, and performance controls",
        "criteria": [
            {
                "criterion": "Contract management policy and governance",
                "weightage": 10,
                "evidence_required": "Contract policy, governance model, approval matrix, and lifecycle procedure.",
                "improvement_action": "Define contract governance standards, lifecycle controls, and contract owner responsibilities.",
            },
            {
                "criterion": "Contract repository completeness",
                "weightage": 10,
                "evidence_required": "Central repository extract, contract inventory, metadata completeness report, and ownership records.",
                "improvement_action": "Create a complete repository with mandatory metadata and assigned contract owners.",
            },
            {
                "criterion": "Standard templates and clause library",
                "weightage": 10,
                "evidence_required": "Approved templates, fallback clauses, clause playbook, and legal approval records.",
                "improvement_action": "Standardize templates and clause playbooks for common contract types and risk positions.",
            },
            {
                "criterion": "Contract request and drafting process",
                "weightage": 10,
                "evidence_required": "Intake forms, drafting workflow, version history, and legal/business review records.",
                "improvement_action": "Implement structured contract intake, drafting workflow, and version control.",
            },
            {
                "criterion": "Approval and signature controls",
                "weightage": 10,
                "evidence_required": "Approval logs, delegation of authority, signature records, and exception approvals.",
                "improvement_action": "Enforce approval thresholds, authorized signatories, and complete execution evidence.",
            },
            {
                "criterion": "Obligation and deliverable management",
                "weightage": 10,
                "evidence_required": "Obligation register, deliverable tracker, owner assignments, and completion evidence.",
                "improvement_action": "Extract key obligations and assign owners, due dates, and monitoring routines.",
            },
            {
                "criterion": "Renewal, expiry, and termination tracking",
                "weightage": 10,
                "evidence_required": "Renewal calendar, expiry alerts, termination notice requirements, and decision logs.",
                "improvement_action": "Implement automated renewal and expiry alerts with documented renewal decisions.",
            },
            {
                "criterion": "Contract risk review",
                "weightage": 10,
                "evidence_required": "Risk scoring, non-standard terms report, liability exposure summary, and mitigation actions.",
                "improvement_action": "Introduce risk scoring for key contracts and require mitigation for high-risk terms.",
            },
            {
                "criterion": "Supplier/customer performance linkage",
                "weightage": 10,
                "evidence_required": "SLA reports, KPI scorecards, service credits, dispute logs, and performance reviews.",
                "improvement_action": "Link contract obligations to performance reviews and commercial remedies.",
            },
            {
                "criterion": "Contract technology and reporting",
                "weightage": 10,
                "evidence_required": "CLM system workflows, dashboards, access controls, and reporting packs.",
                "improvement_action": "Use CLM reporting to monitor metadata quality, obligations, renewals, and risk exposure.",
            },
        ],
    },
    "Finance Audit Assessment": {
        "model_name": "Finance audit control maturity",
        "focus": "financial governance, transaction controls, reconciliations, tax compliance, reporting, and audit monitoring",
        "criteria": [
            {
                "criterion": "Financial governance and policies",
                "weightage": 10,
                "evidence_required": "Finance policy, accounting manual, financial governance framework, and policy approval evidence.",
                "improvement_action": "Approve and communicate finance policies covering accounting, reporting, close, and control responsibilities.",
            },
            {
                "criterion": "Delegation of authority and approval controls",
                "weightage": 10,
                "evidence_required": "DOA matrix, approval workflow, sampled approvals, and exception reports.",
                "improvement_action": "Update the DOA matrix and test approval compliance for key financial transactions.",
            },
            {
                "criterion": "Budgeting and budgetary control",
                "weightage": 10,
                "evidence_required": "Approved budget, budget variance reports, forecast updates, and management review minutes.",
                "improvement_action": "Implement monthly variance review with accountable owners and corrective actions.",
            },
            {
                "criterion": "Accounts payable controls",
                "weightage": 10,
                "evidence_required": "AP aging, invoice samples, PO-invoice matching, GRN support, and payment approval evidence.",
                "improvement_action": "Strengthen invoice validation, three-way matching, supplier master controls, and payment approval evidence.",
            },
            {
                "criterion": "Accounts receivable controls",
                "weightage": 10,
                "evidence_required": "AR aging, customer statements, collection follow-up records, credit notes, and bad debt review.",
                "improvement_action": "Introduce AR aging reviews, collection escalation, credit control, and bad debt provisioning governance.",
            },
            {
                "criterion": "Bank and cash controls",
                "weightage": 10,
                "evidence_required": "Bank reconciliations, cash count records, bank signatory list, and unreconciled item review.",
                "improvement_action": "Complete monthly bank reconciliations and review aged unreconciled items with segregation of duties.",
            },
            {
                "criterion": "Fixed asset controls",
                "weightage": 10,
                "evidence_required": "Fixed asset register, capitalization policy, asset tagging, physical verification, and disposal approvals.",
                "improvement_action": "Maintain a controlled fixed asset register with periodic verification and approved additions/disposals.",
            },
            {
                "criterion": "Tax/VAT compliance",
                "weightage": 10,
                "evidence_required": "VAT returns, tax workings, VAT reconciliations, tax invoices, and filing/payment evidence.",
                "improvement_action": "Formalize VAT return preparation, review, reconciliation, filing, and evidence retention controls.",
            },
            {
                "criterion": "Financial reporting and reconciliations",
                "weightage": 10,
                "evidence_required": "Trial balance, financial statements, close checklist, balance sheet reconciliations, and review sign-offs.",
                "improvement_action": "Implement a month-end close checklist and reconciliation review process for all material accounts.",
            },
            {
                "criterion": "Internal audit, risk and compliance monitoring",
                "weightage": 10,
                "evidence_required": "Internal audit reports, finance risk register, control testing results, and remediation action tracker.",
                "improvement_action": "Track internal audit findings, test key finance controls, and report remediation progress to management.",
            },
        ],
    },
}


def build_scoring_model(
    module_name: str,
    scores: dict[str, int] | None = None,
    rationales: dict[str, str] | None = None,
    evidence_details: dict[str, dict] | None = None,
) -> pd.DataFrame:
    rows = []
    scores = scores or {}
    rationales = rationales or {}
    evidence_details = evidence_details or {}
    for item in MODULE_CONFIG[module_name]["criteria"]:
        score = int(scores.get(item["criterion"], 0))
        details = evidence_details.get(item["criterion"], {})
        rows.append(
            {
                "Assessment Criteria": item["criterion"],
                "Weightage %": item["weightage"],
                "Score 0-5": score,
                "Evidence Required": item["evidence_required"],
                "Risk Rating": risk_rating_for_score(score),
                "Score Rationale": rationales.get(item["criterion"], "No evidence-based score rationale available."),
                "Negative Evidence Found": details.get("Negative Evidence Found", "None"),
                "Score Cap Applied": details.get("Score Cap Applied", "No cap"),
                "Recommended Improvement Action": item["improvement_action"],
            }
        )
    return pd.DataFrame(rows)


def calculate_weighted_score(module_name: str, scores: dict[str, int]) -> int:
    total = 0.0
    for item in MODULE_CONFIG[module_name]["criteria"]:
        score = int(scores.get(item["criterion"], 0))
        total += (score / 5) * item["weightage"]
    return round(total)


def calculate_weighted_score_from_table(scoring_table: pd.DataFrame) -> int:
    if scoring_table.empty:
        return 0
    total = 0.0
    for _, row in scoring_table.iterrows():
        score = int(row.get("Score 0-5", 0))
        weight = float(row.get("Weightage %", 0))
        total += (score / 5) * weight
    return round(total)


def overall_risk_rating(weighted_score: int) -> str:
    if weighted_score >= 80:
        return "Low"
    if weighted_score >= 60:
        return "Medium"
    if weighted_score >= 25:
        return "High"
    return "Critical"


def risk_rating_for_score(score: int) -> str:
    if score >= 4:
        return "Low"
    if score == 3:
        return "Medium"
    if score == 2:
        return "High"
    return "Critical"


def scoring_model_to_context(module_name: str, scoring_table: pd.DataFrame) -> str:
    model_name = MODULE_CONFIG[module_name]["model_name"]
    return f"{model_name} scoring model:\n{scoring_table.to_string(index=False)}"


def calculate_score(criteria_scores: dict[str, int]) -> int:
    if not criteria_scores:
        return 0
    return round(sum(criteria_scores.values()) / len(criteria_scores))


def score_status(score: int) -> str:
    if score >= 80:
        return "Strong"
    if score >= 60:
        return "Developing"
    if score >= 40:
        return "Needs Improvement"
    return "High Risk"


def build_gap_analysis(module_name: str, criteria_scores: dict[str, int]) -> pd.DataFrame:
    return build_scoring_model(module_name, criteria_scores)[
        ["Assessment Criteria", "Score 0-5", "Risk Rating", "Evidence Required", "Recommended Improvement Action"]
    ]


def build_risk_register(module_name: str, criteria_scores: dict[str, int]) -> pd.DataFrame:
    scoring_model = build_scoring_model(module_name, criteria_scores)
    return scoring_model[["Assessment Criteria", "Risk Rating", "Recommended Improvement Action"]]


def build_action_plan(module_name: str, criteria_scores: dict[str, int]) -> pd.DataFrame:
    scoring_model = build_scoring_model(module_name, criteria_scores)
    return scoring_model.sort_values(["Score 0-5", "Weightage %"], ascending=[True, False])[
        ["Assessment Criteria", "Weightage %", "Risk Rating", "Recommended Improvement Action"]
    ]
