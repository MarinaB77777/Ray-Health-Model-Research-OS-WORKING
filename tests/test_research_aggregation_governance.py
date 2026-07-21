from research.aggregation_governance import (
    evaluate_snapshot_dataset_admission,
)


def make_snapshot():
    return {
        "snapshot_mode": "research",
        "snapshot_scope": "bounded_research_snapshot",
        "snapshot_policy_status": {
            "snapshot_status": "usable_preliminary",
            "usable_for_research_preliminary": True,
            "exclusion_status": "not_evaluated",
            "consent_status": "granted",
            "retention_status": "active",
            "policy_restricted": "not_restricted",
        },
        "source_session": {
            "invalidated": False,
        },
        "participant_reference": {
            "pseudonymized": True,
            "research_identity_risk": "not_evaluated",
        },
        "payload_safety": {
            "payload_safety_status": (
                "bounded_extraction_no_deep_sanitizer"
            ),
            "acquisition_payload_deep_sanitized": True,
            "next_questions_deep_sanitized": True,
        },
        "research_interpretation_boundaries": {
            "no_diagnosis": True,
            "no_authority": True,
            "not_participant_truth": True,
        },
        "limitations": {
            "raw_engine_result_excluded": True,
            "raw_answers_excluded": True,
            "snapshot_is_not_runtime_memory": True,
            "no_longitudinal_aggregation": True,
        },
    }


def test_dataset_admission_allows_clean_snapshot():
    verdict = evaluate_snapshot_dataset_admission(
        make_snapshot()
    )

    assert verdict["governance_scope"] == (
        "research_dataset_admission"
    )
    assert verdict["admission_allowed"] is True
    assert verdict["admission_status"] == "allowed"
    assert verdict["allowed_scope"] == (
        "single_snapshot_dataset_only"
    )
    assert verdict["dataset_use_scope"] == (
        "single_snapshot_dataset_only"
    )
    assert verdict["blockers"] == []
    assert verdict["restrictions"] == []
    assert verdict["warnings"] == []
    assert verdict["aggregation_performed"] is False
    assert verdict["longitudinal_admission_allowed"] is False
    assert verdict["participant_comparison_allowed"] is False
    assert (
        verdict["admission_allowed_is_not_aggregation"]
        is True
    )


def test_dataset_admission_blocks_invalid_payload():
    verdict = evaluate_snapshot_dataset_admission(
        "not-a-snapshot"
    )

    assert verdict["admission_allowed"] is False
    assert verdict["admission_status"] == "blocked"
    assert "INVALID_SNAPSHOT_PAYLOAD" in verdict["blockers"]
    assert verdict["dataset_use_scope"] == "none"


def test_dataset_admission_blocks_invalid_snapshot_mode():
    snapshot = make_snapshot()
    snapshot["snapshot_mode"] = "participant"

    verdict = evaluate_snapshot_dataset_admission(snapshot)

    assert verdict["admission_allowed"] is False
    assert "INVALID_SNAPSHOT_MODE" in verdict["blockers"]


def test_dataset_admission_blocks_invalid_snapshot_scope():
    snapshot = make_snapshot()
    snapshot["snapshot_scope"] = "runtime_dump"

    verdict = evaluate_snapshot_dataset_admission(snapshot)

    assert verdict["admission_allowed"] is False
    assert "INVALID_SNAPSHOT_SCOPE" in verdict["blockers"]


def test_dataset_admission_blocks_invalidated_snapshot():
    snapshot = make_snapshot()
    snapshot["source_session"]["invalidated"] = True

    verdict = evaluate_snapshot_dataset_admission(snapshot)

    assert verdict["admission_allowed"] is False
    assert verdict["admission_status"] == "blocked"
    assert "SNAPSHOT_INVALIDATED" in verdict["blockers"]


def test_dataset_admission_blocks_invalidated_status():
    snapshot = make_snapshot()
    snapshot["snapshot_policy_status"][
        "snapshot_status"
    ] = "invalidated"

    verdict = evaluate_snapshot_dataset_admission(snapshot)

    assert verdict["admission_allowed"] is False
    assert "SNAPSHOT_INVALIDATED" in verdict["blockers"]


def test_dataset_admission_blocks_not_usable_preliminary():
    snapshot = make_snapshot()
    snapshot["snapshot_policy_status"][
        "usable_for_research_preliminary"
    ] = False

    verdict = evaluate_snapshot_dataset_admission(snapshot)

    assert verdict["admission_allowed"] is False
    assert (
        "SNAPSHOT_NOT_USABLE_PRELIMINARY"
        in verdict["blockers"]
    )


def test_dataset_admission_blocks_missing_public_output():
    snapshot = make_snapshot()
    snapshot["snapshot_policy_status"][
        "exclusion_status"
    ] = "missing_public_output"

    verdict = evaluate_snapshot_dataset_admission(snapshot)

    assert verdict["admission_allowed"] is False
    assert "MISSING_PUBLIC_OUTPUT" in verdict["blockers"]


def test_dataset_admission_blocks_source_status_block():
    snapshot = make_snapshot()
    snapshot["snapshot_policy_status"][
        "exclusion_status"
    ] = "blocked_source_status"

    verdict = evaluate_snapshot_dataset_admission(snapshot)

    assert verdict["admission_allowed"] is False
    assert "BLOCKED_SOURCE_STATUS" in verdict["blockers"]


def test_dataset_admission_blocks_without_consent():
    snapshot = make_snapshot()
    snapshot["snapshot_policy_status"][
        "consent_status"
    ] = "not_evaluated"

    verdict = evaluate_snapshot_dataset_admission(snapshot)

    assert verdict["admission_allowed"] is False
    assert "CONSENT_NOT_GRANTED" in verdict["blockers"]


def test_dataset_admission_blocks_retention_expired():
    snapshot = make_snapshot()
    snapshot["snapshot_policy_status"][
        "retention_status"
    ] = "expired"

    verdict = evaluate_snapshot_dataset_admission(snapshot)

    assert verdict["admission_allowed"] is False
    assert "RETENTION_EXPIRED" in verdict["blockers"]


def test_dataset_admission_blocks_retention_not_evaluated_after_retention_contract():
    snapshot = make_snapshot()
    snapshot["snapshot_policy_status"][
        "retention_status"
    ] = "not_evaluated"

    verdict = evaluate_snapshot_dataset_admission(snapshot)

    assert verdict["admission_allowed"] is False
    assert verdict["admission_status"] == "blocked"
    assert "RETENTION_NOT_EVALUATED" in verdict["blockers"]
    assert "RETENTION_NOT_EVALUATED" not in verdict["warnings"]


def test_dataset_admission_blocks_retention_unknown():
    snapshot = make_snapshot()
    snapshot["snapshot_policy_status"].pop(
        "retention_status"
    )

    verdict = evaluate_snapshot_dataset_admission(snapshot)

    assert verdict["admission_allowed"] is False
    assert verdict["admission_status"] == "blocked"
    assert "RETENTION_UNKNOWN" in verdict["blockers"]


def test_dataset_admission_blocks_retention_not_active():
    snapshot = make_snapshot()
    snapshot["snapshot_policy_status"][
        "retention_status"
    ] = "deletion_requested"

    verdict = evaluate_snapshot_dataset_admission(snapshot)

    assert verdict["admission_allowed"] is False
    assert verdict["admission_status"] == "blocked"
    assert "RETENTION_NOT_ACTIVE" in verdict["blockers"]


def test_dataset_admission_blocks_policy_not_evaluated():
    snapshot = make_snapshot()
    snapshot["snapshot_policy_status"][
        "policy_restricted"
    ] = "not_evaluated"

    verdict = evaluate_snapshot_dataset_admission(snapshot)

    assert verdict["admission_allowed"] is False
    assert (
        "POLICY_RESTRICTED_OR_NOT_EVALUATED"
        in verdict["blockers"]
    )


def test_dataset_admission_restricts_non_pseudonymized_mvp_snapshot():
    snapshot = make_snapshot()
    snapshot["participant_reference"]["pseudonymized"] = False
    snapshot["participant_reference"][
        "research_identity_risk"
    ] = "direct_pilot_id_used_mvp"

    verdict = evaluate_snapshot_dataset_admission(snapshot)

    assert verdict["admission_allowed"] is True
    assert verdict["admission_status"] == "restricted"
    assert (
        verdict["dataset_use_scope"]
        == "restricted_single_snapshot_dataset_only"
    )
    assert "NOT_PSEUDONYMIZED" in verdict["restrictions"]
    assert (
        "DIRECT_PILOT_ID_USED_MVP"
        in verdict["restrictions"]
    )


def test_dataset_admission_restricts_when_acquisition_not_deep_sanitized():
    snapshot = make_snapshot()
    snapshot["payload_safety"][
        "acquisition_payload_deep_sanitized"
    ] = False

    verdict = evaluate_snapshot_dataset_admission(snapshot)

    assert verdict["admission_allowed"] is True
    assert verdict["admission_status"] == "restricted"
    assert (
        "ACQUISITION_PAYLOAD_NOT_DEEP_SANITIZED"
        in verdict["restrictions"]
    )


def test_dataset_admission_restricts_when_next_questions_not_deep_sanitized():
    snapshot = make_snapshot()
    snapshot["payload_safety"][
        "next_questions_deep_sanitized"
    ] = False

    verdict = evaluate_snapshot_dataset_admission(snapshot)

    assert verdict["admission_allowed"] is True
    assert verdict["admission_status"] == "restricted"
    assert (
        "NEXT_QUESTIONS_NOT_DEEP_SANITIZED"
        in verdict["restrictions"]
    )


def test_dataset_admission_blocks_missing_no_diagnosis_boundary():
    snapshot = make_snapshot()
    snapshot["research_interpretation_boundaries"][
        "no_diagnosis"
    ] = False

    verdict = evaluate_snapshot_dataset_admission(snapshot)

    assert verdict["admission_allowed"] is False
    assert (
        "MISSING_NO_DIAGNOSIS_BOUNDARY"
        in verdict["blockers"]
    )


def test_dataset_admission_blocks_missing_no_authority_boundary():
    snapshot = make_snapshot()
    snapshot["research_interpretation_boundaries"][
        "no_authority"
    ] = False

    verdict = evaluate_snapshot_dataset_admission(snapshot)

    assert verdict["admission_allowed"] is False
    assert (
        "MISSING_NO_AUTHORITY_BOUNDARY"
        in verdict["blockers"]
    )


def test_dataset_admission_blocks_missing_not_participant_truth_boundary():
    snapshot = make_snapshot()
    snapshot["research_interpretation_boundaries"][
        "not_participant_truth"
    ] = False

    verdict = evaluate_snapshot_dataset_admission(snapshot)

    assert verdict["admission_allowed"] is False
    assert (
        "MISSING_NOT_PARTICIPANT_TRUTH_BOUNDARY"
        in verdict["blockers"]
    )


def test_dataset_admission_blocks_if_raw_engine_result_not_excluded():
    snapshot = make_snapshot()
    snapshot["limitations"]["raw_engine_result_excluded"] = False

    verdict = evaluate_snapshot_dataset_admission(snapshot)

    assert verdict["admission_allowed"] is False
    assert (
        "RAW_ENGINE_RESULT_NOT_EXCLUDED"
        in verdict["blockers"]
    )


def test_dataset_admission_accepts_legacy_answers_excluded_field():
    snapshot = make_snapshot()

    snapshot["limitations"].pop(
        "raw_answers_excluded"
    )

    snapshot["limitations"]["answers_excluded"] = True

    verdict = evaluate_snapshot_dataset_admission(
        snapshot
    )

    assert (
        "RAW_ANSWERS_NOT_EXCLUDED"
        not in verdict["blockers"]
    )



def test_dataset_admission_blocks_if_no_answer_exclusion_marker():
    snapshot = make_snapshot()

    snapshot["limitations"].pop("raw_answers_excluded", None)
    snapshot["limitations"].pop("answers_excluded", None)

    verdict = evaluate_snapshot_dataset_admission(snapshot)

    assert verdict["admission_allowed"] is False
    assert "RAW_ANSWERS_NOT_EXCLUDED" in verdict["blockers"]


def test_dataset_admission_result_is_not_longitudinal_permission():
    verdict = evaluate_snapshot_dataset_admission(
        make_snapshot()
    )

    assert verdict["aggregation_performed"] is False
    assert verdict["longitudinal_admission_allowed"] is False
    assert verdict["participant_comparison_allowed"] is False
    assert (
        verdict[
            "restricted_admission_is_not_longitudinal_permission"
        ]
        is True
    )