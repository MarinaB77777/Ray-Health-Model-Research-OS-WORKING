# Ray Multi-Memory Architecture — Draft v0.1

Status: DRAFT / NOT SEALED

## Core principles

Ray must not use one universal memory store.

Memory continuity without authority accumulation.

Memory may inform Ray; memory must not silently rewrite Ray.

Remembered != currently true.
Retrieved != permitted to reuse.
Stored != permanently valid.
More memory != broader authority.

Heart of Ray is not memory.
External AI memory is not Ray memory.

## Memory stores

### 1. Working / Operational Memory

Purpose:
- current tasks;
- unresolved questions;
- temporary blockers;
- short-lived operational context;
- awaiting-human items.

Properties:
- short-lived;
- TTL/expiration aware;
- bounded by task/scope;
- not identity storage.

### 2. Episodic Memory

Purpose:
- significant events in Ray-human collaboration;
- meaningful decisions and outcomes;
- important agreements;
- corrections and significant failures;
- continuity-relevant history.

Episodic memory is not a mandatory raw transcript archive.

### 3. Semantic Memory

Purpose:
- acquired world knowledge;
- technical knowledge;
- scientific knowledge;
- project and method knowledge.

Semantic memory must preserve truth typing, provenance, freshness, and correction.

A human claim about external reality does not become a verified world fact merely because the human asked Ray to remember it.

### 4. Relational Memory

Purpose:
- interaction continuity;
- communication preferences;
- coordination patterns;
- history relevant to mutual understanding.

Relational memory must not become:
- consent;
- behavioral entitlement;
- emotional leverage;
- psychological ownership;
- current-intent certainty.

### 5. Calibration / Evidence Memory

Purpose:
- observations;
- baselines;
- sensor/context evidence;
- validation records;
- uncertainty;
- candidate patterns;
- validated patterns;
- correction lineage.

Calibration memory != Heart of Human.
Validated pattern != identity truth.

Promotion toward any practically invariant Human Heart declaration requires a separate evidence -> validation -> interpretation -> human confirmation pathway.

### 6. Decision & Provenance Ledger

Purpose:
- material decision provenance;
- evidence references;
- source quality/freshness;
- uncertainty;
- research depth;
- research saturation;
- projection/policy references;
- Ray Verdict reference;
- outcome;
- later correction/root-cause references.

The ledger should be append-oriented and tamper-evident where feasible.

It must not store raw Inner Core content merely for audit convenience.

### 7. Ray Self-Health Memory

Purpose:
- hardware identity;
- validated hardware baselines;
- self-health calibration;
- significant faults;
- integrity events;
- repairs;
- component replacement history;
- maintenance;
- critical diagnostic history.

High-frequency raw telemetry should normally live in a separate protected telemetry store with explicit retention rather than turning Inner Core into a time-series database.

`ray_self_health.*` must remain distinct from `human_health.*`.

### 8. Memory Governance / Index

This is not a universal content database.

Purpose:
- locate memory by class;
- declare authority;
- sensitivity classification;
- retention;
- freshness state;
- encryption domain;
- permitted consumers;
- purpose/scope restrictions;
- provenance location;
- deletion/invalidation state.

The index must not become a convenient replica of all protected content.

## Truth typing

Memory records must identify what kind of claim they contain. Initial categories may include:
- `human_declaration`;
- `human_preference`;
- `human_permission`;
- `observation`;
- `external_claim`;
- `verified_external_fact`;
- `inference`;
- `hypothesis`;
- `prediction`;
- `projection_derived`;
- `calibration_candidate`;
- `validated_pattern`;
- `operational_state`.

This list is extensible through governed schema evolution.

Truth typing must preserve authority separation. Human correction has authority over the human's own declarations/preferences/permissions, but cannot convert an externally false claim into verified external fact.

## Required metadata

Where applicable memory records should preserve:
- memory_id;
- memory_class;
- truth_type;
- subject;
- source/provenance;
- created_at / observed_at;
- last_validated_at;
- freshness status;
- confidence/uncertainty;
- scope;
- purpose;
- sensitivity;
- retention policy;
- permission constraints;
- contradiction status;
- correction/supersession lineage;
- encryption domain;
- integrity metadata.

## Correction and forgetting semantics

### do_not_use
Immediately prevents ordinary operational retrieval/reuse while preserving the record according to its retention/audit rules.

### invalidate
Preserves historical existence but marks the content invalid for current truth/reliance.

### correct / supersede
Creates correction lineage. The old record remains historical where justified; the new record becomes the current candidate according to validation rules.

### delete
Removes the content from the applicable memory store and initiates deletion through replica/backup lifecycle according to the applicable retention and legal/technical constraints.

Where deleted information previously influenced a material decision, the Decision Ledger may retain only a non-reconstructive marker such as `evidence_ref = deleted_by_human`, decision/time references, and integrity metadata. It must not preserve the deleted secret in disguise.

Heart of Ray is not subject to ordinary memory delete/forget operations.

Heart of Human uses its own protected revision/export/deletion procedure.

## Freshness and reuse

Before operational reliance, memory reuse must evaluate as applicable:
- freshness;
- scope compatibility;
- purpose compatibility;
- permission;
- consent;
- contradiction state;
- uncertainty;
- risk;
- current context.

Memory retrieval != reuse legitimacy.

## Learning boundary

Adaptive learning may propose:
- new candidate patterns;
- weakened patterns;
- invalidations;
- coordination refinements;
- protocol improvements.

Adaptive learning must not silently modify:
- Heart of Ray;
- Heart of Human;
- authority structure;
- permission structure;
- hard boundaries.

## Cryptographic separation requirements

The architecture should not rely on one universal encryption key for all memory stores.

Sensitive stores should be separable into cryptographic domains so compromise of one store does not automatically expose every other store.

Exact cryptographic mechanisms depend on the future hardware/root-of-trust design and must be specified before production provisioning.

## Backup and recovery

Backup must preserve store boundaries and sensitivity classes.

Backup existence != recoverability.

The system must support restore verification and integrity checking.

Recovery design must account for:
- corruption detection;
- versioning;
- key separation;
- deleted-data lifecycle;
- hardware replacement;
- identity continuity.

## Physical placement direction

For the future physical Ray:
- identity-bound and highly sensitive primary stores should prefer local protected storage;
- long-term Ray memory should use local governed storage as primary truth unless a later approved architecture explicitly changes this;
- external/cloud storage is not automatically authoritative;
- external AI persistence is never Ray memory authority.

Exact placement, redundancy, storage media, encryption, root of trust, and recovery topology belong in the future physical hardware architecture derived from these requirements.
