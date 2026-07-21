from copy import deepcopy
from datetime import UTC, datetime


CONSENT_POLICY_VERSION = "consent-policy-1"

ALLOWED_CONSENT_STATUSES = {
    "not_evaluated",
    "pending",
    "granted",
    "denied",
    "revoked",
    "expired",
}

ALLOWED_CONSENT_SCOPES = {
    "pilot_participation",
    "research_snapshot_export",
    "dataset_inclusion",
    "future_contact",
    "future_studies",
}

DATETIME_FIELDS = {
    "granted_at",
    "revoked_at",
    "expiration_at",
}


def _parse_iso_datetime(value):
    if value is None:
        return None

    if not isinstance(value, str) or not value.strip():
        raise ValueError("datetime value must be a non-empty ISO string")

    normalized_value = value.strip()

    if normalized_value.endswith("Z"):
        normalized_value = normalized_value[:-1] + "+00:00"

    parsed = datetime.fromisoformat(normalized_value)

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)

    return parsed

DEFAULT_CONSENT_RECORD = {
    "consent_status": "not_evaluated",
    "consent_version": CONSENT_POLICY_VERSION,
    "consent_scope": [],
    "granted_at": None,
    "revoked_at": None,
    "expiration_at": None,
    "consent_basis": "not_evaluated",
    "notes": None,
}


def get_default_consent_record() -> dict:
    return deepcopy(DEFAULT_CONSENT_RECORD)


def _base_result(
    *,
    consent_eligible: bool,
    consent_status,
    consent_evaluation_status: str,
    required_scope: str,
    granted_scopes: list[str],
    reason_code: str,
    reason_codes: list[str],
) -> dict:
    return {
        "consent_eligible": consent_eligible,
        "consent_status": consent_status,
        "consent_evaluation_status": consent_evaluation_status,
        "required_scope": required_scope,
        "granted_scopes": granted_scopes,
        "reason_code": reason_code,
        "reason_codes": reason_codes,
        "consent_policy_version": CONSENT_POLICY_VERSION,
        "consent_evaluation_method": "static_consent_policy",
        "consent_decision_is_not_governance_verdict": True,
        "consent_status_is_not_runtime_permission": True,
        "consent_evaluation_is_not_session_collection_permission": True,
        "session_collection_requires_session_level_agreement": True,
        "declined_session_agreement_blocks_new_collection": True,
        "consent_granted_is_not_export_approval": True,
        "consent_evaluation_is_not_research_approval": True,
        "consent_evaluation_is_not_dataset_admission": True,
        "consent_evaluation_is_not_retention_approval": True,
        "silence_is_not_consent": True,
        "consent_scope_is_not_global_permission": True,
        "consent_record_is_not_identity": True,
        "consent_version_checked": True,
        "consent_scope_checked": True,
    }


def _normalize_required_scope(required_scope: str) -> str:
    if not isinstance(required_scope, str):
        raise ValueError("required_scope must be a string")

    normalized_scope = required_scope.strip()

    if not normalized_scope:
        raise ValueError("required_scope must not be empty")

    if normalized_scope not in ALLOWED_CONSENT_SCOPES:
        raise ValueError("required_scope is not allowed")

    return normalized_scope


def _evaluate_consent_scopes(consent_scope) -> tuple[list[str], list[str]]:
    reason_codes = []

    if consent_scope is None:
        return [], []

    if isinstance(consent_scope, str):
        raw_scopes = [consent_scope]
    elif isinstance(consent_scope, list):
        raw_scopes = consent_scope
    else:
        return [], ["CONSENT_SCOPE_INVALID_TYPE"]

    normalized_scopes = []
    seen_scopes = set()

    for scope in raw_scopes:
        if not isinstance(scope, str) or not scope.strip():
            reason_codes.append("CONSENT_SCOPE_ITEM_INVALID")
            continue

        normalized_scope = scope.strip()

        if normalized_scope not in ALLOWED_CONSENT_SCOPES:
            reason_codes.append("CONSENT_SCOPE_NOT_ALLOWED")
            continue

        if normalized_scope in seen_scopes:
            reason_codes.append("CONSENT_SCOPE_DUPLICATE")
            continue

        seen_scopes.add(normalized_scope)
        normalized_scopes.append(normalized_scope)

    return normalized_scopes, reason_codes


def _collect_record_reason_codes(consent_record: dict) -> list[str]:
    reason_codes = []

    consent_version = consent_record.get("consent_version")
    consent_status = consent_record.get("consent_status")
    consent_basis = consent_record.get("consent_basis")
    parsed_expiration_at = None

    if consent_version != CONSENT_POLICY_VERSION:
        reason_codes.append("CONSENT_VERSION_MISMATCH")

    if consent_status is None:
        reason_codes.append("CONSENT_STATUS_MISSING")
    elif consent_status not in ALLOWED_CONSENT_STATUSES:
        reason_codes.append("CONSENT_STATUS_INVALID")

    if (
        consent_basis is not None
        and (
            not isinstance(consent_basis, str)
            or not consent_basis.strip()
        )
    ):
        reason_codes.append("CONSENT_BASIS_INVALID")

    for field_name in sorted(DATETIME_FIELDS):
        value = consent_record.get(field_name)

        if value is None:
            continue

        try:
            parsed_value = _parse_iso_datetime(value)
        except (TypeError, ValueError):
            reason_codes.append(
                f"CONSENT_DATETIME_FIELD_INVALID:{field_name}"
            )
            continue

        if field_name == "expiration_at":
            parsed_expiration_at = parsed_value


    if (
        consent_status == "granted"
        and consent_record.get("granted_at") is None
    ):
        reason_codes.append("GRANTED_CONSENT_MISSING_GRANTED_AT")

    if (
        consent_status == "granted"
        and consent_record.get("revoked_at") is not None
    ):
        reason_codes.append("GRANTED_CONSENT_HAS_REVOKED_AT")

    if (
        consent_status == "revoked"
        and consent_record.get("revoked_at") is None
    ):
        reason_codes.append("REVOKED_CONSENT_MISSING_REVOKED_AT")
    
    if (
        consent_status == "expired"
        and consent_record.get("expiration_at") is None
    ):
        reason_codes.append("EXPIRED_CONSENT_MISSING_EXPIRATION_AT")

    if (
        consent_status == "granted"
        and consent_basis == "not_evaluated"
    ):
        reason_codes.append("GRANTED_CONSENT_BASIS_NOT_EVALUATED")

    if (
        consent_status == "granted"
        and parsed_expiration_at is not None
        and parsed_expiration_at <= datetime.now(UTC)
    ):
        reason_codes.append("GRANTED_CONSENT_EXPIRED_BY_DATE")

    return reason_codes


def _blocked_reason_for_status(consent_status) -> str:
    if consent_status == "not_evaluated":
        return "CONSENT_NOT_EVALUATED"

    if consent_status == "pending":
        return "CONSENT_PENDING"

    if consent_status == "denied":
        return "CONSENT_DENIED"

    if consent_status == "revoked":
        return "CONSENT_REVOKED"

    if consent_status == "expired":
        return "CONSENT_EXPIRED"

    return "CONSENT_BLOCKED"


def evaluate_consent_for_scope(
    consent_record: dict | None,
    required_scope: str,
) -> dict:
    normalized_required_scope = _normalize_required_scope(
        required_scope
    )

    if consent_record is None:
        return _base_result(
            consent_eligible=False,
            consent_status=None,
            consent_evaluation_status="missing_record",
            required_scope=normalized_required_scope,
            granted_scopes=[],
            reason_code="CONSENT_RECORD_MISSING",
            reason_codes=["CONSENT_RECORD_MISSING"],
        )

    if not isinstance(consent_record, dict):
        raise ValueError("consent_record must be a dict or None")

    consent_status = consent_record.get("consent_status")

    granted_scopes, scope_reason_codes = _evaluate_consent_scopes(
        consent_record.get("consent_scope")
    )

    record_reason_codes = _collect_record_reason_codes(
        consent_record
    )

    invalid_reason_codes = (
        record_reason_codes
        + scope_reason_codes
    )

    if invalid_reason_codes:
        return _base_result(
            consent_eligible=False,
            consent_status=consent_status,
            consent_evaluation_status="invalid_record",
            required_scope=normalized_required_scope,
            granted_scopes=granted_scopes,
            reason_code="CONSENT_RECORD_INVALID",
            reason_codes=invalid_reason_codes,
        )

    if consent_status != "granted":
        reason_code = _blocked_reason_for_status(consent_status)

        return _base_result(
            consent_eligible=False,
            consent_status=consent_status,
            consent_evaluation_status="blocked",
            required_scope=normalized_required_scope,
            granted_scopes=granted_scopes,
            reason_code=reason_code,
            reason_codes=[reason_code],
        )

    if normalized_required_scope not in granted_scopes:
        return _base_result(
            consent_eligible=False,
            consent_status=consent_status,
            consent_evaluation_status="blocked",
            required_scope=normalized_required_scope,
            granted_scopes=granted_scopes,
            reason_code="CONSENT_SCOPE_NOT_GRANTED",
            reason_codes=["CONSENT_SCOPE_NOT_GRANTED"],
        )

    return _base_result(
        consent_eligible=True,
        consent_status=consent_status,
        consent_evaluation_status="eligible",
        required_scope=normalized_required_scope,
        granted_scopes=granted_scopes,
        reason_code="CONSENT_GRANTED_FOR_SCOPE",
        reason_codes=["CONSENT_GRANTED_FOR_SCOPE"],
    )
