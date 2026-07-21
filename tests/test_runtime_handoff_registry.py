from runtime.handoff.registry import (
    HandoffTargetDefinition,
    HandoffTargetRegistry,
    HandoffTargetStatus,
    HandoffTargetType,
    HandoffCapability,
    HandoffBoundaryRule,
    HandoffTruthLimit,
    build_default_handoff_registry,
)


def test_target_requires_capability():
    try:
        HandoffTargetDefinition(
            target_id="invalid",
            target_type=HandoffTargetType.ADAPTER,
            capabilities=[],
            boundary_rules=[
                HandoffBoundaryRule.NO_DIRECT_EXECUTION,
            ],
            truth_limits=[
                HandoffTruthLimit.HANDOFF_ALLOWED_NOT_EXECUTION_SUCCESS,
            ],
        )

        assert False, "Expected ValueError"

    except ValueError:
        assert True


def test_target_requires_boundary_rules():
    try:
        HandoffTargetDefinition(
            target_id="invalid",
            target_type=HandoffTargetType.ADAPTER,
            capabilities=[
                HandoffCapability.CALL_EMAIL_ADAPTER,
            ],
            boundary_rules=[],
            truth_limits=[
                HandoffTruthLimit.HANDOFF_ALLOWED_NOT_EXECUTION_SUCCESS,
            ],
        )

        assert False, "Expected ValueError"

    except ValueError:
        assert True


def test_target_requires_truth_limits():
    try:
        HandoffTargetDefinition(
            target_id="invalid",
            target_type=HandoffTargetType.ADAPTER,
            capabilities=[
                HandoffCapability.CALL_EMAIL_ADAPTER,
            ],
            boundary_rules=[
                HandoffBoundaryRule.NO_DIRECT_EXECUTION,
            ],
            truth_limits=[],
        )

        assert False, "Expected ValueError"

    except ValueError:
        assert True


def test_registry_register_and_get():
    registry = HandoffTargetRegistry()

    target = HandoffTargetDefinition(
        target_id="email_adapter",
        target_type=HandoffTargetType.ADAPTER,
        capabilities=[
            HandoffCapability.CALL_EMAIL_ADAPTER,
        ],
        boundary_rules=[
            HandoffBoundaryRule.NO_DIRECT_EXECUTION,
        ],
        truth_limits=[
            HandoffTruthLimit.EMAIL_SENT_NOT_PROBLEM_SOLVED,
        ],
    )

    registry.register(target)

    loaded = registry.get("email_adapter")

    assert loaded is not None
    assert loaded.target_id == "email_adapter"


def test_registry_exists():
    registry = build_default_handoff_registry()

    assert registry.exists("communicator") is True
    assert registry.exists("missing_target") is False


def test_registry_availability():
    registry = HandoffTargetRegistry()

    target = HandoffTargetDefinition(
        target_id="sandbox_target",
        target_type=HandoffTargetType.ADAPTER,
        capabilities=[
            HandoffCapability.CALL_FILE_ADAPTER,
        ],
        boundary_rules=[
            HandoffBoundaryRule.NO_DIRECT_EXECUTION,
        ],
        truth_limits=[
            HandoffTruthLimit.HANDOFF_ALLOWED_NOT_EXECUTION_SUCCESS,
        ],
        status=HandoffTargetStatus.SANDBOX,
    )

    registry.register(target)

    assert registry.is_available("sandbox_target") is True


def test_disabled_target_not_available():
    registry = HandoffTargetRegistry()

    target = HandoffTargetDefinition(
        target_id="disabled_target",
        target_type=HandoffTargetType.ADAPTER,
        capabilities=[
            HandoffCapability.CALL_FILE_ADAPTER,
        ],
        boundary_rules=[
            HandoffBoundaryRule.NO_DIRECT_EXECUTION,
        ],
        truth_limits=[
            HandoffTruthLimit.HANDOFF_ALLOWED_NOT_EXECUTION_SUCCESS,
        ],
        status=HandoffTargetStatus.DISABLED,
    )

    registry.register(target)

    assert registry.is_available("disabled_target") is False


def test_default_registry_contains_external_ai():
    registry = build_default_handoff_registry()

    target = registry.get("external_ai")

    assert target is not None

    assert (
        HandoffBoundaryRule
        .REQUIRES_GOVERNANCE_FOR_EXTERNAL_EXPOSURE
        in target.boundary_rules
    )

    assert (
        HandoffTruthLimit.EXTERNAL_RESULT_NOT_RAY_TRUTH
        in target.truth_limits
    )


def test_sensor_acquisition_not_equal_external_exposure():
    registry = build_default_handoff_registry()

    target = registry.get("sensor_acquisition")

    assert target is not None

    assert (
        HandoffBoundaryRule
        .REQUIRES_GOVERNANCE_FOR_SENSITIVE_ACQUISITION
        in target.boundary_rules
    )

    assert (
        HandoffBoundaryRule
        .REQUIRES_GOVERNANCE_FOR_EXTERNAL_EXPOSURE
        not in target.boundary_rules
    )


def test_continuous_monitoring_requires_explicit_consent():
    registry = build_default_handoff_registry()

    target = registry.get("continuous_monitoring")

    assert target is not None

    assert target.requires_confirmation is True

    assert (
        HandoffBoundaryRule
        .REQUIRES_EXPLICIT_MONITORING_CONSENT
        in target.boundary_rules
    )


def test_email_adapter_preserves_execution_truth_limit():
    registry = build_default_handoff_registry()

    target = registry.get("email_adapter")

    assert target is not None

    assert (
        HandoffTruthLimit
        .HANDOFF_ALLOWED_NOT_EXECUTION_SUCCESS
        in target.truth_limits
    )