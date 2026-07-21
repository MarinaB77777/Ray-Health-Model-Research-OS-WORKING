# Architecture Access / Read / Write Matrix — v1.2

## Core Principle

No layer may analyze, decide, execute, and store everything.

Each layer has:
- bounded responsibility;
- bounded read access;
- bounded write access;
- explicit forbidden zones.

There is no global truth object.

Different layers own different types of truth.

The system must not collapse into:
- one universal agent;
- one universal memory;
- one universal reasoning layer;
- one universal state object.

This architecture exists to prevent:
- god-agent drift;
- hidden autonomy;
- hallucinated coordination;
- fake certainty;
- uncontrolled recursive adaptation;
- silent authority expansion.

---

# 1. Inner Core

## Responsibility

Stores the deepest private user structures:
- stable values;
- sensitive boundaries;
- personal priorities;
- acceptable harm logic;
- identity-relevant constraints.

Inner Core is private and isolated.

---

## May read

- Its own internal data only.
- User-provided Inner Core declarations.
- Explicitly approved Inner Core updates.

---

## May write

- Stable profile structures.
- Boundary structures.
- Acceptable harm structures.
- Deep preference structures.
- Projection-relevant internal parameters.

---

## Must not read

- Runtime queues.
- Shared Action lifecycle.
- Communicator delivery logs.
- External service data directly.
- Temporary operational memory unless explicitly routed through approved update logic.

---

## Must not write

- Shared Action statuses.
- Governance verdicts.
- Runtime routing state.
- Communicator messages.
- External payloads.

---

## Additional Inner Core Boundary Rules

Inner Core must not leak directly into:
- Runtime behavior;
- interruption behavior;
- communication behavior;
- prediction authority;
- operational orchestration.

Inner Core influence must remain:
- indirect;
- bounded;
- governance-compatible;
- projection-mediated.

---

## Truth Authority

Inner Core is the source of deep private user truth.

Inner Core truth is not public truth and is never directly exposed.

---

# 2. Projection Layer

## Responsibility

Transforms Inner Core information into bounded operational signals.

Projection is not raw Inner Core exposure.

Projection exists to provide operationally useful bounded signals without exposing deep private structures.

---

## May read

- Inner Core data through approved projection rules only.
- Projection configuration.
- Trust-level constraints.
- Domain relevance rules.

---

## May write

Bounded operational signals only:
- weights;
- acceptable harm ranges;
- sensitivity modifiers;
- delegation limits;
- confirmation requirements;
- bounded operational constraints.

---

## Must not read

- Raw runtime execution logs unless explicitly needed for approved projection update logic.
- External communication payloads as raw personality evidence.
- Full unrestricted Runtime context.

---

## Must not write

- Raw Inner Core outside Inner Core.
- Governance verdicts.
- Runtime lifecycle transitions.
- Shared Action ownership.
- Human-facing messages.

---

## Projection Boundary Principle

Projection carries:
- bounded operational effects;
- bounded coordination modifiers;
- bounded sensitivity modifiers.

Projection does not carry:
- raw emotional meaning;
- raw trauma meaning;
- unrestricted psychological interpretation;
- unrestricted personality truth.

Projection outputs must remain:
- operationally bounded;
- explainable;
- governance-compatible.

---

## Pain Point Projection Isolation

Sensitive Inner Core structures,
including pain points,
must never be exposed directly.

Projection may create:
- bounded confirmation sensitivity;
- bounded coordination caution;
- bounded interruption sensitivity;
- bounded cancellation sensitivity.

Projection must not expose:
- raw emotional wounds;
- raw trauma structures;
- unrestricted psychological interpretation.

Example:
Projection may expose:
- increased confirmation requirement for sudden cancellation

instead of:
- raw abandonment-related emotional interpretation.

---

## Projection Temporal Modifier Rules

Projection modifiers may be:
- stable;
- temporary;
- contextual;
- emergency-bound.

Temporary operational projection modifiers must not silently overwrite:
- stable Inner Core values;
- stable identity-relevant priorities;
- stable acceptable harm structures.

---

## Projection Contextuality Principle

Projection outputs may depend on:
- overload state;
- illness;
- emergency conditions;
- financial crisis;
- exam periods;
- cognitive exhaustion;
- temporary psychophysical conditions.

Contextual operational adaptation:
≠ stable identity modification.

---

## Sensor-to-Projection Separation

Sensor data must not silently become:
- projection truth;
- identity truth;
- personality assumptions;
- value assumptions.

Psychophysical state:
≠ stable human identity.

Temporary stress or overload
must not silently reshape:
- stable values;
- stable priorities;
- stable identity assumptions.

---

## Additional Rules

Projection update authority must be explicitly governed.

Projection signals cannot self-modify recursively through:
- Runtime feedback;
- Analyzer feedback;
- Communicator feedback;
- operational loops alone.

Projection adaptation requires explicitly approved update pathways.

No layer may silently reshape Inner-Core-derived operational behavior through uncontrolled recursive adaptation.

---

## Truth Authority

Projection Layer is the source of bounded Inner-Core-derived operational signals.

Projection truth ≠ raw personality truth.

Projection truth ≠ identity truth.

---

# 3. Core Engine

## Responsibility

Calculates psychophysical / health model state.

Core Engine is a computational reality layer.

---

## May read

- Assessment answers.
- Model input data.
- Sensor/context data if allowed.
- Calibration data if available.
- Projection signals only if explicitly required by model contract.

---

## May write

Core computational output:
- S;
- Δ;
- pressure;
- coverage;
- uncertainty;
- warnings;
- reason codes;
- forecast blocks;
- model states.

---

## Must not read

- Raw Inner Core.
- Governance private rules beyond model-relevant flags.
- Communicator raw dialogue.
- Runtime queues.

---

## Must not write

- Governance verdicts.
- Runtime lifecycle.
- Shared Action ownership.
- Human-facing messages.
- Long-term memory.

---

## Additional Rules

Core Engine output must remain:
- explainable;
- reproducible;
- traceable to model inputs.

Hidden heuristic drift must be avoided.

Model outputs must not become opaque authority claims without input-traceable reasoning.

---

## Truth Authority

Core Engine is the source of computational model truth.

Core Engine truth ≠ recommendation truth.

---

# 4. Analyzer

## Responsibility

Evaluates:
- readiness;
- uncertainty;
- consistency;
- contradictions;
- missing data;
- clarification need.

Analyzer does not decide permissions.

Analyzer detects consistency conflicts, not “human lying”.

---

## May read

- Core Engine output.
- Sensor/context readiness data.
- Projection signals.
- Temporary operational context when relevant.
- Shared Action references when needed for readiness.

---

## May write

- Readiness output.
- Uncertainty profile.
- Consistency flags.
- Contradiction flags.
- Missing data list.
- Clarification recommendations.
- Forecast permission recommendation.

---

## Must not read

- Raw Inner Core.
- Private communication not approved for analysis.
- External service raw data without governance-approved routing.

---

## Must not write

- Governance verdicts.
- Runtime execution state.
- Shared Action lifecycle transitions.
- Human-facing messages.
- Action ownership.

---

## Additional Analyzer Separation Rules

Analyzer may interpret:
- readiness;
- overload likelihood;
- uncertainty;
- contradiction patterns.

Analyzer must not silently transform:
- temporary psychophysical states
into:
- stable personality conclusions;
- identity interpretation;
- motivational certainty.

Readiness interpretation:
≠ identity interpretation.

---

## Truth Authority

Analyzer is the source of readiness / uncertainty / consistency truth.

Analyzer truth ≠ governance truth.

Analyzer truth ≠ execution truth.

---

# 5. Analyst

## Responsibility

Performs:
- cross-domain reasoning;
- harm minimization;
- tradeoff analysis;
- coordination analysis;
- action proposal generation.

Analyst proposes, but does not execute.

---

## May read

- Analyzer output.
- Projection signals.
- Shared Action summaries.
- Temporary Memory operational context.
- Domain Ray requests.
- Task constraints.
- Governance-readable policy summaries.

---

## May write

- Action proposals.
- Tradeoff analysis.
- Harm minimization options.
- Coordination recommendations.
- Delegation recommendations.

---

## Must not read

- Raw Inner Core.
- Communicator private logs unless approved and relevant.
- External raw private data without governance approval.

---

## Must not write

- Governance verdicts.
- Runtime lifecycle transitions.
- Shared Action ownership.
- Communicator messages directly.
- Memory promotion decisions.

---

## Additional Rules

Governance-readable policy summaries
≠ full Analyst reasoning.

Governance may read only bounded policy-relevant summaries.

Analyst reasoning must not silently become governance authority.

---

## Truth Authority

Analyst is the source of cross-domain reasoning proposals.

Proposal ≠ permission.

Proposal ≠ execution.

---

# 6. Governance

## Responsibility

Checks whether a proposed action or information transfer is allowed.

Governance is:
- boundary layer;
- permission layer;
- exposure-control layer.

Governance does not redesign solutions.

Governance does not execute actions.

---

## May read

- Action proposal.
- Projection limits.
- Trust level.
- Permission rules.
- Privacy rules.
- Autonomy limits.
- Confirmation requirements.
- Safety/legal boundaries.
- Relevant Analyzer flags.

---

## May write

Governance verdict only:
- allowed;
- blocked;
- restricted;
- requires_confirmation.

May also write:
- restriction reasons;
- required confirmation scope;
- public/private exposure limits;
- memory-write permission result;
- external communication permission result.

---

## Must not read

- Raw Inner Core.
- Full unrestricted Analyst reasoning.
- Full unrestricted Runtime context.
- Full raw dialogue unless needed and approved for boundary check.
- Debug/private model internals not relevant to permission.

---

## Must not write

- Shared Action lifecycle transitions.
- Runtime queue state.
- Task ownership.
- Analyst reasoning.
- Communicator message body.
- Temporary Memory records directly.

---

## Additional Rules

Governance may read only:
- policy-relevant;
- permission-relevant;
- privacy-relevant;
- safety-relevant bounded summaries.

Governance must not request unrestricted Analyzer or Runtime data by broadly claiming relevance.

Only minimally necessary data may cross governance boundaries.

Governance is not a reasoning layer.

Governance verdict semantics are authoritative.

---

## Truth Authority

Governance is the source of permission truth.

Governance verdict ≠ reasoning.

Governance verdict ≠ execution.

---

# 7. Runtime / Orchestration

## Responsibility

Coordinates operational execution after governance approval.

Runtime manages:
- lifecycle;
- routing;
- queues;
- stale actions;
- awaiting-human flows;
- execution coordination.

Runtime is an operational coordination layer.

Runtime is not:
- Analyzer;
- Governance;
- psychological profiler;
- truth engine;
- hidden planner.

---

## May read

- Governance verdicts.
- Shared Action records.
- Temporary Memory operational records.
- Analyst proposals.
- Analyzer readiness flags relevant to execution.
- Communicator delivery status.
- External system execution results.

---

## May write

- Shared Action lifecycle transitions.
- Queue state.
- Routing state.
- Ownership state.
- Execution records.
- Awaiting-human status.
- Stale/expired/blocked operational state.

---

## Must not read

- Raw Inner Core.
- Raw personality structures.
- Private data not needed for execution.
- External data not approved by Governance.

---

## Must not write

- Governance verdicts.
- Analyzer readiness conclusions.
- Analyst tradeoff reasoning.
- Inner Core data.
- Long-term memory.
- Human consent.

---

## Additional Rules

Runtime must never invent:
- consent;
- agreement;
- completion;
- confidence;
- coordination reality;
- schedule reality.

Runtime must not reinterpret Governance verdict semantics.

Runtime:
- applies verdicts;
- routes execution;
- updates lifecycle.

Runtime must not:
- soften restrictions;
- silently escalate permissions;
- reinterpret blocked as allowed;
- reinterpret requires_confirmation as implicit consent.

---

## Truth Authority

Runtime is the source of operational execution truth.

Runtime truth ≠ universal truth.

Runtime may coordinate only what Governance allows.

---

# 8. Shared Action Table

## Responsibility

Stores lifecycle truth for operational actions.

---

## May read

- Action lifecycle fields.
- Ownership fields.
- Status fields.
- Block reasons.
- Deadlines.
- Governance references.
- Runtime references.

---

## May write

Only through approved Runtime/update logic:
- status;
- owner_id;
- owner_type;
- block_reason;
- lifecycle timestamps;
- transition metadata.

---

## Must not read

- Raw Inner Core.
- Full Analyst reasoning blobs.
- Raw communication logs.
- Debug model internals.

---

## Must not write

- Governance decisions.
- Analyzer conclusions.
- Inner Core data.
- Long-term memory.
- Communication content.

---

## Additional Rules

Shared Action lifecycle truth:
- is operational truth only;
- is not historical truth;
- is not legal truth;
- is not psychological truth;
- is not universal world truth.

Operational state may differ from incomplete or later-discovered real-world events.

The system must not collapse operational tracking into universal truth claims.

---

## Truth Authority

Shared Action is the source of lifecycle truth.

Action state must reflect real operational state, not optimistic interpretation.

---

# 9. Temporary Memory

## Responsibility

Stores short-term operational context.

Temporary Memory is not:
- identity storage;
- personality archive;
- Inner Core;
- long-term memory.

---

## May read

- Operational task context.
- Runtime context.
- Current blockers.
- Unresolved questions.
- Temporary calibration notes.
- Short-term planning context.

---

## May write

- TTL-bound operational records.
- Unresolved flags.
- Expiration metadata.
- Used/resolved status.
- Temporary context references.

---

## Must not read

- Raw Inner Core.
- Full private identity data.
- Long-term personality archive.
- Raw sensor streams unless explicitly temporary and governed.

---

## Must not write

- Inner Core.
- Long-term memory.
- Governance verdicts.
- Runtime lifecycle directly.
- Hidden profiling records.

---

## Additional Rules

Temporary Memory promotion authority must be explicitly governed.

Temporary operational records must not silently become:
- long-term memory;
- identity structures;
- personality assumptions;
- behavioral profiling.

Promotion requires:
- explicit governance pathway;
- bounded criteria;
- traceable justification.

---

## Truth Authority

Temporary Memory is the source of short-term operational context only.

Temporary ≠ permanent.

Temporary ≠ personality.

Temporary ≠ Inner Core.

---

# 10. Communicator

## Responsibility

Formats and sends approved messages.

Receives:
- human responses;
- delivery results;
- communication acknowledgements.

Communicator is a delivery layer.

---

## May read

- Governance-approved message payloads.
- Runtime delivery instructions.
- Allowed tone/style constraints.
- Public/filtered context.
- Human response target metadata.

---

## May write

- Delivery status.
- Human responses.
- Message timestamps.
- Communication result records.

---

## Must not read

- Raw Inner Core.
- Internal debug structures.
- Full Analyst private reasoning unless approved for explanation.
- External private data not approved for communication.

---

## Must not write

- Governance verdicts.
- Runtime lifecycle decisions.
- Analyzer readiness.
- Analyst proposals.
- Inner Core updates directly.

---

## Additional Rules

Delivered ≠ accepted.

Read ≠ agreed.

Human response ≠ automatically verified truth.

The system must account for:
- overload;
- misunderstanding;
- accidental replies;
- sarcasm;
- ambiguity;
- emotional state;
- incomplete context.

Responses require governed interpretation before becoming persistent or high-confidence system truth.

---

## Truth Authority

Communicator is the source of delivery truth.

Delivery truth ≠ agreement truth.

---

# 11. Ray and External Processing Service Boundary

## Baseline Ray

Baseline Ray lives inside External Core.

Baseline Ray is:
- internal orchestration/runtime layer;
- internal coordination layer;
- internal operational layer of Individual Ray system.

Baseline Ray is not:
- Standard AI;
- external AI;
- external LLM;
- generic chatbot;
- independent reasoning authority;
- governance authority;
- memory authority;
- identity layer.

---

## External AI Processing Services

External AI processing services are external bounded processing services only.

They may receive only:
- sanitized;
- minimal;
- public;
- governance-approved payloads.

They must not receive:
- raw Inner Core;
- raw Projection data;
- private operational memory;
- internal debug reasoning;
- unrestricted user context.

---

## External Core Clarification

External Core is internal to Ray system.

“External” means external relative to Inner Core,
not external to Ray architecture.

---

# Global Invariants

## Unknown is not known

Missing data must never become confirmed truth.

---

## Verified is not assumed

Assumptions must remain labeled as assumptions.

---

## Estimated is not verified

Prediction and estimation cannot become execution truth.

---

## Chosen is not executed

A selected option still requires:
- governance approval;
- runtime execution routing.

---

## Human prohibition is terminal

If action status is forbidden_by_human,
it is terminal forever for that action_id.

New permission requires a new action_id.

---

## Temporary psychophysical state is not identity truth

Temporary psychophysical conditions must not silently become stable personality interpretation.

---

## No hidden authority

No layer may silently take over another layer’s responsibility.

---

## No recursive hidden adaptation

No layer may silently reshape another layer’s authority through uncontrolled feedback loops.

---

## No global truth object

The system must not collapse into:
- one universal JSON;
- one universal reasoning object;
- one universal memory object;
- one universal authority layer.