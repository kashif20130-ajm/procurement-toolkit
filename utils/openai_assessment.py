from __future__ import annotations

import json
import os

from openai import OpenAI

from utils.assessment import MODULE_CONFIG


ASSESSMENT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "assessment_score": {"type": "integer", "minimum": 0, "maximum": 100},
        "key_findings": {"type": "array", "items": {"type": "string"}},
        "compliance_gaps": {"type": "array", "items": {"type": "string"}},
        "risk_level": {"type": "string", "enum": ["Low", "Medium", "High", "Critical"]},
        "recommended_actions": {"type": "array", "items": {"type": "string"}},
        "required_evidence": {"type": "array", "items": {"type": "string"}},
        "executive_summary": {"type": "string"},
    },
    "required": [
        "assessment_score",
        "key_findings",
        "compliance_gaps",
        "risk_level",
        "recommended_actions",
        "required_evidence",
        "executive_summary",
    ],
}


def run_openai_assessment(
    module_name: str,
    client_profile: dict,
    document_context: str,
    consultant_notes: str,
    scoring_model_context: str,
    evidence_mapping_context: str,
    evidence_register_context: str,
    scp_reference_context: str,
    api_key: str | None,
    model: str,
) -> dict:
    resolved_api_key = resolve_openai_api_key(api_key)
    if not resolved_api_key:
        raise ValueError("Add an OpenAI API key in the sidebar or set OPENAI_API_KEY.")

    client = OpenAI(api_key=resolved_api_key)
    module = MODULE_CONFIG[module_name]
    prompt = _build_prompt(
        module_name,
        module["focus"],
        client_profile,
        document_context,
        consultant_notes,
        scoring_model_context,
        evidence_mapping_context,
        evidence_register_context,
        scp_reference_context,
    )

    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": (
                    "You are a senior management consultant performing evidence-based company assessments. "
                    "Use the supplied client profile, client documents, scoring model, evidence mapping, and SCP toolkit references. "
                    "Compare uploaded client documents against the relevant SCP advisory standards. "
                    "Recommendations, gaps, risks, maturity scoring rationale, and evidence requirements must be grounded in SCP toolkit standards when SCP references are provided. "
                    "Do not invent SCP standards. If SCP references are insufficient, state what additional SCP standard content is required."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "company_assessment",
                "schema": ASSESSMENT_SCHEMA,
                "strict": True,
            }
        },
    )

    return _parse_response(response)


def _build_prompt(
    module_name: str,
    module_focus: str,
    client_profile: dict,
    document_context: str,
    consultant_notes: str,
    scoring_model_context: str,
    evidence_mapping_context: str,
    evidence_register_context: str,
    scp_reference_context: str,
) -> str:
    profile_text = "\n".join(f"{key}: {value}" for key, value in client_profile.items())
    return f"""
Assessment module: {module_name}
Module focus: {module_focus}

Client profile:
{profile_text}

Consultant notes:
{consultant_notes or "No additional consultant notes provided."}

Assessment scoring model:
{scoring_model_context}

Evidence mapping results:
{evidence_mapping_context}

Deduplicated uploaded-document evidence register:
{evidence_register_context}

Local SCP knowledge base advisory standards:
{scp_reference_context}

Extracted document content:
{document_context}

Generate a practical consulting assessment. Use the scoring model, 0-5 criterion scores,
weightage percentages, evidence mapping results, confidence levels, compliance statuses,
retrieved SCP toolkit reference material, and uploaded document content when forming the score,
risk level, findings, gaps, actions, required evidence, and executive summary. Recommendations
must be based on SCP advisory standards rather than generic AI advice. Compare the client
documents against the retrieved SCP standards and refer to knowledge base source names where useful.
If the evidence mapping contains negative evidence, score caps, or language such as "not required",
"optional", "without review", or "price only", treat that as control weakness even when positive
keywords are also present. Do not award high scores for keyword matches that are contradicted by
negative policy language.
""".strip()


def _parse_response(response) -> dict:
    output_text = getattr(response, "output_text", None)
    if not output_text:
        for item in getattr(response, "output", []) or []:
            for content in getattr(item, "content", []) or []:
                text = getattr(content, "text", None)
                if text:
                    output_text = text
                    break
            if output_text:
                break

    if not output_text:
        raise ValueError("OpenAI returned no text output.")

    return json.loads(output_text)


def resolve_openai_api_key(api_key: str | None = None) -> str | None:
    for value in (api_key, os.getenv("OPENAI_API_KEY"), _secret_api_key()):
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _secret_api_key() -> str | None:
    try:
        import streamlit as st

        return st.secrets.get("OPENAI_API_KEY")
    except Exception:
        return None
