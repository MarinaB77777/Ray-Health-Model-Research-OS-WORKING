"""External Core operational contracts.

External Core is mutable operational configuration and domain infrastructure.
It is not Heart of Ray, Heart of Human, Projection authority, Governance, or
universal Ray memory.
"""

from .identity import (
    OPERATIONAL_IDENTITY_SCOPE,
    DetachmentRequest,
    RayIdentity,
    RayIdentityRegistry,
    RayConnectionState,
)
from .settings import (
    ClarificationPolicy,
    EffectiveRaySettings,
    EffectiveSettingsResolver,
    ExternalAIMode,
    RaySettingsRegistry,
    RaySettingsRevision,
    SettingsLayer,
    SettingsStatus,
    UncertaintyDetail,
)
from .domains import (
    DomainCapability,
    DomainDependency,
    DomainLifecycle,
    DomainOperation,
    DomainRayRegistration,
    DomainRayRegistry,
    DomainRisk,
    health_model_research_domain,
)
from .service import ExternalCoreService

__all__ = [
    "OPERATIONAL_IDENTITY_SCOPE",
    "DetachmentRequest",
    "RayConnectionState",
    "RayIdentity",
    "RayIdentityRegistry",
    "ClarificationPolicy",
    "EffectiveRaySettings",
    "EffectiveSettingsResolver",
    "ExternalAIMode",
    "RaySettingsRegistry",
    "RaySettingsRevision",
    "SettingsLayer",
    "SettingsStatus",
    "UncertaintyDetail",
    "DomainCapability",
    "DomainDependency",
    "DomainLifecycle",
    "DomainOperation",
    "DomainRayRegistration",
    "DomainRayRegistry",
    "DomainRisk",
    "health_model_research_domain",
    "ExternalCoreService",
]
