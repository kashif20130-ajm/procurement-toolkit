from __future__ import annotations

import pandas as pd

from utils.assessment import overall_risk_rating
from utils.recommendation_engine import build_compliance_roadmap


PARENT_MODULE_NAME = "Sustainability & Climate Compliance Assessment"
ESG_MODULE_NAME = "ESG Assessment"
CLIMATE_MODULE_NAME = "UAE Climate Law Compliance Assessment"
ESG_WEIGHT = 0.40
CLIMATE_WEIGHT = 0.60


def calculate_combined_sustainability_score(esg_score: int, climate_score: int) -> int:
    return round((int(esg_score) * ESG_WEIGHT) + (int(climate_score) * CLIMATE_WEIGHT))


def build_combined_sustainability_dashboard(esg_assessment: dict, climate_assessment: dict) -> pd.DataFrame:
    esg_score = int(esg_assessment.get("score", 0))
    climate_score = int(climate_assessment.get("score", 0))
    combined_score = calculate_combined_sustainability_score(esg_score, climate_score)
    return pd.DataFrame(
        [
            {
                "Section": "Section A - ESG Governance & Reporting",
                "Weight": "40%",
                "Score": esg_score,
                "Risk Level": esg_assessment.get("risk_level", overall_risk_rating(esg_score)),
            },
            {
                "Section": "Section B - UAE Climate Law Compliance",
                "Weight": "60%",
                "Score": climate_score,
                "Risk Level": climate_assessment.get("risk_level", overall_risk_rating(climate_score)),
            },
            {
                "Section": "Combined Sustainability Score",
                "Weight": "100%",
                "Score": combined_score,
                "Risk Level": overall_risk_rating(combined_score),
            },
        ]
    )


def build_combined_sustainability_kpi_dashboard(esg_assessment: dict, climate_assessment: dict) -> pd.DataFrame:
    frames = []
    for section, assessment in [
        ("ESG Governance & Reporting", esg_assessment),
        ("UAE Climate Law Compliance", climate_assessment),
    ]:
        table = assessment.get("kpi_table")
        if isinstance(table, pd.DataFrame) and not table.empty:
            frame = table.copy()
            frame.insert(0, "Sustainability Section", section)
            frames.append(frame)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def build_parent_sustainability_assessment(esg_assessment: dict, climate_assessment: dict, mode: str) -> dict:
    esg_score = int(esg_assessment.get("score", 0))
    climate_score = int(climate_assessment.get("score", 0))
    combined_score = calculate_combined_sustainability_score(esg_score, climate_score)
    combined_risk = overall_risk_rating(combined_score)
    dashboard = build_combined_sustainability_dashboard(esg_assessment, climate_assessment)
    kpi_dashboard = build_combined_sustainability_kpi_dashboard(esg_assessment, climate_assessment)
    full_compliance_guidance = _combine_guidance(esg_assessment, climate_assessment)

    return {
        "score": combined_score,
        "risk_level": combined_risk,
        "status": combined_risk,
        "assessment_mode": mode,
        "esg_score": esg_score,
        "climate_score": climate_score,
        "esg_assessment": esg_assessment,
        "climate_assessment": climate_assessment,
        "sustainability_dashboard": dashboard,
        "combined_sustainability_kpi_dashboard": kpi_dashboard,
        "executive_summary": (
            f"The combined Sustainability & Climate Compliance Assessment produced a score of "
            f"{combined_score}/100, weighted 40% ESG Governance & Reporting and 60% UAE Climate Law "
            f"Compliance. ESG scored {esg_score}/100 and UAE Climate Law Compliance scored "
            f"{climate_score}/100, resulting in {combined_risk.lower()} combined sustainability risk."
        ),
        "key_findings": [
            f"ESG Governance & Reporting score: {esg_score}/100.",
            f"UAE Climate Law Compliance score: {climate_score}/100.",
            f"Combined weighted sustainability score: {combined_score}/100.",
        ],
        "compliance_gaps": list(esg_assessment.get("compliance_gaps", []))
        + list(climate_assessment.get("compliance_gaps", [])),
        "recommended_actions": list(esg_assessment.get("recommended_actions", []))
        + list(climate_assessment.get("recommended_actions", [])),
        "required_evidence": list(esg_assessment.get("required_evidence", []))
        + list(climate_assessment.get("required_evidence", [])),
        "gap_analysis": _combine_tables(esg_assessment, climate_assessment, "gap_analysis"),
        "risk_register": _combine_tables(esg_assessment, climate_assessment, "risk_register"),
        "action_plan": _combine_tables(esg_assessment, climate_assessment, "action_plan"),
        "evidence_register": _combine_evidence_registers(esg_assessment, climate_assessment),
        "evidence_matrix": _combine_tables(esg_assessment, climate_assessment, "evidence_matrix"),
        "full_compliance_guidance": full_compliance_guidance,
        "compliance_roadmap": build_compliance_roadmap(full_compliance_guidance),
        "gap_remediation_plan": _combine_tables(esg_assessment, climate_assessment, "gap_remediation_plan"),
    }


def _combine_tables(esg_assessment: dict, climate_assessment: dict, key: str) -> pd.DataFrame:
    frames = []
    for section, assessment in [
        ("ESG Governance & Reporting", esg_assessment),
        ("UAE Climate Law Compliance", climate_assessment),
    ]:
        table = assessment.get(key)
        if isinstance(table, pd.DataFrame) and not table.empty:
            frame = table.copy()
            frame.insert(0, "Sustainability Section", section)
            frames.append(frame)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def _combine_evidence_registers(esg_assessment: dict, climate_assessment: dict) -> pd.DataFrame:
    evidence_items = {}
    for section, assessment in [
        ("ESG Governance & Reporting", esg_assessment),
        ("UAE Climate Law Compliance", climate_assessment),
    ]:
        table = assessment.get("evidence_register")
        if not isinstance(table, pd.DataFrame) or table.empty:
            continue
        for _, row in table.iterrows():
            source = str(row.get("Source Document", "Unknown document"))
            extract = str(row.get("Extract", ""))
            if not extract:
                continue
            key = (source.lower(), " ".join(extract.lower().split()))
            if key not in evidence_items:
                evidence_items[key] = {
                    "Source Document": source,
                    "Extract": extract,
                    "Affected Criteria": set(),
                }
            criteria = str(row.get("Affected Criteria", ""))
            for criterion in [item.strip() for item in criteria.split(";") if item.strip()]:
                evidence_items[key]["Affected Criteria"].add(f"{section}: {criterion}")

    rows = []
    for index, item in enumerate(evidence_items.values(), start=1):
        rows.append(
            {
                "Evidence ID": f"EV-{index:03d}",
                "Source Document": item["Source Document"],
                "Extract": item["Extract"],
                "Affected Criteria": "; ".join(sorted(item["Affected Criteria"])),
            }
        )
    return pd.DataFrame(rows, columns=["Evidence ID", "Source Document", "Extract", "Affected Criteria"])


def _combine_guidance(esg_assessment: dict, climate_assessment: dict) -> list[dict]:
    combined = []
    for section, assessment in [
        ("ESG Governance & Reporting", esg_assessment),
        ("UAE Climate Law Compliance", climate_assessment),
    ]:
        for item in assessment.get("full_compliance_guidance", []):
            copied = dict(item)
            copied["Title"] = f"{section}: {copied.get('Title', 'Assessment area')}"
            combined.append(copied)
    return combined
