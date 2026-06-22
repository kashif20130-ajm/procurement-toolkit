from __future__ import annotations

import pandas as pd

from utils.assessment import scoring_model_to_context
from utils.demo_assessment import run_demo_assessment
from utils.document_processing import build_document_context
from utils.evidence_mapping import evidence_matrix_to_context
from utils.evidence_mapping import evidence_register_to_context
from utils.gap_planning import build_gap_remediation_plan
from utils.openai_assessment import resolve_openai_api_key
from utils.openai_assessment import run_openai_assessment
from utils.rag import references_to_context
from utils.recommendation_engine import build_compliance_roadmap
from utils.recommendation_engine import build_full_compliance_guidance


def determine_assessment_mode(force_demo_mode: bool, api_key: str | None) -> str:
    if force_demo_mode:
        return "Demo"
    if not resolve_openai_api_key(api_key):
        return "Demo"
    return "OpenAI"


def run_assessment(
    module_name: str,
    client_profile: dict,
    extracted_documents: list[dict],
    consultant_notes: str,
    scoring_table: pd.DataFrame,
    evidence_matrix: pd.DataFrame,
    evidence_register: pd.DataFrame,
    scp_references: list[dict],
    model_score: int,
    model_risk: str,
    force_demo_mode: bool,
    api_key: str | None,
    model: str,
) -> tuple[dict, str]:
    mode = determine_assessment_mode(force_demo_mode, api_key)

    if mode == "Demo":
        return (
            run_demo_assessment(
                module_name=module_name,
                scoring_table=scoring_table,
                evidence_matrix=evidence_matrix,
                scp_references=scp_references,
                model_score=model_score,
                model_risk=model_risk,
            ),
            mode,
        )

    resolved_api_key = resolve_openai_api_key(api_key)
    return (
        run_openai_assessment(
            module_name=module_name,
            client_profile=client_profile,
            document_context=build_document_context(extracted_documents),
            consultant_notes=consultant_notes,
            scoring_model_context=scoring_model_to_context(module_name, scoring_table),
            evidence_mapping_context=evidence_matrix_to_context(evidence_matrix),
            evidence_register_context=evidence_register_to_context(evidence_register),
            scp_reference_context=references_to_context(scp_references),
            api_key=resolved_api_key,
            model=model,
        ),
        mode,
    )


def normalize_assessment_result(
    module_name: str,
    result: dict,
    notes: str,
    scoring_table: pd.DataFrame,
    evidence_matrix: pd.DataFrame,
    evidence_register: pd.DataFrame,
    scp_references: pd.DataFrame,
    radar_table: pd.DataFrame | None,
    kpi_table: pd.DataFrame,
    model_score: int,
    model_risk: str,
) -> dict:
    ai_score = int(result["assessment_score"])
    full_compliance_guidance = build_full_compliance_guidance(
        module_name,
        scoring_table,
        evidence_register,
        kpi_table,
    )
    return {
        "score": model_score,
        "ai_assessment_score": ai_score,
        "status": model_risk,
        "risk_level": model_risk,
        "ai_risk_level": result["risk_level"],
        "key_findings": result["key_findings"],
        "compliance_gaps": result["compliance_gaps"],
        "recommended_actions": result["recommended_actions"],
        "required_evidence": result["required_evidence"],
        "executive_summary": result["executive_summary"],
        "notes": notes,
        "scoring_model": scoring_table,
        "evidence_matrix": evidence_matrix,
        "evidence_register": evidence_register,
        "scp_references": scp_references,
        "procurement_radar": radar_table,
        "kpi_table": kpi_table,
        "gap_remediation_plan": build_gap_remediation_plan(
            module_name=module_name,
            compliance_gaps=result["compliance_gaps"],
            evidence_matrix=evidence_matrix,
            scoring_table=scoring_table,
        ),
        "gap_analysis": pd.DataFrame({"Compliance Gap": result["compliance_gaps"]}),
        "risk_register": pd.DataFrame(
            {
                "Risk Level": [model_risk],
                "AI Risk Level": [result["risk_level"]],
                "Summary": [result["executive_summary"]],
            }
        ),
        "action_plan": pd.DataFrame({"Recommended Action": result["recommended_actions"]}),
        "full_compliance_guidance": full_compliance_guidance,
        "compliance_roadmap": build_compliance_roadmap(full_compliance_guidance),
    }
