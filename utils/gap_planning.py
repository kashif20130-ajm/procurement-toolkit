from __future__ import annotations

from datetime import date
from datetime import timedelta

import pandas as pd


def build_gap_remediation_plan(
    module_name: str,
    compliance_gaps: list[str],
    evidence_matrix: pd.DataFrame,
    scoring_table: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    seen = set()
    seen_criteria = set()

    for gap in compliance_gaps:
        key = _dedupe_key(gap)
        if key in seen:
            continue
        seen.add(key)
        rows.append(_build_row(module_name, gap, "AI identified compliance gap", "High"))

    for _, row in evidence_matrix.iterrows():
        status = row.get("Compliance Status", "")
        cap_applied = str(row.get("Score Cap Applied", "No cap"))
        has_negative_evidence = cap_applied.startswith("Score capped")
        if status not in {"Partially Compliant", "Non-Compliant"} and not has_negative_evidence:
            continue
        if has_negative_evidence:
            gap = f"{row['Assessment Criteria']}: negative evidence detected and {cap_applied.lower()}."
        else:
            gap = f"{row['Assessment Criteria']}: {status.lower()} evidence coverage."
        key = _dedupe_key(gap)
        if key in seen:
            continue
        seen.add(key)
        seen_criteria.add(str(row["Assessment Criteria"]).lower())
        priority = "High" if status == "Non-Compliant" or has_negative_evidence else "Medium"
        root_cause = "Uploaded policy contains negative control language" if has_negative_evidence else "Missing or incomplete required evidence"
        rows.append(_build_row(module_name, gap, root_cause, priority, row))

    for _, row in scoring_table.iterrows():
        score = int(row.get("Score 0-5", 0))
        if score > 2:
            continue
        criterion_key = str(row["Assessment Criteria"]).lower()
        if criterion_key in seen_criteria:
            continue
        gap = f"{row['Assessment Criteria']}: maturity score {score}/5."
        key = _dedupe_key(gap)
        if key in seen:
            continue
        seen.add(key)
        priority = "High" if score <= 1 else "Medium"
        rows.append(_build_row(module_name, gap, "Low maturity against assessment model", priority, row))

    return pd.DataFrame(
        rows,
        columns=[
            "Gap",
            "Risk",
            "Root Cause",
            "Impact",
            "Recommendation",
            "Priority",
            "Estimated Effort",
            "Responsible Function",
            "Target Date",
        ],
    )


def _build_row(
    module_name: str,
    gap: str,
    root_cause: str,
    priority: str,
    source_row: pd.Series | None = None,
) -> dict:
    recommendation = _recommendation(gap, source_row)
    return {
        "Gap": gap,
        "Risk": _risk_statement(module_name, gap, priority),
        "Root Cause": root_cause,
        "Impact": _impact_statement(module_name, gap, priority),
        "Recommendation": recommendation,
        "Priority": priority,
        "Estimated Effort": _estimated_effort(priority),
        "Responsible Function": _responsible_function(module_name, gap),
        "Target Date": _target_date(priority),
    }


def _recommendation(gap: str, source_row: pd.Series | None) -> str:
    if source_row is not None:
        negative_evidence = source_row.get("Negative Evidence Found")
        if isinstance(negative_evidence, str) and negative_evidence.strip() and negative_evidence != "None":
            return (
                "Remove or revise negative control language and replace it with mandatory, documented, "
                "segregated, and reviewable procurement controls. Evidence to address: "
                f"{negative_evidence[:500]}"
            )

        action = source_row.get("Recommended Improvement Action")
        if isinstance(action, str) and action.strip():
            return action

        required_evidence = source_row.get("Required Evidence")
        if isinstance(required_evidence, str) and required_evidence.strip():
            return f"Collect, approve, and maintain evidence for: {required_evidence}"

    return f"Define an owner, remediation steps, evidence requirements, and monitoring cadence for: {gap}"


def _risk_statement(module_name: str, gap: str, priority: str) -> str:
    if priority == "High":
        severity = "material"
    elif priority == "Medium":
        severity = "moderate"
    else:
        severity = "limited"
    return f"{severity.title()} {module_name.lower()} risk due to unresolved gap: {gap}"


def _impact_statement(module_name: str, gap: str, priority: str) -> str:
    if priority == "High":
        return "May lead to control failure, regulatory exposure, audit findings, value leakage, or unmanaged operational risk."
    if priority == "Medium":
        return "May reduce process consistency, evidence quality, management visibility, and readiness for review."
    return "May create minor inefficiency or documentation weakness if not addressed."


def _estimated_effort(priority: str) -> str:
    if priority == "High":
        return "High - 4 to 8 weeks"
    if priority == "Medium":
        return "Medium - 2 to 4 weeks"
    return "Low - 1 to 2 weeks"


def _target_date(priority: str) -> str:
    days = {"High": 30, "Medium": 60, "Low": 90}.get(priority, 60)
    return (date.today() + timedelta(days=days)).isoformat()


def _responsible_function(module_name: str, gap: str) -> str:
    text = f"{module_name} {gap}".lower()
    if "procurement" in text or "supplier" in text or "sourcing" in text or "category" in text:
        return "Procurement"
    if "contract" in text or "clause" in text or "obligation" in text:
        return "Legal / Contract Management"
    if "climate" in text or "emissions" in text or "ghg" in text:
        return "Sustainability / Compliance"
    if "esg" in text or "human rights" in text or "environmental" in text:
        return "ESG / Sustainability"
    if "data" in text or "analytics" in text or "technology" in text or "digital" in text:
        return "IT / Data Analytics"
    if "risk" in text or "audit" in text or "compliance" in text:
        return "Risk / Compliance"
    return "Process Owner"


def _dedupe_key(text: str) -> str:
    return " ".join(text.lower().split())[:120]
