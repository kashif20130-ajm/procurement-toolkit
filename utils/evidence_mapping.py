from __future__ import annotations

import re

import pandas as pd

from utils.assessment import MODULE_CONFIG


STOP_WORDS = {
    "and",
    "the",
    "for",
    "with",
    "from",
    "into",
    "this",
    "that",
    "their",
    "records",
    "record",
    "evidence",
    "required",
    "approved",
    "current",
    "relevant",
    "management",
    "process",
    "controls",
    "control",
}

EVIDENCE_STRENGTH_LABELS = {
    0: "No Evidence",
    1: "Weak Evidence",
    2: "Partial Evidence",
    3: "Moderate Evidence",
    4: "Strong Evidence",
    5: "Best Practice Evidence",
}

NEGATIVE_CAP_NONE = "No cap"

PROCUREMENT_NEGATIVE_EVIDENCE_RULES = [
    {
        "patterns": [
            "not required",
            "optional",
            "may approve without review",
            "no due diligence required",
            "due diligence not required",
            "performance reviews not required",
            "kpis not mandatory",
        ],
        "cap": 1,
        "label": "Negative evidence: policy language makes key procurement controls optional or not required.",
        "criteria": [
            "Procurement policy and procedures",
            "Strategic sourcing and tender controls",
            "Supplier due diligence and onboarding",
            "Purchase-to-pay controls",
            "Supplier performance management",
            "Procurement risk and compliance monitoring",
        ],
    },
    {
        "patterns": [
            "suppliers assessed on price only",
            "supplier assessed on price only",
            "based on price only",
            "price only evaluation",
        ],
        "cap": 1,
        "label": "Negative evidence: suppliers are assessed on price only.",
        "criteria": [
            "Strategic sourcing and tender controls",
            "Supplier due diligence and onboarding",
            "Supplier performance management",
        ],
    },
    {
        "patterns": [
            "trade license verification not required",
            "trade licence verification not required",
            "trade license not required",
            "trade licence not required",
            "vat verification not required",
            "trn verification not required",
            "vat/trn verification not required",
            "tax registration verification not required",
        ],
        "cap": 1,
        "label": "Negative evidence: supplier legal or VAT/TRN verification is not required.",
        "criteria": ["Supplier due diligence and onboarding"],
    },
    {
        "patterns": [
            "no sanctions checks required",
            "sanctions checks not required",
            "sanctions screening not required",
            "no sanction screening required",
        ],
        "cap": 1,
        "label": "Negative evidence: sanctions screening is not required.",
        "criteria": ["Supplier due diligence and onboarding", "Procurement risk and compliance monitoring"],
    },
    {
        "patterns": [
            "no esg checks required",
            "esg checks not required",
            "esg assessment not required",
            "supplier esg assessment not required",
        ],
        "cap": 1,
        "label": "Negative evidence: supplier ESG assessment is not required.",
        "criteria": ["Supplier due diligence and onboarding", "Supplier performance management"],
    },
    {
        "patterns": [
            "no conflict of interest checks required",
            "no conflict-of-interest checks required",
            "conflict of interest checks not required",
            "conflict-of-interest checks not required",
        ],
        "cap": 1,
        "label": "Negative evidence: conflict-of-interest checks are not required.",
        "criteria": ["Supplier due diligence and onboarding", "Procurement risk and compliance monitoring"],
    },
    {
        "patterns": [
            "supplier assessment forms optional",
            "supplier assessments optional",
            "supplier assessment optional",
            "supplier performance reviews are not required",
            "supplier performance review not required",
            "periodic supplier review not required",
        ],
        "cap": 1,
        "label": "Negative evidence: supplier assessment or performance review is optional or not required.",
        "criteria": ["Supplier due diligence and onboarding", "Supplier performance management"],
    },
    {
        "patterns": [
            "may approve all suppliers without secondary review",
            "may approve suppliers without secondary review",
            "may approve without review",
            "without secondary review",
            "without independent review",
        ],
        "cap": 1,
        "label": "Negative evidence: suppliers may be approved without independent or secondary review.",
        "criteria": [
            "Procurement policy and procedures",
            "Supplier due diligence and onboarding",
            "Procurement risk and compliance monitoring",
        ],
    },
    {
        "patterns": [
            "same employee may request, approve, receive and approve invoice",
            "same employee can request, approve, receive and approve invoice",
            "same person may request approve receive and approve invoice",
            "same person can request approve receive and approve invoice",
            "segregation of duties not required",
            "no segregation of duties required",
        ],
        "cap": 0,
        "label": "Severe negative evidence: segregation of duties is absent across purchase-to-pay.",
        "criteria": ["Purchase-to-pay controls"],
    },
    {
        "patterns": [
            "verbal quotation accepted",
            "verbal quotations accepted",
            "single quotation sufficient for all purchases",
            "one quotation sufficient for all purchases",
            "three quotations not required",
            "competitive tender not required",
        ],
        "cap": 1,
        "label": "Negative evidence: competitive sourcing or quotation controls are weak.",
        "criteria": ["Strategic sourcing and tender controls", "Procurement policy and procedures"],
    },
    {
        "patterns": [
            "contracts are optional",
            "contract register not required",
            "contract register is not required",
            "contracts optional",
        ],
        "cap": 1,
        "label": "Negative evidence: contract controls or contract register are optional or not required.",
        "criteria": ["Strategic sourcing and tender controls", "Procurement policy and procedures"],
    },
    {
        "patterns": [
            "kpis are not mandatory",
            "kpi not mandatory",
            "supplier kpis not mandatory",
            "performance kpis not mandatory",
        ],
        "cap": 1,
        "label": "Negative evidence: supplier or procurement KPIs are not mandatory.",
        "criteria": ["Supplier performance management", "Procurement risk and compliance monitoring"],
    },
    {
        "patterns": [
            "records may be deleted after one year",
            "records can be deleted after one year",
            "records retained for one year only",
            "procurement records may be deleted",
        ],
        "cap": 1,
        "label": "Negative evidence: procurement record retention is insufficient.",
        "criteria": ["Procurement policy and procedures", "Procurement risk and compliance monitoring"],
    },
    {
        "patterns": [
            "emergency purchases do not require approval",
            "urgent purchases do not require approval",
            "emergency procurement does not require approval",
            "emergency purchases without approval",
        ],
        "cap": 0,
        "label": "Severe negative evidence: emergency purchases do not require approval.",
        "criteria": ["Purchase-to-pay controls"],
    },
]

PROCUREMENT_POSITIVE_EVIDENCE_PATTERNS = [
    "must be approved",
    "shall be approved",
    "shall be verified",
    "must be verified",
    "mandatory",
    "documented approval",
    "segregation of duties",
    "three quotations required",
    "3 quotations required",
    "supplier due diligence required",
    "trade license required",
    "trade licence required",
    "vat/trn verification required",
    "vat verification required",
    "trn verification required",
    "sanctions screening required",
    "conflict of interest declaration required",
    "periodic supplier review required",
    "contract register maintained",
    "records retained for minimum period",
]

NEGATED_POSITIVE_EVIDENCE_PATTERNS = [
    "not mandatory",
    "not required",
    "optional",
    "without approval",
    "without review",
    "without secondary review",
    "without independent review",
    "no due diligence required",
]


def build_evidence_matrix(module_name: str, extracted_documents: list[dict]) -> pd.DataFrame:
    rows = []
    for criterion in MODULE_CONFIG[module_name]["criteria"]:
        required_evidence = criterion["evidence_required"]
        search_terms = _build_search_terms(criterion["criterion"], required_evidence)
        matches = _find_matches(search_terms, extracted_documents)
        evidence_score, score_rationale = _evidence_score(
            module_name,
            criterion["criterion"],
            matches,
            search_terms,
            extracted_documents,
        )
        positive_evidence = _positive_evidence_details(module_name, criterion["criterion"], extracted_documents)
        negative_evidence = _negative_evidence_details(module_name, criterion["criterion"], extracted_documents)
        final_score, cap_applied, final_rationale = _apply_negative_evidence_cap(
            evidence_score,
            score_rationale,
            positive_evidence,
            negative_evidence,
        )
        confidence = _confidence_level(final_score)
        compliance_status = _compliance_status(final_score)

        rows.append(
            {
                "Assessment Criteria": criterion["criterion"],
                "Required Evidence": required_evidence,
                "Evidence Found": _format_evidence_found(matches),
                "Source Documents": _format_sources(matches),
                "Positive Evidence Found": _format_detection_list(positive_evidence),
                "Negative Evidence Found": _format_detection_list(negative_evidence),
                "Negative Evidence Source": _format_detection_sources(negative_evidence),
                "Score Cap Applied": cap_applied,
                "Score Before Cap": evidence_score,
                "Score After Cap": final_score,
                "Evidence Strength": EVIDENCE_STRENGTH_LABELS[final_score],
                "Evidence Score 0-5": final_score,
                "Confidence Level": confidence,
                "Compliance Status": compliance_status,
                "Score Rationale": score_rationale,
                "Final Score Rationale": final_rationale,
            }
        )

    return pd.DataFrame(rows)


def build_evidence_register(module_name: str, extracted_documents: list[dict]) -> pd.DataFrame:
    evidence_items: dict[tuple[str, str], dict] = {}

    for criterion in MODULE_CONFIG[module_name]["criteria"]:
        criterion_name = criterion["criterion"]
        search_terms = _build_search_terms(criterion_name, criterion["evidence_required"])
        matches = _find_matches(search_terms, extracted_documents)
        positive_evidence = _positive_evidence_details(module_name, criterion_name, extracted_documents)
        negative_evidence = _negative_evidence_details(module_name, criterion_name, extracted_documents)

        for match in matches:
            source_document = match.get("document", "Unknown document")
            for term in match.get("matched_terms", []):
                extract = _extract_for_register(extracted_documents, source_document, term)
                _add_evidence_register_item(evidence_items, source_document, extract, criterion_name)

        for detection in positive_evidence + negative_evidence:
            source_document = detection.get("document", "Unknown document")
            extract = detection.get("snippet", detection.get("pattern", ""))
            _add_evidence_register_item(evidence_items, source_document, extract, criterion_name)

    rows = []
    for index, item in enumerate(evidence_items.values(), start=1):
        rows.append(
            {
                "Evidence ID": f"EV-{index:03d}",
                "Source Document": item["Source Document"],
                "Extract": item["Extract"],
                "Affected Criteria": "; ".join(sorted(item["Affected Criteria"])),
            }
        )
    return pd.DataFrame(rows, columns=["Evidence ID", "Source Document", "Extract", "Affected Criteria"])


def build_procurement_evidence_detail_table(extracted_documents: list[dict]) -> pd.DataFrame:
    module_name = "Procurement Assessment"
    rows = []

    for criterion in MODULE_CONFIG[module_name]["criteria"]:
        criterion_name = criterion["criterion"]
        search_terms = _build_search_terms(criterion_name, criterion["evidence_required"])
        matches = _find_matches(search_terms, extracted_documents)
        score_before_cap, _ = _evidence_score(
            module_name,
            criterion_name,
            matches,
            search_terms,
            extracted_documents,
        )
        positive = _positive_evidence_details(module_name, criterion_name, extracted_documents)
        negative = _negative_evidence_details(module_name, criterion_name, extracted_documents)
        score_after_cap, _, _ = _apply_negative_evidence_cap(
            score_before_cap,
            "",
            positive,
            negative,
        )

        statements: dict[tuple[str, str], dict] = {}

        def add_statement(source: str, sentence: str, positive_label: str = "", negative_label: str = "") -> None:
            exact_sentence = _normalize_space(sentence)
            if not exact_sentence:
                return
            key = (source.lower(), _normalize_for_policy_detection(exact_sentence))
            if key not in statements:
                statements[key] = {
                    "source": source,
                    "sentence": exact_sentence,
                    "positive": [],
                    "negative": [],
                }
            if positive_label and positive_label not in statements[key]["positive"]:
                statements[key]["positive"].append(positive_label)
            if negative_label and negative_label not in statements[key]["negative"]:
                statements[key]["negative"].append(negative_label)

        negative_sentences = {
            (
                str(item.get("document", "Unknown document")).lower(),
                _normalize_for_policy_detection(str(item.get("snippet", ""))),
            )
            for item in negative
        }

        for match in matches:
            source = str(match.get("document", "Unknown document"))
            sentence_terms: dict[str, list[str]] = {}
            for term in match.get("matched_terms", []):
                sentence = _extract_for_register(extracted_documents, source, term)
                normalized = _normalize_for_policy_detection(sentence)
                if not sentence or _sentence_contains_negated_positive(sentence):
                    continue
                if (source.lower(), normalized) in negative_sentences:
                    continue
                sentence_terms.setdefault(sentence, []).append(term)
            for sentence, terms in sentence_terms.items():
                add_statement(
                    source,
                    sentence,
                    positive_label=f"Matched evidence terms: {', '.join(dict.fromkeys(terms))}",
                )

        for item in positive:
            add_statement(
                str(item.get("document", "Unknown document")),
                str(item.get("snippet", item.get("pattern", ""))),
                positive_label=str(item.get("label", item.get("pattern", "Positive control evidence"))),
            )

        for item in negative:
            add_statement(
                str(item.get("document", "Unknown document")),
                str(item.get("snippet", item.get("pattern", ""))),
                negative_label=str(item.get("label", item.get("pattern", "Negative control evidence"))),
            )

        if not statements:
            rows.append(
                {
                    "Criterion": criterion_name,
                    "Positive Evidence Found": "None",
                    "Negative Evidence Found": "None",
                    "Source File": "None",
                    "Exact Sentence": "No relevant evidence sentence was identified.",
                    "Score Before Cap": score_before_cap,
                    "Score After Cap": score_after_cap,
                }
            )
            continue

        for statement in statements.values():
            rows.append(
                {
                    "Criterion": criterion_name,
                    "Positive Evidence Found": "; ".join(statement["positive"]) or "None",
                    "Negative Evidence Found": "; ".join(statement["negative"]) or "None",
                    "Source File": statement["source"],
                    "Exact Sentence": statement["sentence"],
                    "Score Before Cap": score_before_cap,
                    "Score After Cap": score_after_cap,
                }
            )

    return pd.DataFrame(
        rows,
        columns=[
            "Criterion",
            "Positive Evidence Found",
            "Negative Evidence Found",
            "Source File",
            "Exact Sentence",
            "Score Before Cap",
            "Score After Cap",
        ],
    )


def evidence_scores_from_matrix(evidence_matrix: pd.DataFrame) -> dict[str, int]:
    if evidence_matrix.empty or "Evidence Score 0-5" not in evidence_matrix:
        return {}
    return {
        str(row["Assessment Criteria"]): int(row["Evidence Score 0-5"])
        for _, row in evidence_matrix.iterrows()
    }


def evidence_rationales_from_matrix(evidence_matrix: pd.DataFrame) -> dict[str, str]:
    rationale_column = "Final Score Rationale" if "Final Score Rationale" in evidence_matrix else "Score Rationale"
    if evidence_matrix.empty or rationale_column not in evidence_matrix:
        return {}
    return {
        str(row["Assessment Criteria"]): str(row[rationale_column])
        for _, row in evidence_matrix.iterrows()
    }


def evidence_matrix_to_context(evidence_matrix: pd.DataFrame) -> str:
    if evidence_matrix.empty:
        return "No evidence mapping results available."
    return evidence_matrix.to_string(index=False)


def evidence_register_to_context(evidence_register: pd.DataFrame) -> str:
    if evidence_register.empty:
        return "No uploaded-document evidence statements were identified."
    return evidence_register.to_string(index=False)


def _build_search_terms(criterion: str, required_evidence: str) -> list[str]:
    phrases = []
    for text in (criterion, required_evidence):
        phrases.extend(re.findall(r"[A-Za-z0-9][A-Za-z0-9 /&-]{2,}", text))

    words = re.findall(r"[A-Za-z][A-Za-z-]{2,}", f"{criterion} {required_evidence}".lower())
    terms = []

    for phrase in phrases:
        cleaned = _normalize_space(phrase.lower().strip(" .,;:()"))
        if 3 <= len(cleaned) <= 80 and cleaned not in STOP_WORDS:
            terms.append(cleaned)

    for word in words:
        word = word.strip("-")
        if len(word) >= 4 and word not in STOP_WORDS:
            terms.append(word)

    deduped = []
    for term in terms:
        if term not in deduped:
            deduped.append(term)
    return deduped[:16]


def _find_matches(search_terms: list[str], extracted_documents: list[dict]) -> list[dict]:
    matches = []
    for document in extracted_documents:
        content = document.get("content", "")
        normalized_content = content.lower()
        matched_terms = []
        snippets = []

        for term in search_terms:
            if term in normalized_content:
                matched_terms.append(term)
                snippet = _snippet(content, term)
                if snippet and snippet not in snippets:
                    snippets.append(snippet)

        if matched_terms:
            matches.append(
                {
                    "document": document.get("name", "Unknown document"),
                    "matched_terms": matched_terms,
                    "snippets": snippets[:2],
                }
            )
    return matches


def _extract_for_register(extracted_documents: list[dict], source_document: str, term: str) -> str:
    for document in extracted_documents:
        if document.get("name", "Unknown document") != source_document:
            continue
        content = str(document.get("content", ""))
        sentence = _sentence_with_pattern(content, term)
        if sentence:
            return _normalize_space(sentence)
        return _snippet(content, term, radius=140) or term
    return term


def _add_evidence_register_item(
    evidence_items: dict[tuple[str, str], dict],
    source_document: str,
    extract: str,
    criterion_name: str,
) -> None:
    cleaned_extract = _normalize_space(str(extract))
    if not cleaned_extract or cleaned_extract.lower() in {"none", "no relevant evidence found in uploaded documents."}:
        return

    key = (source_document, _normalize_for_policy_detection(cleaned_extract))
    if key not in evidence_items:
        evidence_items[key] = {
            "Source Document": source_document,
            "Extract": cleaned_extract,
            "Affected Criteria": set(),
        }
    evidence_items[key]["Affected Criteria"].add(criterion_name)


def _evidence_score(
    module_name: str,
    criterion: str,
    matches: list[dict],
    search_terms: list[str],
    extracted_documents: list[dict],
) -> tuple[int, str]:
    procurement_score = _procurement_evidence_score(module_name, criterion, extracted_documents)
    if procurement_score is not None:
        return procurement_score

    finance_score = _finance_audit_evidence_score(module_name, criterion, extracted_documents)
    if finance_score is not None:
        return finance_score

    if not matches or not search_terms:
        return 0, "No relevant document evidence was identified for this criterion."

    matched_terms = {term for match in matches for term in match["matched_terms"]}
    coverage = len(matched_terms) / len(search_terms)
    document_count = len(matches)

    if coverage >= 0.65 and document_count >= 3:
        score = 5
    elif coverage >= 0.45 or (coverage >= 0.35 and document_count >= 2):
        score = 4
    elif coverage >= 0.25 or document_count >= 2:
        score = 3
    elif coverage >= 0.12:
        score = 2
    else:
        score = 1

    rationale = (
        f"{EVIDENCE_STRENGTH_LABELS[score]}: matched {len(matched_terms)} of "
        f"{len(search_terms)} evidence terms across {document_count} document(s)."
    )
    return score, rationale


def _positive_evidence_details(
    module_name: str,
    criterion: str,
    extracted_documents: list[dict],
) -> list[dict]:
    if module_name != "Procurement Assessment":
        return []
    detections = _find_pattern_evidence(
        PROCUREMENT_POSITIVE_EVIDENCE_PATTERNS,
        extracted_documents,
        exclude_negated=True,
    )
    criterion_config = next(
        item for item in MODULE_CONFIG[module_name]["criteria"] if item["criterion"] == criterion
    )
    generic_terms = {
        "approval",
        "approved",
        "mandatory",
        "required",
        "review",
        "verified",
        "documented",
        "records",
    }
    relevant_terms = [
        term
        for term in _build_search_terms(criterion, criterion_config["evidence_required"])
        if term not in generic_terms and len(term) >= 4
    ]
    return [
        detection
        for detection in detections
        if any(
            term in _normalize_for_policy_detection(
                f"{detection.get('document', '')} {detection.get('snippet', '')}"
            )
            for term in relevant_terms
        )
    ]


def _negative_evidence_details(
    module_name: str,
    criterion: str,
    extracted_documents: list[dict],
) -> list[dict]:
    if module_name != "Procurement Assessment":
        return []

    criterion_text = criterion.lower()
    detections = []
    for rule in PROCUREMENT_NEGATIVE_EVIDENCE_RULES:
        if not _rule_applies_to_criterion(rule, criterion_text):
            continue
        for detection in _find_pattern_evidence(rule["patterns"], extracted_documents):
            detection["cap"] = int(rule["cap"])
            detection["label"] = rule["label"]
            detections.append(detection)
    return detections


def _rule_applies_to_criterion(rule: dict, criterion_text: str) -> bool:
    criteria = rule.get("criteria", [])
    return any(str(criterion).lower() in criterion_text for criterion in criteria)


def _find_pattern_evidence(
    patterns: list[str],
    extracted_documents: list[dict],
    exclude_negated: bool = False,
) -> list[dict]:
    detections = []
    for document in extracted_documents:
        content = str(document.get("content", ""))
        for pattern in patterns:
            sentence = _sentence_with_pattern(content, pattern)
            if sentence:
                if exclude_negated and _sentence_contains_negated_positive(sentence):
                    continue
                detections.append(
                    {
                        "document": document.get("name", "Unknown document"),
                        "pattern": pattern,
                        "snippet": _normalize_space(sentence) or _snippet(content, pattern, radius=110) or pattern,
                    }
                )
    return detections


def _apply_negative_evidence_cap(
    base_score: int,
    base_rationale: str,
    positive_evidence: list[dict],
    negative_evidence: list[dict],
) -> tuple[int, str, str]:
    if not negative_evidence:
        positive_note = ""
        if positive_evidence:
            positive_note = f" Positive control evidence also found: {_format_detection_list(positive_evidence)}."
        return base_score, NEGATIVE_CAP_NONE, f"{base_rationale}{positive_note}"

    cap = min(int(item.get("cap", 1)) for item in negative_evidence)
    final_score = min(base_score, cap)
    cap_label = f"Score capped at {cap} due to negative evidence"
    strongest = [item for item in negative_evidence if int(item.get("cap", 1)) == cap]
    negative_note = _format_detection_list(strongest)
    return (
        final_score,
        cap_label,
        (
            f"{base_rationale} Negative evidence found: {negative_note}. "
            f"{cap_label}; final score is {final_score}/5."
        ),
    )


def _confidence_level(evidence_score: int) -> str:
    if evidence_score <= 1:
        return "Low"
    if evidence_score >= 4:
        return "High"
    return "Medium"


def _compliance_status(evidence_score: int) -> str:
    if evidence_score >= 4:
        return "Compliant"
    if evidence_score >= 2:
        return "Partially Compliant"
    return "Non-Compliant"


def _procurement_evidence_score(
    module_name: str,
    criterion: str,
    extracted_documents: list[dict],
) -> tuple[int, str] | None:
    if module_name != "Procurement Assessment":
        return None

    criterion_text = criterion.lower()
    corpus = _document_corpus(extracted_documents)
    doc_names = " ".join(str(document.get("name", "")) for document in extracted_documents).lower()

    has_rfq = _contains_any(corpus, ["rfq", "request for quotation", "request for quote"])
    quote_count = _count_quote_evidence(extracted_documents)
    has_evaluation = _contains_any(corpus, ["evaluation sheet", "evaluation matrix", "bid evaluation", "technical evaluation", "commercial evaluation"])
    has_award = _contains_any(corpus, ["award recommendation", "award memo"]) or _contains_positive_evidence_any(
        extracted_documents,
        ["award approval", "approval"],
    )
    has_supplier_assessment = _contains_positive_evidence_any(
        extracted_documents,
        ["supplier assessment", "supplier evaluation", "vendor assessment", "vendor evaluation", "supplier scorecard"],
    )
    has_po = _contains_any(corpus, ["purchase order", " po ", "po number", "lpo"])
    has_grn = _contains_any(corpus, ["goods received note", "goods receipt note", " grn ", "goods receipt"])
    has_invoice = _contains_any(corpus, ["invoice", "three-way match", "3-way match", "payment approval"])
    has_policy = _contains_any(corpus, ["procurement policy", "sop", "procedure", "delegation of authority", "approval workflow"])
    has_spend = _contains_any(corpus, ["spend dashboard", "spend report", "spend cube", "savings dashboard"])
    has_risk = _contains_any(corpus, ["risk register", "audit finding", "compliance report", "remediation"])
    has_system = _contains_any(corpus, ["erp", "e-procurement", "system workflow", "automation", "access matrix"])
    has_category = _contains_any(corpus, ["category plan", "category strategy", "demand forecast", "sourcing calendar"])

    strong_policy_controls = _contains_positive_evidence_any(
        extracted_documents,
        [
            "must be approved",
            "shall be approved",
            "shall be verified",
            "mandatory",
            "documented approval",
            "segregation of duties",
            "delegation of authority",
            "conflict of interest declaration required",
            "records retained for minimum period",
        ],
    )
    strong_due_diligence = _contains_positive_evidence_any(
        extracted_documents,
        [
            "supplier due diligence required",
            "trade license required",
            "trade licence required",
            "vat/trn verification required",
            "vat verification required",
            "trn verification required",
            "sanctions screening required",
        ],
    )
    strong_sourcing_controls = _contains_positive_evidence_any(
        extracted_documents,
        ["three quotations required", "3 quotations required", "evaluation criteria must", "award approval required"],
    )
    strong_contract_controls = _contains_positive_evidence_any(
        extracted_documents,
        ["contract register maintained", "contract register must", "contracts must be approved"],
    )

    if "strategic sourcing" in criterion_text or "tender" in criterion_text:
        if has_rfq and quote_count >= 3 and has_evaluation and strong_sourcing_controls:
            return 5, "Best Practice Evidence: RFQ, at least three quotations, evaluation evidence, and mandatory sourcing controls were found."
        if has_rfq and quote_count >= 3 and has_evaluation and has_award:
            return 5, "Best Practice Evidence: RFQ, at least three quotations, evaluation evidence, and award approval were found."
        if has_rfq and quote_count >= 3 and has_evaluation:
            return 4, "Strong Evidence: RFQ, at least three quotations, and an evaluation sheet were found."
        if has_rfq and quote_count >= 1 and has_evaluation:
            return 3, "Moderate Evidence: RFQ, quotation evidence, and evaluation evidence were found."
        if has_rfq and quote_count >= 1:
            return 2, "Partial Evidence: RFQ and quotation evidence were found, but evaluation or award evidence is incomplete."
        if has_rfq or quote_count >= 1 or has_evaluation:
            return 1, "Weak Evidence: one sourcing artifact was found, but the sourcing file is incomplete."

    if "supplier due diligence" in criterion_text or "onboarding" in criterion_text:
        if has_supplier_assessment and strong_due_diligence and _contains_any(corpus, ["approval", "approved", "secondary review"]):
            return 5, "Best Practice Evidence: supplier assessment, mandatory due diligence checks, and approval control evidence were found."
        if strong_due_diligence and _contains_any(corpus, ["approval", "approved", "secondary review"]):
            return 4, "Strong Evidence: mandatory supplier due diligence and approval control evidence were found."
        if has_supplier_assessment and _contains_any(corpus, ["kyc", "sanctions", "esg check", "approval"]):
            return 4, "Strong Evidence: supplier assessment plus due diligence or approval evidence was found."
        if has_supplier_assessment:
            return 3, "Moderate Evidence: supplier assessment form or supplier evaluation evidence was found."

    if "supplier performance" in criterion_text:
        if has_supplier_assessment and _contains_positive_evidence_any(
            extracted_documents,
            ["kpi", "sla", "corrective action", "review meeting"],
        ):
            return 4, "Strong Evidence: supplier assessment and performance review or KPI evidence were found."
        if has_supplier_assessment:
            return 3, "Moderate Evidence: supplier assessment or scorecard evidence was found."

    if "purchase-to-pay" in criterion_text:
        if has_po and has_grn and has_invoice and strong_policy_controls:
            return 5, "Best Practice Evidence: purchase order, GRN, invoice or three-way match evidence, and mandatory approval or segregation controls were found."
        if has_po and has_grn and has_invoice:
            return 4, "Strong Evidence: purchase order, GRN, and invoice or three-way match evidence were found."
        if has_po and has_grn:
            return 3, "Moderate Evidence: purchase order and GRN evidence were found."
        if has_po or has_grn:
            return 2, "Partial Evidence: one purchase-to-pay control document was found."

    if "policy" in criterion_text and has_policy and strong_policy_controls and strong_contract_controls:
        return 5, "Best Practice Evidence: procurement policy, mandatory approval/segregation controls, and contract register controls were found."
    if "policy" in criterion_text and has_policy and strong_policy_controls:
        return 4, "Strong Evidence: procurement policy and mandatory approval, verification, segregation, or retention controls were found."
    if "policy" in criterion_text and has_policy:
        return 3, "Moderate Evidence: procurement policy, procedure, delegation, or approval workflow evidence was found."
    if "policy" in criterion_text and has_evaluation and has_award:
        return 2, "Partial Evidence: quote evaluation and approval trail evidence were found, but policy or SOP evidence is incomplete."
    if "spend" in criterion_text and has_spend:
        return 3, "Moderate Evidence: spend reporting or dashboard evidence was found."
    if "risk" in criterion_text and has_risk and (strong_due_diligence or strong_policy_controls):
        return 4, "Strong Evidence: risk, compliance, audit, or remediation evidence plus mandatory control requirements were found."
    if "risk" in criterion_text and has_risk:
        return 3, "Moderate Evidence: risk, compliance, audit, or remediation evidence was found."
    if "technology" in criterion_text and has_system:
        return 3, "Moderate Evidence: system workflow, ERP, access, or automation evidence was found."
    if "category" in criterion_text and has_category:
        return 3, "Moderate Evidence: category plan, demand forecast, or sourcing calendar evidence was found."
    if "category" in criterion_text and (has_rfq or quote_count >= 1 or "purchase" in corpus or "supplier" in corpus):
        return 1, "Weak Evidence: purchasing, supplier, or quotation language was found, but category planning evidence is missing."
    if "strategy" in criterion_text and (has_policy or "strategy" in doc_names):
        return 3, "Moderate Evidence: procurement policy or strategy documentation was found, indicating a basic operating model."

    return None


def _document_corpus(extracted_documents: list[dict]) -> str:
    parts = []
    for document in extracted_documents:
        parts.append(str(document.get("name", "")))
        parts.append(str(document.get("content", "")))
    return f" {' '.join(parts).lower()} "


def _contains_any(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)


def _contains_positive_evidence_any(extracted_documents: list[dict], patterns: list[str]) -> bool:
    for document in extracted_documents:
        content = f"{document.get('name', '')}\n{document.get('content', '')}"
        for pattern in patterns:
            sentence = _sentence_with_pattern(content, pattern)
            if sentence and not _sentence_contains_negated_positive(sentence):
                return True
    return False


def _sentence_with_pattern(content: str, pattern: str) -> str:
    normalized_pattern = _normalize_for_policy_detection(pattern)
    if not normalized_pattern:
        return ""

    for sentence in _split_sentences(content):
        if normalized_pattern in _normalize_for_policy_detection(sentence):
            return sentence
    return ""


def _sentence_contains_negated_positive(sentence: str) -> bool:
    normalized_sentence = _normalize_for_policy_detection(sentence)
    return any(
        _normalize_for_policy_detection(pattern) in normalized_sentence
        for pattern in NEGATED_POSITIVE_EVIDENCE_PATTERNS
    )


def _split_sentences(content: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+|\n+", content)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def _count_quote_evidence(extracted_documents: list[dict]) -> int:
    count = 0
    for document in extracted_documents:
        text = f"{document.get('name', '')} {document.get('content', '')}".lower()
        if any(term in text for term in ["quotation", "quote", "supplier quote", "vendor quote"]):
            count += 1
    corpus = _document_corpus(extracted_documents)
    explicit_count = re.search(r"\b([3-9])\s+(quotes|quotations)\b", corpus)
    if explicit_count:
        count = max(count, int(explicit_count.group(1)))
    return count


def _finance_audit_evidence_score(
    module_name: str,
    criterion: str,
    extracted_documents: list[dict],
) -> tuple[int, str] | None:
    if module_name != "Finance Audit Assessment":
        return None

    criterion_text = criterion.lower()
    corpus = _document_corpus(extracted_documents)

    has_finance_policy = _contains_any(corpus, ["finance policy", "accounting policy", "accounting manual", "financial control framework"])
    has_doa = _contains_any(corpus, ["doa matrix", "delegation of authority", "approval matrix", "approval workflow"])
    has_budget = _contains_any(corpus, ["budget", "budget variance", "forecast", "budgetary control"])
    has_ap = _contains_any(corpus, ["ap aging", "accounts payable", "supplier invoice", "invoice sample", "payment approval"])
    has_matching = _contains_any(corpus, ["po invoice matching", "three-way match", "3-way match", "purchase order", "grn", "goods received note"])
    has_ar = _contains_any(corpus, ["ar aging", "accounts receivable", "customer statement", "collection", "credit note"])
    has_bank = _contains_any(corpus, ["bank reconciliation", "bank rec", "cash count", "bank signatory", "unreconciled"])
    has_fixed_asset = _contains_any(corpus, ["fixed asset register", "asset register", "asset tagging", "physical verification", "disposal approval"])
    has_vat = _contains_any(corpus, ["vat return", "vat reconciliation", "tax invoice", "tax working", "fta", "tax compliance"])
    has_reporting = _contains_any(corpus, ["trial balance", "financial statements", "balance sheet reconciliation", "close checklist", "month-end close"])
    has_internal_audit = _contains_any(corpus, ["internal audit report", "audit finding", "risk register", "control testing", "remediation action"])

    if "financial governance" in criterion_text:
        if has_finance_policy and has_doa:
            return 4, "Strong Evidence: finance policy and authority control evidence were found."
        if has_finance_policy:
            return 3, "Moderate Evidence: finance policy or accounting manual evidence was found."

    if "delegation" in criterion_text or "approval controls" in criterion_text:
        if has_doa and _contains_any(corpus, ["sampled approval", "approval evidence", "exception report"]):
            return 4, "Strong Evidence: DOA matrix and approval testing evidence were found."
        if has_doa:
            return 3, "Moderate Evidence: DOA matrix or approval workflow evidence was found."

    if "budget" in criterion_text:
        if has_budget and _contains_any(corpus, ["variance review", "management review", "forecast update"]):
            return 4, "Strong Evidence: budget and variance review evidence were found."
        if has_budget:
            return 3, "Moderate Evidence: budget or budget variance evidence was found."

    if "accounts payable" in criterion_text:
        if has_ap and has_matching:
            return 4, "Strong Evidence: AP aging or invoice evidence plus PO/GRN matching support were found."
        if has_ap:
            return 3, "Moderate Evidence: accounts payable aging, invoice, or payment approval evidence was found."
        if has_matching:
            return 2, "Partial Evidence: purchase order, GRN, or matching support was found without AP aging evidence."

    if "accounts receivable" in criterion_text:
        if has_ar and _contains_any(corpus, ["collection follow-up", "bad debt", "credit review"]):
            return 4, "Strong Evidence: AR aging and collection or credit review evidence were found."
        if has_ar:
            return 3, "Moderate Evidence: AR aging or customer statement evidence was found."

    if "bank" in criterion_text or "cash" in criterion_text:
        if has_bank and _contains_any(corpus, ["review sign-off", "cash count", "bank signatory"]):
            return 4, "Strong Evidence: bank reconciliation and review, cash, or signatory evidence were found."
        if has_bank:
            return 3, "Moderate Evidence: bank reconciliation or cash control evidence was found."

    if "fixed asset" in criterion_text:
        if has_fixed_asset and _contains_any(corpus, ["physical verification", "asset tagging", "disposal approval"]):
            return 4, "Strong Evidence: fixed asset register plus verification or disposal evidence were found."
        if has_fixed_asset:
            return 3, "Moderate Evidence: fixed asset register evidence was found."

    if "tax" in criterion_text or "vat" in criterion_text:
        if has_vat and _contains_any(corpus, ["filing", "payment evidence", "vat reconciliation"]):
            return 4, "Strong Evidence: VAT return and reconciliation, filing, or payment evidence were found."
        if has_vat:
            return 3, "Moderate Evidence: VAT return or tax working evidence was found."

    if "financial reporting" in criterion_text or "reconciliations" in criterion_text:
        if has_reporting and _contains_any(corpus, ["review sign-off", "close checklist", "financial statements"]):
            return 4, "Strong Evidence: reporting package and reconciliation or close review evidence were found."
        if has_reporting:
            return 3, "Moderate Evidence: trial balance, financial statement, or reconciliation evidence was found."

    if "internal audit" in criterion_text or "risk" in criterion_text:
        if has_internal_audit and _contains_any(corpus, ["action tracker", "remediation", "control testing"]):
            return 4, "Strong Evidence: internal audit, risk, and remediation monitoring evidence were found."
        if has_internal_audit:
            return 3, "Moderate Evidence: internal audit report or risk monitoring evidence was found."

    return None


def _format_evidence_found(matches: list[dict]) -> str:
    if not matches:
        return "No relevant evidence found in uploaded documents."

    evidence = []
    for match in matches:
        terms = ", ".join(match["matched_terms"][:8])
        snippets = " | ".join(match["snippets"])
        if snippets:
            evidence.append(f"{match['document']}: matched {terms}. Snippet: {snippets}")
        else:
            evidence.append(f"{match['document']}: matched {terms}.")
    return "\n".join(evidence)


def _format_sources(matches: list[dict]) -> str:
    if not matches:
        return "None"
    return ", ".join(match["document"] for match in matches)


def _format_detection_list(detections: list[dict]) -> str:
    if not detections:
        return "None"
    parts = []
    seen = set()
    for detection in detections:
        label = detection.get("label") or detection.get("pattern", "")
        snippet = detection.get("snippet", "")
        text = f"{detection.get('document', 'Unknown document')}: {label}"
        if snippet:
            text += f" ({snippet})"
        if text not in seen:
            seen.add(text)
            parts.append(text)
    return " | ".join(parts[:8])


def _format_detection_sources(detections: list[dict]) -> str:
    if not detections:
        return "None"
    sources = []
    for detection in detections:
        source = detection.get("document", "Unknown document")
        if source not in sources:
            sources.append(source)
    return ", ".join(sources)


def _snippet(content: str, term: str, radius: int = 90) -> str:
    index = content.lower().find(term.lower())
    if index < 0:
        return ""
    start = max(0, index - radius)
    end = min(len(content), index + len(term) + radius)
    return _normalize_space(content[start:end])


def _normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _normalize_for_policy_detection(text: str) -> str:
    text = text.lower()
    text = text.replace("/", " ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return _normalize_space(text)
