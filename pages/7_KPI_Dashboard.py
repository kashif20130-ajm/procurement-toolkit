import streamlit as st

from utils.dashboard import render_kpi_dashboard
from utils.state import initialize_state


st.set_page_config(page_title="KPI Dashboard", page_icon=":bar_chart:", layout="wide")
initialize_state()

st.title("KPI Dashboard")
st.caption("Traffic-light KPI status across completed assessment modules.")

render_kpi_dashboard(st.session_state.assessments)
