from datetime import date

import streamlit as st


def initialize_state() -> None:
    if "client_profile" not in st.session_state:
        st.session_state["client_profile"] = {
            "client_name": "",
            "industry": "",
            "country": "United Arab Emirates",
            "consultant_name": "",
            "assessment_date": date.today(),
            "company_size": "Medium",
            "assessment_objective": "",
        }

    if "uploaded_documents" not in st.session_state:
        st.session_state["uploaded_documents"] = []

    if "extracted_documents" not in st.session_state:
        st.session_state["extracted_documents"] = []

    if "assessments" not in st.session_state:
        st.session_state["assessments"] = {}

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-5.2"

    if "portfolio_notes" not in st.session_state:
        st.session_state["portfolio_notes"] = ""

    if "portfolio_assessment_mode" not in st.session_state:
        st.session_state["portfolio_assessment_mode"] = "Not Run"

    if "scp_knowledge_base" not in st.session_state:
        st.session_state["scp_knowledge_base"] = {"root": "", "chunks": [], "documents": [], "indexed_at": ""}
