from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4
import json
import os
import tempfile

from .contracts import LearningStatus, RayRole


@dataclass
class LearningCandidate:
    role: RayRole
    submitted_by: str
    target_type: str
    target_id: str
    feedback: str
    expected_behavior: str
    context_scope: str
    contains_participant_data: bool = False
    candidate_id: str = field(default_factory=lambda: str(uuid4()))
    status: LearningStatus = LearningStatus.DRAFT
    evaluation: dict[str, Any] = field(default_factory=dict)
    human_approval: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def validate(self) -> None:
        required = (
            self.submitted_by,
            self.target_type,
            self.target_id,
            self.feedback,
            self.expected_behavior,
            self.context_scope,
        )
        if any(not value.strip() for value in required):
            raise ValueError("INCOMPLETE_LEARNING_CANDIDATE")
        if self.contains_participant_data:
            raise PermissionError("RAW_PARTICIPANT_DATA_NOT_ALLOWED_IN_LEARNING")


class LearningRegistry:
    TRANSITIONS = {
        LearningStatus.DRAFT: {LearningStatus.TRIAL, LearningStatus.REJECTED},
        LearningStatus.TRIAL: {LearningStatus.ACTIVE, LearningStatus.REJECTED},
        LearningStatus.ACTIVE: {LearningStatus.TRIAL, LearningStatus.REJECTED},
        LearningStatus.REJECTED: set(),
    }

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def add(self, candidate: LearningCandidate) -> dict[str, Any]:
        candidate.validate()
        records = self._load()
        records.append(self._serialize(candidate))
        self._write(records)
        return records[-1]

    def transition(
        self,
        candidate_id: str,
        status: LearningStatus,
        *,
        evaluation: dict[str, Any] | None = None,
        approved_by: str | None = None,
    ) -> dict[str, Any]:
        records = self._load()
        for item in records:
            if item["candidate_id"] != candidate_id:
                continue
            current = LearningStatus(item["status"])
            if status not in self.TRANSITIONS[current]:
                raise ValueError("INVALID_LEARNING_STATUS_TRANSITION")
            if status in {LearningStatus.TRIAL, LearningStatus.ACTIVE} and not evaluation:
                raise ValueError("LEARNING_EVALUATION_REQUIRED")
            if status == LearningStatus.ACTIVE and not (approved_by or "").strip():
                raise ValueError("HUMAN_APPROVAL_REQUIRED_FOR_ACTIVE")
            item["status"] = status.value
            item["evaluation"] = evaluation or item.get("evaluation", {})
            if approved_by:
                item["human_approval"] = {
                    "approved_by": approved_by,
                    "approved_at": datetime.now(UTC).isoformat(),
                }
            item["updated_at"] = datetime.now(UTC).isoformat()
            self._write(records)
            return item
        raise KeyError("LEARNING_CANDIDATE_NOT_FOUND")

    @staticmethod
    def _serialize(candidate: LearningCandidate) -> dict[str, Any]:
        data = asdict(candidate)
        data["role"] = candidate.role.value
        data["status"] = candidate.status.value
        return data

    def _load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("INVALID_LEARNING_REGISTRY")
        return data

    def _write(self, records: list[dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(
            prefix=self.path.name,
            dir=self.path.parent,
            text=True,
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(records, handle, ensure_ascii=False, indent=2)
            os.replace(temp_name, self.path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
