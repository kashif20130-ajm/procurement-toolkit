import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from utils.assessment import MODULE_CONFIG
from utils.assessment import build_scoring_model
from utils.assessment import calculate_weighted_score_from_table
from utils.assessment import overall_risk_rating
from utils.evidence_mapping import build_evidence_matrix
from utils.evidence_mapping import build_evidence_register
from utils.evidence_mapping import build_procurement_evidence_detail_table
from utils.evidence_mapping import evidence_rationales_from_matrix
from utils.evidence_mapping import evidence_scores_from_matrix
from utils.gap_planning import build_gap_remediation_plan
from utils.kpi import build_kpi_table
from utils.radar import PROCUREMENT_RADAR_DIMENSIONS
from utils.radar import build_procurement_radar_svg
from utils.radar import build_procurement_radar_table
from utils.rag import references_to_dataframe
from utils.rag import retrieve_scp_references
from utils.recommendation_engine import build_compliance_roadmap
from utils.recommendation_engine import build_full_compliance_guidance
from utils.report import build_kpi_diagnostics
from utils.state import initialize_state


def render_assessment_page(module_name: str, caption: str, icon: str) -> None:
    st.set_page_config(page_title=module_name, page_icon=icon, layout="wide")
    initialize_state()

    st.title(module_name)
    st.caption(caption)

    with st.sidebar:
        st.info("Assessment execution is centralized on the main Run Assessment tab.")
        st.metric("Extracted Documents", len(st.session_state.extracted_documents))

    if not st.session_state.extracted_documents:
        st.warning("Upload documents and run the combined assessment from the main page.")

    st.subheader("Assessment Inputs")
    st.write(f"Focus: {MODULE_CONFIG[module_name]['focus']}")
    notes = st.session_state.get("portfolio_notes", "")
    if notes:
        st.caption(f"Portfolio notes: {notes}")

    evidence_matrix = build_evidence_matrix(module_name, st.session_state.extracted_documents)
    evidence_register = build_evidence_register(module_name, st.session_state.extracted_documents)
    evidence_scores = evidence_scores_from_matrix(evidence_matrix)
    evidence_rationales = evidence_rationales_from_matrix(evidence_matrix)
    evidence_details = _evidence_details_from_matrix(evidence_matrix)
    _render_scoring_inputs(module_name, evidence_scores)
    scoring_table = build_scoring_model(module_name, evidence_scores, evidence_rationales, evidence_details)
    model_score = calculate_weighted_score_from_table(scoring_table)
    model_risk = overall_risk_rating(model_score)

    col1, col2 = st.columns(2)
    col1.metric("Weighted Model Score", f"{model_score} / 100")
    col2.metric("Model Risk Rating", model_risk)
    assessment = st.session_state.assessments.get(module_name)
    current_assessment_mode = assessment.get("assessment_mode", "Not Run") if assessment else "Not Run"
    st.info(f"Current Assessment Mode: {current_assessment_mode}")

    st.subheader("Evidence-Based Scoring Model")
    st.dataframe(scoring_table, use_container_width=True, hide_index=True)

    radar_table = None
    if module_name == "Procurement Assessment":
        radar_table = _render_procurement_radar(scoring_table)

    st.subheader("Evidence Mapping Matrix")
    st.dataframe(evidence_register, use_container_width=True, hide_index=True)
    if module_name == "Procurement Assessment":
        st.subheader("Procurement Evidence Audit Table")
        st.caption("Every unique evidence sentence is shown once with its source and score-cap effect.")
        procurement_evidence_details = build_procurement_evidence_detail_table(
            st.session_state.extracted_documents
        )
        st.dataframe(procurement_evidence_details, use_container_width=True, hide_index=True)
    with st.expander("Criterion Scoring Matrix", expanded=False):
        st.dataframe(_compact_evidence_matrix(evidence_matrix), use_container_width=True, hide_index=True)
    _render_scoring_debug_panel(evidence_matrix)

    retrieval_query = " ".join(
        [
            notes,
            scoring_table.to_string(index=False),
            evidence_matrix.to_string(index=False),
            evidence_register.to_string(index=False),
        ]
    )
    scp_references = retrieve_scp_references(
        module_name,
        retrieval_query,
        st.session_state.scp_knowledge_base,
    )
    st.subheader("Relevant Knowledge Base Standards")
    if scp_references:
        st.dataframe(references_to_dataframe(scp_references), use_container_width=True, hide_index=True)
    else:
        st.warning("No relevant SCP knowledge base standards retrieved. Build the local knowledge base on the main page before running AI assessment.")

    preliminary_gap_plan = build_gap_remediation_plan(module_name, [], evidence_matrix, scoring_table)
    st.subheader("Automatic Gap Remediation Plan")
    st.dataframe(preliminary_gap_plan, use_container_width=True, hide_index=True)
    kpi_table = _render_kpi_section(module_name)
    _refresh_existing_assessment(
        module_name,
        scoring_table,
        evidence_matrix,
        evidence_register,
        radar_table,
        kpi_table,
        model_score,
        model_risk,
    )

    assessment = st.session_state.assessments.get(module_name)
    if assessment:
        _render_results(assessment)
    else:
        st.info("Run the Combined Assessment on the main page to populate this module result.")


def _render_scoring_inputs(module_name: str, evidence_scores: dict[str, int]) -> None:
    st.subheader(f"{MODULE_CONFIG[module_name]['model_name']} Criteria")
    st.caption(
        "Scores are calculated from uploaded-document evidence strength: 0 No Evidence, 1 Weak, "
        "2 Partial, 3 Moderate, 4 Strong, 5 Best Practice."
    )
    score_rows = []
    for item in MODULE_CONFIG[module_name]["criteria"]:
        score_rows.append(
            {
                "Assessment Criteria": item["criterion"],
                "Calculated Score 0-5": int(evidence_scores.get(item["criterion"], 0)),
                "Weightage %": item["weightage"],
                "Evidence Required": item["evidence_required"],
            }
        )
    st.dataframe(pd.DataFrame(score_rows), use_container_width=True, hide_index=True)


def _render_procurement_radar(scoring_table: pd.DataFrame) -> pd.DataFrame:
    st.subheader("Procurement Maturity Radar")
    st.caption("Evidence-based maturity from 1 (initial) to 5 (optimized) across procurement dimensions.")

    radar_scores = _procurement_radar_scores_from_scoring_model(scoring_table)
    radar_table = build_procurement_radar_table(radar_scores)
    components.html(build_procurement_radar_svg(radar_scores), height=640)
    st.dataframe(radar_table, use_container_width=True, hide_index=True)
    return radar_table


def _render_scoring_debug_panel(evidence_matrix: pd.DataFrame) -> None:
    with st.expander("Scoring Debug Panel", expanded=False):
        if evidence_matrix.empty:
            st.info("No evidence mapping results available.")
            return
        debug_columns = [
            "Assessment Criteria",
            "Source Documents",
            "Positive Evidence Found",
            "Negative Evidence Found",
            "Negative Evidence Source",
            "Score Cap Applied",
            "Evidence Strength",
            "Evidence Score 0-5",
            "Final Score Rationale",
        ]
        available_columns = [column for column in debug_columns if column in evidence_matrix.columns]
        debug_table = evidence_matrix[available_columns].rename(
            columns={
                "Assessment Criteria": "Criterion",
                "Source Documents": "Matched Source Documents",
                "Evidence Score 0-5": "Calculated Score",
                "Final Score Rationale": "Reason for Score",
            }
        )
        st.dataframe(debug_table, use_container_width=True, hide_index=True)


def _compact_evidence_matrix(evidence_matrix: pd.DataFrame) -> pd.DataFrame:
    compact_columns = [
        "Assessment Criteria",
        "Required Evidence",
        "Source Documents",
        "Evidence Strength",
        "Evidence Score 0-5",
        "Confidence Level",
        "Compliance Status",
        "Score Cap Applied",
        "Final Score Rationale",
    ]
    available_columns = [column for column in compact_columns if column in evidence_matrix.columns]
    return evidence_matrix[available_columns].copy()


def _evidence_details_from_matrix(evidence_matrix: pd.DataFrame) -> dict[str, dict]:
    if evidence_matrix.empty:
        return {}
    detail_columns = [
        "Negative Evidence Found",
        "Negative Evidence Source",
        "Score Cap Applied",
        "Final Score Rationale",
    ]
    details = {}
    for _, row in evidence_matrix.iterrows():
        criterion = str(row.get("Assessment Criteria", ""))
        details[criterion] = {
            column: row.get(column, "")
            for column in detail_columns
            if column in evidence_matrix.columns
        }
    return details


def _render_kpi_section(module_name: str) -> pd.DataFrame:
    st.subheader(f"{module_name.replace(' Assessment', '')} KPIs")
    st.caption("KPI status is separate from the core compliance score and supports dashboard tracking.")
    kpi_table = build_kpi_table(module_name)
    display_columns = ["KPI Name", "Current", "Current Value Reason", "Target", "Maturity", "Risk", "Status"]
    st.dataframe(
        kpi_table.reindex(columns=display_columns).rename(
            columns={"KPI Name": "KPI", "Current": "Current Value"}
        ),
        use_container_width=True,
        hide_index=True,
    )
    return kpi_table


def _refresh_existing_assessment(
    module_name: str,
    scoring_table: pd.DataFrame,
    evidence_matrix: pd.DataFrame,
    evidence_register: pd.DataFrame,
    radar_table: pd.DataFrame | None,
    kpi_table: pd.DataFrame,
    model_score: int,
    model_risk: str,
) -> None:
    assessment = st.session_state.assessments.get(module_name)
    if not assessment:
        return

    assessment["score"] = model_score
    assessment["risk_level"] = model_risk
    assessment["status"] = model_risk
    assessment["scoring_model"] = scoring_table
    assessment["evidence_matrix"] = evidence_matrix
    assessment["evidence_register"] = evidence_register
    assessment["procurement_radar"] = radar_table
    assessment["kpi_table"] = kpi_table
    guidance = build_full_compliance_guidance(module_name, scoring_table, evidence_register, kpi_table)
    assessment["full_compliance_guidance"] = guidance
    assessment["compliance_roadmap"] = build_compliance_roadmap(guidance)
    assessment["gap_remediation_plan"] = build_gap_remediation_plan(
        module_name=module_name,
        compliance_gaps=assessment.get("compliance_gaps", []),
        evidence_matrix=evidence_matrix,
        scoring_table=scoring_table,
    )
    st.session_state.assessments[module_name] = assessment


def _procurement_radar_scores_from_scoring_model(scoring_table: pd.DataFrame) -> dict[str, int]:
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
    radar_scores = {}
    for dimension in PROCUREMENT_RADAR_DIMENSIONS:
        source_criteria = mapping.get(dimension, [])
        scores = [criteria_scores[criterion] for criterion in source_criteria if criterion in criteria_scores]
        radar_scores[dimension] = round(sum(scores) / len(scores)) if scores else 1
    return radar_scores


def _render_results(assessment: dict) -> None:
    col1, col2, col3 = st.columns(3)
    col1.metric("Weighted Model Score", f"{assessment['score']} / 100")
    col2.metric("Model Risk Level", assessment["risk_level"])
    col3.metric("AI Suggested Score", f"{assessment.get('ai_assessment_score', assessment['score'])} / 100")
    if assessment.get("assessment_mode") == "Demo":
        st.info("Demo Assessment Mode: findings were generated locally without calling OpenAI.")

    st.subheader("Executive Summary")
    st.write(assessment["executive_summary"])

    _render_module_charts(assessment)

    if "scoring_model" in assessment:
        st.subheader("Applied Scoring Model")
        st.dataframe(assessment["scoring_model"], use_container_width=True, hide_index=True)

    if "evidence_register" in assessment:
        st.subheader("Evidence Mapping Matrix")
        st.dataframe(assessment["evidence_register"], use_container_width=True, hide_index=True)

    if "evidence_matrix" in assessment:
        with st.expander("Criterion Scoring Matrix", expanded=False):
            st.dataframe(_compact_evidence_matrix(assessment["evidence_matrix"]), use_container_width=True, hide_index=True)

    diagnostics = build_kpi_diagnostics(assessment)
    with st.expander("KPI Measurement Diagnostics", expanded=False):
        warning = diagnostics.attrs.get("placeholder_warning", "")
        if warning:
            st.warning(warning)
        st.dataframe(diagnostics, use_container_width=True, hide_index=True)

    if "scp_references" in assessment and not assessment["scp_references"].empty:
        st.subheader("Knowledge Base Used")
        st.dataframe(assessment["scp_references"], use_container_width=True, hide_index=True)

    if assessment.get("procurement_radar") is not None:
        st.subheader("Procurement Maturity Radar")
        radar_scores = dict(
            zip(
                assessment["procurement_radar"]["Dimension"],
                assessment["procurement_radar"]["Maturity 1-5"],
            )
        )
        components.html(build_procurement_radar_svg(radar_scores), height=640)
        st.dataframe(assessment["procurement_radar"], use_container_width=True, hide_index=True)

    if "gap_remediation_plan" in assessment:
        st.subheader("Automatic Gap Remediation Plan")
        st.dataframe(assessment["gap_remediation_plan"], use_container_width=True, hide_index=True)

    if assessment.get("compliance_roadmap") is not None:
        st.subheader("100% Compliance Roadmap")
        st.dataframe(assessment["compliance_roadmap"], use_container_width=True, hide_index=True)

    if assessment.get("full_compliance_guidance"):
        st.subheader("How to Achieve Full Compliance (5/5)")
        _render_full_compliance_guidance(assessment["full_compliance_guidance"])

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Key Findings")
        st.write(pd.DataFrame({"Finding": assessment["key_findings"]}))
        st.subheader("Compliance Gaps")
        st.write(pd.DataFrame({"Gap": assessment["compliance_gaps"]}))
    with col2:
        st.subheader("Recommended Actions")
        st.write(pd.DataFrame({"Action": assessment["recommended_actions"]}))
        st.subheader("Required Evidence")
        st.write(pd.DataFrame({"Evidence": assessment["required_evidence"]}))


def _render_full_compliance_guidance(guidance: list[dict]) -> None:
    for item in guidance:
        title = item.get("Title", "Assessment area")
        item_type = item.get("Type", "Assessment Criterion")
        with st.expander(f"{title} ({item_type})", expanded=False):
            for label in [
                "Current State",
                "Gap Identified",
                "Risk Impact",
                "Required Actions",
                "Required Documents",
                "Required Controls",
                "Evidence Expected",
                "Target State",
                "Expected Score Improvement",
            ]:
                st.markdown(f"**{label}:**")
                st.write(item.get(label, "Not available."))


def _render_module_charts(assessment: dict) -> None:
    st.subheader("Module Dashboard")
    chart_col1, chart_col2 = st.columns(2)

    scoring_model = assessment.get("scoring_model")
    if isinstance(scoring_model, pd.DataFrame) and not scoring_model.empty:
        with chart_col1:
            score_chart = scoring_model[["Assessment Criteria", "Score 0-5"]].set_index("Assessment Criteria")
            st.caption("Criterion Scores")
            st.bar_chart(score_chart)

    evidence_matrix = assessment.get("evidence_matrix")
    if isinstance(evidence_matrix, pd.DataFrame) and not evidence_matrix.empty:
        with chart_col2:
            evidence_counts = evidence_matrix["Compliance Status"].value_counts().rename("Count")
            st.caption("Evidence Compliance")
            st.bar_chart(evidence_counts)

    plan = assessment.get("gap_remediation_plan")
    if isinstance(plan, pd.DataFrame) and not plan.empty:
        st.caption("Remediation Priority")
        st.bar_chart(plan["Priority"].value_counts().rename("Count"))
