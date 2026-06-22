from __future__ import annotations

import pandas as pd


def build_full_compliance_guidance(
    module_name: str,
    scoring_table: pd.DataFrame,
    evidence_register: pd.DataFrame | None = None,
    kpi_table: pd.DataFrame | None = None,
) -> list[dict]:
    guidance = []
    evidence_register = evidence_register if isinstance(evidence_register, pd.DataFrame) else pd.DataFrame()

    for _, row in scoring_table.iterrows():
        criterion = str(row.get("Assessment Criteria", "Assessment criterion"))
        current_score = int(row.get("Score 0-5", 0))
        required_evidence = str(row.get("Evidence Required", "Documented evidence is required."))
        rationale = str(row.get("Score Rationale", row.get("Final Score Rationale", "")))
        negative_evidence = str(row.get("Negative Evidence Found", "None"))
        score_cap = str(row.get("Score Cap Applied", "No cap"))
        improvement_action = str(row.get("Recommended Improvement Action", ""))
        evidence_refs = _evidence_references_for_criterion(evidence_register, criterion)

        guidance.append(
            {
                "Type": "Assessment Criterion",
                "Title": criterion,
                "Current Score": current_score,
                "Target Score": 5,
                "Improvement": max(0, 5 - current_score),
                "Priority": _priority(current_score, score_cap),
                "Estimated Implementation Time": _implementation_time(current_score),
                "Estimated Maturity Impact": _maturity_impact(current_score),
                "Current State": _current_state(criterion, current_score, rationale, evidence_refs, negative_evidence, score_cap),
                "Gap Identified": _gap_identified(criterion, current_score, required_evidence, negative_evidence, score_cap),
                "Risk Impact": _risk_impact(module_name, criterion),
                "Required Actions": _required_actions(module_name, criterion, improvement_action, required_evidence, negative_evidence),
                "Required Documents": _required_documents(module_name, criterion, required_evidence),
                "Required Controls": _required_controls(module_name, criterion),
                "Evidence Expected": _evidence_expected(criterion, required_evidence),
                "Target State": _target_state(module_name, criterion),
                "Expected Score Improvement": (
                    f"Current Score: {current_score}/5. Target Score: 5/5. "
                    f"Improvement: {max(0, 5 - current_score)} maturity point(s)."
                ),
            }
        )

    if isinstance(kpi_table, pd.DataFrame) and not kpi_table.empty:
        guidance.extend(_build_kpi_guidance(module_name, kpi_table))

    return guidance


def build_compliance_roadmap(full_compliance_guidance: list[dict]) -> pd.DataFrame:
    rows = []
    for item in full_compliance_guidance:
        current_score = int(item.get("Current Score", 0))
        if current_score >= 5:
            continue
        rows.append(
            {
                "Area": item.get("Title", ""),
                "Type": item.get("Type", "Assessment Criterion"),
                "Current Score": current_score,
                "Target Score": item.get("Target Score", 5),
                "Priority": item.get("Priority", "Medium"),
                "Estimated Implementation Time": item.get("Estimated Implementation Time", "3 Months"),
                "Estimated Maturity Impact": item.get("Estimated Maturity Impact", "Managed"),
            }
        )
    return pd.DataFrame(
        rows,
        columns=[
            "Area",
            "Type",
            "Current Score",
            "Target Score",
            "Priority",
            "Estimated Implementation Time",
            "Estimated Maturity Impact",
        ],
    )


def executive_action_summary(full_compliance_guidance: list[dict]) -> dict[str, list[str]]:
    failed_items = [
        item
        for item in full_compliance_guidance
        if int(item.get("Current Score", 0)) < int(item.get("Target Score", 5))
    ]
    ordered = sorted(failed_items, key=lambda item: (_priority_rank(item.get("Priority", "Medium")), int(item.get("Current Score", 0))))

    return {
        "Top 10 Findings": [_short_finding(item) for item in ordered[:10]],
        "Top 10 Recommendations": [_short_recommendation(item) for item in ordered[:10]],
        "Quick Win Actions (30 Days)": [
            _short_recommendation(item)
            for item in ordered
            if item.get("Estimated Implementation Time") == "1 Month"
        ][:10],
        "Medium-Term Actions (90 Days)": [
            _short_recommendation(item)
            for item in ordered
            if item.get("Estimated Implementation Time") == "3 Months"
        ][:10],
        "Strategic Actions (180 Days)": [
            _short_recommendation(item)
            for item in ordered
            if item.get("Estimated Implementation Time") in {"6 Months", "12 Months"}
        ][:10],
    }


def concise_finding_blocks(full_compliance_guidance: list[dict]) -> list[dict]:
    blocks = []
    for item in full_compliance_guidance:
        current_score = int(item.get("Current Score", 0))
        target_score = int(item.get("Target Score", 5))
        if current_score >= target_score:
            continue
        blocks.append(
            {
                "Title": item.get("Title", "Assessment area"),
                "Type": item.get("Type", "Assessment Criterion"),
                "Finding": _limit_words(_short_finding(item), 34),
                "Risk": item.get("Priority", "Medium"),
                "Recommendation": _limit_words(_short_recommendation(item), 75),
                "Required Documents": _top_documents(item.get("Required Documents", "")),
                "Target Score": f"{current_score}/5 -> {target_score}/5",
                "Priority": item.get("Priority", "Medium"),
                "Timeline": item.get("Estimated Implementation Time", "3 Months"),
            }
        )
    return blocks


def _build_kpi_guidance(module_name: str, kpi_table: pd.DataFrame) -> list[dict]:
    guidance = []
    for _, row in kpi_table.iterrows():
        kpi_name = str(row.get("KPI Name", "KPI"))
        raw_score = row.get("KPI Score 0-5", pd.NA)
        current_score = 0 if pd.isna(raw_score) else int(raw_score)
        status = str(row.get("Status", "Not Measured"))
        data_source = str(row.get("Data Source", "Defined source data"))
        target = str(row.get("Target", "Defined target"))
        owner = str(row.get("Owner", "Process owner"))
        formula = str(row.get("Formula", "Defined formula"))
        improvement_action = str(row.get("Improvement Action", "Implement KPI governance and monitoring."))
        risk = str(row.get("Risk If Not Measured", "Management cannot reliably monitor performance."))

        guidance.append(
            {
                "Type": "KPI Framework",
                "Title": kpi_name,
                "Current Score": current_score,
                "Target Score": 5,
                "Improvement": max(0, 5 - current_score),
                "Priority": "High" if status in {"Red", "Not Measured"} else "Medium",
                "Estimated Implementation Time": "3 Months" if status != "Green" else "12 Months",
                "Estimated Maturity Impact": _maturity_impact(current_score),
                "Current State": (
                    f"The KPI is currently recorded with a {status} status and a maturity score of {current_score}/5. "
                    f"The intended data source is {data_source}, the formula is {formula}, and the stated target is {target}."
                ),
                "Gap Identified": (
                    f"The KPI is not yet demonstrated as a fully controlled management measure because ownership, source-data quality, "
                    f"calculation evidence, review cadence, and action tracking must be consistently evidenced by {owner}."
                ),
                "Risk Impact": (
                    f"Operational Risk: Performance issues may not be identified early enough for corrective action. "
                    f"Financial Risk: Weak KPI monitoring may allow value leakage, avoidable cost, or missed savings to continue. "
                    f"Compliance Risk: Management may be unable to evidence that required controls are monitored. "
                    f"Reputational Risk: Poor performance visibility may undermine stakeholder confidence. Specific risk if not measured: {risk}"
                ),
                "Required Actions": (
                    f"The organization should define the KPI owner, calculation method, reporting calendar, source-system owner, "
                    f"thresholds, escalation route, and corrective-action workflow. Management should calculate the KPI at the required "
                    f"frequency, review exceptions, document actions, and report status through the relevant governance forum. {improvement_action}"
                ),
                "Required Documents": (
                    "KPI definition sheet, KPI data collection template, KPI dashboard, exception log, action tracker, "
                    "management review minutes, and evidence pack supporting each reporting cycle."
                ),
                "Required Controls": (
                    "Governance controls should assign KPI ownership and reporting cadence. Approval controls should require management sign-off "
                    "of KPI definitions and results. Monitoring controls should track trends, breaches, and corrective actions. Segregation controls "
                    "should separate data preparation from management review wherever practical."
                ),
                "Evidence Expected": (
                    f"A score of 5/5 would require complete KPI definitions, reliable source data from {data_source}, recurring calculations, "
                    f"documented management review, exception analysis, corrective actions, and evidence that performance is meeting or trending toward {target}."
                ),
                "Target State": (
                    f"The KPI operates as a controlled management measure owned by {owner}, reported at the defined frequency, linked to decisions, "
                    f"and supported by auditable source data and action tracking."
                ),
                "Expected Score Improvement": (
                    f"Current Score: {current_score}/5. Target Score: 5/5. "
                    f"Improvement: {max(0, 5 - current_score)} maturity point(s)."
                ),
            }
        )
    return guidance


def _short_finding(item: dict) -> str:
    title = item.get("Title", "Assessment area")
    current_score = item.get("Current Score", 0)
    current_state = str(item.get("Current State", ""))
    return _limit_words(f"{title}: current maturity is {current_score}/5. {current_state}", 55)


def _short_recommendation(item: dict) -> str:
    title = item.get("Title", "Assessment area")
    recommendation = str(item.get("Required Actions", item.get("Recommendation", "")))
    evidence = str(item.get("Evidence Expected", ""))
    return _limit_words(f"For {title}, {recommendation} Evidence for full compliance should demonstrate {evidence}", 120)


def _priority_rank(priority: str) -> int:
    return {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}.get(str(priority), 2)


def _top_documents(required_documents: str) -> list[str]:
    if not required_documents:
        return ["Approved policy", "Procedure", "Register", "Checklist", "Review log"]
    parts = []
    for raw in required_documents.replace(" and ", ", ").split(","):
        cleaned = raw.strip(" .")
        if cleaned and cleaned not in parts:
            parts.append(cleaned)
        if len(parts) == 5:
            break
    return parts or ["Approved policy", "Procedure", "Register", "Checklist", "Review log"]


def _limit_words(text: str, max_words: int) -> str:
    words = str(text).split()
    if len(words) <= max_words:
        return " ".join(words)
    return " ".join(words[:max_words]).rstrip(" .,;:") + "."


def _current_state(
    criterion: str,
    current_score: int,
    rationale: str,
    evidence_refs: list[str],
    negative_evidence: str,
    score_cap: str,
) -> str:
    refs = "; ".join(evidence_refs[:5]) if evidence_refs else "No uploaded evidence reference was linked to this criterion."
    state = (
        f"The current assessment score for {criterion} is {current_score}/5. "
        f"The assessment evidence indicates: {rationale or 'the required control evidence is incomplete.'} "
        f"Concise evidence references: {refs}."
    )
    if negative_evidence and negative_evidence != "None":
        state += f" Negative evidence was identified and should be remediated. Score cap status: {score_cap}."
    return state


def _gap_identified(
    criterion: str,
    current_score: int,
    required_evidence: str,
    negative_evidence: str,
    score_cap: str,
) -> str:
    if current_score >= 5:
        return (
            f"No material gap was identified for {criterion}. The organization should maintain the control design, "
            f"retain evidence, and continue periodic monitoring against the full evidence standard: {required_evidence}"
        )
    if negative_evidence and negative_evidence != "None":
        return (
            f"The current control design is inadequate because uploaded evidence includes negative control language that weakens or overrides "
            f"expected mandatory controls. The score was constrained by {score_cap}. To reach full compliance, the organization must replace "
            f"optional or non-mandatory wording with enforceable requirements and retain evidence for: {required_evidence}"
        )
    return (
        f"The current control is inadequate because the uploaded evidence does not yet demonstrate a complete, approved, consistently operated, "
        f"and monitored process for {criterion}. Full compliance requires evidence covering: {required_evidence}"
    )


def _risk_impact(module_name: str, criterion: str) -> str:
    domain = _domain_terms(module_name, criterion)
    return (
        f"Operational Risk: Weak {domain} controls may cause inconsistent execution, delays, avoidable exceptions, and poor management visibility. "
        f"Financial Risk: The organization may experience value leakage, unreconciled cost, avoidable penalties, supplier or contract loss, or inefficient resource use. "
        f"Compliance Risk: Management may be unable to demonstrate that required policies, approvals, reporting obligations, and review controls are operating effectively. "
        f"Reputational Risk: Control failures, regulatory gaps, supplier issues, or inaccurate reporting may reduce stakeholder confidence."
    )


def _required_actions(
    module_name: str,
    criterion: str,
    improvement_action: str,
    required_evidence: str,
    negative_evidence: str,
) -> str:
    action = improvement_action.strip() if improvement_action and improvement_action != "nan" else ""
    negative_step = ""
    if negative_evidence and negative_evidence != "None":
        negative_step = (
            "The organization should first remove policy language that states controls are optional, not required, or may be bypassed without review. "
        )
    return (
        f"{negative_step}The organization should appoint an accountable owner for {criterion}, document the end-to-end process, define mandatory control points, "
        f"approve the procedure through the relevant governance forum, and communicate the requirements to all process users. "
        f"The organization should implement templates and registers that capture {required_evidence.lower()} and should require management review before the process is treated as complete. "
        f"Control performance should be monitored through periodic reporting, exception review, and remediation tracking. {action}"
    )


def _required_documents(module_name: str, criterion: str, required_evidence: str) -> str:
    docs = _document_pack(module_name, criterion)
    return f"{docs} The document pack should also include evidence for: {required_evidence}"


def _required_controls(module_name: str, criterion: str) -> str:
    domain = _domain_terms(module_name, criterion)
    return (
        f"Governance controls should assign ownership for {domain}, define review forums, and require periodic status reporting. "
        f"Approval controls should document authority thresholds, approval evidence, and exception handling. "
        f"Monitoring controls should track completion, exceptions, overdue actions, and recurring issues. "
        f"Segregation controls should separate request, preparation, approval, execution, and review responsibilities wherever the process risk justifies it."
    )


def _evidence_expected(criterion: str, required_evidence: str) -> str:
    return (
        f"A 5/5 score would require complete, current, approved, and operating evidence for {criterion}. "
        f"The evidence pack should include policy or procedure approval, completed templates, registers or logs, management review records, "
        f"exception resolution, and retained source documents demonstrating: {required_evidence}"
    )


def _target_state(module_name: str, criterion: str) -> str:
    domain = _domain_terms(module_name, criterion)
    return (
        f"In the target state, {domain} is governed by a documented and approved process, operated consistently by trained owners, "
        f"supported by complete templates and registers, monitored through management reporting, and evidenced through a clear audit trail. "
        f"The process is mature enough that an independent reviewer can confirm design, operation, approval, monitoring, and continuous improvement without relying on verbal explanations."
    )


def _evidence_references_for_criterion(evidence_register: pd.DataFrame, criterion: str) -> list[str]:
    if evidence_register.empty or "Affected Criteria" not in evidence_register:
        return []
    criterion_lower = criterion.lower()
    refs = []
    for _, row in evidence_register.iterrows():
        affected = str(row.get("Affected Criteria", "")).lower()
        if criterion_lower not in affected:
            continue
        evidence_id = str(row.get("Evidence ID", "")).strip()
        source = str(row.get("Source Document", "Unknown document")).strip()
        ref = f"{evidence_id} - {source}" if evidence_id else source
        if ref not in refs:
            refs.append(ref)
    return refs


def _priority(score: int, score_cap: str) -> str:
    if "0 due to negative" in score_cap or score == 0:
        return "Critical"
    if score <= 1:
        return "High"
    if score <= 3:
        return "Medium"
    return "Low"


def _implementation_time(score: int) -> str:
    if score == 0:
        return "1 Month"
    if score <= 1:
        return "3 Months"
    if score <= 3:
        return "6 Months"
    return "12 Months"


def _maturity_impact(score: int) -> str:
    if score <= 1:
        return "Basic"
    if score == 2:
        return "Developing"
    if score == 3:
        return "Managed"
    return "Optimized"


def _domain_terms(module_name: str, criterion: str) -> str:
    text = f"{module_name} {criterion}".lower()
    if "supplier" in text or "procurement" in text or "sourcing" in text:
        return "procurement and supplier management"
    if "contract" in text or "clause" in text or "obligation" in text:
        return "contract management"
    if "climate" in text or "emissions" in text or "ghg" in text:
        return "climate compliance"
    if "esg" in text or "environmental" in text or "human rights" in text:
        return "ESG governance and reporting"
    if "finance" in text or "bank" in text or "vat" in text or "accounts" in text or "budget" in text:
        return "finance control"
    if "kpi" in text:
        return "performance measurement"
    return "process"


def _document_pack(module_name: str, criterion: str) -> str:
    text = f"{module_name} {criterion}".lower()
    if "supplier due diligence" in text or "onboarding" in text:
        return (
            "Supplier Registration Form, Supplier Due Diligence Checklist, Conflict of Interest Declaration, "
            "Supplier Risk Assessment Form, sanctions screening record, ESG questionnaire, and Approved Vendor List."
        )
    if "sourcing" in text or "tender" in text:
        return "Sourcing Procedure, RFQ/RFP templates, evaluation matrix, negotiation log, award recommendation, approval memo, and tender file checklist."
    if "purchase-to-pay" in text or "accounts payable" in text:
        return "Purchase-to-Pay Procedure, purchase order template, GRN log, invoice approval checklist, three-way match report, and exception register."
    if "contract" in text:
        return "Contract Management Policy, contract register, obligation tracker, clause playbook, approval matrix, renewal calendar, and change log."
    if "climate" in text or "emissions" in text or "ghg" in text:
        return "Climate Compliance Procedure, GHG inventory workbook, data collection templates, obligation register, evidence library, and climate risk register."
    if "esg" in text or "environmental" in text or "human rights" in text:
        return "ESG Policy, materiality assessment, ESG data workbook, supplier ESG checklist, disclosure checklist, and ESG action tracker."
    if "finance" in text or "bank" in text or "vat" in text or "accounts" in text or "budget" in text:
        return "Finance Policy, DOA matrix, reconciliation checklist, close checklist, VAT working file, exception log, and management review minutes."
    if "kpi" in text:
        return "KPI Register, KPI definition sheets, dashboard, source-data workbook, exception log, and action tracker."
    return "Approved policy, procedure, template, register, log, checklist, review minutes, and action tracker."
