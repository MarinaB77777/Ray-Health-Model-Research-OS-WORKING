from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any
import json
import os
import tempfile

from .contracts import ActionStatus, RayActionProposal, RayRole


class RayActionStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def add(
        self,
        proposal: RayActionProposal,
        *,
        role: RayRole,
        owner_id: str,
        page_id: str,
    ) -> dict[str, Any]:
        records = self._load()
        data = asdict(proposal)
        data["status"] = proposal.status.value
        data["role"] = role.value
        data["owner_id"] = owner_id
        data["page_id"] = page_id
        records.append(data)
        self._write(records)
        return data

    def confirm(
        self,
        action_id: str,
        *,
        role: RayRole,
        owner_id: str,
    ) -> dict[str, Any]:
        records = self._load()
        for item in records:
            if item["action_id"] != action_id:
                continue
            if item["role"] != role.value or item["owner_id"] != owner_id:
                raise PermissionError("ACTION_OWNERSHIP_MISMATCH")
            if item["status"] != ActionStatus.PROPOSED.value:
                raise ValueError("ACTION_NOT_IN_PROPOSED_STATE")
            item["status"] = ActionStatus.CONFIRMED.value
            self._write(records)
            return item
        raise KeyError("ACTION_NOT_FOUND")

    def _load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("INVALID_RAY_ACTION_STORE")
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
