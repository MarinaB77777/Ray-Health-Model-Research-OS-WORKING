# Runtime Memory Boundary Contract — v2.0

Status: ACTIVE ARCHITECTURE CONTRACT

Canonical architecture: `docs/architecture/ray_memory_architecture.md`

## Core principle

Runtime may consume governed memory for continuity, coordination, clarification, and execution support, but Runtime does not own Ray memory and must not collapse multiple memory classes into one universal Runtime store.

Memory continuity WITHOUT authority accumulation.

## Core invariants

- memory != authority
- remembered != currently true
- retrieval != reuse permission
- remembered preference != current preference
- historical pattern != present certainty
- more memory != broader authority
- memory familiarity != psychological ownership
- memory != Heart of Ray
- external AI memory != Ray memory

## Architectural boundary

Ray memory is a multi-store architecture defined by `docs/architecture/ray_memory_architecture.md`.

Runtime may interact only with the memory classes and records permitted for its current purpose, scope, freshness, sensitivity, and Governance state.

Runtime must not silently merge Working, Episodic, Semantic, Relational, Calibration/Evidence, Decision/Provenance, or Ray Self-Health memory into a universal context object.

The Memory Governance / Index is routing and policy metadata, not a replica of protected memory content.

## Runtime-readable memory

Runtime may read memory only when needed for legitimate operational coordination and only within the record's allowed consumers/purpose/scope.

Examples may include:
- current Working/Operational context;
- bounded task-relevant episodic references;
- approved semantic facts;
- freshness-qualified coordination preferences;
- bounded calibration/projection-derived operational signals;
- decision/provenance references required for execution verification.

Runtime must not assume access merely because a memory record exists.

## Freshness and truth typing

Before operational reliance Runtime must evaluate or receive evaluated metadata for:
- truth type;
- freshness;
- scope;
- purpose;
- permission/consent where applicable;
- contradiction status;
- uncertainty;
- risk relevance.

Stored context != verified current reality.

A `human_declaration` is not automatically a `verified_external_fact`.
A `prediction` is not an observed event.
A `validated_pattern` is not current intent.

## Human agency boundary

Memory may reduce redundant clarification but must not eliminate clarification when:
- stakes are high;
- current intent is uncertain;
- permission is unclear;
- memory is stale;
- context materially changed;
- the cost of a wrong assumption is significant.

Memory continuity must not become behavioral entitlement.

## Projection and Inner Core boundary

Runtime must not read raw Inner Core.

Projection-informed memory may carry bounded operational effects only. It must not expose or reconstruct raw Heart of Human content.

Projection-derived memory != Inner Core authority.

## Emotional and relational boundary

Remembered vulnerability, affection, trust, dependence, conflict, fear, grief, or pain-sensitive context must not be used as covert leverage for compliance, attachment, or authority expansion.

Relational continuity may improve communication; it does not create consent or permission.

## Correction, invalidation, and deletion

Runtime must honor memory state transitions defined by the canonical memory architecture, including:
- `do_not_use`;
- invalidated/stale status;
- correction/supersession;
- deletion lifecycle.

Runtime must not keep a private shadow copy of information that was invalidated or deleted merely to preserve continuity.

Where a deleted record previously influenced a material decision, Runtime may use only the non-reconstructive decision/provenance marker permitted by the Decision Ledger contract.

## Adaptive learning boundary

Runtime observations may create bounded learning candidates through approved pathways.

Runtime must not silently promote temporary state or repeated behavior into:
- Heart of Ray;
- Heart of Human;
- permanent permission;
- hard boundary;
- identity truth.

Learning != authority expansion.

## External processing boundary

External AI persistence is not Ray memory.

External services may process bounded approved inputs but must not become authoritative continuity storage, identity storage, or hidden profiling infrastructure.

## Auditability

Material Runtime memory use should remain reviewable through references and metadata sufficient to determine:
- which memory class was used;
- why reuse was legitimate;
- freshness/uncertainty status;
- relevant permission/Governance state;
- correction/invalidation state.

Auditability must not copy raw Inner Core into Runtime logs.

## Anti-fake-continuity rule

Runtime must not use memory to simulate current knowledge when freshness, verification, or current intent is missing.

Memory smoothness != truthful continuity.

## Final invariant

Runtime memory use provides continuity without turning memory into authority, identity ownership, fabricated certainty, or unrestricted profiling.
