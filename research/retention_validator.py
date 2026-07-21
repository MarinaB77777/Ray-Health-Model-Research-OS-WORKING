from datetime import UTC, datetime

RETENTION_POLICY_VERSION = "retention-policy-1"
RETENTION_VALIDATOR_VERSION = "retention-validator-1"

ALLOWED_RETENTION_STATUSES = {
    "not_evaluated",
    "active",
    "expired",
    "deleted",
    "deletion_requested",
    "retention_blocked",
    "policy_restricted",
}

ALLOWED_RETENTION_CLASSES = {
    "not_defined",
    "bounded_research",
}

REQUIRED_RETENTION_KEYS = {
    "retention_status",
    "retention_version",
    "retention_class",
    "retention_basis",
    "retention_reviewed_at",
    "expiration_at",
    "deletion_requested_at",
    "deleted_at",
    "notes",
}

DATETIME_FIELDS = {
    "retention_reviewed_at",
    "expiration_at",
    "deletion_requested_at",
    "deleted_at",
}

STRING_KEYS = {
    "retention_status",
    "retention_version",
    "retention_class",
    "retention_basis",
}


def _base_result(
    *,
    valid: bool,
    reason_codes: list[str],
) -> dict:
    return {
        "valid": valid,
        "reason_codes": reason_codes,
        "validator_version": RETENTION_VALIDATOR_VERSION,
        "validator_is_static_structural_validator": True,
        "validator_is_not_retention_authority": True,
        "validator_does_not_repair_record": True,
        "validator_does_not_grant_retention": True,
        "validator_does_not_delete_data": True,
        "validator_does_not_schedule_deletion": True,
        "validator_does_not_authorize_export": True,
        "validator_does_not_authorize_reuse": True,
        "validator_does_not_evaluate_dataset_admission": True,
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


def _add_missing_key_reasons(
    record: dict,
    reason_codes: list[str],
) -> None:
    missing_keys = sorted(
        REQUIRED_RETENTION_KEYS - set(record.keys())
    )

    for key in missing_keys:
        reason_codes.append(
            f"MISSING_REQUIRED_KEY:{key}"
        )


def _add_string_field_reasons(
    record: dict,
    reason_codes: list[str],
) -> None:
    for key in sorted(STRING_KEYS):
        value = record.get(key)

        if value is None:
            continue

        if not isinstance(value, str) or not value.strip():
            reason_codes.append(
                f"STRING_FIELD_INVALID:{key}"
            )


def _add_datetime_field_reasons(
    record: dict,
    reason_codes: list[str],
) -> dict:
    parsed_datetimes = {}

    for key in sorted(DATETIME_FIELDS):
        value = record.get(key)

        if value is None:
            parsed_datetimes[key] = None
            continue

        try:
            parsed_datetimes[key] = _parse_iso_datetime(value)
        except (TypeError, ValueError):
            parsed_datetimes[key] = None
            reason_codes.append(
                f"DATETIME_FIELD_INVALID:{key}"
            )

    return parsed_datetimes


def _add_status_and_class_reasons(
    record: dict,
    reason_codes: list[str],
) -> None:
    retention_status = record.get("retention_status")
    retention_class = record.get("retention_class")

    if (
        retention_status is not None
        and retention_status not in ALLOWED_RETENTION_STATUSES
    ):
        reason_codes.append("INVALID_RETENTION_STATUS")

    if (
        retention_class is not None
        and retention_class not in ALLOWED_RETENTION_CLASSES
    ):
        reason_codes.append("INVALID_RETENTION_CLASS")


def _add_version_reason(
    record: dict,
    reason_codes: list[str],
) -> None:
    if record.get("retention_version") != RETENTION_POLICY_VERSION:
        reason_codes.append("RETENTION_VERSION_MISMATCH")


def _add_status_consistency_reasons(
    record: dict,
    parsed_datetimes: dict,
    reason_codes: list[str],
) -> None:
    retention_status = record.get("retention_status")
    retention_class = record.get("retention_class")

    expiration_at = parsed_datetimes.get("expiration_at")
    deletion_requested_at = parsed_datetimes.get(
        "deletion_requested_at"
    )
    deleted_at = parsed_datetimes.get("deleted_at")

    if retention_status == "active":
        if retention_class == "not_defined":
            reason_codes.append(
                "ACTIVE_RETENTION_REQUIRES_DEFINED_CLASS"
            )

        if record.get("retention_basis") == "not_evaluated":
            reason_codes.append(
                "ACTIVE_RETENTION_BASIS_NOT_EVALUATED"
            )

        if deletion_requested_at is not None:
            reason_codes.append(
                "ACTIVE_RETENTION_HAS_DELETION_REQUESTED_AT"
            )

        if deleted_at is not None:
            reason_codes.append(
                "ACTIVE_RETENTION_HAS_DELETED_AT"
            )

    if retention_status == "expired" and expiration_at is None:
        reason_codes.append(
            "EXPIRED_RETENTION_MISSING_EXPIRATION_AT"
        )

    if (
        retention_status == "deletion_requested"
        and deletion_requested_at is None
    ):
        reason_codes.append(
            "DELETION_REQUESTED_MISSING_DELETION_REQUESTED_AT"
        )

    if retention_status == "deleted" and deleted_at is None:
        reason_codes.append(
            "DELETED_RETENTION_MISSING_DELETED_AT"
        )


def validate_retention_record(record: dict) -> dict:
    reason_codes = []

    if not isinstance(record, dict):
        return _base_result(
            valid=False,
            reason_codes=["RETENTION_RECORD_NOT_DICT"],
        )

    _add_missing_key_reasons(record, reason_codes)
    _add_string_field_reasons(record, reason_codes)
    _add_status_and_class_reasons(record, reason_codes)
    _add_version_reason(record, reason_codes)

    parsed_datetimes = _add_datetime_field_reasons(
        record,
        reason_codes,
    )

    _add_status_consistency_reasons(
        record,
        parsed_datetimes,
        reason_codes,
    )

    return _base_result(
        valid=len(reason_codes) == 0,
        reason_codes=reason_codes,
    )
