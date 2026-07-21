import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from assessment.prepared_output import build_prepared_domain_output


RESEARCH_RECORDS_PATH = Path("data/research_records.json")


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_research_records() -> list[dict]:
    if not RESEARCH_RECORDS_PATH.exists():
        return []

    raw = RESEARCH_RECORDS_PATH.read_text(encoding="utf-8").strip()

    if not raw:
        return []

    return json.loads(raw)


def save_research_records(records: list[dict]) -> None:
    RESEARCH_RECORDS_PATH.parent.mkdir(parents=True, exist_ok=True)

    RESEARCH_RECORDS_PATH.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def save_research_record_from_export(research_export: dict) -> dict:
    snapshot = research_export.get("research_snapshot", {})
    source_session = snapshot.get("source_session", {})

    records = load_research_records()

    session_id = research_export.get("session_id")

    records = [
        record for record in records
        if record.get("session_id") != session_id
    ]

    record = {
        "record_id": str(uuid4()),
        "record_type": "research_snapshot",
        "status": "saved",
        "created_at": now_utc(),
        "updated_at": now_utc(),

        "export_id": research_export.get("export_id"),
        "export_mode": research_export.get("export_mode"),
        "export_scope": research_export.get("export_scope"),
        "export_schema_version": research_export.get("export_schema_version"),
        "export_policy_version": research_export.get("export_policy_version"),

        "session_id": session_id,
        "study_id": source_session.get("study_id"),
        "source_session_status": source_session.get("source_session_status"),

        "research_snapshot": snapshot,
    }

    records.append(record)
    save_research_records(records)

    return record


def list_research_records(
    study_id: str | None = None,
    session_id: str | None = None,
) -> list[dict]:
    records = load_research_records()

    if study_id:
        records = [
            record for record in records
            if record.get("study_id") == study_id
        ]

    if session_id:
        records = [
            record for record in records
            if record.get("session_id") == session_id
        ]

    return records

def save_du_research_record(
    session_id: str,
    account_id: str | None,
    answers: dict,
    result: dict,
    language: str = "ru",
    domain_data_identity: dict | None = None,
) -> dict:
    records = load_research_records()

    records = [
        record for record in records
        if not (
            record.get("session_id") == session_id
            and record.get("study_id") == "decision_under_uncertainty"
        )
    ]

    raw_payload = {
        "payload_type": "questionnaire_answers",
        "study_id": "decision_under_uncertainty",
        "answers": answers,
    }


    analysis_output = result

    prepared_domain_output = build_prepared_domain_output(
        domain_data_identity=domain_data_identity or {},
        raw_payload=raw_payload,
        analysis_output=analysis_output,
    )

    identity = dict(domain_data_identity or {})
    created_at = now_utc()
    submission_id = str(uuid4())

    research_answer_records = []

    for question_code, answer_value in answers.items():
        research_answer_records.append({
            "answer_record_id": str(uuid4()),
            "submission_id": submission_id,
            "record_type": "questionnaire_answer",
            "created_at": created_at,
            "participant_id": identity.get("participant_id") or account_id,
            "subject_link_id": identity.get("subject_link_id"),
            "session_id": session_id,
            "study_id": "decision_under_uncertainty",
            "language": language,
            "questionnaire_id": identity.get(
                "data_source_path",
                "decision_under_uncertainty",
            ),
            "questionnaire_version": identity.get(
                "questionnaire_version"
            ),
            "question_code": question_code,
            "answer_value": answer_value,
            "answer_value_type": type(answer_value).__name__,
            "answer_revision": 1,
            "source_mode": "du_complete",
            "domain_data_identity": identity,
        })

    record = {
        "record_id": str(uuid4()),
        "record_type": "completed_questionnaire",
        "status": "saved",
        "created_at": now_utc(),
        "updated_at": now_utc(),

        "session_id": session_id,
        "account_id": account_id,
        "participant_id": (
            identity.get("participant_id")
            or account_id
        ),
        "study_id": "decision_under_uncertainty",
        "language": language,

        "domain_data_identity": domain_data_identity or {},
        "raw_payload": raw_payload,
        "prepared_domain_output": prepared_domain_output,
        "analysis_output": analysis_output,

        "answers": answers,
        "result": result,
        "research_answer_records": research_answer_records,
    }

    records.append(record)
    save_research_records(records)

    return record