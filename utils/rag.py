from __future__ import annotations

import math
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

import pandas as pd

from utils.assessment import MODULE_CONFIG
from utils.document_processing import extract_file_bytes
from utils.document_processing import extract_file_path


SUPPORTED_KNOWLEDGE_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".xls", ".txt", ".md"}
APP_ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_BASE_DIR = APP_ROOT / "knowledge_base"
MODULE_KNOWLEDGE_FOLDERS = {
    "Procurement Assessment": "Procurement",
    "ESG Assessment": "ESG",
    "UAE Climate Law Compliance Assessment": "UAE_Climate_Law",
    "Contract Management Assessment": "Contract_Management",
    "Finance Audit Assessment": "Finance_Audit",
}
KNOWLEDGE_FOLDER_LABELS = {
    "Procurement": "Procurement",
    "ESG": "ESG",
    "UAE_Climate_Law": "UAE Climate Law",
    "Contract_Management": "Contract Management",
    "Finance_Audit": "Finance Audit",
}
EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "outputs",
    "pages",
    "scripts",
    "utils",
}
EXCLUDED_FILES = {"README.md", "requirements.txt"}
CHUNK_SIZE = 1400
CHUNK_OVERLAP = 220


def build_scp_knowledge_base(root: str | Path) -> dict:
    root_path = Path(root).resolve()
    knowledge_root = KNOWLEDGE_BASE_DIR if KNOWLEDGE_BASE_DIR.is_absolute() else root_path / KNOWLEDGE_BASE_DIR
    chunks = []
    indexed_documents = []
    indexed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for file_path, module_name, category in _iter_knowledge_files(root_path):
        try:
            text = extract_file_path(file_path)
            word_count = _word_count(text)
        except Exception as exc:
            indexed_documents.append(
                {
                    "Module": module_name,
                    "Category": KNOWLEDGE_FOLDER_LABELS.get(category, category),
                    "Document": str(file_path.relative_to(knowledge_root if knowledge_root.exists() else root_path)),
                    "Status": f"Failed: {exc}",
                    "Chunks": 0,
                    "Words Indexed": 0,
                    "Last Indexed": indexed_at,
                }
            )
            continue

        file_chunks = _chunk_text(text)
        for chunk_index, chunk in enumerate(file_chunks, start=1):
            chunks.append(
                {
                    "module": module_name,
                    "category": KNOWLEDGE_FOLDER_LABELS.get(category, category),
                    "source": str(file_path.relative_to(knowledge_root if knowledge_root.exists() else root_path)),
                    "chunk_id": chunk_index,
                    "text": chunk,
                    "tokens": Counter(_tokenize(chunk)),
                    "word_count": _word_count(chunk),
                    "indexed_at": indexed_at,
                }
            )
        indexed_documents.append(
            {
                "Module": module_name,
                "Category": KNOWLEDGE_FOLDER_LABELS.get(category, category),
                "Document": str(file_path.relative_to(knowledge_root if knowledge_root.exists() else root_path)),
                "Status": "Indexed",
                "Chunks": len(file_chunks),
                "Words Indexed": word_count,
                "Last Indexed": indexed_at,
            }
        )

    return {
        "root": str(knowledge_root if knowledge_root.exists() else root_path),
        "chunks": chunks,
        "documents": indexed_documents,
        "indexed_at": indexed_at,
    }


def build_scp_knowledge_base_from_uploads(uploaded_files: list) -> dict:
    chunks = []
    indexed_documents = []

    for uploaded_file in uploaded_files:
        try:
            text = extract_file_bytes(uploaded_file.getvalue(), uploaded_file.name)
            file_chunks = _chunk_text(text)
        except Exception as exc:
            indexed_documents.append({"Document": uploaded_file.name, "Status": f"Failed: {exc}", "Chunks": 0})
            continue

        for chunk_index, chunk in enumerate(file_chunks, start=1):
            chunks.append(
                {
                    "source": uploaded_file.name,
                    "chunk_id": chunk_index,
                    "text": chunk,
                    "tokens": Counter(_tokenize(chunk)),
                }
            )
        indexed_documents.append({"Document": uploaded_file.name, "Status": "Indexed", "Chunks": len(file_chunks)})

    return {"root": "uploaded_scp_toolkit", "chunks": chunks, "documents": indexed_documents}


def merge_knowledge_bases(*knowledge_bases: dict) -> dict:
    chunks = []
    documents = []
    roots = []
    for knowledge_base in knowledge_bases:
        if not knowledge_base:
            continue
        chunks.extend(knowledge_base.get("chunks", []))
        documents.extend(knowledge_base.get("documents", []))
        root = knowledge_base.get("root")
        if root:
            roots.append(root)
    indexed_at_values = [kb.get("indexed_at") for kb in knowledge_bases if kb and kb.get("indexed_at")]
    return {
        "root": "; ".join(roots),
        "chunks": chunks,
        "documents": documents,
        "indexed_at": max(indexed_at_values) if indexed_at_values else "",
    }


def retrieve_scp_references(module_name: str, assessment_inputs: str, knowledge_base: dict, top_k: int = 6) -> list[dict]:
    chunks = [
        chunk
        for chunk in (knowledge_base.get("chunks", []) if knowledge_base else [])
        if chunk.get("module") in {module_name, "General"}
    ]
    if not chunks:
        return []

    query = _build_query(module_name, assessment_inputs)
    query_terms = Counter(_tokenize(query))
    scored = []

    for chunk in chunks:
        score = _score_chunk(query_terms, chunk["tokens"])
        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda item: item[0], reverse=True)
    references = []
    for rank, (score, chunk) in enumerate(scored[:top_k], start=1):
        references.append(
            {
                "Reference": rank,
                "Module": chunk.get("module", module_name),
                "Category": chunk.get("category", ""),
                "Source": chunk["source"],
                "Chunk": chunk["chunk_id"],
                "Relevance Score": round(score, 3),
                "Excerpt": chunk["text"][:1200],
            }
        )
    return references


def references_to_context(references: list[dict]) -> str:
    if not references:
        return "No SCP toolkit reference passages were retrieved."

    sections = []
    for reference in references:
        sections.append(
            "\n".join(
                [
                    f"SCP Reference {reference['Reference']}",
                    f"Source: {reference['Source']} | Category: {reference.get('Category', '')} | Chunk: {reference['Chunk']} | Score: {reference['Relevance Score']}",
                    reference["Excerpt"],
                ]
            )
        )
    return "\n\n---\n\n".join(sections)


def references_to_dataframe(references: list[dict]) -> pd.DataFrame:
    if not references:
        return pd.DataFrame(columns=["Reference", "Module", "Category", "Source", "Chunk", "Relevance Score", "Excerpt"])
    return pd.DataFrame(references)


def knowledge_base_summary(knowledge_base: dict) -> pd.DataFrame:
    documents = knowledge_base.get("documents", []) if knowledge_base else []
    return pd.DataFrame(
        documents,
        columns=["Module", "Category", "Document", "Status", "Chunks", "Words Indexed", "Last Indexed"],
    )


def knowledge_base_module_stats(knowledge_base: dict) -> pd.DataFrame:
    documents = knowledge_base_summary(knowledge_base)
    rows = []
    for module_name, folder in MODULE_KNOWLEDGE_FOLDERS.items():
        label = KNOWLEDGE_FOLDER_LABELS[folder]
        module_docs = documents[documents["Module"] == module_name] if not documents.empty else pd.DataFrame()
        indexed_docs = module_docs[module_docs["Status"] == "Indexed"] if not module_docs.empty else pd.DataFrame()
        rows.append(
            {
                "Module Name": label,
                "Number of Documents": int(len(indexed_docs)),
                "Number of Chunks": int(indexed_docs["Chunks"].sum()) if not indexed_docs.empty else 0,
                "Total Words Indexed": int(indexed_docs["Words Indexed"].sum()) if not indexed_docs.empty else 0,
                "Last Indexed Date": _latest_value(indexed_docs, "Last Indexed"),
            }
        )
    return pd.DataFrame(rows)


def documents_for_category(knowledge_base: dict, category_label: str) -> pd.DataFrame:
    documents = knowledge_base_summary(knowledge_base)
    if documents.empty:
        return documents
    return documents[documents["Category"] == category_label].reset_index(drop=True)


def verify_knowledge_base_searchability(knowledge_base: dict) -> pd.DataFrame:
    rows = []
    documents = knowledge_base_summary(knowledge_base)
    chunks = knowledge_base.get("chunks", []) if knowledge_base else []

    for _, document in documents.iterrows():
        source = document["Document"]
        module_name = document["Module"]
        doc_chunks = [chunk for chunk in chunks if chunk.get("source") == source and chunk.get("module") == module_name]
        if document["Status"] != "Indexed":
            rows.append(
                {
                    "Module": document["Category"],
                    "Document": source,
                    "Searchable": "No",
                    "Verification Result": document["Status"],
                }
            )
            continue

        if not doc_chunks:
            rows.append(
                {
                    "Module": document["Category"],
                    "Document": source,
                    "Searchable": "No",
                    "Verification Result": "No chunks available for retrieval.",
                }
            )
            continue

        query = f"{source} {doc_chunks[0]['text'][:300]}"
        references = retrieve_scp_references(module_name, query, knowledge_base, top_k=max(10, len(chunks)))
        matched = any(reference["Source"] == source for reference in references)
        rows.append(
            {
                "Module": document["Category"],
                "Document": source,
                "Searchable": "Yes" if matched else "No",
                "Verification Result": "Retrieved by RAG engine." if matched else "Indexed but not retrieved in verification query.",
            }
        )

    return pd.DataFrame(rows, columns=["Module", "Document", "Searchable", "Verification Result"])


def _iter_knowledge_files(root_path: Path):
    knowledge_root = KNOWLEDGE_BASE_DIR if KNOWLEDGE_BASE_DIR.is_absolute() else root_path / KNOWLEDGE_BASE_DIR
    if not knowledge_root.exists():
        return

    folder_to_module = {folder: module for module, folder in MODULE_KNOWLEDGE_FOLDERS.items()}
    for file_path in knowledge_root.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in SUPPORTED_KNOWLEDGE_EXTENSIONS:
            continue
        if file_path.name in EXCLUDED_FILES:
            continue
        relative_path = file_path.relative_to(knowledge_root)
        if not relative_path.parts:
            continue
        category = relative_path.parts[0]
        module_name = folder_to_module.get(category)
        if not module_name:
            continue
        relative_parts = set(relative_path.parts[:-1])
        if relative_parts.intersection(EXCLUDED_DIRS):
            continue
        yield file_path, module_name, category


def _chunk_text(text: str) -> list[str]:
    clean_text = re.sub(r"\s+", " ", text).strip()
    if not clean_text:
        return []

    chunks = []
    start = 0
    while start < len(clean_text):
        end = min(len(clean_text), start + CHUNK_SIZE)
        chunks.append(clean_text[start:end])
        if end == len(clean_text):
            break
        start = max(0, end - CHUNK_OVERLAP)
    return chunks


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def _latest_value(dataframe: pd.DataFrame, column: str) -> str:
    if dataframe.empty or column not in dataframe:
        return "Not indexed"
    values = [value for value in dataframe[column].dropna().tolist() if value]
    return max(values) if values else "Not indexed"


def _build_query(module_name: str, assessment_inputs: str) -> str:
    module = MODULE_CONFIG[module_name]
    criteria = " ".join(item["criterion"] + " " + item["evidence_required"] for item in module["criteria"])
    return f"{module_name} {module['focus']} {criteria} {assessment_inputs}"


def _score_chunk(query_terms: Counter, chunk_terms: Counter) -> float:
    if not query_terms or not chunk_terms:
        return 0.0
    overlap = set(query_terms).intersection(chunk_terms)
    if not overlap:
        return 0.0

    weighted_overlap = sum(min(query_terms[term], chunk_terms[term]) for term in overlap)
    query_norm = math.sqrt(sum(value * value for value in query_terms.values()))
    chunk_norm = math.sqrt(sum(value * value for value in chunk_terms.values()))
    if query_norm == 0 or chunk_norm == 0:
        return 0.0
    return weighted_overlap / (query_norm * chunk_norm)


def _tokenize(text: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[a-zA-Z][a-zA-Z0-9-]{2,}", text.lower())
        if token not in {"the", "and", "for", "with", "from", "that", "this", "into", "are", "was"}
    ]


