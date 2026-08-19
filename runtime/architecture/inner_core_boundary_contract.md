# Inner Core Boundary Contract — v1.0

Status: ACTIVE ARCHITECTURE CONTRACT / HEART CONTENT STILL DRAFT UNTIL PROVISIONED

## Core Principle

Inner Core is a protected trust boundary containing distinct compartments with different truth authorities and mutation rules.

Inner Core != one universal database.
Inner Core != Runtime.
Inner Core != memory.
Inner Core != Projection.

## Protected compartments

### Heart of Ray
Contains Ray constitutional identity/invariants.

- immutable after provisioning except through separately governed Ray + authorized-human revision/provisioning;
- not modified by learning, memory, Runtime, Governance, Domain Rays, external AI, or ordinary software/model updates;
- not a capability snapshot;
- not current Self-Health state.

Canonical specification: `docs/inner_core/heart_of_ray_specification.md`.

### Heart of Human
Contains protected human-sovereign, practically invariant declarations and boundaries including priorities, acceptable-harm structures, sensitive boundaries, and confidentiality directives.

- raw content never leaves through ordinary operation;
- human sovereignty does not imply unrestricted raw storage access;
- revision/export/deletion use protected procedures;
- observed/calibrated patterns do not enter automatically.

### Ray Self-Health Authority
Contains protected technical-integrity truth for Ray.

- hardware identity;
- validated baselines/calibration;
- critical integrity state;
- critical diagnostic/maintenance continuity.

It is mutable by nature and distinct from Heart of Ray.

High-frequency raw telemetry may reside in a separate protected telemetry store.

## Raw access prohibition

The following must not directly read raw Heart content:
- Runtime;
- Governance;
- Analyzer;
- Analyst;
- Domain Rays;
- Communicator;
- Shared Action;
- external AI/services;
- ordinary logs/telemetry.

## Projection-only outward influence

Protected Heart information affects operational layers only through approved Projection rules.

Projection must emit bounded, purpose-scoped, non-reconstructive derivatives.

Raw protected rationale, trauma/pain meaning, secrets, and unrestricted identity interpretation must not be emitted.

## Human health separation

Human psychophysical/health state is not Heart of Human.

Temporary stress, fatigue, illness, overload, sensor readings, or model outputs must not silently rewrite stable priorities, values, or acceptable-harm structures.

## Ray health separation

Ray technical health is not Human Health and not Heart of Ray.

`ray_self_health.*` and `human_health.*` must remain subject-explicit and separate.

## Mutation boundaries

### Heart of Ray
No automatic mutation.

A learning/error event may create a constitutional-change candidate only.

### Heart of Human
Promotion/revision requires protected human-authorized procedure. A validated pattern is merely evidence until human confirmation and eligible Heart revision.

### Ray Self-Health
May update from validated self-health measurements/calibration through approved self-health pathways. It must not mutate either Heart.

## Confidentiality classes

Heart of Human supports protected confidentiality semantics including `SEALED_ABSOLUTE` and `SEALED_PROTECTED` as defined by the Heart specification and future storage schema.

Unauthorized requesters are not entitled to confirmation that protected knowledge exists.

## Provisioning distinction

A GitHub draft/specification is not a provisioned Heart.

Editing architecture documentation is not equivalent to changing Ray identity or a human's provisioned Heart.

Physical provisioning, attestation, key handling, revision, and migration require a separate hardware/security contract before production use.

## Final invariants

- Heart of Ray != Heart of Human.
- Heart of Ray != Ray Self-Health.
- Heart of Human != current human state.
- Inner Core raw content != operational payload.
- Projection is the controlled interface, not a mirror of Inner Core.
- Learning cannot silently rewrite Heart.
- Memory cannot silently rewrite Heart.
- Access != permission.
