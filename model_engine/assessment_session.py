from datetime import datetime, timezone
from model_engine.assessment_profile_service import get_profile_questions
from model_engine.assessment_result_builder import build_assessment_result

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_assessment_session(
    session_id: str,
    participant_id: str,
    profile_id: str,
    lang: str = "ru",
) -> dict:
    questions = get_profile_questions(
        profile_id=profile_id,
        lang=lang,
    )

    return {
        "session_id": session_id,
        "participant_id": participant_id,
        "profile_id": profile_id,
        "lang": lang,
        "status": "ACTIVE",
        "created_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
        "current_index": 0,
        "answers": {},
        "questions": questions,
        "result": None,
    }


def get_current_question(session: dict) -> dict | None:
    index = session.get("current_index", 0)
    questions = session.get("questions", [])

    if index >= len(questions):
        return None

    return questions[index]


def build_assessment_step(session: dict) -> dict:
    question = get_current_question(session)
    total = len(session.get("questions", []))
    current_index = session.get("current_index", 0)

    if question is None:
        return {
            "status": "READY_FOR_RESULT",
            "question": None,
            "progress": {
                "current": total,
                "total": total,
            },
        }

    return {
        "status": session.get("status"),
        "question": question,
        "progress": {
            "current": current_index + 1,
            "total": total,
        },
    }


def submit_assessment_answer(
    session: dict,
    question_code: str,
    value,
) -> dict:
    current_question = get_current_question(session)

    if current_question is None:
        session["status"] = "READY_FOR_RESULT"
        return session

    expected_code = current_question.get("code")

    if question_code != expected_code:
        raise ValueError(
            f"Expected answer for {expected_code}, got {question_code}"
        )

    session["answers"][question_code] = value
    session["current_index"] += 1
    session["updated_at"] = utc_now_iso()

    if session["current_index"] >= len(session.get("questions", [])):
        session["status"] = "READY_FOR_RESULT"

    return session

def finish_assessment_session(session: dict) -> dict:
    if session.get("status") != "READY_FOR_RESULT":
        raise ValueError("Assessment is not complete yet")

    result = build_assessment_result(
        profile_id=session["profile_id"],
        answers=session["answers"],
    )

    session["result"] = result
    session["status"] = "COMPLETED"
    session["updated_at"] = utc_now_iso()

    return session