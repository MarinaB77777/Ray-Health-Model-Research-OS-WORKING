import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime, timezone


MEASUREMENT_STORAGE_ROOT = Path("measurement_storage")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_name(value: str) -> str:
    return (
        str(value or "unknown")
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
    )


def file_checksum(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def measurement_folder(graph: dict) -> Path:
    identity = graph["measurement_identity"]

    return (
        MEASUREMENT_STORAGE_ROOT
        / safe_name(identity.get("study_id"))
        / safe_name(identity.get("participant_id"))
        / safe_name(identity.get("session_id"))
    )


def save_raw_file_for_measurement(
    *,
    graph: dict,
    source_file_path: str,
    original_file_name: str | None = None,
) -> dict:
    measurement_id = graph["measurement_identity"]["measurement_id"]
    source = Path(source_file_path)

    if not source.exists():
        raise FileNotFoundError(f"Raw file not found: {source_file_path}")

    raw_folder = measurement_folder(graph) / "raw"
    raw_folder.mkdir(parents=True, exist_ok=True)

    suffix = source.suffix or ""
    target = raw_folder / f"{measurement_id}{suffix}"

    shutil.copy2(source, target)

    return {
        "file_id": measurement_id,
        "file_name": target.name,
        "file_path": str(target),
        "original_file_name": original_file_name or source.name,
        "file_type": suffix.lstrip(".").lower() or None,
        "checksum": file_checksum(target),
        "data_included": False,
    }


def save_measurement_graph(graph: dict) -> dict:
    measurement_id = graph["measurement_identity"]["measurement_id"]

    folder = measurement_folder(graph) / "measurements"
    folder.mkdir(parents=True, exist_ok=True)

    path = folder / f"{measurement_id}.measurement"

    graph["saved_at"] = utc_now()

    path.write_text(
        json.dumps(graph, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return {
        "measurement_id": measurement_id,
        "file_path": str(path),
    }


def load_measurement_graph(file_path: str) -> dict:
    return json.loads(
        Path(file_path).read_text(encoding="utf-8")
    )