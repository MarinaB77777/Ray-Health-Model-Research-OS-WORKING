from enum import Enum
from pydantic import BaseModel, Field, model_validator
from typing import Optional


class HandoffTargetType(str, Enum):
    INTERNAL_RUNTIME_LAYER = "internal_runtime_layer"
    INTERNAL_RAY_MODULE = "internal_ray_module"
    DOMAIN_RAY = "domain_ray"
    ADAPTER = "adapter"
    EXTERNAL_SERVICE = "external_service"
    ACQUISITION_SOURCE = "acquisition_source"
    MEMORY_LAYER = "memory_layer"


class HandoffOperationalProfile(str, Enum):
    PERSONAL_LIFE = "personal_life"
    ACADEMIC_ANALYTICAL = "academic_analytical"
    BUSINESS_OPERATIONS = "business_operations"
    HEALTH_READINESS = "health_readiness"
    SYSTEM_RUNTIME = "system_runtime"
    CUSTOM = "custom"


class HandoffCapability(str, Enum):
    COMMUNICATE = "communicate"
    REQUEST_GOVERNANCE_REVIEW = "request_governance_review"
    REQUEST_ANALYZER_REVIEW = "request_analyzer_review"
    REQUEST_ANALYST_REASONING = "request_analyst_reasoning"
    ROUTE_TO_DOMAIN_RAY = "route_to_domain_ray"
    WRITE_TEMPORARY_MEMORY = "write_temporary_memory"
    UPDATE_SHARED_ACTION = "update_shared_action"
    CALL_EXTERNAL_AI = "call_external_ai"
    CALL_CALENDAR_ADAPTER = "call_calendar_adapter"
    CALL_EMAIL_ADAPTER = "call_email_adapter"
    CALL_FILE_ADAPTER = "call_file_adapter"
    REQUEST_SENSOR_ACQUISITION = "request_sensor_acquisition"
    REQUEST_CONTINUOUS_MONITORING = "request_continuous_monitoring"
    REQUEST_DATA_ACQUISITION = "request_data_acquisition"


class HandoffTruthLimit(str, Enum):
    ADAPTER_RESPONSE_NOT_VERIFIED_REALITY = (
        "adapter_response_not_verified_reality"
    )
    EXTERNAL_RESULT_NOT_RAY_TRUTH = "external_result_not_ray_truth"
    DELIVERY_ATTEMPT_NOT_DELIVERED = "delivery_attempt_not_delivered"
    CALENDAR_API_OK_NOT_HUMAN_ATTENDED = (
        "calendar_api_ok_not_human_attended"
    )
    EMAIL_SENT_NOT_PROBLEM_SOLVED = "email_sent_not_problem_solved"
    HANDOFF_ALLOWED_NOT_EXECUTION_SUCCESS = (
        "handoff_allowed_not_execution_success"
    )
    MEMORY_WRITE_REQUEST_NOT_MEMORY_AUTHORITY = (
        "memory_write_request_not_memory_authority"
    )
    SENSOR_RESULT_NOT_IDENTITY_TRUTH = "sensor_result_not_identity_truth"


class HandoffBoundaryRule(str, Enum):
    REQUIRES_GOVERNANCE_FOR_EXTERNAL_EXPOSURE = (
        "requires_governance_for_external_exposure"
    )
    REQUIRES_GOVERNANCE_FOR_SENSITIVE_ACQUISITION = (
        "requires_governance_for_sensitive_acquisition"
    )
    REQUIRES_CONFIRMATION_FOR_REAL_WORLD_ACTION = (
        "requires_confirmation_for_real_world_action"
    )
    REQUIRES_EXPLICIT_MONITORING_CONSENT = (
        "requires_explicit_monitoring_consent"
    )
    REQUIRES_TRACE = "requires_trace"
    REQUIRES_UNCERTAINTY_PRESERVATION = (
        "requires_uncertainty_preservation"
    )
    NO_DIRECT_EXECUTION = "no_direct_execution"
    NO_AUTHORITY_EXPANSION = "no_authority_expansion"
    NO_TRUTH_PROMOTION = "no_truth_promotion"
    NO_MEMORY_PROMOTION_WITHOUT_PERMISSION = (
        "no_memory_promotion_without_permission"
    )


class HandoffTargetStatus(str, Enum):
    ACTIVE = "active"
    SANDBOX = "sandbox"
    DISABLED = "disabled"
    DEPRECATED = "deprecated"


class HandoffTargetDefinition(BaseModel):
    target_id: str
    target_type: HandoffTargetType

    profile: HandoffOperationalProfile = (
        HandoffOperationalProfile.SYSTEM_RUNTIME
    )

    capabilities: list[HandoffCapability] = Field(default_factory=list)
    boundary_rules: list[HandoffBoundaryRule] = Field(default_factory=list)
    truth_limits: list[HandoffTruthLimit] = Field(default_factory=list)

    status: HandoffTargetStatus = HandoffTargetStatus.ACTIVE

    version: str = "1.0"
    owner_layer: Optional[str] = None
    requires_confirmation: bool = False
    allowed_payload_types: list[str] = Field(default_factory=list)

    description: Optional[str] = None

    @model_validator(mode="after")
    def validate_target_definition(self) -> "HandoffTargetDefinition":
        if not self.capabilities:
            raise ValueError(
                "Handoff target requires at least one capability"
            )

        if not self.boundary_rules:
            raise ValueError(
                "Handoff target requires boundary rules"
            )

        if not self.truth_limits:
            raise ValueError(
                "Handoff target requires truth limits"
            )

        return self

    def is_available(self) -> bool:
        return self.status in {
            HandoffTargetStatus.ACTIVE,
            HandoffTargetStatus.SANDBOX,
        }


class HandoffTargetRegistry:
    """
    Registry of explicit handoff targets.

    Registry is NOT:
    - executor;
    - governance authority;
    - planner;
    - truth authority.

    It defines where Runtime may prepare handoff requests,
    but does not prove permission, execution, or success.

    New targets must be explicitly registered.
    No hidden or automatic target expansion.
    """

    def __init__(self) -> None:
        self._targets: dict[str, HandoffTargetDefinition] = {}

    def register(
        self,
        target: HandoffTargetDefinition,
    ) -> HandoffTargetDefinition:
        self._targets[target.target_id] = target
        return target

    def get(
        self,
        target_id: str,
    ) -> Optional[HandoffTargetDefinition]:
        return self._targets.get(target_id)

    def exists(self, target_id: str) -> bool:
        return target_id in self._targets

    def is_available(self, target_id: str) -> bool:
        target = self.get(target_id)

        if target is None:
            return False

        return target.is_available()

    def list_all(self) -> list[HandoffTargetDefinition]:
        return list(self._targets.values())

    def list_available(self) -> list[HandoffTargetDefinition]:
        return [
            target
            for target in self._targets.values()
            if target.is_available()
        ]


DEFAULT_HANDOFF_BOUNDARY_RULES = [
    HandoffBoundaryRule.REQUIRES_TRACE,
    HandoffBoundaryRule.REQUIRES_UNCERTAINTY_PRESERVATION,
    HandoffBoundaryRule.NO_DIRECT_EXECUTION,
    HandoffBoundaryRule.NO_AUTHORITY_EXPANSION,
    HandoffBoundaryRule.NO_TRUTH_PROMOTION,
]


DEFAULT_TRUTH_LIMITS = [
    HandoffTruthLimit.HANDOFF_ALLOWED_NOT_EXECUTION_SUCCESS,
    HandoffTruthLimit.ADAPTER_RESPONSE_NOT_VERIFIED_REALITY,
]


def build_default_handoff_registry() -> HandoffTargetRegistry:
    registry = HandoffTargetRegistry()

    registry.register(
        HandoffTargetDefinition(
            target_id="communicator",
            target_type=HandoffTargetType.INTERNAL_RAY_MODULE,
            profile=HandoffOperationalProfile.SYSTEM_RUNTIME,
            capabilities=[HandoffCapability.COMMUNICATE],
            boundary_rules=DEFAULT_HANDOFF_BOUNDARY_RULES,
            truth_limits=[
                HandoffTruthLimit.DELIVERY_ATTEMPT_NOT_DELIVERED,
                HandoffTruthLimit.HANDOFF_ALLOWED_NOT_EXECUTION_SUCCESS,
            ],
            owner_layer="runtime/handoff",
            description="Human-facing communication boundary.",
        )
    )

    registry.register(
        HandoffTargetDefinition(
            target_id="governance",
            target_type=HandoffTargetType.INTERNAL_RUNTIME_LAYER,
            capabilities=[HandoffCapability.REQUEST_GOVERNANCE_REVIEW],
            boundary_rules=DEFAULT_HANDOFF_BOUNDARY_RULES,
            truth_limits=DEFAULT_TRUTH_LIMITS,
            owner_layer="governance",
            description="Governance review boundary.",
        )
    )

    registry.register(
        HandoffTargetDefinition(
            target_id="analyzer",
            target_type=HandoffTargetType.INTERNAL_RAY_MODULE,
            capabilities=[HandoffCapability.REQUEST_ANALYZER_REVIEW],
            boundary_rules=DEFAULT_HANDOFF_BOUNDARY_RULES,
            truth_limits=DEFAULT_TRUTH_LIMITS,
            owner_layer="analyzer",
            description=(
                "Readiness / uncertainty / consistency review boundary."
            ),
        )
    )

    registry.register(
        HandoffTargetDefinition(
            target_id="analyst",
            target_type=HandoffTargetType.INTERNAL_RAY_MODULE,
            capabilities=[HandoffCapability.REQUEST_ANALYST_REASONING],
            boundary_rules=DEFAULT_HANDOFF_BOUNDARY_RULES,
            truth_limits=DEFAULT_TRUTH_LIMITS,
            owner_layer="analyst",
            description="Bounded reasoning / tradeoff analysis boundary.",
        )
    )

    registry.register(
        HandoffTargetDefinition(
            target_id="domain_ray",
            target_type=HandoffTargetType.DOMAIN_RAY,
            capabilities=[HandoffCapability.ROUTE_TO_DOMAIN_RAY],
            boundary_rules=DEFAULT_HANDOFF_BOUNDARY_RULES,
            truth_limits=DEFAULT_TRUTH_LIMITS,
            owner_layer="domain_ray",
            description="Generic domain Ray handoff boundary.",
        )
    )

    registry.register(
        HandoffTargetDefinition(
            target_id="temporary_memory",
            target_type=HandoffTargetType.MEMORY_LAYER,
            capabilities=[HandoffCapability.WRITE_TEMPORARY_MEMORY],
            boundary_rules=[
                *DEFAULT_HANDOFF_BOUNDARY_RULES,
                HandoffBoundaryRule.NO_MEMORY_PROMOTION_WITHOUT_PERMISSION,
            ],
            truth_limits=[
                *DEFAULT_TRUTH_LIMITS,
                HandoffTruthLimit.MEMORY_WRITE_REQUEST_NOT_MEMORY_AUTHORITY,
            ],
            owner_layer="temporary_memory",
            description="Temporary operational memory boundary.",
        )
    )

    registry.register(
        HandoffTargetDefinition(
            target_id="shared_action",
            target_type=HandoffTargetType.INTERNAL_RUNTIME_LAYER,
            capabilities=[HandoffCapability.UPDATE_SHARED_ACTION],
            boundary_rules=DEFAULT_HANDOFF_BOUNDARY_RULES,
            truth_limits=DEFAULT_TRUTH_LIMITS,
            owner_layer="shared_action",
            description="Shared action state boundary.",
        )
    )

    registry.register(
        HandoffTargetDefinition(
            target_id="external_ai",
            target_type=HandoffTargetType.EXTERNAL_SERVICE,
            capabilities=[HandoffCapability.CALL_EXTERNAL_AI],
            boundary_rules=[
                *DEFAULT_HANDOFF_BOUNDARY_RULES,
                HandoffBoundaryRule.REQUIRES_GOVERNANCE_FOR_EXTERNAL_EXPOSURE,
            ],
            truth_limits=[
                HandoffTruthLimit.EXTERNAL_RESULT_NOT_RAY_TRUTH,
                HandoffTruthLimit.ADAPTER_RESPONSE_NOT_VERIFIED_REALITY,
                HandoffTruthLimit.HANDOFF_ALLOWED_NOT_EXECUTION_SUCCESS,
            ],
            owner_layer="external_service",
            description="External AI processing boundary.",
        )
    )

    registry.register(
        HandoffTargetDefinition(
            target_id="calendar_adapter",
            target_type=HandoffTargetType.ADAPTER,
            capabilities=[HandoffCapability.CALL_CALENDAR_ADAPTER],
            boundary_rules=[
                *DEFAULT_HANDOFF_BOUNDARY_RULES,
                HandoffBoundaryRule.REQUIRES_CONFIRMATION_FOR_REAL_WORLD_ACTION,
            ],
            truth_limits=[
                HandoffTruthLimit.CALENDAR_API_OK_NOT_HUMAN_ATTENDED,
                HandoffTruthLimit.ADAPTER_RESPONSE_NOT_VERIFIED_REALITY,
                HandoffTruthLimit.HANDOFF_ALLOWED_NOT_EXECUTION_SUCCESS,
            ],
            owner_layer="calendar_adapter",
            requires_confirmation=True,
            description="Calendar adapter boundary.",
        )
    )

    registry.register(
        HandoffTargetDefinition(
            target_id="email_adapter",
            target_type=HandoffTargetType.ADAPTER,
            capabilities=[HandoffCapability.CALL_EMAIL_ADAPTER],
            boundary_rules=[
                *DEFAULT_HANDOFF_BOUNDARY_RULES,
                HandoffBoundaryRule.REQUIRES_CONFIRMATION_FOR_REAL_WORLD_ACTION,
            ],
            truth_limits=[
                HandoffTruthLimit.EMAIL_SENT_NOT_PROBLEM_SOLVED,
                HandoffTruthLimit.DELIVERY_ATTEMPT_NOT_DELIVERED,
                HandoffTruthLimit.ADAPTER_RESPONSE_NOT_VERIFIED_REALITY,
                HandoffTruthLimit.HANDOFF_ALLOWED_NOT_EXECUTION_SUCCESS,
            ],
            owner_layer="email_adapter",
            requires_confirmation=True,
            description="Email adapter boundary.",
        )
    )

    registry.register(
        HandoffTargetDefinition(
            target_id="file_adapter",
            target_type=HandoffTargetType.ADAPTER,
            capabilities=[HandoffCapability.CALL_FILE_ADAPTER],
            boundary_rules=DEFAULT_HANDOFF_BOUNDARY_RULES,
            truth_limits=DEFAULT_TRUTH_LIMITS,
            owner_layer="file_adapter",
            description="File processing adapter boundary.",
        )
    )

    registry.register(
        HandoffTargetDefinition(
            target_id="sensor_acquisition",
            target_type=HandoffTargetType.ACQUISITION_SOURCE,
            capabilities=[HandoffCapability.REQUEST_SENSOR_ACQUISITION],
            boundary_rules=[
                *DEFAULT_HANDOFF_BOUNDARY_RULES,
                (
                    HandoffBoundaryRule
                    .REQUIRES_GOVERNANCE_FOR_SENSITIVE_ACQUISITION
                ),
            ],
            truth_limits=[
                HandoffTruthLimit.SENSOR_RESULT_NOT_IDENTITY_TRUTH,
                HandoffTruthLimit.ADAPTER_RESPONSE_NOT_VERIFIED_REALITY,
                HandoffTruthLimit.HANDOFF_ALLOWED_NOT_EXECUTION_SUCCESS,
            ],
            owner_layer="acquisition",
            requires_confirmation=True,
            description="Sensor acquisition boundary.",
        )
    )
    
    registry.register(
        HandoffTargetDefinition(
            target_id="continuous_monitoring",
            target_type=HandoffTargetType.ACQUISITION_SOURCE,
            capabilities=[
                HandoffCapability.REQUEST_CONTINUOUS_MONITORING,
            ],
            boundary_rules=[
                *DEFAULT_HANDOFF_BOUNDARY_RULES,
                (
                    HandoffBoundaryRule
                    .REQUIRES_GOVERNANCE_FOR_SENSITIVE_ACQUISITION
                ),
                (
                    HandoffBoundaryRule
                    .REQUIRES_EXPLICIT_MONITORING_CONSENT
                ),
            ],
            truth_limits=[
                HandoffTruthLimit.SENSOR_RESULT_NOT_IDENTITY_TRUTH,
                HandoffTruthLimit.ADAPTER_RESPONSE_NOT_VERIFIED_REALITY,
                HandoffTruthLimit.HANDOFF_ALLOWED_NOT_EXECUTION_SUCCESS,
            ],
            owner_layer="acquisition",
            requires_confirmation=True,
            description=(
                "Continuous monitoring boundary. Requires explicit, "
                "scope-bounded, revocable monitoring consent."
            ),
        )
    )

    registry.register(
        HandoffTargetDefinition(
            target_id="acquisition_request",
            target_type=HandoffTargetType.ACQUISITION_SOURCE,
            capabilities=[HandoffCapability.REQUEST_DATA_ACQUISITION],
            boundary_rules=DEFAULT_HANDOFF_BOUNDARY_RULES,
            truth_limits=[
                HandoffTruthLimit.ADAPTER_RESPONSE_NOT_VERIFIED_REALITY,
                HandoffTruthLimit.HANDOFF_ALLOWED_NOT_EXECUTION_SUCCESS,
            ],
            owner_layer="acquisition",
            description="General data acquisition request boundary.",
        )
    )

    return registry