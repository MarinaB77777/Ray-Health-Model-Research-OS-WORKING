"""External Core contracts shared by Base Ray and registered domain Rays."""

from .identity import (
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
