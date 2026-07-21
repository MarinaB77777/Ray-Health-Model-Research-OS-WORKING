from __future__ import annotations

import json
import re
import unicodedata
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock
from uuid import uuid4


QUESTION_BANK_REGISTRY_SCHEMA_VERSION = "registered-question-bank-registry-1"
QUESTION_BANK_DEFINITION_SCHEMA_VERSION = "registered-question-bank-definition-1"
DEFAULT_PATH = Path("data/question_bank_registry.json")
LANGUAGES = ("ru", "en", "es")
STATUSES = ("draft", "trial", "active")
_LOCK = RLock()


def _read(path: Path = DEFAULT_PATH) -> list[dict]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8") or "[]")
    if isinstance(payload, dict):
        payload = payload.get("banks", [])
    if not isinstance(payload, list):
        raise ValueError("question bank registry must contain a list")
    return payload


def _write(banks: list[dict], path: Path = DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(
            {
                "schema_version": QUESTION_BANK_REGISTRY_SCHEMA_VERSION,
                "banks": banks,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    temporary.replace(path)


def _slug(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", ascii_value.lower())).strip("_")


def list_registered_question_banks(*, path: Path = DEFAULT_PATH) -> list[dict]:
    return sorted((deepcopy(item) for item in _read(path)), key=lambda item: item["bank_code"])


def get_registered_question_bank(bank_code: str, *, path: Path = DEFAULT_PATH) -> dict | None:
    return next(
        (item for item in list_registered_question_banks(path=path) if item["bank_code"] == bank_code),
        None,
    )


def register_question_bank(
    *,
    title: str,
    language: str,
    actor_id: str,
    reason: str,
    preferred_code: str | None = None,
    reserved_codes: set[str] | None = None,
    path: Path = DEFAULT_PATH,
) -> dict:
    title = str(title or "").strip()
    actor_id = str(actor_id or "").strip()
    reason = str(reason or "").strip()
    if language not in LANGUAGES:
        return {"ok": False, "status": "unsupported_language"}
    if not title or not actor_id or not reason:
        return {"ok": False, "status": "title_actor_and_reason_required"}

    with _LOCK:
        banks = _read(path)
        existing_codes = {
            str(item.get("bank_code")) for item in banks
        } | set(reserved_codes or set())
        generated_id = str(uuid4())
        base_code = _slug(preferred_code or title) or f"bank_{generated_id[:8]}"
        bank_code = base_code
        suffix = 2
        while bank_code in existing_codes:
            bank_code = f"{base_code}_{suffix}"
            suffix += 1
        now = datetime.now(UTC).isoformat()
        bank = {
            "schema_version": QUESTION_BANK_DEFINITION_SCHEMA_VERSION,
            "registry_schema_version": QUESTION_BANK_REGISTRY_SCHEMA_VERSION,
            "bank_id": generated_id,
            "bank_code": bank_code,
            "definition_version": 1,
            "development_status": "draft",
            "titles": {lang: title if lang == language else "" for lang in LANGUAGES},
            "created_at": now,
            "updated_at": now,
            "authorship": {"created_by": actor_id},
            "provenance": {"creation_reason": reason, "registry_source": "question_editor"},
        }
        banks.append(bank)
        _write(banks, path)
    return {"ok": True, "status": "question_bank_registered", "bank": deepcopy(bank)}


def update_question_bank_title(
    bank_code: str,
    *,
    language: str,
    title: str,
    actor_id: str,
    reason: str,
    path: Path = DEFAULT_PATH,
) -> dict:
    if language not in LANGUAGES or not all(str(value or "").strip() for value in (title, actor_id, reason)):
        return {"ok": False, "status": "title_actor_and_reason_required"}
    with _LOCK:
        banks = _read(path)
        selected = None
        for bank in banks:
            if bank.get("bank_code") != bank_code:
                continue
            if bank.get("development_status") != "draft":
                return {"ok": False, "status": "immutable_non_draft_bank"}
            bank.setdefault("titles", {})[language] = title.strip()
            bank["updated_at"] = datetime.now(UTC).isoformat()
            bank.setdefault("provenance", {})["last_edited_by"] = actor_id.strip()
            bank["provenance"]["last_change_reason"] = reason.strip()
            selected = deepcopy(bank)
            break
        if selected is None:
            return {"ok": False, "status": "question_bank_not_found"}
        _write(banks, path)
    return {"ok": True, "status": "question_bank_title_updated", "bank": selected}


def rollback_question_bank_registration(
    bank_code: str,
    bank_id: str,
    *,
    path: Path = DEFAULT_PATH,
) -> None:
    """Rollback only the exact record created by a failed atomic create flow."""
    with _LOCK:
        banks = _read(path)
        kept = [
            bank
            for bank in banks
            if not (
                bank.get("bank_code") == bank_code
                and bank.get("bank_id") == bank_id
                and bank.get("development_status") == "draft"
            )
        ]
        if len(kept) != len(banks):
            _write(kept, path)
