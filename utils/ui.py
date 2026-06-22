from __future__ import annotations

import pandas as pd
import streamlit as st


STATUS_COLORS = {
    "Low": "#1f7a4d",
    "Medium": "#8a6d1d",
    "High": "#a94a1f",
    "Critical": "#9b1c1c",
    "Strong": "#1f7a4d",
    "Developing": "#8a6d1d",
    "Needs Improvement": "#a94a1f",
}


def apply_app_theme() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
        div[data-testid="stMetric"] {
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 14px 16px;
            background: #ffffff;
        }
        div[data-testid="stMetricValue"] {
            color: #0b2545;
            font-size: 1.65rem;
        }
        .section-note {
            border-left: 4px solid #2e74b5;
            background: #f4f6f9;
            padding: 12px 14px;
            border-radius: 6px;
            color: #1f2937;
            margin: 0.5rem 0 1rem 0;
        }
        .risk-pill {
            display: inline-block;
            padding: 3px 9px;
            border-radius: 999px;
            background: #eef2f7;
            font-size: 0.82rem;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def section_note(text: str) -> None:
    st.markdown(f'<div class="section-note">{text}</div>', unsafe_allow_html=True)


def render_sidebar_summary() -> None:
    with st.sidebar:
        st.header("Workspace")
        st.metric("Client Docs", len(st.session_state.uploaded_documents))
        st.metric("Extracted Docs", len(st.session_state.extracted_documents))
        st.metric("Completed Modules", len(st.session_state.assessments))
        st.metric("SCP KB Chunks", len(st.session_state.scp_knowledge_base.get("chunks", [])))


def risk_badge(label: str) -> str:
    color = STATUS_COLORS.get(label, "#475569")
    return f"<span class='risk-pill' style='color:{color}'>{label}</span>"


def dataframe_or_info(dataframe: pd.DataFrame | list[dict], message: str) -> None:
    is_empty_list = isinstance(dataframe, list) and len(dataframe) == 0
    is_empty_frame = hasattr(dataframe, "empty") and dataframe.empty
    if dataframe is None or is_empty_list or is_empty_frame:
        st.info(message)
    else:
        st.dataframe(dataframe, use_container_width=True, hide_index=True)
