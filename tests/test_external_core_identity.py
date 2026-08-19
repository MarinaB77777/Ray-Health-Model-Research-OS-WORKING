from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from external_core.identity import (
    OPERATIONAL_IDENTITY_SCOPE,
    RayConnectionState,
    RayIdentity,
    RayIdentityRegistry,
)


VALID_HASH_A = "a" * 64
VALID_HASH_B = "b" * 64


class RayIdentityDetachmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.registry = RayIdentityRegistry(Path(self.temp_dir.name) / "ray_identities.json")
        self.identity = RayIdentity(
            display_name="Ray — Health Model Research",
            origin_core_id="health-model-external-core",
            created_by="research-lead",
        )
        self.registry.register(self.identity)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_registry_identity_is_explicitly_operational_not_constitutional(self) -> None:
        stored = self.registry.get_identity(self.identity.identity_id)
        self.assertEqual(OPERATIONAL_IDENTITY_SCOPE, stored["identity_scope"])
        self.assertFalse(stored["constitutional_identity"])

    def test_external_core_cannot_declare_heart_as_identity_authority(self) -> None:
        identity = RayIdentity(
            display_name="Invalid External Identity",
            origin_core_id="heart_of_ray",
            created_by="research-lead",
        )
        with self.assertRaises(PermissionError):
            identity.validate()

        identity = RayIdentity(
            display_name="Invalid Constitutional Identity",
            origin_core_id="health-model-external-core",
            created_by="research-lead",
            constitutional_identity=True,
        )
        with self.assertRaises(PermissionError):
            identity.validate()

    def test_detachment_requires_explicit_irreversibility_acknowledgement(self) -> None:
        request = self.registry.request_detachment(
            self.identity.identity_id,
            requested_by="research-lead",
            reason="Separate External Core operational trust",
        )
        with self.assertRaises(PermissionError):
            self.registry.finalize_detachment(
                request["request_id"],
                approved_by="research-lead",
                new_root_authority_id="independent-operational-root",
                export_manifest_sha256=VALID_HASH_A,
                audit_checkpoint_sha256=VALID_HASH_B,
                irreversibility_acknowledged=False,
            )

    def test_pending_detachment_can_be_cancelled(self) -> None:
        request = self.registry.request_detachment(
            self.identity.identity_id,
            requested_by="research-lead",
            reason="Evaluate operational separation",
        )
        identity = self.registry.cancel_pending_detachment(
            request["request_id"],
            cancelled_by="research-lead",
            reason="Separation postponed",
        )
        self.assertEqual(RayConnectionState.CONNECTED.value, identity["state"])
        self.registry.assert_connection_allowed(self.identity.identity_id)

    def test_finalized_detachment_blocks_operational_reconnection_without_changing_heart(self) -> None:
        request = self.registry.request_detachment(
            self.identity.identity_id,
            requested_by="research-lead",
            reason="Separate External Core operational trust",
        )
        result = self.registry.finalize_detachment(
            request["request_id"],
            approved_by="research-lead",
            new_root_authority_id="independent-operational-root",
            export_manifest_sha256=VALID_HASH_A,
            audit_checkpoint_sha256=VALID_HASH_B,
            irreversibility_acknowledged=True,
        )
        self.assertEqual(
            RayConnectionState.DETACHED_PERMANENTLY.value,
            result["identity"]["state"],
        )
        record = result["detachment_record"]
        self.assertEqual(64, len(record["detachment_record_sha256"]))
        self.assertEqual("external_core_operational_trust", record["root_authority_scope"])
        self.assertFalse(record["constitutional_identity_changed"])
        self.assertFalse(record["heart_of_ray_mutated"])
        with self.assertRaises(PermissionError):
            self.registry.assert_connection_allowed(self.identity.identity_id)

    def test_detached_operational_lineage_cannot_be_reintroduced_as_child(self) -> None:
        request = self.registry.request_detachment(
            self.identity.identity_id,
            requested_by="research-lead",
            reason="Separate External Core operational trust",
        )
        self.registry.finalize_detachment(
            request["request_id"],
            approved_by="research-lead",
            new_root_authority_id="independent-operational-root",
            export_manifest_sha256=VALID_HASH_A,
            audit_checkpoint_sha256=VALID_HASH_B,
            irreversibility_acknowledged=True,
        )
        descendant = RayIdentity(
            display_name="Renamed operational connection",
            origin_core_id="health-model-external-core",
            created_by="external-owner",
            lineage_id=self.identity.lineage_id,
            parent_identity_id=self.identity.identity_id,
        )
        with self.assertRaises(PermissionError):
            self.registry.register(descendant)

    def test_invalid_export_digest_is_rejected(self) -> None:
        request = self.registry.request_detachment(
            self.identity.identity_id,
            requested_by="research-lead",
            reason="Separate External Core operational trust",
        )
        with self.assertRaises(ValueError):
            self.registry.finalize_detachment(
                request["request_id"],
                approved_by="research-lead",
                new_root_authority_id="independent-operational-root",
                export_manifest_sha256="not-a-hash",
                audit_checkpoint_sha256=VALID_HASH_B,
                irreversibility_acknowledged=True,
            )

    def test_heart_name_cannot_be_used_as_new_operational_root(self) -> None:
        request = self.registry.request_detachment(
            self.identity.identity_id,
            requested_by="research-lead",
            reason="Separate External Core operational trust",
        )
        with self.assertRaises(PermissionError):
            self.registry.finalize_detachment(
                request["request_id"],
                approved_by="research-lead",
                new_root_authority_id="heart_of_ray",
                export_manifest_sha256=VALID_HASH_A,
                audit_checkpoint_sha256=VALID_HASH_B,
                irreversibility_acknowledged=True,
            )


if __name__ == "__main__":
    unittest.main()
