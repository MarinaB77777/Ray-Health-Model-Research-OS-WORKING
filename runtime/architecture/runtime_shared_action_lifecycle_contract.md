# Runtime Shared Action Lifecycle Contract

## Core Principle

Shared Action lifecycle truth must remain independent from temporary Runtime orchestration state.

Shared Action lifecycle must not be mutated by coordination state, helper output, routing visibility, WAITING persistence, timeout observation, cleanup, expiration, or inbound result presence alone.

Core invariant:

Shared Action lifecycle truth ≠ temporary Runtime orchestration state

---

## Purpose

This document defines the lifecycle boundary contract for Shared Actions.

It protects Shared Actions from:
- hidden completion;
- fake progress semantics;
- orchestration authority creep;
- routing becoming execution;
- external response becoming verified truth;
- WAITING becoming resolved;
- timeout becoming failure;
- cleanup becoming cancellation;
- temporary state becoming durable lifecycle truth.

---

## Shared Action Definition

A Shared Action is a durable operational lifecycle object.

It represents a coordinated action whose lifecycle state must remain:
- explicit;
- bounded;
- reviewable;
- authority-separated;
- independent from temporary orchestration state.

Shared Action lifecycle state is durable coordination truth.

Runtime orchestration may support Shared Action visibility and routing.

Runtime orchestration does not own Shared Action truth.

---

## Shared Action Lifecycle Ownership

Shared Action lifecycle mutation requires:
- explicit lifecycle event;
- valid transition;
- clear authority source;
- reviewable reason;
- observable state change;
- bounded target state.

Runtime may participate in Shared Action lifecycle flow only by:
- routing lifecycle-relevant information;
- exposing bounded operational visibility;
- maintaining temporary orchestration state;
- receiving authorized lifecycle events;
- applying authorized lifecycle mutations through explicit contract.

Runtime must not independently infer Shared Action truth.

---

## Shared Action vs Runtime Orchestration

Runtime orchestration may:
- prepare coordination context;
- track temporary WAITING;
- expose unresolved visibility;
- expose retry visibility;
- route inbound results;
- route acquisition requests;
- clean up expired temporary orchestration state.

Runtime orchestration must not:
- complete Shared Actions;
- resolve Shared Actions;
- verify Shared Actions;
- approve Shared Actions;
- execute Shared Actions;
- cancel Shared Actions;
- fail Shared Actions;
- externally expose Shared Actions;
- infer Shared Action truth from temporary state.

Critical invariant:

Runtime orchestration supports Shared Action lifecycle visibility.

Runtime orchestration does not own Shared Action lifecycle truth.

---

## Valid Shared Action Lifecycle Mutation Standard

Every Shared Action lifecycle mutation must have:
- previous lifecycle state;
- target lifecycle state;
- explicit lifecycle event;
- authority source;
- actor or system component;
- reason code;
- timestamp;
- transition validity check;
- boundary checks applied.

A Shared Action mutation must answer:

1. What Shared Action state is changing?
2. What explicit event caused the change?
3. Which authority allows this change?
4. Why is the target state valid?
5. What evidence supports the transition?
6. What prevents this transition from being orchestration drift?

---
## Additional Shared Action Lifecycle Safeguards
### Replay Is Not Re-Authorization

A previously valid lifecycle event must not silently authorize a new lifecycle mutation when replayed.

Core invariant:

replayed lifecycle event ≠ re-authorized lifecycle mutation

A replayed event must not cause mutation unless it passes current validation again:
- authority still valid;
- scope still valid;
- lifecycle transition still valid;
- Governance still valid where applicable;
- context still compatible;
- event has not already been consumed;
- replay is explicitly allowed by policy.

Replay protection prevents:
- duplicate lifecycle mutation;
- stale authority reuse;
- repeated execution;
- repeated external exposure;
- hidden lifecycle advancement from old events.

---

### Historical Authority Is Not Current Authority

Authority that was valid in the past is not automatically valid in the present.

Core invariant:

historically valid authority ≠ currently valid authority

Long-running or resumed workflows may require renewed authority validation when:
- Governance state changed;
- human permission changed;
- autonomy scope changed;
- external dependency changed;
- risk level changed;
- context changed;
- action scope expanded;
- time-sensitive approval expired.

Historical approval may preserve audit history.

Historical approval must not silently create current execution authority.

---

### Persistence Must Not Resurrect Execution Authority

Persisted unresolved state must not silently restart or resume execution authority.

Core invariant:

persisted unresolved state ≠ resurrected execution authority

A persisted Shared Action may remain visible, reviewable, recoverable, and unresolved.

But persistence alone must not:
- restart execution;
- resume external calls;
- retry acquisition;
- expose information externally;
- mark action in progress;
- create new authority;
- bypass renewed validation.

Resuming execution requires:
- current authority validation;
- valid lifecycle transition;
- compatible operational context;
- Governance approval where applicable;
- explicit resume/retry/recovery event.

Persistence preserves lifecycle continuity.

Persistence does not resurrect operational authority.

---

## Forbidden Shared Action Mutation Sources

Shared Action lifecycle must not be mutated solely by:
- WAITING state;
- WAITING persistence;
- timeout observation;
- retry visibility;
- route availability;
- route preparation;
- helper output;
- Coordinator readiness flag;
- acquisition request existence;
- temporary orchestration context;
- cleanup execution;
- TTL expiration;
- inbound result presence;
- external response presence;
- source availability;
- prepared artifact presence.

Forbidden examples:

WAITING → completed is forbidden.  
WAITING → resolved is forbidden.  
timeout → failed is forbidden without explicit authorized timeout policy event.  
cleanup → cancelled is forbidden.  
expiration → failed is forbidden.  
inbound_result → verified is forbidden without verification authority.  
prepared → externally_exposed is forbidden without exposure authority.  

---

## WAITING Isolation Rule

WAITING is a temporary orchestration condition.

WAITING may indicate:
- acquisition is pending;
- external response is pending;
- human response is pending;
- verification is pending;
- routing is paused;
- unresolved state exists.

WAITING does not mean:
- answered;
- verified;
- solved;
- approved;
- completed;
- failed;
- cancelled;
- executed;
- externally exposed;
- human intent inferred.

Core invariant:

WAITING ≠ Shared Action completion

WAITING must remain isolated from durable Shared Action completion semantics.

---

## Unresolved State Legitimacy

Shared Action unresolved is a valid durable lifecycle condition.

Unresolved does not mean failed.

Unresolved does not mean cancelled.

Unresolved does not mean completed.

Unresolved does not mean abandoned.

Unresolved means lifecycle truth is not yet known or not yet authorized for final mutation.

Core invariant:

unknown lifecycle truth must remain unresolved

Runtime must prefer unresolved truth over fake progress.

---

## Completion Requirements

Shared Action completion requires explicit completion semantics.

Completion must not be inferred from:
- WAITING ending;
- timeout;
- cleanup;
- expiration;
- inbound result presence;
- source response;
- prepared artifact;
- route success;
- message sent;
- acquisition request created;
- acquisition request sent.

Completion requires:
- explicit completion event;
- valid authority;
- transition check;
- reviewable reason;
- evidence appropriate to the action type.

completed ≠ routed  
completed ≠ answered  
completed ≠ externally responded  
completed ≠ message sent  
completed ≠ cleanup finished  

---

## Verification Requirements

Verified state requires verification authority.

Verification must not be inferred from:
- inbound result presence;
- external response presence;
- source availability;
- human message presence;
- successful routing;
- successful delivery;
- helper return value.

verified ≠ received  
verified ≠ routed  
verified ≠ answered  
verified ≠ plausible  
verified ≠ source-provided  

Inbound result may be routed for verification.

Runtime does not verify truth by itself.

---

## Cancellation Requirements

Cancellation requires explicit cancellation event.

Cancellation must not be inferred from:
- cleanup;
- expiration;
- timeout;
- no response;
- silence;
- unresolved state;
- retry not taken;
- temporary state deletion.

cancelled ≠ cleanup  
cancelled ≠ expired  
cancelled ≠ no response  
cancelled ≠ unresolved  

Human cancellation requires explicit human cancellation semantics.

System cancellation requires explicit authorized lifecycle policy.

---

## Failure Requirements

Failure requires explicit failure event or authorized failure policy event.

Failure must not be inferred from:
- timeout observation alone;
- cleanup;
- expiration;
- unresolved state;
- missing response;
- retry availability;
- temporary state deletion.

failed ≠ timeout  
failed ≠ expired  
failed ≠ unresolved  
failed ≠ cleanup  

A Shared Action may remain unresolved instead of failed when evidence is insufficient.

---

## External Exposure Requirements

External exposure requires explicit exposure authority.

External exposure must not be inferred from:
- prepared artifact;
- route availability;
- message draft existence;
- outbound request preparation;
- helper success;
- Runtime coordination readiness.

externally_exposed ≠ prepared  
externally_exposed ≠ routed  
externally_exposed ≠ approved  
externally_exposed ≠ ready  

External exposure requires:
- explicit exposure event;
- proper authority;
- Governance approval where applicable;
- observable delivery/exposure result.

---

## Human Intent Boundary

Human intent must not be inferred from weak signals.

human message presence ≠ human approval  
human silence ≠ human approval  
human silence ≠ human rejection  
ambiguous response ≠ authorization  
continued conversation ≠ consent  
prior preference ≠ current approval  

Shared Action mutation based on human intent requires explicit intent semantics.

---

## External Response Boundary

External response does not equal task resolution.

external response ≠ verified truth  
external response ≠ solved  
external response ≠ approved  
external response ≠ completed  
external response ≠ safe to act  

External response may be:
- routed;
- stored as inbound result where allowed;
- sent for verification;
- sent for human review;
- sent for Governance review.

External response must not directly mutate Shared Action truth.

---

## Runtime Coordination Restrictions

Runtime may coordinate Shared Action flow.

Runtime may not own Shared Action truth.

Runtime may not silently advance Shared Action lifecycle.

Runtime may not mutate Shared Action lifecycle from:
- temporary orchestration state;
- helper return values;
- visibility state;
- retry state;
- cleanup state;
- inbound presence alone.

Runtime must preserve explicit lifecycle event discipline.

---

## Cross-Layer Boundary

Shared Action lifecycle must not be mutated by impersonating another layer.

Governance decision ≠ execution  
Analyst recommendation ≠ completion  
Planner proposal ≠ approval  
Memory record ≠ lifecycle truth  
External response ≠ verified truth  
Runtime visibility ≠ lifecycle mutation  

A layer may provide an authorized event only within its proper authority.

Runtime must not manufacture missing authority.

---

## Anti-Fake-Progress Rule

Shared Action lifecycle must prefer unresolved truth over fake progress.

If truth is unknown, do not complete.

If answer is unverified, do not solve.

If exposure is not confirmed, do not mark exposed.

If execution is not verified, do not mark executed.

If cancellation is not explicit, do not cancel.

If failure is not explicit or policy-authorized, do not fail.

Core rule:

No fake lifecycle progress.

---

## Final Contract Summary

Shared Action lifecycle truth is durable.

Runtime orchestration state is temporary.

Temporary state may support visibility.

Temporary state must not own truth.

Shared Action unresolved is valid.

Lifecycle mutation requires explicit event and authority.

Final invariant:

Shared Action lifecycle truth must remain independent from temporary Runtime orchestration state.