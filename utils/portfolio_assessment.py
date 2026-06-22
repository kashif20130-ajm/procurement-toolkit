from __future__ import annotations

import pandas as pd

from utils.assessment import build_scoring_model
from utils.assessment import calculate_weighted_score_from_table
from utils.assessment import overall_risk_rating
from utils.assessment_runner import normalize_assessment_result
from utils.assessment_runner import run_assessment
from utils.evidence_mapping import build_evidence_matrix
from utils.evidence_mapping import build_evidence_register
from utils.evidence_mapping import evidence_rationales_from_matrix
from utils.evidence_mapping import evidence_scores_from_matrix
from utils.kpi import build_kpi_table
from utils.radar import PROCUREMENT_RADAR_DIMENSIONS
from utils.radar import build_procurement_radar_table
from utils.rag import references_to_dataframe
from utils.rag import retrieve_scp_references
from utils.sustainability import CLIMATE_MODULE_NAME
from utils.sustainability import ESG_MODULE_NAME
from utils.sustainability import PARENT_MODULE_NAME
from utils.sustainability import build_parent_sustainability_assessment


PROCUREMENT_MODULE = "Procurement Assessment"
CONTRACT_MODULE = "Contract Management Assessment"
FINANCE_MODULE = "Finance Audit Assessment"
PORTFOLIO_MODULES = [PROCUREMENT_MODULE, PARENT_MODULE_NAME, CONTRACT_MODULE, FINANCE_MODULE]
ASSESSMENT_SEQUENCE = [PROCUREMENT_MODULE, ESG_MODULE_NAME, CLIMATE_MODULE_NAME, CONTRACT_MODULE, FINANCE_MODULE]


def run_portfolio_assessment(
    client_profile: dict,
    extracted_documents: list[dict],
    consultant_notes: str,
    knowledge_base: dict,
    force_demo_mode: bool,
    api_key: str | None,
    model: str,
) -> tuple[dict, str]:
    completed = {}
    modes = set()

    for module_name in ASSESSMENT_SEQUENCE:
        context = _module_context(module_name, extracted_documents, consultant_notes, knowledge_base)
        if not context["references"]:
            raise ValueError(
                f"No SCP knowledge-base references were retrieved for {module_name}. "
                "Rebuild the knowledge base and confirm the relevant module folder contains indexed documents."
            )

        result, mode = run_assessment(
            module_name=module_name,
            client_profile=client_profile,
            extracted_documents=extracted_documents,
            consultant_notes=consultant_notes,
            scoring_table=context["scoring_table"],
            evidence_matrix=context["evidence_matrix"],
            evidence_register=context["evidence_register"],
            scp_references=context["references"],
            model_score=context["score"],
            model_risk=context["risk"],
            force_demo_mode=force_demo_mode,
            api_key=api_key,
            model=model,
        )
        assessment = normalize_assessment_result(
            module_name,
            result,
            consultant_notes,
            context["scoring_table"],
            context["evidence_matrix"],
            context["evidence_register"],
            references_to_dataframe(context["references"]),
            context["radar_table"],
            context["kpi_table"],
            context["score"],
            context["risk"],
        )
        assessment["assessment_mode"] = mode
        assessment["extracted_documents"] = extracted_documents
        completed[module_name] = assessment
        modes.add(mode)

    portfolio_mode = "Demo" if "Demo" in modes else "OpenAI"
    sustainability = build_parent_sustainability_assessment(
        completed[ESG_MODULE_NAME],
        completed[CLIMATE_MODULE_NAME],
        portfolio_mode,
    )
    sustainability["extracted_documents"] = extracted_documents

    portfolio = {
        PROCUREMENT_MODULE: completed[PROCUREMENT_MODULE],
        PARENT_MODULE_NAME: sustainability,
        CONTRACT_MODULE: completed[CONTRACT_MODULE],
        FINANCE_MODULE: completed[FINANCE_MODULE],
    }
    return portfolio, portfolio_mode


def _module_context(
    module_name: str,
    extracted_documents: list[dict],
    consultant_notes: str,
    knowledge_base: dict,
) -> dict:
    evidence_matrix = build_evidence_matrix(module_name, extracted_documents)
    evidence_register = build_evidence_register(module_name, extracted_documents)
    evidence_scores = evidence_scores_from_matrix(evidence_matrix)
    evidence_rationales = evidence_rationales_from_matrix(evidence_matrix)
    scoring_table = build_scoring_model(
        module_name,
        evidence_scores,
        evidence_rationales,
        _evidence_details(evidence_matrix),
    )
    score = calculate_weighted_score_from_table(scoring_table)
    risk = overall_risk_rating(score)
    query = " ".join(
        [
            consultant_notes,
            scoring_table.to_string(index=False),
            evidence_matrix.to_string(index=False),
            evidence_register.to_string(index=False),
        ]
    )
    references = retrieve_scp_references(module_name, query, knowledge_base)
    radar_table = _procurement_radar(scoring_table) if module_name == PROCUREMENT_MODULE else None
    return {
        "evidence_matrix": evidence_matrix,
        "evidence_register": evidence_register,
        "scoring_table": scoring_table,
        "score": score,
        "risk": risk,
        "references": references,
        "radar_table": radar_table,
        "kpi_table": build_kpi_table(module_name),
    }


def _evidence_details(evidence_matrix: pd.DataFrame) -> dict[str, dict]:
    if evidence_matrix.empty:
        return {}
    columns = ["Negative Evidence Found", "Negative Evidence Source", "Score Cap Applied", "Final Score Rationale"]
    details = {}
    for _, row in evidence_matrix.iterrows():
        criterion = str(row.get("Assessment Criteria", ""))
        details[criterion] = {column: row.get(column, "") for column in columns if column in evidence_matrix.columns}
    return details


def _procurement_radar(scoring_table: pd.DataFrame) -> pd.DataFrame:
    criteria_scores = {
        str(row["Assessment Criteria"]): max(1, int(row["Score 0-5"]))
        for _, row in scoring_table.iterrows()
    }
    mapping = {
        "Governance": ["Procurement strategy and operating model", "Procurement policy and procedures"],
        "Strategic Sourcing": ["Strategic sourcing and tender controls"],
        "Supplier Management": ["Supplier due diligence and onboarding", "Supplier performance management"],
        "Contract Management": ["Strategic sourcing and tender controls"],
        "Risk Management": ["Procurement risk and compliance monitoring"],
        "Category Management": ["Category management"],
        "Analytics": ["Spend visibility and analytics"],
        "Digitalization": ["Procurement technology and automation"],
        "ESG Procurement": ["Supplier due diligence and onboarding"],
        "Performance Management": ["Supplier performance management", "Spend visibility and analytics"],
    }
    scores = {}
    for dimension in PROCUREMENT_RADAR_DIMENSIONS:
        values = [criteria_scores[item] for item in mapping.get(dimension, []) if item in criteria_scores]
        scores[dimension] = round(sum(values) / len(values)) if values else 1
    return build_procurement_radar_table(scores)
