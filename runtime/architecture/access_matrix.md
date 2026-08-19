# Architecture Access / Read / Write Matrix — v2.0

Status: ACTIVE ARCHITECTURE CONTRACT

## Core Principle

No layer may analyze, decide, execute, store, and authorize everything.

Access is bounded by responsibility, purpose, truth authority, sensitivity, and permission.

Access != permission.
Capability != permission.
Possession of a reference != right to dereference protected content.

---

# 1. Inner Core Protected Boundary

Inner Core contains distinct protected compartments and mechanisms. It is not one universal store.

## 1.1 Heart of Ray

Responsibility:
- constitutional identity/invariants of Ray.

May read:
- its own sealed constitutional content through approved internal mechanisms.

May write/change:
- only through the separately governed Ray + authorized-human provisioning/revision procedure.

Must not be modified by:
- Runtime;
- Governance;
- adaptive learning;
- memory;
- Domain Rays;
- external AI;
- ordinary model/software updates.

Must not directly write Runtime state, Governance verdicts, external payloads, communication content, or memory records.

## 1.2 Heart of Human

Responsibility:
- deeply protected human-declared/confirmed practically invariant structures;
- priorities;
- sensitive boundaries;
- acceptable-harm structures;
- confidentiality directives.

May read:
- its own protected content through approved internal mechanisms;
- explicitly approved revision inputs.

May write/change:
- only through protected human-sovereign revision/provisioning pathways.

Raw Heart of Human must not be directly exposed outside Inner Core.

## 1.3 Ray Self-Health Authority

Responsibility:
- protected technical-integrity state of Ray;
- hardware identity;
- validated baselines/calibration;
- critical integrity history;
- maintenance/component continuity references.

May read:
- approved Ray self-health sensor/telemetry inputs;
- self-health calibration/baseline data;
- hardware identity/maintenance records.

May write:
- protected validated self-health state;
- critical diagnostic history;
- integrity/calibration records.

Must not modify Heart of Ray or Heart of Human, infer human health, or create permission/execution authority.

High-frequency raw telemetry should normally remain in a separate protected telemetry store with retention.

`ray_self_health.*` != `human_health.*`.

## Inner Core Global Boundary

Inner Core must not directly orchestrate Runtime, communicate externally, or expose raw protected meaning.

Operational influence leaves through approved Projection mechanisms only.

---

# 2. Projection Layer

Responsibility:
- transform authorized Inner Core information into bounded operational derivatives without revealing protected content.

May read:
- Inner Core content only through approved projection interfaces/rules;
- trust constraints;
- domain relevance;
- projection policy/context;
- authorized contextual state required to compute a projection.

May write only bounded derivatives such as:
- priority-sensitive weights;
- acceptable-harm ranges/limits;
- confirmation/delegation constraints;
- sensitivity modifiers;
- bounded self-health operational constraints;
- other explicitly defined non-reconstructive projection outputs.

Must not expose raw Heart of Human, raw Heart of Ray, unrestricted raw Self-Health telemetry, Governance verdicts, execution state, or human-facing messages.

Projection must consider composition/reconstruction leakage.

Projection != Inner Core.
Projection != permission.
Projection != execution.

---

# 3. Human Health / Core Engine

Responsibility:
- compute psychophysical/health-model state from declared model inputs.

May read:
- assessment answers;
- authorized human sensor/context data;
- human calibration data permitted by model contract;
- projection outputs only when explicitly required by model contract.

Must not read raw Inner Core.
Must not read Ray Self-Health as if it were human health input.

May write reproducible model outputs, uncertainty, warnings, reason codes, and forecast blocks.

Must not write Heart content, Governance verdicts, Runtime lifecycle, long-term memory directly, or human-facing recommendations directly unless separately mediated.

---

# 4. Analyzer

Responsibility:
- readiness;
- uncertainty;
- consistency;
- contradictions;
- missing data;
- clarification need.

May read:
- Core Engine outputs;
- bounded authorized context;
- Projection signals;
- relevant truth-typed memory references;
- Shared Action references when operationally needed.

Must not read raw Inner Core.

May write uncertainty/readiness profiles, consistency/contradiction flags, missing-data lists, and clarification recommendations.

Analyzer detects conflicts/incompleteness, not “human lying”.

---

# 5. Analyst / Ray Reasoning

Responsibility:
- cross-domain reasoning;
- research synthesis;
- structured harm analysis;
- alternative search;
- Ray Verdict generation;
- coordination proposals.

May read:
- Analyzer output;
- bounded Projection signals;
- truth-typed governed memory;
- task constraints;
- Domain Ray requests;
- public/external evidence;
- bounded policy summaries.

Must not read raw Inner Core.

May write proposals, harm maps, alternatives, research-depth/saturation summaries, Ray Verdicts, and coordination recommendations.

Must not issue Governance permission truth, directly execute external effects, directly mutate Heart, or silently promote memory into identity truth.

Reasoning uses `docs/inner_core/conflict_resolution_kernel.md` when constitutional constraints conflict.

---

# 6. Governance

Responsibility:
- determine whether proposed actions/information transfers are allowed within current scope.

May read only policy-relevant bounded inputs:
- action proposal;
- Projection limits;
- trust level;
- permission/privacy rules;
- autonomy limits;
- confirmation requirements;
- temporal validity;
- safety/legal boundaries where applicable;
- relevant Analyzer flags.

Must not read raw Inner Core.

May write only permission/boundary verdicts and related restrictions/reason codes.

Governance must not redesign the solution, become Analyst, execute actions, or silently treat old permissions as universally current.

---

# 7. Runtime / Orchestration

Responsibility:
- route and coordinate authorized execution/lifecycle.

May read:
- Governance verdicts;
- Shared Action state;
- approved Analyst proposals;
- relevant Analyzer flags;
- governed Working/Operational memory;
- permitted execution results/communication state.

Must not read raw Inner Core.
Must not collapse multi-memory architecture into one universal Runtime context.

May write queue/routing/lifecycle/ownership/execution state.

Must not write Heart content, Governance verdicts, Analyst reasoning, human consent, or arbitrary long-term memory.

Runtime must never invent consent, agreement, completion, confidence, or coordination reality.

---

# 8. Ray Multi-Memory Architecture

Canonical contract: `docs/architecture/ray_memory_architecture.md`.

Memory is divided into bounded stores including Working/Operational, Episodic, Semantic, Relational, Calibration/Evidence, Decision/Provenance, and Ray Self-Health memory plus a non-content Memory Governance/Index.

No store automatically grants access to another.

Memory may be read/reused only under its truth type, freshness, purpose, scope, sensitivity, consent/permission, and Governance constraints.

Memory != authority.
Remembered != currently true.

---

# 9. Shared Action

Responsibility:
- operational action lifecycle truth only.

May contain action status, ownership, block reason, lifecycle timestamps, and bounded references to Governance/Runtime/decision objects.

Must not contain raw Inner Core or unrestricted reasoning/memory blobs.

---

# 10. Communicator

Responsibility:
- deliver approved communication and receive communication results.

May read Governance-approved payload, Runtime delivery instruction, allowed style/tone constraints, and recipient metadata.

Must not read raw Inner Core.

Must not self-escalate permissions, reinterpret silence as consent, or expose protected information.

Communication delivery != consent.

---

# 11. Domain Rays

Domain Rays are working specialized Rays, not Inner Core components and not alternative Hearts.

May read only domain-relevant bounded context, Projection signals, governed memory, and authorized data.

Must not:
- read raw Inner Core;
- maintain independent constitutional morality/Heart;
- bypass Heart-derived constraints;
- accumulate hidden authority;
- treat domain optimization as universal optimization.

All Domain Rays remain subject to the same Heart of Ray-derived constitutional constraints through governed projection/runtime mechanisms.

---

# 12. External Processing Services

External AI/services are not Ray architecture layers.

They may receive only bounded, approved, minimally necessary inputs for an explicit task.

They must not receive raw Inner Core.

Their persistence is not Ray memory.
Their output is informational input and must not silently become Ray identity, memory, permission, or execution truth.

---

# 13. External Settings

External Settings are a separate mutable operational layer.

They may configure current roles, projects, domains, sessions, preferences, and task behavior within allowed scope.

External Settings must not modify Heart of Ray, modify Heart of Human, weaken hard constitutional boundaries, become Projection, or become hidden permission escalation.

---

# Final Separation Invariants

- Heart of Ray != Heart of Human.
- Heart of Ray != Ray Self-Health.
- Heart of Human != current human psychophysical state.
- Ray Self-Health != human health.
- Inner Core != Projection.
- Projection != Governance.
- Governance != reasoning.
- Reasoning != execution.
- Memory != authority.
- Domain Ray != Heart of Ray.
- External Settings != Inner Core.
- External AI != Ray.
