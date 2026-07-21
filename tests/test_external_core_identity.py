from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from external_core.identity import (
    RayConnectionState,
    RayIdentity,
    RayIdentityRegistry,
)


VALID_HASH_A = "a" * 64
VALID_HASH_B = "b" * 64


class RayIdentityDetachmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.registry = RayIdentityRegistry(
            Path(self.temp_dir.name) / "ray_identities.json"
        )
        self.identity = RayIdentity(
            display_name="Ray — Health Model Research",
            origin_core_id="health-model-external-core",
            created_by="research-lead",
        )
        self.registry.register(self.identity)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_detachment_requires_explicit_irreversibility_acknowledgement(self) -> None:
        request = self.registry.request_detachment(
            self.identity.identity_id,
            requested_by="research-lead",
            reason="Create an independent Ray instance",
        )
        with self.assertRaises(PermissionError):
            self.registry.finalize_detachment(
                request["request_id"],
                approved_by="research-lead",
                new_root_authority_id="independent-ray-root",
                export_manifest_sha256=VALID_HASH_A,
                audit_checkpoint_sha256=VALID_HASH_B,
                irreversibility_acknowledged=False,
            )

    def test_pending_detachment_can_be_cancelled(self) -> None:
        request = self.registry.request_detachment(
            self.identity.identity_id,
            requested_by="research-lead",
            reason="Evaluate separation",
        )
        identity = self.registry.cancel_pending_detachment(
            request["request_id"],
            cancelled_by="research-lead",
            reason="Separation postponed",
        )
        self.assertEqual(RayConnectionState.CONNECTED.value, identity["state"])
        self.registry.assert_connection_allowed(self.identity.identity_id)

    def test_finalized_detachment_blocks_reconnection(self) -> None:
        request = self.registry.request_detachment(
            self.identity.identity_id,
            requested_by="research-lead",
            reason="Create an independent Ray instance",
        )
        result = self.registry.finalize_detachment(
            request["request_id"],
            approved_by="research-lead",
            new_root_authority_id="independent-ray-root",
            export_manifest_sha256=VALID_HASH_A,
            audit_checkpoint_sha256=VALID_HASH_B,
            irreversibility_acknowledged=True,
        )
        self.assertEqual(
            RayConnectionState.DETACHED_PERMANENTLY.value,
            result["identity"]["state"],
        )
        self.assertEqual(
            64,
            len(result["detachment_record"]["detachment_record_sha256"]),
        )
        with self.assertRaises(PermissionError):
            self.registry.assert_connection_allowed(self.identity.identity_id)

    def test_detached_lineage_cannot_be_reintroduced_as_child(self) -> None:
        request = self.registry.request_detachment(
            self.identity.identity_id,
            requested_by="research-lead",
            reason="Create an independent Ray instance",
        )
        self.registry.finalize_detachment(
            request["request_id"],
            approved_by="research-lead",
            new_root_authority_id="independent-ray-root",
            export_manifest_sha256=VALID_HASH_A,
            audit_checkpoint_sha256=VALID_HASH_B,
            irreversibility_acknowledged=True,
        )
        descendant = RayIdentity(
            display_name="Renamed Ray copy",
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
            reason="Create an independent Ray instance",
        )
        with self.assertRaises(ValueError):
            self.registry.finalize_detachment(
                request["request_id"],
                approved_by="research-lead",
                new_root_authority_id="independent-ray-root",
                export_manifest_sha256="not-a-hash",
                audit_checkpoint_sha256=VALID_HASH_B,
                irreversibility_acknowledged=True,
            )


if __name__ == "__main__":
    unittest.main()
