import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from pilot_account.schemas import (
    PilotAccount,
    PilotAccountStatus,
)


class PilotAccountPersistentStore:
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._accounts: dict[str, PilotAccount] = {}
        self._load()

    def save(self, account: PilotAccount) -> None:
        self._accounts[account.account_id] = account
        self._persist()

    def get(self, account_id: str) -> Optional[PilotAccount]:
        return self._accounts.get(account_id)

    def exists(self, account_id: str) -> bool:
        return account_id in self._accounts

    def list_all(self) -> list[PilotAccount]:
        return list(self._accounts.values())

    def _persist(self) -> None:
        data = [
            self._serialize_account(account)
            for account in self._accounts.values()
        ]

        self.storage_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _load(self) -> None:
        if not self.storage_path.exists():
            return

        raw = self.storage_path.read_text(encoding="utf-8").strip()

        if not raw:
            return

        data = json.loads(raw)

        for item in data:
            account = self._deserialize_account(item)
            self._accounts[account.account_id] = account

    def _serialize_account(self, account: PilotAccount) -> dict:
        data = asdict(account)

        data["status"] = account.status.value
        data["created_at"] = account.created_at.isoformat()
        data["updated_at"] = account.updated_at.isoformat()

        return data

    def _deserialize_account(self, data: dict) -> PilotAccount:
        return PilotAccount(
            account_id=data["account_id"],
            participant_id=data["participant_id"],
            subject_link_id=data["subject_link_id"],
            preferred_language=data.get("preferred_language", "ru"),
            status=PilotAccountStatus(
                data.get("status", PilotAccountStatus.ACTIVE.value)
            ),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )