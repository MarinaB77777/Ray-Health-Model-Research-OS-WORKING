from __future__ import annotations

import json
from pathlib import Path

from pilot_session.schemas import SessionStatus
from research.editors.audit import append_audit_event


EMPTY_SESSION_PURGE_CONTRACT_VERSION = "empty-session-purge-1"
REFERENCE_FILES = (
    Path("data/research_records.json"),
    Path("data/research_analysis_results.json"),
    Path("data/model_calculation_runs.json"),
)


def _contains_session_reference(value, session_id: str) -> bool:
    if isinstance(value, dict):
        return any(
            (key in {"session_id", "source_session_id"} and str(item) == session_id)
            or _contains_session_reference(item, session_id)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_session_reference(item, session_id) for item in value)
    return False


def _collect_session_references(value, found: set[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"session_id", "source_session_id"} and item not in (None, ""):
                found.add(str(item))
            _collect_session_references(item, found)
    elif isinstance(value, list):
        for item in value:
            _collect_session_references(item, found)


def build_downstream_reference_index(paths=REFERENCE_FILES) -> dict[str, list[str]]:
    """Read each downstream store once and index referenced sessions for large catalogs."""
    index: dict[str, list[str]] = {}
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8") or "null")
        except (json.JSONDecodeError, OSError):
            index.setdefault("__unreadable__", []).append(str(path))
            continue
        session_ids: set[str] = set()
        _collect_session_references(payload, session_ids)
        for session_id in session_ids:
            index.setdefault(session_id, []).append(str(path))
    return index


def downstream_references(session_id: str, paths=REFERENCE_FILES) -> list[str]:
    references = []
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8") or "null")
        except (json.JSONDecodeError, OSError):
            references.append(f"{path}:unreadable")
            continue
        if _contains_session_reference(payload, session_id):
            references.append(str(path))
    return references


def assess_empty_session_purge(
    session,
    *,
    reference_paths=REFERENCE_FILES,
    reference_index: dict[str, list[str]] | None = None,
) -> dict:
    blockers = []
    if session.status != SessionStatus.CREATED:
        blockers.append("SESSION_STATUS_NOT_CREATED")
    checks = {
        "answers": session.answers,
        "questionnaire_submissions": session.questionnaire_submissions,
        "research_answer_records": session.research_answer_records,
        "run_history": session.run_history,
        "raw_engine_result": session.raw_engine_result,
        "public_output": session.public_output,
        "next_question_snapshots": session.next_question_snapshots,
        "acquisition_request_snapshots": session.acquisition_request_snapshots,
        "uncertainty_snapshot": session.uncertainty_snapshot,
    }
    for name, value in checks.items():
        if value:
            blockers.append(f"SESSION_HAS_{name.upper()}")
    if session.run_count:
        blockers.append("SESSION_HAS_RUN_COUNT")
    if session.answer_revision_count:
        blockers.append("SESSION_HAS_ANSWER_REVISIONS")
    if session.answer_merge_history:
        blockers.append("SESSION_HAS_ANSWER_HISTORY")
    if session.export_generated:
        blockers.append("SESSION_HAS_EXPORT")
    if reference_index is None:
        references = downstream_references(session.session_id, reference_paths)
    else:
        references = list(reference_index.get(session.session_id, []))
        references.extend(
            f"{path}:unreadable"
            for path in reference_index.get("__unreadable__", [])
        )
    if references:
        blockers.append("SESSION_HAS_DOWNSTREAM_REFERENCES")
    return {
        "schema_version": EMPTY_SESSION_PURGE_CONTRACT_VERSION,
        "session_id": session.session_id,
        "eligible": not blockers,
        "blockers": blockers,
        "downstream_references": references,
        "preserved_records": ["consent_or_agreement_record", "minimal_deletion_audit"],
    }


def purge_empty_session(
    store,
    session_id: str,
    *,
    actor_id: str,
    reason: str,
    confirmation: str,
) -> dict:
    if not str(actor_id or "").strip() or not str(reason or "").strip():
        return {"ok": False, "status": "actor_and_reason_required"}
    session = store.get(session_id)
    if session is None:
        return {"ok": False, "status": "session_not_found"}
    assessment = assess_empty_session_purge(session)
    if not assessment["eligible"]:
        return {"ok": False, "status": "session_not_empty_or_referenced", "assessment": assessment}
    expected = f"DELETE EMPTY SESSION {session_id}"
    if confirmation != expected:
        return {"ok": False, "status": "confirmation_mismatch", "expected_confirmation": expected}
    removed = store.delete(session_id)
    if removed is None:
        return {"ok": False, "status": "session_not_found"}
    audit = append_audit_event(
        action="empty_technical_session_purged", actor_id=actor_id,
        object_type="pilot_session", object_id=session_id, reason=reason,
        details={
            "contract_version": EMPTY_SESSION_PURGE_CONTRACT_VERSION,
            "study_id": session.study_id,
            "created_at": session.created_at.isoformat(),
            "status_before_deletion": session.status.value,
            "scientific_payload_present": False,
            "participant_content_retained_in_audit": False,
        },
    )
    return {"ok": True, "status": "empty_session_purged", "assessment": assessment, "audit_event": audit}
