import hashlib


PSEUDONYMIZATION_VERSION = "1"
PSEUDONYMIZATION_METHOD = "sha256_export_scoped"


def _normalize_required(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} is required")

    normalized = value.strip()

    if not normalized:
        raise ValueError(f"{field_name} is required")

    return normalized


def build_export_scoped_participant_reference(
    participant_id: str,
    export_scope: str,
    salt: str,
) -> dict:
    normalized_participant_id = _normalize_required(
        participant_id,
        "participant_id",
    )

    normalized_export_scope = _normalize_required(
        export_scope,
        "export_scope",
    )

    normalized_salt = _normalize_required(
        salt,
        "salt",
    )

    raw_value = (
        f"{normalized_salt}:"
        f"{normalized_export_scope}:"
        f"{normalized_participant_id}"
    )

    digest = hashlib.sha256(
        raw_value.encode("utf-8")
    ).hexdigest()

    return {
        "reference_type": "export_scoped_pseudonymous_id",
        "participant_reference_id": digest,
        "pseudonymized": True,
        "pseudonymization_scope": normalized_export_scope,
        "pseudonymization_method": PSEUDONYMIZATION_METHOD,
        "pseudonymization_version": PSEUDONYMIZATION_VERSION,
        "hash_algorithm": "sha256",
        "salt_exported": False,
        "reidentification_risk": "reduced_not_zero",
        "identity_boundary": (
            "not_global_identity_not_longitudinal_identity"
        ),
        "cross_scope_linkage_allowed": False,
        "longitudinal_linkage_allowed": False,
        "global_identity": False,
        "runtime_identity_authority": False,
        "pseudonymization_is_not_anonymization": True,
    }

# TODO:
# Add a separate consent-bound longitudinal reference builder later.
# It must use subject_link_id, not participant_id.
# It must explicitly mark longitudinal_linkage_allowed=True
# and requires_longitudinal_consent=True.
# Do not change build_export_scoped_participant_reference()
# because it intentionally remains non-longitudinal.