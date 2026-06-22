import pandas as pd
import streamlit as st

from utils.assessment import MODULE_CONFIG
from utils.assessment import build_scoring_model
from utils.assessment import calculate_weighted_score_from_table
from utils.assessment import overall_risk_rating
from utils.evidence_mapping import build_evidence_matrix
from utils.evidence_mapping import build_evidence_register
from utils.evidence_mapping import evidence_rationales_from_matrix
from utils.evidence_mapping import evidence_scores_from_matrix
from utils.gap_planning import build_gap_remediation_plan
from utils.kpi import build_kpi_table
from utils.rag import references_to_dataframe
from utils.rag import retrieve_scp_references
from utils.state import initialize_state
from utils.sustainability import CLIMATE_MODULE_NAME
from utils.sustainability import ESG_MODULE_NAME
from utils.sustainability import PARENT_MODULE_NAME


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


def _render_section_preview(module_name: str, notes: str) -> dict:
    st.subheader(module_name)
    st.write(f"Focus: {MODULE_CONFIG[module_name]['focus']}")
    evidence_matrix = build_evidence_matrix(module_name, st.session_state.extracted_documents)
    evidence_register = build_evidence_register(module_name, st.session_state.extracted_documents)
    evidence_scores = evidence_scores_from_matrix(evidence_matrix)
    evidence_rationales = evidence_rationales_from_matrix(evidence_matrix)
    evidence_details = _evidence_details_from_matrix(evidence_matrix)
    scoring_table = build_scoring_model(module_name, evidence_scores, evidence_rationales, evidence_details)
    score = calculate_weighted_score_from_table(scoring_table)
    risk = overall_risk_rating(score)

    metric_col1, metric_col2 = st.columns(2)
    metric_col1.metric("Section Score", f"{score} / 100")
    metric_col2.metric("Section Risk", risk)
    st.dataframe(scoring_table, use_container_width=True, hide_index=True)

    st.caption("Evidence Mapping Matrix")
    st.dataframe(evidence_register, use_container_width=True, hide_index=True)
    with st.expander("Criterion Scoring Matrix", expanded=False):
        st.dataframe(_compact_evidence_matrix(evidence_matrix), use_container_width=True, hide_index=True)

    query = " ".join(
        [
            notes,
            scoring_table.to_string(index=False),
            evidence_matrix.to_string(index=False),
            evidence_register.to_string(index=False),
        ]
    )
    references = retrieve_scp_references(module_name, query, st.session_state.scp_knowledge_base)
    if references:
        st.caption("Relevant Knowledge Base Standards")
        st.dataframe(references_to_dataframe(references), use_container_width=True, hide_index=True)
    else:
        st.warning("No relevant SCP knowledge base standards retrieved for this section.")

    gap_plan = build_gap_remediation_plan(module_name, [], evidence_matrix, scoring_table)
    st.caption("Section Gap Remediation Plan")
    st.dataframe(gap_plan, use_container_width=True, hide_index=True)
    return {
        "module_name": module_name,
        "evidence_matrix": evidence_matrix,
        "evidence_register": evidence_register,
        "scoring_table": scoring_table,
        "score": score,
        "risk": risk,
        "references": references,
        "references_df": references_to_dataframe(references),
        "gap_plan": gap_plan,
        "kpi_table": build_kpi_table(module_name),
    }


def _render_parent_results(assessment: dict) -> None:
    st.subheader("Completed Sustainability Assessment")
    result_col1, result_col2, result_col3 = st.columns(3)
    result_col1.metric("ESG Score", f"{assessment['esg_score']} / 100")
    result_col2.metric("Climate Compliance Score", f"{assessment['climate_score']} / 100")
    result_col3.metric("Combined Sustainability Score", f"{assessment['score']} / 100")
    st.metric("Combined Sustainability Risk", assessment["risk_level"])

    st.subheader("Combined Sustainability Dashboard")
    st.dataframe(assessment["sustainability_dashboard"], use_container_width=True, hide_index=True)
    st.bar_chart(assessment["sustainability_dashboard"].set_index("Section")[["Score"]])

    if isinstance(assessment.get("combined_sustainability_kpi_dashboard"), pd.DataFrame):
        st.subheader("Combined Sustainability KPI Dashboard")
        st.dataframe(assessment["combined_sustainability_kpi_dashboard"], use_container_width=True, hide_index=True)

    st.subheader("ESG Findings")
    st.write(pd.DataFrame({"Finding": assessment["esg_assessment"].get("key_findings", [])}))
    st.subheader("Climate Compliance Findings")
    st.write(pd.DataFrame({"Finding": assessment["climate_assessment"].get("key_findings", [])}))


st.set_page_config(page_title=PARENT_MODULE_NAME, page_icon=":seedling:", layout="wide")
initialize_state()

st.title(PARENT_MODULE_NAME)
st.caption("Combined assessment covering ESG governance, ESG reporting, and UAE climate-law compliance.")

with st.sidebar:
    st.info("Assessment execution is centralized on the main Run Assessment tab.")
    st.metric("Extracted Documents", len(st.session_state.extracted_documents))

if not st.session_state.extracted_documents:
    st.warning("Upload documents on the main page before running the sustainability assessment.")

notes = st.session_state.get("portfolio_notes", "")
if notes:
    st.caption(f"Portfolio notes: {notes}")

section_a, section_b = st.tabs(["Section A - ESG Governance & Reporting", "Section B - UAE Climate Law Compliance"])

with section_a:
    esg_context = _render_section_preview(ESG_MODULE_NAME, notes)

with section_b:
    climate_context = _render_section_preview(CLIMATE_MODULE_NAME, notes)

combined_score = round((esg_context["score"] * 0.4) + (climate_context["score"] * 0.6))
combined_risk = overall_risk_rating(combined_score)

st.subheader("Combined Sustainability Dashboard")
col1, col2, col3 = st.columns(3)
col1.metric("ESG Score", f"{esg_context['score']} / 100")
col2.metric("Climate Compliance Score", f"{climate_context['score']} / 100")
col3.metric("Combined Sustainability Score", f"{combined_score} / 100")
st.metric("Combined Sustainability Risk Level", combined_risk)
st.caption("Combined weighting: ESG Governance & Reporting = 40%; UAE Climate Law Compliance = 60%.")
st.bar_chart(
    pd.DataFrame(
        {
            "Score": {
                "ESG Governance & Reporting": esg_context["score"],
                "UAE Climate Law Compliance": climate_context["score"],
                "Combined Sustainability": combined_score,
            }
        }
    )
)

assessment = st.session_state.assessments.get(PARENT_MODULE_NAME)
if assessment:
    _render_parent_results(assessment)
else:
    st.info("Run the Combined Assessment on the main page to populate the sustainability result.")
