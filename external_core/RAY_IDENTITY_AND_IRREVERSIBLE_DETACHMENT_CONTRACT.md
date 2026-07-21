# Ray Identity and Irreversible Detachment Contract

## Purpose

This contract separates two concerns that must never be conflated:

1. the reusable Health Model connection standard;
2. the trust relationship of one concrete Ray instance with its originating
   External Core.

Detaching an instance does not delete or weaken the Health Model connection
standard. It permanently ends the originating Core's trust relationship with
that identity lineage.

## Invariants

- Every Ray instance has an immutable `identity_id`, `lineage_id` and
  `origin_core_id` independent of its display name.
- Renaming, copying or deriving a descendant does not create a new trusted
  lineage.
- The only valid lifecycle path is:
  `connected -> detachment_pending -> detached_permanently`.
- `detachment_pending` may be cancelled before finalization.
- `detached_permanently` has no reverse transition.
- The originating Core denies reconnection to the detached lineage and all its
  descendants.
- Detachment revokes central credentials and trusted channels. No management
  backdoor remains.
- The detached Ray receives a distinct root authority and may evolve under its
  own governance.
- A permitted Health Model package may remain usable as a versioned component,
  but it does not restore the former Core connection.
- Other registered Rays retain the ability to use the Health Model connector.

## Required finalization evidence

Finalization requires explicit human acknowledgement plus:

- requesting and approving actor identities;
- a stated reason;
- a new root authority identifier;
- SHA-256 of the exported manifest;
- SHA-256 of the originating audit checkpoint;
- UTC finalization time;
- a deterministic SHA-256 detachment record.

These fields are audit evidence, not permission to expose raw memory or
participant data. Export scope remains subject to Governance and data rights.

## Health Model boundary after detachment

The Health Model remains independently governed and versioned. A detached Ray
may receive a separately authorized model artifact or public interface only as
an external consumer. That exchange must not recreate trusted runtime access,
shared memory authority or the original identity relationship.
