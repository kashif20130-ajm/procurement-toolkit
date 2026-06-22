from __future__ import annotations

import pandas as pd


KPI_TARGET_METADATA = {
    "Cost savings %": {"unit": "%", "target_value": 5, "target_direction": "higher_is_better"},
    "PO cycle time": {"unit": "days", "target_value": 5, "target_direction": "lower_is_better"},
    "Spend under contract %": {"unit": "%", "target_value": 80, "target_direction": "higher_is_better"},
    "Supplier on-time delivery %": {"unit": "%", "target_value": 95, "target_direction": "higher_is_better"},
    "Maverick spend %": {"unit": "%", "target_value": 5, "target_direction": "lower_is_better"},
    "Competitive sourcing coverage %": {"unit": "%", "target_value": 70, "target_direction": "higher_is_better"},
    "Supplier evaluation completion %": {"unit": "%", "target_value": 90, "target_direction": "higher_is_better"},
    "Contract renewal compliance %": {"unit": "%", "target_value": 95, "target_direction": "higher_is_better"},
    "Procurement policy compliance %": {"unit": "%", "target_value": 95, "target_direction": "higher_is_better"},
    "Supplier risk review completion %": {"unit": "%", "target_value": 90, "target_direction": "higher_is_better"},
}


KPI_MATURITY_LEVELS = {
    0: "Not Established",
    1: "Defined",
    2: "Measured Occasionally",
    3: "Measured Regularly",
    4: "Managed",
    5: "Optimized",
}


def format_kpi_maturity(score: int) -> str:
    normalized = max(0, min(5, int(score)))
    return f"{normalized} - {KPI_MATURITY_LEVELS[normalized]}"


def kpi_risk_from_maturity(score: int) -> str:
    normalized = max(0, min(5, int(score)))
    return {0: "High", 1: "High", 2: "High", 3: "Medium", 4: "Low", 5: "Low"}[normalized]


KPI_CONFIG = {
    "Procurement Assessment": [
        ("Cost savings %", "Realized savings as a share of addressable spend.", "Savings realized / addressable spend x 100", "Savings tracker, spend reports", "5% or more", "Monthly", "Procurement", "Savings leakage and weak value delivery.", "Track savings pipeline and validate realized benefits."),
        ("PO cycle time", "Average time from approved requisition to issued PO.", "Average PO issue date - requisition approval date", "ERP workflow, PO register", "5 days or less", "Monthly", "Procurement Operations", "Delayed purchasing and stakeholder dissatisfaction.", "Remove approval bottlenecks and automate PO workflows."),
        ("Spend under contract %", "Spend covered by active contracts.", "Contracted spend / total spend x 100", "Spend cube, contract register", "80% or more", "Monthly", "Procurement", "Maverick buying and weaker commercial control.", "Prioritize contract coverage for high-spend categories."),
        ("Supplier on-time delivery %", "Supplier deliveries received on or before committed date.", "On-time deliveries / total deliveries x 100", "GRN, delivery logs, supplier scorecards", "95% or more", "Monthly", "Procurement / Operations", "Operational disruption and expediting costs.", "Use supplier scorecards and corrective action plans."),
        ("Maverick spend %", "Spend outside approved channels or contracts.", "Non-compliant spend / total spend x 100", "Spend analytics, PO compliance report", "5% or less", "Monthly", "Procurement Compliance", "Policy breaches and value leakage.", "Monitor exceptions and enforce buying channels."),
        ("Competitive sourcing coverage %", "Spend sourced through competitive RFQ/RFP.", "Competitively sourced spend / addressable spend x 100", "Sourcing tracker, RFQ/RFP files", "70% or more", "Quarterly", "Strategic Sourcing", "Weak price discovery and audit trail gaps.", "Mandate competitive sourcing thresholds."),
        ("Supplier evaluation completion %", "Active critical suppliers with completed evaluations.", "Evaluated suppliers / critical suppliers x 100", "Supplier assessment records", "90% or more", "Quarterly", "Supplier Management", "Unmanaged supplier risk.", "Complete risk-based supplier assessments."),
        ("Contract renewal compliance %", "Renewals completed before expiry.", "On-time renewals / renewals due x 100", "Contract register", "95% or more", "Monthly", "Contract Owner", "Service gaps or unfavorable rollover terms.", "Set renewal alerts and ownership."),
        ("Procurement policy compliance %", "Transactions complying with policy and approvals.", "Compliant transactions / sampled transactions x 100", "Audit samples, approval logs", "95% or more", "Quarterly", "Procurement Compliance", "Audit findings and control failure.", "Run compliance reviews and training."),
        ("Supplier risk review completion %", "High-risk suppliers reviewed within schedule.", "Reviewed high-risk suppliers / high-risk suppliers x 100", "Risk register, review logs", "90% or more", "Quarterly", "Risk / Procurement", "Unmitigated supplier risk.", "Schedule supplier risk reviews."),
    ],
    "ESG Assessment": [
        ("ESG policy coverage", "Business units covered by ESG policies.", "Covered units / total units x 100", "ESG policy register", "100%", "Annually", "ESG Lead", "Inconsistent ESG practices.", "Publish and cascade ESG policies."),
        ("Supplier ESG screening %", "Priority suppliers screened for ESG risk.", "Screened suppliers / priority suppliers x 100", "Supplier ESG questionnaires", "90% or more", "Quarterly", "Procurement / ESG", "Supply chain ESG exposure.", "Embed ESG screening in onboarding."),
        ("Waste reduction %", "Reduction in waste against baseline.", "(Baseline waste - current waste) / baseline x 100", "Waste records", "5% annual reduction", "Quarterly", "Operations", "Higher environmental impact and cost.", "Implement waste reduction initiatives."),
        ("Energy intensity", "Energy consumed per output or revenue.", "Energy consumption / output or revenue", "Utility bills, production data", "Year-on-year reduction", "Monthly", "Facilities", "Higher emissions and energy cost.", "Track energy hotspots and efficiency projects."),
        ("ESG training completion %", "Employees completing ESG training.", "Completed employees / assigned employees x 100", "Training records", "95% or more", "Quarterly", "HR / ESG", "Low awareness and inconsistent execution.", "Assign mandatory ESG training."),
        ("GHG data completeness %", "Required emissions data points collected.", "Completed data points / required data points x 100", "GHG data templates", "95% or more", "Quarterly", "Sustainability", "Incomplete emissions inventory.", "Assign data owners and due dates."),
        ("ESG action closure %", "ESG roadmap actions closed on time.", "Closed on-time actions / due actions x 100", "ESG action plan", "90% or more", "Monthly", "ESG PMO", "Delayed ESG progress.", "Track action owners and escalations."),
        ("Incident reporting rate", "ESG incidents reported and investigated.", "Reported incidents investigated / reported incidents x 100", "Incident register", "100%", "Monthly", "Compliance", "Unresolved ESG incidents.", "Standardize incident reporting workflow."),
        ("Board ESG agenda frequency", "Board or executive ESG reviews held.", "ESG meetings held / planned meetings x 100", "Meeting minutes", "100%", "Quarterly", "Company Secretary / ESG", "Weak governance oversight.", "Schedule recurring ESG governance reviews."),
        ("ESG disclosure readiness %", "Required disclosure items prepared.", "Prepared disclosures / required disclosures x 100", "Disclosure checklist", "95% or more", "Annually", "ESG Reporting", "Poor reporting readiness.", "Maintain disclosure calendar and evidence."),
    ],
    "UAE Climate Law Compliance Assessment": [
        ("Scope 1 emissions tracked", "Scope 1 sources measured and recorded.", "Tracked Scope 1 sources / applicable Scope 1 sources x 100", "GHG inventory", "100%", "Quarterly", "Sustainability", "Incomplete climate inventory.", "Identify and assign Scope 1 data owners."),
        ("Scope 2 emissions tracked", "Electricity and purchased energy measured.", "Tracked Scope 2 sources / applicable Scope 2 sources x 100", "Utility bills, GHG workbook", "100%", "Quarterly", "Facilities / Sustainability", "Incomplete emissions reporting.", "Collect utility data monthly."),
        ("Climate reporting completeness", "Required reporting fields completed.", "Completed fields / required fields x 100", "Climate reporting checklist", "95% or more", "Annually", "Compliance", "Regulatory submission gaps.", "Maintain reporting checklist."),
        ("Energy consumption intensity", "Energy use per revenue or activity.", "Energy consumption / revenue or output", "Utility and activity data", "Year-on-year reduction", "Monthly", "Facilities", "Higher emissions exposure.", "Track intensity and reduction projects."),
        ("Carbon reduction initiatives completed", "Planned decarbonization actions completed.", "Completed initiatives / planned initiatives x 100", "Transition plan", "90% or more", "Quarterly", "Sustainability PMO", "Delayed transition plan.", "Track owners, budgets, and milestones."),
        ("Climate obligation register coverage", "Applicable obligations captured in register.", "Captured obligations / applicable obligations x 100", "Obligation register", "100%", "Quarterly", "Compliance", "Missed legal obligations.", "Refresh obligation mapping."),
        ("Climate data owner assignment %", "Data points with accountable owners.", "Assigned data points / required data points x 100", "Data ownership matrix", "100%", "Quarterly", "Sustainability", "Poor data accountability.", "Assign named owners and backups."),
        ("Climate risk assessment completion", "Relevant climate risks assessed.", "Assessed risks / identified risks x 100", "Climate risk register", "90% or more", "Annually", "Risk Management", "Unassessed transition or physical risk.", "Complete climate risk assessment."),
        ("Evidence pack completeness", "Required climate evidence available.", "Available evidence / required evidence x 100", "Evidence library", "95% or more", "Quarterly", "Compliance", "Audit readiness gaps.", "Maintain climate evidence library."),
        ("Climate training completion %", "Assigned staff completing climate training.", "Completed staff / assigned staff x 100", "Training logs", "95% or more", "Annually", "HR / Compliance", "Low awareness of obligations.", "Run role-based climate training."),
    ],
    "Contract Management Assessment": [
        ("Contracts with assigned owners %", "Active contracts with named owner.", "Contracts with owner / active contracts x 100", "Contract register", "100%", "Monthly", "Contract Management", "Unowned obligations and renewals.", "Assign contract owners."),
        ("Contracts renewed before expiry %", "Renewals completed before expiry date.", "On-time renewals / renewals due x 100", "Renewal calendar", "95% or more", "Monthly", "Contract Owners", "Service interruption or auto-renewal risk.", "Use renewal alerts and decision logs."),
        ("Contract leakage %", "Value leakage from missed terms or obligations.", "Leakage value / contract value x 100", "Claims, credits, performance reports", "2% or less", "Quarterly", "Commercial / Legal", "Margin erosion and missed remedies.", "Track obligations and commercial remedies."),
        ("SLA compliance %", "SLA obligations achieved.", "Met SLAs / applicable SLAs x 100", "SLA reports", "95% or more", "Monthly", "Service Owner", "Poor service performance.", "Review SLAs and corrective actions."),
        ("Contract risk reviews completed %", "High-risk contracts reviewed on schedule.", "Reviewed contracts / high-risk contracts x 100", "Risk review log", "90% or more", "Quarterly", "Legal / Risk", "Unmitigated contractual exposure.", "Run scheduled risk reviews."),
        ("Metadata completeness %", "Mandatory contract metadata complete.", "Complete metadata fields / required fields x 100", "CLM or register extract", "95% or more", "Monthly", "Contract Management", "Poor reporting and missed dates.", "Cleanse metadata and set mandatory fields."),
        ("Obligations captured %", "Key obligations recorded in tracker.", "Captured obligations / identified obligations x 100", "Obligation tracker", "95% or more", "Monthly", "Contract Owners", "Missed obligations.", "Extract obligations during contract activation."),
        ("Non-standard clauses reviewed %", "Non-standard terms reviewed by legal.", "Reviewed non-standard clauses / total non-standard clauses x 100", "Clause review log", "100%", "Monthly", "Legal", "Unapproved legal exposure.", "Mandate legal review for deviations."),
        ("Executed contracts stored %", "Signed contracts stored centrally.", "Stored executed contracts / executed contracts x 100", "Repository", "100%", "Monthly", "Contract Admin", "Missing contractual evidence.", "Store final executed copies centrally."),
        ("Contract close-out completion %", "Expired contracts formally closed.", "Closed contracts / expired contracts x 100", "Close-out checklist", "90% or more", "Quarterly", "Contract Owners", "Residual obligations unmanaged.", "Use close-out checklist."),
    ],
    "Finance Audit Assessment": [
        ("Bank reconciliations completed on time %", "Bank reconciliations completed by deadline.", "On-time bank reconciliations / required reconciliations x 100", "Bank reconciliations", "100%", "Monthly", "Finance", "Cash misstatement and unreconciled items.", "Enforce monthly reconciliation timetable."),
        ("AP invoice exception rate", "Supplier invoices with exceptions.", "Exception invoices / total invoices x 100", "AP aging, invoice samples", "5% or less", "Monthly", "Accounts Payable", "Payment errors and duplicate payments.", "Strengthen invoice validation."),
        ("PO-invoice matching rate", "Invoices matched to PO/GRN.", "Matched invoices / PO-backed invoices x 100", "ERP, PO, GRN, invoice samples", "95% or more", "Monthly", "Accounts Payable", "Overpayment or unauthorized spend.", "Enforce three-way matching."),
        ("VAT return accuracy", "VAT returns filed without adjustment.", "Accurate VAT returns / filed VAT returns x 100", "VAT returns, tax workings", "100%", "Quarterly", "Tax / Finance", "Tax penalties and reassessments.", "Review VAT workings before filing."),
        ("Balance sheet reconciliation completion %", "Balance sheet accounts reconciled.", "Completed reconciliations / required reconciliations x 100", "Reconciliation tracker", "100%", "Monthly", "Financial Reporting", "Misstatement risk.", "Track reconciliation owners and review."),
        ("Budget variance review completion %", "Material variances reviewed.", "Reviewed variances / material variances x 100", "Budget reports", "95% or more", "Monthly", "FP&A", "Poor cost control.", "Hold monthly budget reviews."),
        ("DOA compliance %", "Transactions approved per DOA.", "Compliant approvals / sampled approvals x 100", "DOA matrix, approval logs", "95% or more", "Quarterly", "Finance Control", "Unauthorized commitments.", "Test approvals and update DOA."),
        ("AR overdue ratio", "Overdue receivables as share of AR.", "Overdue AR / total AR x 100", "AR aging", "10% or less", "Monthly", "Credit Control", "Cash collection risk.", "Escalate overdue accounts."),
        ("Fixed asset verification completion %", "Assets physically verified.", "Verified assets / asset register items x 100", "Fixed asset register, count sheets", "95% or more", "Annually", "Finance / Operations", "Asset loss or misstatement.", "Run periodic asset verification."),
        ("Internal audit action closure %", "Internal audit actions closed on time.", "Closed on-time actions / due actions x 100", "Internal audit reports, action tracker", "90% or more", "Monthly", "Internal Audit", "Repeat findings and control weakness.", "Track audit actions to closure."),
    ],
}


def _format_target(value: float | int | None, unit: str) -> str:
    if value is None:
        return "Defined target"
    number = int(value) if float(value).is_integer() else round(float(value), 1)
    if unit == "%":
        return f"{number}%"
    if unit:
        return f"{number} {unit}"
    return str(number)


def format_kpi_target(value: float | int | None, unit: str) -> str:
    return _format_target(value, unit)


def _infer_target_metadata(kpi_name: str, target: str) -> dict:
    if kpi_name in KPI_TARGET_METADATA:
        return KPI_TARGET_METADATA[kpi_name].copy()
    target_text = str(target or "")
    lowered = f"{kpi_name} {target_text}".lower()
    unit = "days" if "day" in lowered else "%" if "%" in lowered or " x 100" in lowered else ""
    numeric = pd.to_numeric(
        pd.Series([target_text]).str.extract(r"(\d{1,3}(?:\.\d+)?)", expand=False),
        errors="coerce",
    ).iloc[0]
    lower_terms = ["less", "reduction", "cycle time", "leakage", "exception rate", "intensity", "overdue ratio"]
    return {
        "unit": unit,
        "target_value": None if pd.isna(numeric) else float(numeric),
        "target_direction": "lower_is_better" if any(term in lowered for term in lower_terms) else "higher_is_better",
    }


def build_kpi_table(module_name: str) -> pd.DataFrame:
    rows = []
    for item in KPI_CONFIG.get(module_name, []):
        if len(item) != 9:
            raise ValueError(f"KPI definition for {module_name} must contain 9 fields: {item}")
        metadata = _infer_target_metadata(item[0], item[4])
        target_display = _format_target(metadata["target_value"], metadata["unit"])
        rows.append(
            {
                "KPI Name": item[0],
                "Definition": item[1],
                "Formula": item[2],
                "Data Source": item[3],
                "Unit": metadata["unit"],
                "Target Value": metadata["target_value"],
                "Target Direction": metadata["target_direction"],
                "Target": target_display,
                "Frequency": item[5],
                "Owner": item[6],
                "Risk If Not Measured": item[7],
                "Improvement Action": item[8],
                "Current Value": pd.NA,
                "Current": "Not Established",
                "Current Value Reason": "No KPI framework or KPI-specific evidence was identified in the uploaded documents.",
                "Maturity Score": 0,
                "Maturity": format_kpi_maturity(0),
                "Risk": kpi_risk_from_maturity(0),
                "Status": "Not Established",
                "KPI Score 0-5": pd.NA,
            }
        )
    return pd.DataFrame(rows)


def normalize_kpi_targets(kpi_table: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(kpi_table, pd.DataFrame) or kpi_table.empty:
        return kpi_table
    frame = kpi_table.copy()
    for index, row in frame.iterrows():
        metadata = _infer_target_metadata(str(row.get("KPI Name", "")), str(row.get("Target", "")))
        frame.at[index, "Unit"] = metadata["unit"]
        frame.at[index, "Target Value"] = metadata["target_value"]
        frame.at[index, "Target Direction"] = metadata["target_direction"]
        frame.at[index, "Target"] = _format_target(metadata["target_value"], metadata["unit"])
        current_value = pd.to_numeric(pd.Series([row.get("Current Value")]), errors="coerce").iloc[0]
        if pd.isna(current_value):
            frame.at[index, "Current Value"] = pd.NA
            frame.at[index, "Current"] = "Not Established"
            frame.at[index, "Current Value Reason"] = "No KPI framework or KPI-specific evidence was identified in the uploaded documents."
            frame.at[index, "Maturity Score"] = 0
            frame.at[index, "Maturity"] = format_kpi_maturity(0)
            frame.at[index, "Risk"] = kpi_risk_from_maturity(0)
            frame.at[index, "Status"] = "Not Established"
            frame.at[index, "KPI Score 0-5"] = pd.NA
    return frame


def kpi_portfolio_dataframe(assessments: dict) -> pd.DataFrame:
    frames = []
    for module_name, assessment in assessments.items():
        table = assessment.get("kpi_table")
        if isinstance(table, pd.DataFrame) and not table.empty:
            frame = normalize_kpi_targets(table)
            frame.insert(0, "Module", module_name)
            frames.append(frame)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)
