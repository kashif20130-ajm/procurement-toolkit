from __future__ import annotations

from collections import Counter

import pandas as pd
import streamlit as st

from utils.report import build_kpi_dashboard_dataframe


def assessment_progress_dataframe(assessments: dict) -> pd.DataFrame:
    rows = []
    for module, data in assessments.items():
        rows.append(
            {
                "Module": module,
                "Score": int(data.get("score", 0)),
                "Risk Level": data.get("risk_level", data.get("status", "Not assessed")),
                "AI Score": int(data.get("ai_assessment_score", data.get("score", 0))),
            }
        )
    return pd.DataFrame(rows)


def gap_portfolio_dataframe(assessments: dict) -> pd.DataFrame:
    frames = []
    for module, data in assessments.items():
        plan = data.get("gap_remediation_plan")
        if isinstance(plan, pd.DataFrame) and not plan.empty:
            frame = plan.copy()
            frame.insert(0, "Module", module)
            frames.append(frame)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def evidence_status_dataframe(assessments: dict) -> pd.DataFrame:
    rows = []
    for module, data in assessments.items():
        matrix = data.get("evidence_matrix")
        if isinstance(matrix, pd.DataFrame) and not matrix.empty:
            counts = Counter(matrix["Compliance Status"])
            for status, count in counts.items():
                rows.append({"Module": module, "Compliance Status": status, "Count": count})
    return pd.DataFrame(rows)


def render_executive_dashboard(assessments: dict) -> None:
    st.subheader("Executive Dashboard")
    progress = assessment_progress_dataframe(assessments)
    gaps = gap_portfolio_dataframe(assessments)
    evidence = evidence_status_dataframe(assessments)

    if progress.empty:
        st.info("Complete at least one assessment module to populate the dashboard.")
        return

    avg_score = round(progress["Score"].mean())
    high_priority = int((gaps["Priority"] == "High").sum()) if not gaps.empty else 0
    open_gaps = len(gaps)
    critical_modules = int(progress["Risk Level"].isin(["High", "Critical"]).sum())

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Average Score", f"{avg_score} / 100")
    col2.metric("Open Gaps", open_gaps)
    col3.metric("High Priority", high_priority)
    col4.metric("High/Critical Modules", critical_modules)

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.caption("Assessment Scores")
        st.bar_chart(progress.set_index("Module")[["Score", "AI Score"]])
    with chart_col2:
        st.caption("Evidence Compliance")
        if evidence.empty:
            st.info("No evidence matrix stored yet.")
        else:
            pivot = evidence.pivot_table(
                index="Module",
                columns="Compliance Status",
                values="Count",
                aggfunc="sum",
                fill_value=0,
            )
            st.bar_chart(pivot)

    if not gaps.empty:
        st.caption("Gap Portfolio")
        priority_counts = gaps.groupby("Priority").size().rename("Count").reset_index()
        st.bar_chart(priority_counts.set_index("Priority"))
        st.dataframe(
            gaps[["Module", "Gap", "Priority", "Estimated Effort", "Responsible Function", "Target Date"]],
            use_container_width=True,
            hide_index=True,
        )

    sustainability = assessments.get("Sustainability & Climate Compliance Assessment")
    if sustainability and isinstance(sustainability.get("sustainability_dashboard"), pd.DataFrame):
        st.subheader("Combined Sustainability Dashboard")
        st.dataframe(sustainability["sustainability_dashboard"], use_container_width=True, hide_index=True)
        st.bar_chart(sustainability["sustainability_dashboard"].set_index("Section")[["Score"]])


def render_kpi_dashboard(assessments: dict) -> None:
    st.subheader("KPI Dashboard")
    portfolio = build_kpi_dashboard_dataframe(assessments)
    sustainability = assessments.get("Sustainability & Climate Compliance Assessment")
    sustainability_kpis = sustainability.get("combined_sustainability_kpi_dashboard") if sustainability else None
    if portfolio.empty:
        if not isinstance(sustainability_kpis, pd.DataFrame) or sustainability_kpis.empty:
            st.info("Complete at least one assessment module to populate KPI status.")
            return
        st.subheader("Combined Sustainability KPI Dashboard")
        st.dataframe(sustainability_kpis, use_container_width=True, hide_index=True)
        return

    status_counts = portfolio.groupby("Status").size().rename("Count")
    col1, col2, col3 = st.columns(3)
    col1.metric("Measured", int(status_counts.get("Measured", 0)))
    col2.metric("Data Unavailable", int(status_counts.get("Data Not Available", 0)))
    col3.metric("Not Established", int(status_counts.get("Not Established", 0)))

    st.caption("KPI Traffic-Light Status")
    pivot = portfolio.pivot_table(index="Module", columns="Status", values="KPI", aggfunc="count", fill_value=0)
    st.bar_chart(pivot)
    dashboard_columns = ["KPI", "Current Display", "Current Value Reason", "Target Display", "Maturity", "Risk", "Status"]
    dashboard = portfolio.reindex(columns=dashboard_columns).rename(
        columns={"Current Display": "Current Value", "Target Display": "Target"}
    )
    st.dataframe(dashboard, use_container_width=True, hide_index=True)

    if isinstance(sustainability_kpis, pd.DataFrame) and not sustainability_kpis.empty:
        st.subheader("Combined Sustainability KPI Dashboard")
        st.dataframe(sustainability_kpis, use_container_width=True, hide_index=True)
