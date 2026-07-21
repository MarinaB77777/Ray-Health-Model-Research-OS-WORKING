import pytest

from research.pseudonymization import (
    build_export_scoped_participant_reference,
)


def test_build_export_scoped_reference_returns_pseudonymous_reference():
    reference = build_export_scoped_participant_reference(
        participant_id="participant-1",
        export_scope="research_snapshot",
        salt="test-salt",
    )

    assert (
        reference["reference_type"]
        == "export_scoped_pseudonymous_id"
    )
    assert reference["pseudonymized"] is True
    assert (
        reference["pseudonymization_scope"]
        == "research_snapshot"
    )
    assert (
        reference["pseudonymization_method"]
        == "sha256_export_scoped"
    )
    assert (
        reference["reidentification_risk"]
        == "reduced_not_zero"
    )
    assert (
        reference["identity_boundary"]
        == "not_global_identity_not_longitudinal_identity"
    )


def test_same_participant_same_scope_same_salt_returns_same_reference():
    first = build_export_scoped_participant_reference(
        participant_id="participant-1",
        export_scope="research_snapshot",
        salt="test-salt",
    )

    second = build_export_scoped_participant_reference(
        participant_id="participant-1",
        export_scope="research_snapshot",
        salt="test-salt",
    )

    assert (
        first["participant_reference_id"]
        == second["participant_reference_id"]
    )


def test_same_participant_different_scope_returns_different_reference():
    first = build_export_scoped_participant_reference(
        participant_id="participant-1",
        export_scope="research_snapshot",
        salt="test-salt",
    )

    second = build_export_scoped_participant_reference(
        participant_id="participant-1",
        export_scope="other_export_scope",
        salt="test-salt",
    )

    assert (
        first["participant_reference_id"]
        != second["participant_reference_id"]
    )


def test_reference_does_not_expose_raw_participant_id_or_salt():
    reference = build_export_scoped_participant_reference(
        participant_id="participant-1",
        export_scope="research_snapshot",
        salt="test-salt",
    )

    assert reference["participant_reference_id"] != "participant-1"
    assert "participant-1" not in str(reference)
    assert "test-salt" not in str(reference)


def test_pseudonymization_is_not_anonymization_boundary():
    reference = build_export_scoped_participant_reference(
        participant_id="participant-1",
        export_scope="research_snapshot",
        salt="test-salt",
    )

    assert (
        reference["pseudonymization_is_not_anonymization"]
        is True
    )


@pytest.mark.parametrize(
    "participant_id, export_scope, salt",
    [
        ("", "research_snapshot", "test-salt"),
        ("participant-1", "", "test-salt"),
        ("participant-1", "research_snapshot", ""),
    ],
)
def test_build_export_scoped_reference_requires_inputs(
    participant_id,
    export_scope,
    salt,
):
    with pytest.raises(ValueError):
        build_export_scoped_participant_reference(
            participant_id=participant_id,
            export_scope=export_scope,
            salt=salt,
        )

def test_same_participant_different_salt_returns_different_reference():
    first = build_export_scoped_participant_reference(
        participant_id="participant-1",
        export_scope="research_snapshot",
        salt="test-salt-1",
    )

    second = build_export_scoped_participant_reference(
        participant_id="participant-1",
        export_scope="research_snapshot",
        salt="test-salt-2",
    )

    assert (
        first["participant_reference_id"]
        != second["participant_reference_id"]
    )


def test_reference_normalizes_inputs():
    first = build_export_scoped_participant_reference(
        participant_id=" participant-1 ",
        export_scope=" research_snapshot ",
        salt=" test-salt ",
    )

    second = build_export_scoped_participant_reference(
        participant_id="participant-1",
        export_scope="research_snapshot",
        salt="test-salt",
    )

    assert (
        first["participant_reference_id"]
        == second["participant_reference_id"]
    )
    assert (
        first["pseudonymization_scope"]
        == "research_snapshot"
    )


def test_reference_declares_linkage_boundaries():
    reference = build_export_scoped_participant_reference(
        participant_id="participant-1",
        export_scope="research_snapshot",
        salt="test-salt",
    )

    assert reference["cross_scope_linkage_allowed"] is False
    assert reference["longitudinal_linkage_allowed"] is False
    assert reference["global_identity"] is False
    assert reference["runtime_identity_authority"] is False
    assert reference["salt_exported"] is False
    assert reference["hash_algorithm"] == "sha256"
    assert reference["pseudonymization_version"] == "1"