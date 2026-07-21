from datetime import UTC, datetime

from research.consent_policy import (
    ALLOWED_CONSENT_SCOPES,
    ALLOWED_CONSENT_STATUSES,
    CONSENT_POLICY_VERSION,
)


CONSENT_VALIDATOR_VERSION = "consent-validator-1"

REQUIRED_CONSENT_KEYS = {
    "consent_status",
    "consent_version",
    "consent_scope",
    "granted_at",
    "revoked_at",
    "expiration_at",
    "consent_basis",
    "notes",
}

DATETIME_FIELDS = {
    "granted_at",
    "revoked_at",
    "expiration_at",
}


def _base_result(
    *,
    valid: bool,
    reason_codes: list[str],
) -> dict:
    return {
        "valid": valid,
        "reason_codes": reason_codes,
        "validator_version": CONSENT_VALIDATOR_VERSION,
        "validator_is_not_consent_authority": True,
        "validator_does_not_grant_consent": True,
        "validator_does_not_authorize_session_creation": True,
        "validator_does_not_authorize_collection": True,
        "session_collection_requires_session_level_agreement": True,
        "declined_session_agreement_blocks_new_collection": True,
        "validator_does_not_authorize_export": True,
        "validator_does_not_evaluate_scope_eligibility": True,
        "validator_is_static_structural_validator": True,
        "validator_does_not_store_consent": True,
        "validator_does_not_modify_record": True,
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


def _validate_required_keys(record: dict, reason_codes: list[str]) -> None:
    missing_keys = sorted(
        REQUIRED_CONSENT_KEYS - set(record.keys())
    )

    for key in missing_keys:
        reason_codes.append(
            f"CONSENT_RECORD_MISSING_KEY:{key}"
        )


def _validate_datetime_fields(
    record: dict,
    reason_codes: list[str],
) -> dict:
    parsed_datetimes = {}

    for field_name in sorted(DATETIME_FIELDS):
        value = record.get(field_name)

        if value is None:
            parsed_datetimes[field_name] = None
            continue

        try:
            parsed_datetimes[field_name] = _parse_iso_datetime(value)
        except (TypeError, ValueError):
            parsed_datetimes[field_name] = None
            reason_codes.append(
                f"CONSENT_DATETIME_FIELD_INVALID:{field_name}"
            )

    return parsed_datetimes


def _normalize_scope_items(
    consent_scope,
    reason_codes: list[str],
) -> list[str]:
    if consent_scope is None:
        return []

    if isinstance(consent_scope, str):
        raw_scopes = [consent_scope]
    elif isinstance(consent_scope, list):
        raw_scopes = consent_scope
    else:
        reason_codes.append("CONSENT_SCOPE_INVALID_TYPE")
        return []

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

    return normalized_scopes


def validate_consent_record(record: dict) -> dict:
    reason_codes = []

    if not isinstance(record, dict):
        return _base_result(
            valid=False,
            reason_codes=["CONSENT_RECORD_NOT_DICT"],
        )

    _validate_required_keys(record, reason_codes)

    consent_status = record.get("consent_status")
    consent_version = record.get("consent_version")
    consent_basis = record.get("consent_basis")

    if consent_status is None:
        reason_codes.append("CONSENT_STATUS_MISSING")
    elif consent_status not in ALLOWED_CONSENT_STATUSES:
        reason_codes.append("CONSENT_STATUS_INVALID")

    if consent_version != CONSENT_POLICY_VERSION:
        reason_codes.append("CONSENT_VERSION_MISMATCH")

    if (
        not isinstance(consent_basis, str)
        or not consent_basis.strip()
    ):
        reason_codes.append("CONSENT_BASIS_INVALID")

    normalized_scopes = _normalize_scope_items(
        record.get("consent_scope"),
        reason_codes,
    )
    parsed_datetimes = _validate_datetime_fields(
        record,
        reason_codes,
    )

    granted_at = parsed_datetimes.get("granted_at")
    revoked_at = parsed_datetimes.get("revoked_at")
    expiration_at = parsed_datetimes.get("expiration_at")

    if consent_status == "granted" and granted_at is None:
        reason_codes.append("GRANTED_CONSENT_MISSING_GRANTED_AT")

    if consent_status == "granted" and revoked_at is not None:
        reason_codes.append("GRANTED_CONSENT_HAS_REVOKED_AT")

    if consent_status == "granted" and not normalized_scopes:
        reason_codes.append("GRANTED_CONSENT_MISSING_SCOPE")

    if (
        consent_status == "granted"
        and consent_basis == "not_evaluated"
    ):
        reason_codes.append("GRANTED_CONSENT_BASIS_NOT_EVALUATED")

    if (
        consent_status == "granted"
        and expiration_at is not None
        and expiration_at <= datetime.now(UTC)
    ):
        reason_codes.append("GRANTED_CONSENT_EXPIRED_BY_DATE")

    if consent_status == "revoked" and revoked_at is None:
        reason_codes.append("REVOKED_CONSENT_MISSING_REVOKED_AT")

    if consent_status == "expired" and expiration_at is None:
        reason_codes.append("EXPIRED_CONSENT_MISSING_EXPIRATION_AT")

    return _base_result(
        valid=len(reason_codes) == 0,
        reason_codes=reason_codes,
    )
