from __future__ import annotations

from datetime import UTC, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from governance.rules import governance_check
from governance.schemas import (
    ExternalTargetType,
    GovernanceContext,
    GovernanceDecisionStatus,
    PolicyTemporalValidity,
    ProposedAction,
    TrustLevel,
)
from governance.visibility import apply_visibility_scope

from .contracts import ConnectionScope, ExternalAIConnection, ExternalAIError, ExternalAIPolicy, GatewayResult
from .filters import FILTER_PROFILES, OPTIONAL_CATEGORIES, filter_inbound_text, filter_outbound_text, profile_catalog
from .providers import ProviderRegistry
from .registry import ExternalAIRegistry
from .secrets import EncryptedSecretVault


SettingsProvider = Callable[[str, str | None], dict[str, Any]]


class ExternalAIGateway:
    PLATFORM_OWNER = "platform"
    POLICY_VERSION = "external-ai-gateway-policy-1"

    def __init__(
        self,
        data_root: str | Path,
        *,
        provider_registry: ProviderRegistry | None = None,
        settings_provider: SettingsProvider | None = None,
    ) -> None:
        root = Path(data_root) / "external_ai"
        self.registry = ExternalAIRegistry(root)
        self.vault = EncryptedSecretVault(root)
        self.providers = provider_registry or ProviderRegistry()
        self.settings_provider = settings_provider

    def contract(self, *, account_id: str, can_manage_platform: bool) -> dict[str, Any]:
        return {
            "schema_version": "external-ai-gateway-contract-1.0.0",
            "providers": self.providers.contract(),
            "connection_scopes": [scope.value for scope in ConnectionScope],
            "filter_profiles": profile_catalog(),
            "mandatory_never_send_categories": [
                "credentials_and_secrets", "direct_identifiers", "ray_internal_state",
                "participant_raw_data", "raw_sensor_or_biometric_data", "hidden_diagnostics", "unrestricted_memory",
            ],
            "optional_never_send_categories": list(OPTIONAL_CATEGORIES),
            "outbound_channel": "external_ai_request",
            "inbound_channel": "external_ai_response_artifact",
            "outbound_and_inbound_channels_are_distinct": True,
            "hidden_ray_context_attached": False,
            "external_output_is_ray_truth": False,
            "external_output_memory_write_allowed": False,
            "external_output_execution_authority": False,
            "credential_storage": self.vault.storage_mode,
            "credentials_returned_by_api": False,
            "arbitrary_provider_urls_allowed": False,
            "account_id": account_id,
            "can_manage_platform": can_manage_platform,
        }

    def list_models(self, provider_id: str, credential: str) -> list[dict[str, Any]]:
        return self.providers.get(provider_id).list_models(credential)

    def connect(
        self,
        *,
        actor_account_id: str,
        scope: ConnectionScope,
        provider_id: str,
        model: str,
        credential: str,
        can_manage_platform: bool,
    ) -> dict[str, Any]:
        if scope == ConnectionScope.PLATFORM and not can_manage_platform:
            raise ExternalAIError("PLATFORM_EXTERNAL_AI_ADMIN_REQUIRED", status_code=403)
        owner_id = self.PLATFORM_OWNER if scope == ConnectionScope.PLATFORM else actor_account_id
        provider = self.providers.get(provider_id)
        provider.test_connection(credential, model)
        credential_ref = self.vault.put(credential)
        connection = ExternalAIConnection(scope=scope, owner_id=owner_id, provider_id=provider_id, model=model, credential_ref=credential_ref)
        try:
            saved = self.registry.save_connection(connection)
        except Exception:
            self.vault.delete(credential_ref)
            raise
        if self.registry.latest_policy(scope, owner_id) is None:
            default_profile = "strict_general"
            self.registry.save_policy(ExternalAIPolicy(scope=scope, owner_id=owner_id, profile_id=default_profile, enabled=True))
        return saved

    def list_connections(self, account_id: str) -> dict[str, Any]:
        effective = self.registry.effective_connection(account_id)
        return {
            "connections": self.registry.list_visible(account_id),
            "effective_connection_id": effective.connection_id if effective else None,
            "effective_scope": effective.scope.value if effective else None,
        }

    def delete_connection(self, connection_id: str, *, actor_account_id: str, can_manage_platform: bool) -> None:
        credential_ref = self.registry.delete_connection(connection_id, actor_account_id=actor_account_id, platform_admin=can_manage_platform)
        self.vault.delete(credential_ref)

    def get_policies(self, account_id: str) -> dict[str, Any]:
        platform = self.registry.latest_policy(ConnectionScope.PLATFORM, self.PLATFORM_OWNER) or ExternalAIPolicy(scope=ConnectionScope.PLATFORM, owner_id=self.PLATFORM_OWNER, profile_id="strict_general", enabled=True)
        account = self.registry.latest_policy(ConnectionScope.ACCOUNT, account_id) or ExternalAIPolicy(scope=ConnectionScope.ACCOUNT, owner_id=account_id, profile_id="strict_general", enabled=True)
        return {"platform_policy": platform.to_dict(), "account_policy": account.to_dict()}

    def save_policy(
        self,
        *,
        actor_account_id: str,
        scope: ConnectionScope,
        profile_id: str,
        enabled: bool,
        never_send_categories: list[str],
        never_send_terms: list[str],
        can_manage_platform: bool,
    ) -> dict[str, Any]:
        if scope == ConnectionScope.PLATFORM and not can_manage_platform:
            raise ExternalAIError("PLATFORM_EXTERNAL_AI_ADMIN_REQUIRED", status_code=403)
        owner_id = self.PLATFORM_OWNER if scope == ConnectionScope.PLATFORM else actor_account_id
        clean_terms = tuple(dict.fromkeys(term.strip() for term in never_send_terms if term.strip()))
        policy = ExternalAIPolicy(scope=scope, owner_id=owner_id, profile_id=profile_id, enabled=enabled, never_send_categories=tuple(dict.fromkeys(never_send_categories)), never_send_terms=clean_terms)
        return self.registry.save_policy(policy)

    def ask(self, *, account_id: str | None, role: str, message: str, language: str) -> GatewayResult:
        request_id = str(uuid4())
        connection = self.registry.effective_connection(account_id)
        if connection is None:
            return GatewayResult(request_id=request_id, status="not_configured", error_code="EXTERNAL_AI_NOT_CONFIGURED")
        try:
            self._assert_ray_settings_allow(role=role, account_id=account_id)
            policies = self._effective_policies(account_id)
            outbound = filter_outbound_text(message, policies)
            if not outbound.allowed:
                return GatewayResult(request_id=request_id, status="outbound_blocked", provider_id=connection.provider_id, model=connection.model, connection_scope=connection.scope.value, error_code=outbound.reason_codes[0] if outbound.reason_codes else "OUTBOUND_BLOCKED", outbound_reason_codes=outbound.reason_codes + outbound.matched_categories)
            verdict = self._governance_verdict(request_id)
            if verdict.governance_decision_status in {GovernanceDecisionStatus.BLOCKED, GovernanceDecisionStatus.NOT_ENOUGH_DATA}:
                return GatewayResult(request_id=request_id, status="governance_blocked", provider_id=connection.provider_id, model=connection.model, connection_scope=connection.scope.value, error_code="EXTERNAL_AI_GOVERNANCE_BLOCKED")
            sanitized_payload = apply_visibility_scope({"external_minimal": {"question": outbound.text, "language": language}}, verdict)
            prompt = str(sanitized_payload.get("question") or "").strip()
            if not prompt:
                raise ExternalAIError("EXTERNAL_AI_SANITIZED_PROMPT_EMPTY")
            credential = self.vault.get(connection.credential_ref)
            answer = self.providers.get(connection.provider_id).generate(credential, connection.model, prompt, language)
            inbound = filter_inbound_text(answer.text)
            if not inbound.allowed:
                result = GatewayResult(request_id=request_id, status="inbound_blocked", provider_id=connection.provider_id, model=connection.model, connection_scope=connection.scope.value, error_code=inbound.reason_codes[0], inbound_reason_codes=inbound.reason_codes)
            else:
                result = GatewayResult(request_id=request_id, status="received", content=inbound.text, provider_id=connection.provider_id, model=connection.model, connection_scope=connection.scope.value)
            self.registry.audit("external_ai_exchange_completed", account_id or "platform_participant", request_id, {"provider_id": connection.provider_id, "model": connection.model, "connection_scope": connection.scope.value, "status": result.status, "outbound_sha256": sha256(prompt.encode("utf-8")).hexdigest(), "inbound_sha256": sha256((answer.text or "").encode("utf-8")).hexdigest()})
            return result
        except ExternalAIError as exc:
            self.registry.audit("external_ai_exchange_failed", account_id or "platform_participant", request_id, {"provider_id": connection.provider_id, "model": connection.model, "connection_scope": connection.scope.value, "error_code": exc.code})
            return GatewayResult(request_id=request_id, status="failed", provider_id=connection.provider_id, model=connection.model, connection_scope=connection.scope.value, error_code=exc.code)
        except Exception:
            self.registry.audit("external_ai_exchange_failed", account_id or "platform_participant", request_id, {"provider_id": connection.provider_id, "model": connection.model, "connection_scope": connection.scope.value, "error_code": "EXTERNAL_AI_GATEWAY_INTERNAL_ERROR"})
            return GatewayResult(request_id=request_id, status="failed", provider_id=connection.provider_id, model=connection.model, connection_scope=connection.scope.value, error_code="EXTERNAL_AI_GATEWAY_INTERNAL_ERROR")

    def _effective_policies(self, account_id: str | None) -> tuple[ExternalAIPolicy, ...]:
        platform = self.registry.latest_policy(ConnectionScope.PLATFORM, self.PLATFORM_OWNER) or ExternalAIPolicy(scope=ConnectionScope.PLATFORM, owner_id=self.PLATFORM_OWNER, profile_id="strict_general", enabled=True)
        if not account_id:
            return (platform,)
        account = self.registry.latest_policy(ConnectionScope.ACCOUNT, account_id) or ExternalAIPolicy(scope=ConnectionScope.ACCOUNT, owner_id=account_id, profile_id="strict_general", enabled=True)
        return (platform, account)

    def _assert_ray_settings_allow(self, *, role: str, account_id: str | None) -> None:
        if self.settings_provider is None:
            raise ExternalAIError("EXTERNAL_AI_SETTINGS_PROVIDER_MISSING", status_code=500)
        settings = self.settings_provider(role, account_id)
        if settings.get("external_ai_mode") not in {"sandbox", "trial", "active"}:
            raise ExternalAIError("EXTERNAL_AI_DISABLED_BY_RAY_SETTINGS")
        if "external_ai_request" not in set(settings.get("allowed_capabilities") or ()):
            raise ExternalAIError("EXTERNAL_AI_CAPABILITY_NOT_ALLOWED")
        if "external_ai_request" not in set(settings.get("allowed_channels") or ()):
            raise ExternalAIError("EXTERNAL_AI_OUTBOUND_CHANNEL_NOT_ALLOWED")

    def _governance_verdict(self, request_id: str):
        now = datetime.now(UTC)
        validity = PolicyTemporalValidity(policy_source="external_communication_policy", policy_version=self.POLICY_VERSION, valid_from=now - timedelta(seconds=1), last_revalidated_at=now, revalidation_due_at=now + timedelta(days=30))
        action = ProposedAction(action_id=request_id, action_type="external_ai_information_request", requires_external_communication=True, external_target_type=ExternalTargetType.EXTERNAL_AI)
        context = GovernanceContext(trust_level=TrustLevel.BASIC, external_communication_allowed=True, evaluation_time=now, temporal_policy_enforcement=True, privacy_policy_version=self.POLICY_VERSION, policy_temporal_validity={"external_communication_policy": validity})
        return governance_check(action, context)
