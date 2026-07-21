import pytest

from pilot_session.errors import ExportBlockedError
from pilot_session.export import generate_research_export
from pilot_session.schemas import ParticipantSession, SessionStatus
from research.answer_policy import ANSWER_POLICY_VERSION
from research.answer_policy_validator import validate_answer_policy


def make_completed_session():
    session = ParticipantSession(
        session_id="session-1",
        participant_id="participant-1",
        status=SessionStatus.RUN_COMPLETED,
    )

    session.answers = {
        "k23": 0,
        "secret_answer": "do-not-export",
    }

    session.raw_engine_result = {
        "internal": "do-not-export",
        "warnings": ["internal-warning"],
    }

    session.public_output = {
        "summary_text": "Public summary",
        "result_level": "low",
        "forecast": {
            "allowed": False,
            "reason": "LOW_COVERAGE",
            "confidence": "low",
            "allowed_scope": "none",
        },
        "domain_summary": {
            "physical": {
                "r": None,
                "k_self": None,
                "delta": None,
                "delta_interpretation": "not_calculated",
                "calculated": False,
            }
        },
        "warnings": [
            {
                "code": "LOW_COVERAGE",
                "severity": "info",
            }
        ],
        "public_reasons": [
            {
                "code": "LOW_COVERAGE",
                "public": True,
            }
        ],
    }

    session.uncertainty_snapshot = {
        "uncertainty_score": 10,
        "uncertainty_level": "high",
        "allow_recommendations": False,
        "allow_strong_recommendations": False,
        "dialogue_mode": "soft",
    }

    return session


@pytest.mark.parametrize(
    "status",
    [
        SessionStatus.RUN_COMPLETED,
        SessionStatus.EXPORT_READY,
        SessionStatus.CLOSED,
    ],
)
def test_research_export_allowed_statuses(status):
    session = make_completed_session()
    session.status = status

    export = generate_research_export(session)

    assert export["export_mode"] == "research"
    assert export["export_scope"] == "bounded_research_snapshot"
    assert export["export_valid"] is True
    assert export["purpose"] == "research_snapshot_export"
    assert export["status"] == status.value
    assert "research_snapshot" in export


def test_research_export_blocks_invalidated_flag():
    session = make_completed_session()
    session.invalidated = True

    with pytest.raises(ExportBlockedError):
        generate_research_export(session)


def test_research_export_blocks_invalidated_status():
    session = make_completed_session()
    session.status = SessionStatus.INVALIDATED

    with pytest.raises(ExportBlockedError):
        generate_research_export(session)


@pytest.mark.parametrize(
    "status",
    [
        SessionStatus.CREATED,
        SessionStatus.ANSWERS_RECEIVED,
        SessionStatus.WAITING_FOR_INPUT,
        SessionStatus.PARTIAL_RESULT,
        SessionStatus.EXPORT_BLOCKED,
        SessionStatus.RUN_FAILED,
    ],
)
def test_research_export_blocks_disallowed_statuses(status):
    session = make_completed_session()
    session.status = status

    with pytest.raises(ExportBlockedError):
        generate_research_export(session)


def test_research_export_blocks_missing_public_output():
    session = make_completed_session()
    session.public_output = {}

    with pytest.raises(ExportBlockedError):
        generate_research_export(session)


def test_research_export_contains_research_snapshot():
    session = make_completed_session()

    export = generate_research_export(session)

    snapshot = export["research_snapshot"]

    assert snapshot["snapshot_mode"] == "research"
    assert (
        snapshot["snapshot_scope"]
        == "bounded_research_snapshot"
    )
    assert (
        snapshot["source_session"]["session_id"]
        == "session-1"
    )


def test_research_export_does_not_contain_raw_engine_result_or_answers():
    session = make_completed_session()

    export = generate_research_export(session)

    assert "raw_engine_result" not in export
    assert "answers" not in export
    assert "do-not-export" not in str(export)
    assert "secret_answer" in export["research_snapshot"][
        "answer_summary"
    ]["answer_export_result"]["excluded_answers"]
    assert "internal-warning" not in str(export)


def test_research_snapshot_inside_export_does_not_contain_raw_engine_result_or_answers():
    session = make_completed_session()

    export = generate_research_export(session)
    snapshot = export["research_snapshot"]

    assert "raw_engine_result" not in snapshot
    assert "answers" not in snapshot
    assert "do-not-export" not in str(snapshot)
    assert "secret_answer" in snapshot["answer_summary"][
        "answer_export_result"
    ]["excluded_answers"]
    assert "internal-warning" not in str(snapshot)

def test_individual_snapshot_requires_export_allowed():
    policy = {
        "policy_category": "exportable",
        "allowed_export_scope": ["research_snapshot"],
        "requires_consent": True,
        "consent_scope": "pilot_research",
        "retention_class": "bounded_research",
        "linkage_allowed": False,
        "aggregation_allowed": True,
        "individual_snapshot_allowed": True,
        "dataset_allowed": False,
        "export_allowed": False,
        "policy_version": ANSWER_POLICY_VERSION,
        "review_status": "reviewed",
        "rationale": "invalid test policy",
    }

    result = validate_answer_policy(policy)

    assert result["valid"] is False
    assert (
        "INDIVIDUAL_SNAPSHOT_REQUIRES_EXPORT_ALLOWED"
        in result["reason_codes"]
    )
