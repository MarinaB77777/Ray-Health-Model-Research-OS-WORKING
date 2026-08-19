from model_engine.learning_boundary import normalize_learning_governance


def test_legacy_false_learning_block_becomes_not_evaluated():
    readiness = {
        "learning": {
            "pattern_candidate_detected": False,
            "stable_candidate_detected": False,
            "calibration_update_recommended": False,
            "requires_user_confirmation": False,
            "allow_external_core_update_request": False,
            "reason_codes": [],
        }
    }

    result = normalize_learning_governance(readiness)
    learning = result["learning"]

    assert learning["evaluation_status"] == "not_evaluated"
    assert learning["evaluated"] is False
    assert learning["pattern_candidate_detected"] is None
    assert learning["stable_candidate_detected"] is None
    assert learning["automatic_memory_promotion_allowed"] is False
    assert learning["heart_mutation_allowed"] is False
    assert learning["permission_mutation_allowed"] is False
    assert learning["truth_authority_mutation_allowed"] is False
    assert "LEARNING_ENGINE_NOT_IMPLEMENTED" in learning["reason_codes"]


def test_future_evaluated_learning_still_gets_non_escalation_defaults():
    result = normalize_learning_governance(
        {
            "learning": {
                "evaluated": True,
                "evaluation_status": "evaluated",
                "pattern_candidate_detected": True,
            }
        }
    )

    learning = result["learning"]
    assert learning["pattern_candidate_detected"] is True
    assert learning["automatic_memory_promotion_allowed"] is False
    assert learning["heart_mutation_allowed"] is False
    assert learning["permission_mutation_allowed"] is False
    assert learning["truth_authority_mutation_allowed"] is False
