import streamlit as st

from utils.rag import KNOWLEDGE_FOLDER_LABELS
from utils.rag import build_scp_knowledge_base
from utils.rag import documents_for_category
from utils.rag import knowledge_base_module_stats
from utils.rag import verify_knowledge_base_searchability
from utils.state import initialize_state
from utils.ui import apply_app_theme
from utils.ui import dataframe_or_info
from utils.ui import section_note


st.set_page_config(page_title="Knowledge Base Manager", page_icon=":books:", layout="wide")
initialize_state()
apply_app_theme()

st.title("Knowledge Base Manager")
st.caption("Local SCP policy and toolkit document index for advisory-standard grounded assessments.")

section_note(
    "Place SCP toolkit files under knowledge_base module folders, then rebuild the index. "
    "The RAG engine searches only the relevant module folder during each assessment."
)

if st.button("Rebuild Knowledge Base", type="primary"):
    with st.spinner("Extracting, chunking, and indexing local SCP toolkit documents..."):
        st.session_state.scp_knowledge_base = build_scp_knowledge_base(".")
    st.success("Knowledge base rebuilt.")

stats = knowledge_base_module_stats(st.session_state.scp_knowledge_base)

st.subheader("Index Summary")
total_docs = int(stats["Number of Documents"].sum()) if not stats.empty else 0
total_chunks = int(stats["Number of Chunks"].sum()) if not stats.empty else 0
total_words = int(stats["Total Words Indexed"].sum()) if not stats.empty else 0
last_indexed = st.session_state.scp_knowledge_base.get("indexed_at") or "Not indexed"

col1, col2, col3, col4 = st.columns(4)
col1.metric("Documents", total_docs)
col2.metric("Chunks", total_chunks)
col3.metric("Words Indexed", f"{total_words:,}")
col4.metric("Last Indexed", last_indexed)

dataframe_or_info(stats, "No knowledge base index has been built yet.")

st.subheader("Documents Indexed by Module")
for category in ["Procurement", "ESG", "UAE Climate Law", "Contract Management", "Finance Audit"]:
    with st.expander(category, expanded=True):
        module_docs = documents_for_category(st.session_state.scp_knowledge_base, category)
        dataframe_or_info(module_docs, f"No indexed documents found under {category}.")

st.subheader("RAG Searchability Verification")
verification = verify_knowledge_base_searchability(st.session_state.scp_knowledge_base)
dataframe_or_info(verification, "No indexed documents available to verify.")

if not verification.empty:
    searchable_count = int((verification["Searchable"] == "Yes").sum())
    st.caption(f"Searchable documents verified: {searchable_count} of {len(verification)}")

with st.expander("Expected Local Folder Structure"):
    for folder, label in KNOWLEDGE_FOLDER_LABELS.items():
        st.code(f"knowledge_base/{folder}  # {label}")
