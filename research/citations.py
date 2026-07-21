from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


CITATION_SCHEMA_VERSION = "health-model-citation-collection-1"
STYLES = {
    "apa7": "APA 7",
    "vancouver": "Vancouver / ICMJE",
    "ama11": "AMA 11",
    "chicago_author_date": "Chicago author-date",
    "harvard": "Harvard",
    "ieee": "IEEE",
}
SOURCE_TYPES = {
    "journal_article": "Journal article",
    "book": "Book",
    "book_chapter": "Book chapter",
    "conference_paper": "Conference paper",
    "preprint": "Preprint",
    "dataset": "Dataset",
    "software": "Software",
    "webpage": "Web page",
}
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.I)


def citation_contract() -> dict[str, Any]:
    return {
        "schema_version": CITATION_SCHEMA_VERSION,
        "source_types": SOURCE_TYPES,
        "styles": STYLES,
        "author_schema": {"family": "string", "given": "string"},
        "identifiers": ["doi", "pmid", "isbn", "url"],
        "required_common": ["type", "title"],
        "required_by_type": {
            "journal_article": ["authors", "year", "container_title"],
            "book": ["authors", "year", "publisher"],
            "book_chapter": ["authors", "year", "container_title", "publisher"],
            "conference_paper": ["authors", "year", "container_title"],
            "preprint": ["authors", "year"],
            "dataset": ["authors", "year", "publisher"],
            "software": ["authors", "year"],
            "webpage": ["url", "accessed_at"],
        },
        "invariants": [
            "registered_source_identity_is_preserved",
            "formatting_does_not_change_source_content",
            "missing_bibliographic_data_is_reported_not_invented",
            "saved_collection_is_versioned_and_uses_utc",
        ],
    }


def _clean(value: Any) -> str:
    return str(value or "").strip()


def normalize_reference(raw: dict[str, Any]) -> dict[str, Any]:
    source_type = _clean(raw.get("type"))
    authors = []
    for author in raw.get("authors") or []:
        family, given = _clean(author.get("family")), _clean(author.get("given"))
        if family or given:
            authors.append({"family": family, "given": given})
    return {
        "id": _clean(raw.get("id")) or str(uuid4()),
        "type": source_type,
        "title": _clean(raw.get("title")),
        "authors": authors,
        "year": _clean(raw.get("year")),
        "container_title": _clean(raw.get("container_title")),
        "volume": _clean(raw.get("volume")),
        "issue": _clean(raw.get("issue")),
        "pages": _clean(raw.get("pages")),
        "publisher": _clean(raw.get("publisher")),
        "edition": _clean(raw.get("edition")),
        "doi": _clean(raw.get("doi")).removeprefix("https://doi.org/"),
        "pmid": _clean(raw.get("pmid")),
        "isbn": _clean(raw.get("isbn")),
        "url": _clean(raw.get("url")),
        "accessed_at": _clean(raw.get("accessed_at")),
        "registered_source_ref": _clean(raw.get("registered_source_ref")),
    }


def validate_reference(reference: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    source_type = reference.get("type", "")
    if source_type not in SOURCE_TYPES:
        issues.append({"field": "type", "code": "SOURCE_TYPE_UNSUPPORTED"})
    for field in ["type", "title"]:
        if not reference.get(field):
            issues.append({"field": field, "code": "REQUIRED_FIELD_MISSING"})
    requirements = citation_contract()["required_by_type"].get(source_type, [])
    for field in requirements:
        if not reference.get(field):
            issues.append({"field": field, "code": "REQUIRED_FIELD_MISSING"})
    year = reference.get("year")
    if year and (not str(year).isdigit() or not 1000 <= int(year) <= 3000):
        issues.append({"field": "year", "code": "YEAR_INVALID"})
    doi = reference.get("doi")
    if doi and not DOI_RE.match(doi):
        issues.append({"field": "doi", "code": "DOI_INVALID"})
    url = reference.get("url")
    if url and not (url.startswith("https://") or url.startswith("http://")):
        issues.append({"field": "url", "code": "URL_INVALID"})
    return issues


def _authors(reference: dict[str, Any], style: str) -> str:
    people = reference.get("authors") or []
    if not people:
        raise ValueError("CITATION_AUTHORS_REQUIRED_FOR_FORMATTING")
    if style in {"vancouver", "ama11", "ieee"}:
        return ", ".join(f"{a['family']} {''.join(p[:1] for p in a['given'].split())}".strip() for a in people)
    return ", ".join(f"{a['family']}, {a['given']}".strip(", ") for a in people)


def format_reference(reference: dict[str, Any], style: str, number: int = 1) -> str:
    if style not in STYLES:
        raise ValueError("CITATION_STYLE_UNSUPPORTED")
    title = reference.get("title")
    if not title:
        raise ValueError("CITATION_TITLE_REQUIRED_FOR_FORMATTING")
    year = reference.get("year") or "n.d."
    if reference.get("type") == "webpage" and not reference.get("authors"):
        accessed = f" Accessed {reference['accessed_at']}." if reference.get("accessed_at") else ""
        return f"{title}. ({year}). {reference.get('url', '')}.{accessed}".replace("..", ".").strip()
    authors = _authors(reference, style)
    container = reference.get("container_title") or reference.get("publisher") or ""
    details = ", ".join(x for x in [reference.get("volume"), reference.get("issue"), reference.get("pages")] if x)
    locator = f"https://doi.org/{reference['doi']}" if reference.get("doi") else reference.get("url", "")
    if style == "apa7":
        return f"{authors} ({year}). {title}. {container}{', ' if details else ''}{details}. {locator}".strip()
    if style in {"vancouver", "ama11"}:
        return f"{authors}. {title}. {container}. {year};{details}. {locator}".replace("..", ".").strip()
    if style == "ieee":
        return f"[{number}] {authors}, “{title},” {container}, {details}, {year}. {locator}".strip()
    return f"{authors}. {year}. “{title}.” {container}{', ' if details else ''}{details}. {locator}".strip()


def build_citation_collection(*, title: str, destination: str, style: str,
                              requirements_source: str = "",
                              references: list[dict[str, Any]], version: int = 1) -> dict[str, Any]:
    if style not in STYLES:
        raise ValueError("CITATION_STYLE_UNSUPPORTED")
    normalized = [normalize_reference(item) for item in references]
    validation = []
    formatted = []
    for index, reference in enumerate(normalized, 1):
        issues = validate_reference(reference)
        validation.append({"reference_id": reference["id"], "valid": not issues, "issues": issues})
        formatted.append({
            "reference_id": reference["id"],
            "status": "formatted" if not issues else "blocked_by_validation",
            "text": format_reference(reference, style, index) if not issues else None,
        })
    return {
        "schema_version": CITATION_SCHEMA_VERSION,
        "title": title.strip(),
        "target_destination": destination.strip(),
        "requirements_source": requirements_source.strip(),
        "style": style,
        "style_label": STYLES[style],
        "version": version,
        "references": normalized,
        "formatted_references": formatted,
        "validation": {"valid": all(x["valid"] for x in validation), "references": validation},
        "generated_at": datetime.now(UTC).isoformat(),
    }
