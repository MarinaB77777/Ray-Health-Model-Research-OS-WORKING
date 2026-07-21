# governance/schemas.py.
from enum import Enum
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class GovernanceDecisionStatus(str, Enum):
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    NOT_ENOUGH_DATA = "not_enough_data"


class GovernanceVisibilityLevel(str, Enum):
    INTERNAL_ONLY = "internal_only"
    TRUSTED_HUMAN = "trusted_human"
    HUMAN_SAFE = "human_safe"
    PUBLIC_FILTERED = "public_filtered"
    EXTERNAL_MINIMAL = "external_minimal"


class GovernanceTargetAudience(str, Enum):
    INTERNAL_RAY = "internal_ray"
    PRIMARY_HUMAN = "primary_human"
    TRUSTED_PERSON = "trusted_person"
    EXTERNAL_PERSON = "external_person"
    EXTERNAL_AI = "external_ai"
    INTERNET = "internet"
    EMERGENCY_CONTACT = "emergency_contact"


class TrustLevel(str, Enum):
    BASIC = "basic_trust"
    EXPANDED = "expanded_trust"
    DEEP = "deep_trust"


class ReversibilityLevel(str, Enum):
    FULLY_REVERSIBLE = "fully_reversible"
    PARTIALLY_REVERSIBLE = "partially_reversible"
    HARD_TO_REVERSE = "hard_to_reverse"
    IRREVERSIBLE = "irreversible"


class ExternalTargetType(str, Enum):
    NONE = "none"
    TRUSTED_HUMAN = "trusted_human"
    EXTERNAL_PERSON = "external_person"
    EXTERNAL_AI = "external_ai"
    INTERNET = "internet"
    EMERGENCY_CONTACT = "emergency_contact"


class EmergencyType(str, Enum):
    NONE = "none"
    PROJECTED = "projected_emergency"
    FACTUAL = "factual_emergency"


class DomainImportanceLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class HarmSeverity(str, Enum):
    NONE = "none"
    MINIMAL = "minimal"
    MODERATE = "moderate"
    SERIOUS = "serious"
    CRITICAL = "critical"


class GovernanceSanitizerStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    REQUIRED_PENDING = "required_pending"
    APPLIED = "applied"
    FAILED = "failed"


class GovernancePolicyTemporalStatus(str, Enum):
    NOT_APPLICABLE = "not_applicable"
    VALID = "valid"
    MISSING = "missing"
    VERSION_MISMATCH = "version_mismatch"
    NOT_YET_VALID = "not_yet_valid"
    EXPIRED = "expired"
    REVALIDATION_OVERDUE = "revalidation_overdue"


class AcceptableHarmProfile(BaseModel):
    maximum_severity: HarmSeverity = HarmSeverity.MINIMAL
    permitted_impact_categories: List[str] = Field(default_factory=list)
    reversible_only: bool = True
    documented_benefit_required: bool = True


class PolicyTemporalValidity(BaseModel):
    policy_source: str
    policy_version: str
    valid_from: datetime
    valid_until: Optional[datetime] = None
    last_revalidated_at: Optional[datetime] = None
    revalidation_due_at: Optional[datetime] = None


class SensitiveDomainRule(BaseModel):
    domain_id: str

    requires_confirmation: bool = True
    protected: bool = False

    public_allowed: bool = False
    external_ai_allowed: bool = False
    internet_allowed: bool = False
    delegated_autonomy_allowed: bool = False

    importance_level: DomainImportanceLevel = DomainImportanceLevel.MODERATE
    acceptable_harm_profile: AcceptableHarmProfile = Field(
        default_factory=AcceptableHarmProfile
    )
    allowed_overrides: List[str] = Field(default_factory=list)
    policy_version: str = "sensitive_domain_rule_v1"


class ProposedAction(BaseModel):
    action_id: str
    action_type: str

    requires_external_communication: bool = False
    external_target_type: ExternalTargetType = ExternalTargetType.NONE

    requires_memory_write: bool = False
    memory_target: Optional[str] = None

    requires_autonomy: bool = False
    reversibility_level: ReversibilityLevel = ReversibilityLevel.FULLY_REVERSIBLE

    affected_sensitive_domains: List[str] = Field(default_factory=list)
    unknown_sensitive_domains_present: bool = False

    projected_harm_severity: HarmSeverity = HarmSeverity.NONE
    projected_impact_categories: List[str] = Field(default_factory=list)
    requested_governance_overrides: List[str] = Field(default_factory=list)

    payload: Dict[str, Any] = Field(default_factory=dict)


class GovernanceContext(BaseModel):
    trust_level: TrustLevel

    human_prohibition_active: bool = False

    delegated_autonomy_allowed: bool = False
    external_communication_allowed: bool = False
    memory_write_allowed: bool = False

    emergency_type: EmergencyType = EmergencyType.NONE
    factual_emergency_policy_allowed: bool = False

    sensitive_domain_config: Dict[str, SensitiveDomainRule] = Field(default_factory=dict)
    policy_temporal_validity: Dict[str, PolicyTemporalValidity] = Field(
        default_factory=dict
    )
    evaluation_time: Optional[datetime] = None
    temporal_policy_enforcement: bool = False

    autonomy_policy_version: str = "autonomy_policy_v1"
    privacy_policy_version: str = "privacy_policy_v1"
    emergency_policy_version: str = "emergency_policy_v1"


class GovernanceVerdict(BaseModel):
    action_id: str

    governance_decision_status: GovernanceDecisionStatus
    governance_visibility_level: GovernanceVisibilityLevel
    governance_target_audience: GovernanceTargetAudience

    governance_confirmation_required: bool = False
    governance_reason_codes: List[str] = Field(default_factory=list)

    governance_allowed_action_scopes: List[str] = Field(default_factory=list)
    governance_blocked_action_scopes: List[str] = Field(default_factory=list)

    governance_allowed_external_targets: List[str] = Field(default_factory=list)
    governance_blocked_external_targets: List[str] = Field(default_factory=list)

    governance_allowed_memory_targets: List[str] = Field(default_factory=list)
    governance_blocked_memory_targets: List[str] = Field(default_factory=list)

    governance_restrictions: List[str] = Field(default_factory=list)

    governance_policy_sources: List[str] = Field(default_factory=list)
    governance_policy_versions: List[str] = Field(default_factory=list)

    governance_trace_id: str
    governance_version: str = "governance_mvp_v4_1"
    governance_rule_hits: List[str] = Field(default_factory=list)

    governance_sanitizer_required: bool = False
    governance_sanitizer_status: GovernanceSanitizerStatus = (
        GovernanceSanitizerStatus.NOT_REQUIRED
    )
    governance_sanitizer_policy_version: str = "structured_external_v1"
    governance_sanitizer_removed_fields: List[str] = Field(default_factory=list)

    governance_policy_temporal_status: GovernancePolicyTemporalStatus = (
        GovernancePolicyTemporalStatus.NOT_APPLICABLE
    )
    governance_policy_temporal_details: List[str] = Field(default_factory=list)

    governance_scope_conflicts: List[str] = Field(default_factory=list)
