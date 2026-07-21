from __future__ import annotations

from pathlib import Path
from threading import RLock
from typing import Any
import json
import os
import tempfile


DATA_FILE = Path("research/research_objects.json")
OBJECT_STORE_LOCK = RLock()


def configure_object_store(data_file: str | Path, *, migrate_legacy: bool = True) -> Path:
    """Select persistent runtime storage without changing direct-library test defaults."""
    global DATA_FILE
    destination = Path(data_file)
    legacy = DATA_FILE
    if destination.resolve() == legacy.resolve():
        return DATA_FILE
    if migrate_legacy and legacy.exists() and not destination.exists():
        try:
            value = json.loads(legacy.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError("LEGACY_RESEARCH_OBJECT_STORE_CORRUPTED") from exc
        if not isinstance(value, list):
            raise RuntimeError("LEGACY_RESEARCH_OBJECT_STORE_MUST_BE_LIST")
        destination.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(value, handle, ensure_ascii=False, indent=2)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, destination)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    DATA_FILE = destination
    return DATA_FILE


def load_objects() -> list[dict[str, Any]]:
    if not DATA_FILE.exists():
        return []
    try:
        value = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError("RESEARCH_OBJECT_STORE_CORRUPTED") from exc
    if not isinstance(value, list):
        raise RuntimeError("RESEARCH_OBJECT_STORE_MUST_BE_LIST")
    return value


def save_objects(objects: list[dict[str, Any]]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        prefix=f".{DATA_FILE.name}.", suffix=".tmp", dir=DATA_FILE.parent
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(objects, handle, ensure_ascii=False, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, DATA_FILE)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
