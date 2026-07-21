from pilot_session.schemas import (
    ParticipantSession,
    SessionStatus,
)
from research.snapshot_builder import build_research_snapshot
from pilot_session.schemas import ParticipantSession, SessionStatus
from research.snapshot_builder import build_research_snapshot

from research.aggregation_governance import (
    evaluate_snapshot_dataset_admission,
)

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

    session.next_question_snapshots = [
        {
            "variable_code": "d0",
            "reason_code": "MISSING_FIELD",
        }
    ]

    session.acquisition_request_snapshots = [
        {
            "request_type": "data_acquisition",
            "target_data": "d0",
        }
    ]

    return session


def test_research_snapshot_contains_bounded_metadata():
    session = make_completed_session()

    snapshot = build_research_snapshot(session)

    assert snapshot["snapshot_mode"] == "research"
    assert (
        snapshot["snapshot_scope"]
        == "bounded_research_snapshot"
    )
    assert snapshot["generated_by"] == (
        "research.snapshot_builder"
    )
    assert snapshot["created_from"] == "ParticipantSession"
    assert snapshot["source_session"]["session_id"] == "session-1"
    assert (
        snapshot["source_session"]["source_session_status"]
        == "RUN_COMPLETED"
    )
    assert (
        snapshot["versions"]["engine_version"]
        == "mvp-1"
    )


def test_research_snapshot_excludes_raw_engine_result_and_answers():
    session = make_completed_session()

    snapshot = build_research_snapshot(session)

    assert "raw_engine_result" not in snapshot
    assert "answers" not in snapshot
    assert "secret_answer" in snapshot["answer_summary"][
        "answer_export_result"
    ]["excluded_answers"]
    assert "do-not-export" not in str(snapshot)
    assert "internal-warning" not in str(snapshot)
    assert snapshot["limitations"]["raw_engine_result_excluded"] is True
    assert snapshot["limitations"]["raw_answers_excluded"] is True
    assert (
        snapshot["limitations"][
        "filtered_answer_summary_included"
        ]
        is True
    )


def test_research_snapshot_uses_preliminary_policy_status():
    session = make_completed_session()

    snapshot = build_research_snapshot(session)

    policy = snapshot["snapshot_policy_status"]

    assert policy["snapshot_status"] == "usable_preliminary"
    assert policy["usable_for_research_preliminary"] is True
    assert (
        policy["policy_evaluation"]
        == "preliminary_builder_evaluation"
    )
    assert policy["consent_status"] == "not_evaluated"
    assert policy["retention_status"] == "not_evaluated"
    assert policy["policy_restricted"] == "not_evaluated"
    assert policy["exclusion_status"] == "not_evaluated"


def test_research_snapshot_marks_invalidated_session_unusable():
    session = make_completed_session()
    session.invalidated = True
    session.invalidation_reason = "test invalidation"

    snapshot = build_research_snapshot(session)

    policy = snapshot["snapshot_policy_status"]

    assert snapshot["source_session"]["invalidated"] is True
    assert policy["snapshot_status"] == "invalidated"
    assert policy["usable_for_research_preliminary"] is False
    assert policy["exclusion_status"] == "excluded_invalidated"


def test_research_snapshot_preserves_forecast_blocked_semantics():
    session = make_completed_session()

    snapshot = build_research_snapshot(session)

    forecast = snapshot["forecast_summary"]

    assert forecast["forecast_status"] == "blocked"
    assert forecast["allowed"] is False
    assert forecast["reason"] == "LOW_COVERAGE"
    assert forecast["allowed_scope"] == "none"


def test_research_snapshot_preserves_forecast_missing_semantics():
    session = make_completed_session()
    session.public_output.pop("forecast")

    snapshot = build_research_snapshot(session)

    forecast = snapshot["forecast_summary"]

    assert forecast["forecast_status"] == "missing"
    assert forecast["allowed"] is None
    assert forecast["reason"] is None


def test_research_snapshot_preserves_uncertainty_summary():
    session = make_completed_session()

    snapshot = build_research_snapshot(session)

    uncertainty = snapshot["uncertainty_summary"]

    assert uncertainty["uncertainty_status"] == "present"
    assert uncertainty["uncertainty_score"] == 10
    assert uncertainty["uncertainty_level"] == "high"
    assert uncertainty["allow_recommendations"] is False
    assert uncertainty["allow_strong_recommendations"] is False
    assert uncertainty["dialogue_mode"] == "soft"


def test_research_snapshot_preserves_uncertainty_missing_semantics():
    session = make_completed_session()
    session.uncertainty_snapshot = {}

    snapshot = build_research_snapshot(session)

    uncertainty = snapshot["uncertainty_summary"]

    assert uncertainty["uncertainty_status"] == "missing"
    assert uncertainty["uncertainty_score"] is None
    assert uncertainty["uncertainty_level"] is None


def test_research_snapshot_preserves_not_calculated_domain_summary():
    session = make_completed_session()

    snapshot = build_research_snapshot(session)

    domain = snapshot["operational_summary"]["domain_summary"][
        "physical"
    ]

    assert (
        snapshot["operational_summary"]["calculation_status"]
        == "present"
    )
    assert domain["calculated"] is False
    assert domain["delta_interpretation"] == "not_calculated"


def test_research_snapshot_marks_identity_risk_explicitly():
    session = make_completed_session()

    snapshot = build_research_snapshot(session)

    reference = snapshot["participant_reference"]

    assert reference["participant_reference_id"] != "participant-1"
    assert reference["pseudonymized"] is True
    assert reference["reidentification_risk"] == "reduced_not_zero"
    assert reference["salt_exported"] is False
    assert reference["global_identity"] is False
    assert reference["longitudinal_linkage_allowed"] is False


def test_research_snapshot_marks_payload_safety_limitations():
    session = make_completed_session()

    snapshot = build_research_snapshot(session)

    assert (
        snapshot["payload_safety"]["payload_safety_status"]
        == "bounded_extraction_with_allowlist_sanitizer"
    )


def test_research_snapshot_has_not_implemented_sections():
    session = make_completed_session()

    snapshot = build_research_snapshot(session)

    assert snapshot["sensor_summary"]["status"] == "not_implemented"
    assert (
        snapshot["standard_method_summary"]["status"]
        == "not_implemented"
    )
    assert (
        snapshot["decision_pattern_summary"]["status"]
        == "not_implemented"
    )


def test_research_snapshot_has_interpretation_boundaries():
    session = make_completed_session()

    snapshot = build_research_snapshot(session)

    boundaries = snapshot["research_interpretation_boundaries"]

    assert boundaries["no_diagnosis"] is True
    assert boundaries["no_identity_inference"] is True
    assert boundaries["no_authority"] is True
    assert boundaries["not_participant_truth"] is True
    assert boundaries["not_clinical_record"] is True
    assert boundaries["not_longitudinal_profile"] is True

def test_research_snapshot_includes_policy_allowed_answer():
    session = make_completed_session()
    session.answers["__example_d1"] = 3

    snapshot = build_research_snapshot(session)

    included = snapshot["answer_summary"]["answer_export_result"][
        "included_answers"
    ]

    assert included["__example_d1"]["value"] == 3
    assert (
        included["__example_d1"]["reason_code"]
        == "ANSWER_INCLUDED_BY_POLICY"
    )
    assert (
        included["__example_d1"]["policy_category"]
        == "exportable"
    )


def test_research_snapshot_preserves_answer_filter_metadata():
    session = make_completed_session()

    snapshot = build_research_snapshot(session)

    result = snapshot["answer_summary"]["answer_export_result"]

    assert result["filter_version"] == "answer-export-filter-1"
    assert result["filter_method"] == "static_answer_policy_lookup"
    assert result["filter_scope"] == "research_snapshot"
    assert result["count_basis"] == "unique_normalized_variable_codes"
    assert result["unknown_policy_default_deny"] is True
    assert result["included_answers_are_not_final_export_authorization"] is True


def test_research_snapshot_preserves_duplicate_answer_exclusion():
    session = make_completed_session()
    session.answers = {
        "__example_d1": 3,
        "  __example_d1  ": 4,
    }

    snapshot = build_research_snapshot(session)

    result = snapshot["answer_summary"]["answer_export_result"]

    assert result["included_answers"] == {}
    assert result["excluded_answers"]["__example_d1"][
        "reason_code"
    ] == "DUPLICATE_NORMALIZED_VARIABLE_CODE"
    assert result["duplicate_variable_codes_detected"] == [
        "__example_d1"
    ]


def test_research_snapshot_preserves_builder_non_authority_flags():
    session = make_completed_session()

    snapshot = build_research_snapshot(session)

    answer_summary = snapshot["answer_summary"]

    assert answer_summary["builder_consumed_raw_answers_directly"] is False
    assert answer_summary["builder_is_not_answer_policy_authority"] is True
    assert answer_summary["builder_is_not_consent_authority"] is True
    assert answer_summary["builder_is_not_retention_authority"] is True

def test_preliminary_research_snapshot_is_not_dataset_admissible():
    session = make_completed_session()

    snapshot = build_research_snapshot(session)
    verdict = evaluate_snapshot_dataset_admission(snapshot)

    assert verdict["admission_allowed"] is False
    assert "CONSENT_NOT_GRANTED" in verdict["blockers"]
    assert "RETENTION_NOT_EVALUATED" in verdict["blockers"]
    assert (
        "POLICY_RESTRICTED_OR_NOT_EVALUATED"
        in verdict["blockers"]
    )

def test_snapshot_builder_applies_policy_status_override(monkeypatch):
    monkeypatch.setenv("RESEARCH_PSEUDONYMIZATION_SALT", "test-salt")

    session = ParticipantSession(
        session_id="session-1",
        participant_id="participant-1",
        status=SessionStatus.RUN_COMPLETED,
        public_output={"summary_text": "ok"},
    )

    snapshot = build_research_snapshot(
        session,
        policy_status_override={
            "consent_status": "granted",
            "retention_status": "active",
            "policy_restricted": "not_restricted",
        },
    )

    policy_status = snapshot["snapshot_policy_status"]

    assert policy_status["consent_status"] == "granted"
    assert policy_status["retention_status"] == "active"
    assert policy_status["policy_restricted"] == "not_restricted"
    assert policy_status["policy_status_override_applied"] is True