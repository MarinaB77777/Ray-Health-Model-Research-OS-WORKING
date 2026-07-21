from model_engine.interview_runtime_ru import run_intro_turn
from datetime import datetime, timezone
from model_engine.research_event_store import (
    ResearchEventRecord,
    append_research_event,
)

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def create_intro_session(
    session_id: str,
    participant_id: str,
    subject_link_id: str,
    study_id: str,
    participant_role: str = "participant",
    synchronization_reference: str | None = None,
) -> dict:
    if synchronization_reference is None:
        synchronization_reference = f"sync_{session_id}"

    return {
        "goal": "intro",
        "session_id": session_id,
        "participant_id": participant_id,
        "subject_link_id": subject_link_id,
        "study_id": study_id,
        "participant_role": participant_role,
        "synchronization_reference": synchronization_reference,
        "created_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
        "closed_at": None,
        "knowledge": {},
        "status": "CREATED",
        "complete": False,
        "current_block": None,
        "turns": [],
    }


def process_intro_message(
    session: dict,
    message: str,
) -> dict:
    result = run_intro_turn(
        message=message,
        current_knowledge=session.get("knowledge", {}),
    )

    session["knowledge"] = result["knowledge"]
    session["complete"] = result["status"].get("complete", False)
    session["current_block"] = result["status"].get("next_block")
    session["updated_at"] = utc_now_iso()
    if session["complete"]:
        session["status"] = "CLOSED"
        if session.get("closed_at") is None:
            session["closed_at"] = utc_now_iso()

    session["turns"].append({
        "user_message": message,
        "extracted_blocks": result["extracted_blocks"],
        "status": result["status"],
        "ray": result["ray"],
    })
    turn_index = len(session["turns"]) - 1

    event = ResearchEventRecord(
        session_id=session.get("session_id"),
        participant_id=session.get("participant_id"),
        subject_link_id=session.get("subject_link_id"),
        study_id=session.get("study_id"),
        participant_role=session.get("participant_role"),
        synchronization_reference=session.get("synchronization_reference"),
        stream="intro",
        event_type="intro_turn",
        logic_version="INTRO_V1",
        model_version="health_intro_mvp",
        extraction_version="INTRO_EXTRACTION_RU_V1",
        turn_index=turn_index,
        raw_input={
            "message": message,
        },
        extracted_data=result["extracted_blocks"],
        knowledge_snapshot=session["knowledge"],
        status_snapshot=result["status"],
        output_snapshot=result["ray"],
    )

    append_research_event(event)

    return {
        "session": session,
        "ray": result["ray"],
        "status": result["status"],
    }