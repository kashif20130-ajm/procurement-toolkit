from __future__ import annotations

import pandas as pd


def run_demo_assessment(
    module_name: str,
    scoring_table: pd.DataFrame,
    evidence_matrix: pd.DataFrame,
    scp_references: list[dict],
    model_score: int,
    model_risk: str,
) -> dict:
    compliant_count = _count_status(evidence_matrix, "Compliant")
    partial_count = _count_status(evidence_matrix, "Partially Compliant")
    non_compliant_count = _count_status(evidence_matrix, "Non-Compliant")
    low_score_rows = scoring_table[scoring_table["Score 0-5"] <= 2].copy()
    gap_rows = evidence_matrix[evidence_matrix["Compliance Status"] != "Compliant"].copy()

    key_findings = _key_findings(
        module_name,
        model_score,
        model_risk,
        compliant_count,
        partial_count,
        non_compliant_count,
        scp_references,
    )
    compliance_gaps = _compliance_gaps(gap_rows, low_score_rows)
    recommended_actions = _recommended_actions(gap_rows, low_score_rows)
    required_evidence = _required_evidence(gap_rows, scoring_table)

    return {
        "assessment_score": model_score,
        "key_findings": key_findings,
        "compliance_gaps": compliance_gaps,
        "risk_level": model_risk,
        "recommended_actions": recommended_actions,
        "required_evidence": required_evidence,
        "executive_summary": _executive_summary(
            module_name,
            model_score,
            model_risk,
            compliant_count,
            partial_count,
            non_compliant_count,
            len(scp_references),
        ),
    }


def _count_status(evidence_matrix: pd.DataFrame, status: str) -> int:
    if evidence_matrix.empty or "Compliance Status" not in evidence_matrix:
        return 0
    return int((evidence_matrix["Compliance Status"] == status).sum())


def _key_findings(
    module_name: str,
    model_score: int,
    model_risk: str,
    compliant_count: int,
    partial_count: int,
    non_compliant_count: int,
    scp_references: list[dict],
) -> list[str]:
    sources = _source_names(scp_references)
    findings = [
        f"{module_name} rule-based demo assessment generated a weighted score of {model_score}/100 with {model_risk.lower()} model risk.",
        f"Evidence mapping identified {compliant_count} compliant, {partial_count} partially compliant, and {non_compliant_count} non-compliant criteria.",
    ]
    if sources:
        findings.append(f"RAG retrieved SCP reference material from: {', '.join(sources[:4])}.")
    else:
        findings.append("No SCP knowledge base references were available; rebuild the local knowledge base before relying on results.")
    return findings


def _compliance_gaps(gap_rows: pd.DataFrame, low_score_rows: pd.DataFrame) -> list[str]:
    gaps = []
    for _, row in gap_rows.head(8).iterrows():
        cap_applied = str(row.get("Score Cap Applied", "No cap"))
        if cap_applied.startswith("Score capped"):
            gaps.append(f"{row['Assessment Criteria']}: negative evidence detected and {cap_applied.lower()}.")
        else:
            gaps.append(f"{row['Assessment Criteria']}: {str(row['Compliance Status']).lower()} evidence coverage.")
    for _, row in low_score_rows.head(8).iterrows():
        gap = f"{row['Assessment Criteria']}: maturity score {int(row['Score 0-5'])}/5."
        if gap not in gaps:
            gaps.append(gap)
    return gaps or ["No material gaps identified by the rule-based demo assessment."]


def _recommended_actions(gap_rows: pd.DataFrame, low_score_rows: pd.DataFrame) -> list[str]:
    actions = []
    for _, row in gap_rows.head(8).iterrows():
        negative_evidence = row.get("Negative Evidence Found")
        if isinstance(negative_evidence, str) and negative_evidence.strip() and negative_evidence != "None":
            action = (
                "Revise uploaded policy language that weakens procurement controls and replace it with mandatory, "
                f"documented review controls. Negative evidence: {negative_evidence[:400]}"
            )
            if action not in actions:
                actions.append(action)
    for _, row in low_score_rows.head(8).iterrows():
        action = row.get("Recommended Improvement Action")
        if isinstance(action, str) and action and action not in actions:
            actions.append(action)
    for _, row in gap_rows.head(8).iterrows():
        evidence = row.get("Required Evidence")
        action = f"Collect, approve, and retain evidence for: {evidence}"
        if isinstance(evidence, str) and evidence and action not in actions:
            actions.append(action)
    return actions or ["Maintain current controls and continue periodic evidence reviews."]


def _required_evidence(gap_rows: pd.DataFrame, scoring_table: pd.DataFrame) -> list[str]:
    evidence = []
    source = gap_rows if not gap_rows.empty else scoring_table
    for _, row in source.head(10).iterrows():
        item = row.get("Required Evidence") or row.get("Evidence Required")
        if isinstance(item, str) and item and item not in evidence:
            evidence.append(item)
    return evidence or ["No additional evidence required by the rule-based demo assessment."]


def _executive_summary(
    module_name: str,
    model_score: int,
    model_risk: str,
    compliant_count: int,
    partial_count: int,
    non_compliant_count: int,
    reference_count: int,
) -> str:
    return (
        f"Demo Mode completed a local {module_name.lower()} using the scoring model, evidence mapping engine, "
        f"and retrieved SCP knowledge base references without calling OpenAI. The weighted model score is "
        f"{model_score}/100, indicating {model_risk.lower()} risk. The evidence matrix shows {compliant_count} "
        f"compliant criteria, {partial_count} partially compliant criteria, and {non_compliant_count} "
        f"non-compliant criteria. The assessment used {reference_count} retrieved SCP reference passage(s) to "
        "support workflow testing before API costs are incurred."
    )


def _source_names(scp_references: list[dict]) -> list[str]:
    names = []
    for reference in scp_references:
        source = reference.get("Source") or reference.get("source")
        if source and source not in names:
            names.append(source)
    return names
