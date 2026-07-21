from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4
import json
import os
import tempfile


@dataclass(frozen=True)
class EvidenceRecord:
    title: str
    source_type: str
    source_url: str
    citation: str
    publication_date: str
    source_version: str
    evidence_level: str
    population: str
    applicability: str
    limitations: tuple[str, ...]
    registered_by: str
    evidence_id: str = field(default_factory=lambda: str(uuid4()))
    registered_at: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )

    def validate(self) -> None:
        if not self.title.strip() or not self.citation.strip():
            raise ValueError("EVIDENCE_TITLE_AND_CITATION_REQUIRED")
        parsed = urlparse(self.source_url)
        if parsed.scheme not in {"https", "http"} or not parsed.netloc:
            raise ValueError("VALID_EVIDENCE_URL_REQUIRED")
        if not self.limitations:
            raise ValueError("EVIDENCE_LIMITATIONS_REQUIRED")
        if not self.source_version.strip() or not self.population.strip():
            raise ValueError("EVIDENCE_VERSION_AND_POPULATION_REQUIRED")
        try:
            datetime.fromisoformat(self.publication_date)
        except ValueError as exc:
            raise ValueError("VALID_EVIDENCE_PUBLICATION_DATE_REQUIRED") from exc
        allowed_source_types = {
            "peer_reviewed_article",
            "preprint",
            "official_guidance",
            "technical_standard",
            "dataset_documentation",
            "registered_protocol",
        }
        if self.source_type not in allowed_source_types:
            raise ValueError("UNSUPPORTED_EVIDENCE_SOURCE_TYPE")
        allowed_levels = {
            "systematic_review_meta_analysis",
            "randomized_controlled_trial",
            "controlled_observational",
            "observational",
            "measurement_validation",
            "guideline_consensus",
            "regulatory_standard",
            "primary_technical_standard",
            "other_peer_reviewed",
            "preprint_not_peer_reviewed",
        }
        if self.evidence_level not in allowed_levels:
            raise ValueError("UNSUPPORTED_EVIDENCE_LEVEL")


class EvidenceRegistry:
    """Versioned scientific-source registry; it never invents or fetches citations."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def register(self, record: EvidenceRecord) -> dict[str, Any]:
        record.validate()
        data = self._load()
        data.append(asdict(record))
        self._write(data)
        return asdict(record)

    def get(self, evidence_id: str) -> dict[str, Any] | None:
        return next(
            (item for item in self._load() if item["evidence_id"] == evidence_id),
            None,
        )

    def list_all(self) -> list[dict[str, Any]]:
        return self._load()

    def _load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("INVALID_EVIDENCE_REGISTRY")
        return data

    def _write(self, data: list[dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(
            prefix=self.path.name,
            dir=self.path.parent,
            text=True,
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(data, handle, ensure_ascii=False, indent=2)
            os.replace(temp_name, self.path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
