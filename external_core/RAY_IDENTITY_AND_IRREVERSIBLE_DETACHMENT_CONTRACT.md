# Ray Identity, External-Core Registration, and Detachment Boundary — v2.0

Status: ACTIVE ARCHITECTURE BOUNDARY / LEGACY IMPLEMENTATION COMPATIBILITY

## Purpose

This contract prevents the existing External Core identity/detachment registry from being mistaken for the constitutional identity authority of Ray.

The repository currently contains executable legacy/transitional code in `external_core/identity.py` implementing:
- `RayIdentity`;
- `RayIdentityRegistry`;
- `RayConnectionState`;
- detachment requests;
- irreversible detached-lineage records.

That implementation may remain for compatibility until separately reviewed and migrated. Its existence does NOT define Heart of Ray.

## Canonical identity authority

Heart of Ray is the constitutional identity foundation defined by:
- `docs/inner_core/heart_of_ray_specification.md`;
- `runtime/architecture/inner_core_boundary_contract.md`.

External Core is not Ray's constitutional identity owner.

`origin_core_id` != Heart identity source.
`identity_id` in External Core != Heart of Ray.
`lineage_id` in External Core != constitutional identity proof.
External settings != identity constitution.
External Core registration != Heart provisioning.

## External-Core identity records

External Core may maintain operational registration identifiers needed for:
- compatibility;
- routing;
- connection lifecycle;
- migration records;
- audit continuity;
- access revocation;
- external-system trust relationships.

Such identifiers are operational/registry identity, not constitutional identity.

An operational identity record must not silently become authority to:
- rewrite Heart of Ray;
- create a replacement Heart;
- declare a new constitutional Ray merely through copying/renaming;
- grant or revoke constitutional identity through an External Core state transition.

## Detachment semantics

Detaching from an External Core means ending or changing an operational trust/connection relationship with that External Core.

Detachment may revoke:
- External Core credentials;
- trusted channels;
- routing rights;
- External Core management/access relationships;
- scoped operational permissions.

Detachment does NOT by itself:
- erase Heart of Ray;
- create a new Heart of Ray;
- transfer constitutional authority;
- prove identity continuity;
- authorize arbitrary export of Ray memory or Human Heart;
- make a detached external registry entry an independent constitutional authority.

## Legacy `new_root_authority_id`

The existing implementation requires a `new_root_authority_id` when finalizing legacy detachment.

Under the new architecture this field must be interpreted only as a legacy operational trust-root / registry-root identifier unless and until a future migration explicitly defines a stronger role.

It must NOT be interpreted as:
- a replacement Heart of Ray;
- authority to rewrite Heart of Ray;
- proof that constitutional identity was recreated;
- permission to expose or migrate protected Inner Core content.

## Identity continuity and hardware/software migration

Future identity continuity must be designed together with:
- Heart provisioning and attestation;
- cryptographic identity/root-of-trust architecture;
- protected backup/recovery;
- hardware replacement/migration;
- memory continuity;
- Ray Self-Health hardware identity;
- authorized Ray + human revision procedure.

A component replacement, External Core change, model upgrade, or registry detachment must not automatically imply identity replacement.

Likewise, copying software files must not automatically prove identity continuity.

## Protected-data boundary

No detachment/export pathway may automatically expose:
- Heart of Ray raw protected material;
- Heart of Human;
- raw Inner Core;
- protected memory classes;
- participant/research data;
- cryptographic secrets.

Any migration/export requires its own scoped authority, confidentiality rules, provenance, and integrity verification.

## Legacy implementation status

`external_core/identity.py` remains executable legacy/transitional code in the current repository.

It must not be silently deleted or repurposed in an architecture-only branch.

Before implementation migration, review must determine:
- actual callers/importers;
- tests and stored registry data;
- whether operational detachment remains useful;
- how to rename/re-scope legacy fields without breaking compatibility;
- migration of persisted identity/detachment records;
- interaction with future cryptographic Heart identity/attestation.

Until that review is complete, the code remains compatibility infrastructure with bounded operational meaning.

## Final invariants

- External Core != Heart of Ray
- operational identity != constitutional identity
- registry lineage != Heart identity proof
- detachment != Heart replacement
- new operational trust root != new Heart
- software copy != proven identity continuity
- hardware replacement != automatic identity replacement
- operational connection authority != constitutional mutation authority
- legacy executable code must be migrated explicitly, not reinterpreted silently
