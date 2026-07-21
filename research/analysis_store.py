import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


ANALYSIS_INDEX_PATH = Path("data/research_analysis_results.json")
ANALYSIS_RECORDS_DIR = Path("data/research_analysis_sessions")


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path, default):
    if not path.exists():
        return default

    raw = path.read_text(encoding="utf-8").strip()

    if not raw:
        return default

    return json.loads(raw)


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_analysis_results() -> list[dict]:
    return _read_json(ANALYSIS_INDEX_PATH, [])


def save_analysis_results(results: list[dict]) -> None:
    _write_json(ANALYSIS_INDEX_PATH, results)


def load_analysis_record(analysis_id: str) -> dict | None:
    path = ANALYSIS_RECORDS_DIR / f"{analysis_id}.json"

    if not path.exists():
        return None

    return _read_json(path, None)


def save_analysis_result(analysis: dict) -> dict:
    results = load_analysis_results()

    analysis_id = str(uuid4())
    created_at = now_utc()

    full_record = {
        "analysis_id": analysis_id,
        "analysis_type": analysis.get(
            "analysis_type",
            "research_analysis",
        ),
        "status": "saved",
        "created_at": created_at,
        "updated_at": created_at,
        **analysis,
    }

    record_path = ANALYSIS_RECORDS_DIR / f"{analysis_id}.json"
    _write_json(record_path, full_record)

    index_record = {
        "analysis_id": analysis_id,
        "analysis_type": full_record["analysis_type"],
        "status": "saved",
        "created_at": created_at,
        "updated_at": created_at,
        "study_id": analysis.get("study_id"),
        "record_count": analysis.get("record_count"),
        "analysis_scope": analysis.get("analysis_scope"),
        "file_path": str(record_path),
    }

    results.append(index_record)
    save_analysis_results(results)

    return full_record