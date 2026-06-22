from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pathlib import Path

import streamlit as st

from utils.assessment_runner import determine_assessment_mode
from utils.dashboard import render_executive_dashboard
from utils.dashboard import render_kpi_dashboard
from utils.document_processing import extract_uploaded_file
from utils.rag import build_scp_knowledge_base
from utils.rag import knowledge_base_summary
from utils.portfolio_assessment import PORTFOLIO_MODULES
from utils.portfolio_assessment import run_portfolio_assessment
from utils.report import build_combined_detailed_report_docx
from utils.report import build_combined_executive_summary_docx
from utils.state import initialize_state
from utils.ui import apply_app_theme
from utils.ui import dataframe_or_info
from utils.ui import render_sidebar_summary
from utils.ui import section_note


OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
EXECUTIVE_REPORT_NAME = "combined_executive_summary.docx"
DETAILED_REPORT_NAME = "combined_detailed_assessment_report.docx"


def _generate_combined_report_files() -> tuple[bytes, bytes]:
    executive = build_combined_executive_summary_docx(
        st.session_state.client_profile,
        st.session_state.uploaded_documents,
        st.session_state.assessments,
    ).getvalue()
    detailed = build_combined_detailed_report_docx(
        st.session_state.client_profile,
        st.session_state.uploaded_documents,
        st.session_state.assessments,
    ).getvalue()
    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / EXECUTIVE_REPORT_NAME).write_bytes(executive)
    (OUTPUT_DIR / DETAILED_REPORT_NAME).write_bytes(detailed)
    st.session_state.combined_executive_report_bytes = executive
    st.session_state.combined_detailed_report_bytes = detailed
    return executive, detailed


def _combined_report_bytes() -> tuple[bytes, bytes]:
    executive = st.session_state.get("combined_executive_report_bytes")
    detailed = st.session_state.get("combined_detailed_report_bytes")
    if not executive or not detailed:
        return _generate_combined_report_files()
    return executive, detailed


def _render_combined_downloads(key_prefix: str) -> None:
    executive, detailed = _combined_report_bytes()
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "Download Combined Executive Summary",
            data=executive,
            file_name=EXECUTIVE_REPORT_NAME,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            key=f"{key_prefix}_executive_download",
        )
    with col2:
        st.download_button(
            "Download Combined Detailed Report",
            data=detailed,
            file_name=DETAILED_REPORT_NAME,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            key=f"{key_prefix}_detailed_download",
        )


st.set_page_config(
    page_title="AI Company Assessment App",
    page_icon=":clipboard:",
    layout="wide",
)

initialize_state()
apply_app_theme()
render_sidebar_summary()

st.title("AI Company Assessment App")
st.caption("Assessment command center for procurement, sustainability and climate compliance, contract management, and finance audit.")

profile_tab, docs_tab, assessment_tab, kb_tab, dashboard_tab, kpi_tab, exports_tab = st.tabs(
    ["Client Profile", "Client Documents", "Run Assessment", "SCP Knowledge Base", "Dashboard", "KPI Dashboard", "Exports"]
)


with profile_tab:
    st.subheader("Client Profile")
    section_note("Capture engagement context once, then reuse it across all assessment modules and Word exports.")
    profile = st.session_state.client_profile

    col1, col2 = st.columns(2)
    with col1:
        profile["client_name"] = st.text_input("Client name", value=profile.get("client_name", ""))
        profile["industry"] = st.text_input("Industry", value=profile.get("industry", ""))
        profile["country"] = st.text_input("Country / market", value=profile.get("country", "United Arab Emirates"))
    with col2:
        profile["consultant_name"] = st.text_input("Consultant name", value=profile.get("consultant_name", ""))
        profile["assessment_date"] = st.date_input("Assessment date", value=profile.get("assessment_date"))
        profile["company_size"] = st.selectbox(
            "Company size",
            ["Small", "Medium", "Large", "Enterprise"],
            index=["Small", "Medium", "Large", "Enterprise"].index(profile.get("company_size", "Medium")),
        )

    profile["assessment_objective"] = st.text_area(
        "Assessment objective",
        value=profile.get(
            "assessment_objective",
            "Assess current practices, identify gaps and risks, and recommend a practical improvement roadmap.",
        ),
    )
    st.session_state.client_profile = profile


with docs_tab:
    st.subheader("Client Document Upload")
    section_note("Upload client evidence files. Text and tables are extracted for evidence mapping and AI assessment.")
    uploaded_files = st.file_uploader(
        "Upload client documents",
        type=["pdf", "doc", "docx", "xls", "xlsx", "txt", "md"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        current_names = {doc["name"] for doc in st.session_state.uploaded_documents}
        for file in uploaded_files:
            if file.name not in current_names:
                with st.spinner(f"Extracting content from {file.name}..."):
                    extracted = extract_uploaded_file(file)
                st.session_state.extracted_documents.append(extracted)
                st.session_state.uploaded_documents.append(
                    {
                        "name": extracted["name"],
                        "type": extracted["type"],
                        "size_kb": extracted["size_kb"],
                        "characters_extracted": extracted["characters_extracted"],
                    }
                )
                st.session_state.assessments = {}
                st.session_state.pop("combined_executive_report_bytes", None)
                st.session_state.pop("combined_detailed_report_bytes", None)

    dataframe_or_info(
        st.session_state.uploaded_documents,
        "No client documents uploaded yet.",
    )
    if st.session_state.extracted_documents:
        with st.expander("Preview Extracted Content"):
            for document in st.session_state.extracted_documents:
                st.markdown(f"**{document['name']}**")
                st.text_area(
                    f"Extracted text preview - {document['name']}",
                    value=document.get("content", "")[:3000],
                    height=180,
                    disabled=True,
                    label_visibility="collapsed",
                )


with assessment_tab:
    st.subheader("Combined Company Assessment")
    section_note(
        "Run Procurement, Sustainability and Climate Compliance, Contract Management, and Finance Audit in one workflow."
    )

    settings_col, notes_col = st.columns([1, 2])
    with settings_col:
        api_key = st.text_input(
            "OpenAI API key",
            type="password",
            key="portfolio_openai_api_key",
            help="Leave blank to use the local rule-based assessment.",
        )
        st.session_state.openai_model = st.text_input(
            "OpenAI model",
            value=st.session_state.openai_model,
            key="portfolio_openai_model",
        )
        force_demo_mode = st.checkbox(
            "Force Demo Mode - run without OpenAI API",
            value=True,
            key="portfolio_force_demo_mode",
        )
        current_mode = determine_assessment_mode(force_demo_mode, api_key)
        st.markdown(f"**Current Assessment Mode: {current_mode}**")
    with notes_col:
        portfolio_notes = st.text_area(
            "Consultant notes",
            value=st.session_state.get("portfolio_notes", ""),
            placeholder="Add cross-functional observations, interview notes, or assessment context.",
            height=145,
        )
        st.session_state.portfolio_notes = portfolio_notes

    st.caption("Included modules: " + " | ".join(module.replace(" Assessment", "") for module in PORTFOLIO_MODULES))
    if not st.session_state.extracted_documents:
        st.warning("Upload client documents before running the combined assessment.")

    if st.button(
        "Run Combined Assessment",
        type="primary",
        disabled=not st.session_state.extracted_documents,
        use_container_width=True,
    ):
        with st.spinner("Running the complete company assessment across all modules..."):
            try:
                if not st.session_state.scp_knowledge_base.get("chunks"):
                    st.session_state.scp_knowledge_base = build_scp_knowledge_base(".")
                assessments, completed_mode = run_portfolio_assessment(
                    client_profile=st.session_state.client_profile,
                    extracted_documents=st.session_state.extracted_documents,
                    consultant_notes=portfolio_notes,
                    knowledge_base=st.session_state.scp_knowledge_base,
                    force_demo_mode=force_demo_mode,
                    api_key=api_key,
                    model=st.session_state.openai_model,
                )
            except Exception as exc:
                st.error(f"Combined assessment failed: {exc}")
            else:
                st.session_state.assessments = assessments
                st.session_state.portfolio_assessment_mode = completed_mode
                _generate_combined_report_files()
                st.success(f"Combined assessment completed in {completed_mode} Mode.")

    if st.session_state.assessments:
        status_rows = [
            {
                "Module": module.replace(" Assessment", ""),
                "Score": assessment.get("score", 0),
                "Risk": assessment.get("risk_level", assessment.get("status", "Not assessed")),
            }
            for module, assessment in st.session_state.assessments.items()
        ]
        st.dataframe(status_rows, use_container_width=True, hide_index=True)
        if all(module in st.session_state.assessments for module in PORTFOLIO_MODULES):
            st.subheader("Combined Assessment Reports")
            _render_combined_downloads("assessment_tab")


with kb_tab:
    st.subheader("Local SCP Knowledge Base")
    section_note(
        "Place SCP policy and toolkit files in the knowledge_base module folders, then build the local RAG index."
    )

    st.markdown(
        """
        Expected folders:
        - `knowledge_base/Procurement`
        - `knowledge_base/ESG`
        - `knowledge_base/UAE_Climate_Law`
        - `knowledge_base/Contract_Management`
        - `knowledge_base/Finance_Audit`
        """
    )

    if st.button("Build / Refresh Local Knowledge Base"):
        with st.spinner("Indexing local SCP policy and toolkit documents..."):
            st.session_state.scp_knowledge_base = build_scp_knowledge_base(".")

    kb_summary = knowledge_base_summary(st.session_state.scp_knowledge_base)
    dataframe_or_info(
        kb_summary,
        "No SCP toolkit documents indexed yet. Add files to knowledge_base module folders.",
    )
    st.caption(f"Indexed chunks: {len(st.session_state.scp_knowledge_base.get('chunks', []))}")


with dashboard_tab:
    render_executive_dashboard(st.session_state.assessments)


with kpi_tab:
    render_kpi_dashboard(st.session_state.assessments)


with exports_tab:
    st.subheader("Professional Exports")
    section_note("Generate client-ready Word outputs from completed assessment findings.")

    missing_modules = [module for module in PORTFOLIO_MODULES if module not in st.session_state.assessments]
    if missing_modules:
        st.info("Run the Combined Assessment before exporting the two portfolio reports.")
    else:
        _render_combined_downloads("exports_tab")
