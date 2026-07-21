from datetime import datetime, timezone
from uuid import uuid4


MEASUREMENT_SESSION_SCHEMA_VERSION = (
    "measurement-session-1"
)


VALID_STATUSES = {
    "created",
    "connected",
    "in_progress",
    "finished",
    "saved",
    "failed",
    "invalid",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_measurement_session(
    *,
    measurement_type: str,
    connector: dict,
    study_id: str | None = None,
    participant_id: str | None = None,
    session_id: str | None = None,
    series_id: str | None = None,
    series_position: int | None = None,
) -> dict:
    now = utc_now()

    return {
        "schema_version": MEASUREMENT_SESSION_SCHEMA_VERSION,
        "measurement_id": str(uuid4()),
        "status": "created",

        "identity": {
            "measurement_type": measurement_type,
            "study_id": study_id,
            "participant_id": participant_id,
            "session_id": session_id,
            "series_id": series_id,
            "series_position": series_position,
            "is_repeated_measurement": series_id is not None,
        },

        "connector": connector,

        "time": {
            "created_at": now,
            "connected_at": None,
            "started_at": None,
            "finished_at": None,
            "saved_at": None,
            "global_time_reference": now,
        },

        "raw_data": {
            "raw_file_path": None,
            "original_file_name": None,
            "file_type": None,
            "checksum": None,
            "data_exists": False,
        },

        "events": [
            {
                "event": "created",
                "at": now,
            }
        ],

        "error": None,
    }


def set_measurement_status(
    measurement_session: dict,
    *,
    status: str,
    event: str,
    extra: dict | None = None,
) -> dict:
    if status not in VALID_STATUSES:
        raise ValueError(
            f"Invalid measurement status: {status}"
        )

    now = utc_now()
    measurement_session["status"] = status

    if status == "connected":
        measurement_session["time"]["connected_at"] = now

    if status == "in_progress":
        measurement_session["time"]["started_at"] = now

    if status == "finished":
        measurement_session["time"]["finished_at"] = now

    if status == "saved":
        measurement_session["time"]["saved_at"] = now

    item = {
        "event": event,
        "at": now,
    }

    if extra:
        item["extra"] = extra

    measurement_session.setdefault(
        "events",
        [],
    ).append(item)

    return measurement_session


def mark_connected(
    measurement_session: dict,
) -> dict:
    return set_measurement_status(
        measurement_session,
        status="connected",
        event="connected",
    )


def mark_started(
    measurement_session: dict,
) -> dict:
    return set_measurement_status(
        measurement_session,
        status="in_progress",
        event="measurement_started",
    )


def mark_finished(
    measurement_session: dict,
    *,
    raw_file_path: str | None = None,
    original_file_name: str | None = None,
    file_type: str | None = None,
    checksum: str | None = None,
) -> dict:
    measurement_session["raw_data"] = {
        "raw_file_path": raw_file_path,
        "original_file_name": original_file_name,
        "file_type": file_type,
        "checksum": checksum,
        "data_exists": raw_file_path is not None,
    }

    return set_measurement_status(
        measurement_session,
        status="finished",
        event="measurement_finished",
        extra={
            "raw_file_path": raw_file_path,
            "file_type": file_type,
        },
    )


def mark_saved(
    measurement_session: dict,
    *,
    measurement_file_path: str,
) -> dict:
    return set_measurement_status(
        measurement_session,
        status="saved",
        event="measurement_saved",
        extra={
            "measurement_file_path": measurement_file_path,
        },
    )


def mark_failed(
    measurement_session: dict,
    *,
    reason: str,
) -> dict:
    measurement_session["error"] = reason

    return set_measurement_status(
        measurement_session,
        status="failed",
        event="measurement_failed",
        extra={
            "reason": reason,
        },
    )