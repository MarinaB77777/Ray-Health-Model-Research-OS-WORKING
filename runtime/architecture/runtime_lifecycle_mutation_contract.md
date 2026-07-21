# Runtime Lifecycle Mutation Contract

## Core Principle

Lifecycle mutation is a governed explicit operation.

Lifecycle mutation must never occur as an implicit side effect of orchestration, routing, observation, retry visibility, timeout handling, cleanup, or temporary state expiration.

Core invariant:

lifecycle mutation ≠ orchestration side-effect

---

## Purpose

This document defines the boundary contract for Runtime lifecycle mutations.

It protects Runtime architecture from:
- hidden completion;
- implicit lifecycle drift;
- orchestration authority creep;
- coordination becoming execution;
- observation becoming mutation;
- temporary state becoming durable truth;
- fake lifecycle progress semantics.

---

## Lifecycle Mutation Definition

A lifecycle mutation is any change to durable lifecycle truth.

Examples include changing a Shared Action or Runtime task into:
- prepared;
- waiting;
- answered;
- verified;
- approved;
- executed;
- completed;
- resolved;
- cancelled;
- failed;
- externally_exposed;
- blocked;
- expired.

A lifecycle mutation changes durable lifecycle state.

Therefore, it requires explicit authority and explicit lifecycle event semantics.

---

## What Is Not Lifecycle Mutation

The following are not lifecycle mutations by themselves:
- observing temporary orchestration state;
- observing WAITING;
- observing timeout;
- observing inbound result presence;
- observing retry availability;
- preparing an artifact;
- routing an artifact;
- exposing retry visibility;
- running cleanup;
- expiring temporary orchestration state;
- receiving source response;
- detecting unresolved state;
- creating temporary orchestration context.

These may inform lifecycle decisions.

They must not directly mutate lifecycle truth.

---

## Required Lifecycle Mutation Standard

Every lifecycle mutation must have:
- explicit lifecycle event;
- bounded target state;
- clear source of authority;
- observable transition;
- reviewable reason;
- mutation source record;
- separation from temporary orchestration state.

A lifecycle mutation must answer:

1. What lifecycle state is changing?
2. What explicit event caused the change?
3. Which authority allows this mutation?
4. What target state is being assigned?
5. Why is this transition valid?
6. What evidence or event supports it?
7. What boundaries prevent overreach?

---

## Explicit Lifecycle Event Rule

Lifecycle mutation requires an explicit lifecycle event.

state observation ≠ state mutation

Examples:

WAITING observed ≠ answered  
timeout observed ≠ failed  
inbound result observed ≠ verified  
retry visible ≠ retry required  
source available ≠ truth confirmed  
cleanup completed ≠ cancelled  
expiration reached ≠ failed  
artifact prepared ≠ externally exposed  

Observed orchestration state may inform lifecycle decisions, but must not itself mutate lifecycle truth.

---

## Allowed Mutation Sources

Lifecycle mutation may be allowed only from explicit, bounded sources such as:
- human confirmation;
- Governance-approved action;
- verified execution result;
- verified external exposure event;
- explicit cancellation event;
- explicit failure event;
- explicit system lifecycle event;
- authorized Shared Action transition;
- verified acquisition completion;
- explicit rejection or decline event;
- explicit timeout policy event where timeout policy is itself authorized.

Allowed source does not mean automatic mutation.

The source must still pass:
- authority check;
- boundary check;
- transition validity check;
- observability requirement;
- auditability requirement.

---

## Forbidden Mutation Sources

Lifecycle mutation must not be caused only by:
- WAITING persistence;
- temporary orchestration state;
- retry visibility;
- route availability;
- route preparation;
- inbound presence;
- source availability;
- cleanup execution;
- TTL expiration;
- timeout observation;
- unresolved state visibility;
- helper return value;
- Coordinator readiness flag;
- acquisition request existence;
- external response presence;
- prepared artifact presence.

Forbidden source examples:

WAITING → completed is forbidden.  
timeout → failed is forbidden unless explicit authorized timeout policy event exists.  
inbound_result → verified is forbidden without verification authority.  
prepared → externally_exposed is forbidden without explicit exposure event.  
cleanup → cancelled is forbidden.  
expiration → failure is forbidden.  

---

## Runtime Authority Boundary

Runtime may coordinate lifecycle-relevant operations.

Runtime may observe lifecycle-relevant state.

Runtime may route lifecycle-relevant information.

Runtime may expose bounded operational visibility.

Runtime must not independently grant:
- approval;
- verification;
- execution authority;
- external exposure authority;
- final completion;
- final resolution;
- cancellation;
- failure;
- durable truth.

Runtime can participate in lifecycle mutation only when an explicit authorized event is provided.

Runtime coordination ≠ lifecycle authority

---

## Shared Action Mutation Boundary

Shared Action lifecycle must not be mutated by orchestration state alone.

Shared Action mutation requires:
- explicit Shared Action lifecycle event;
- valid transition;
- known authority source;
- bounded target state;
- reviewable reason;
- no dependency on temporary orchestration state as sole cause.

WAITING orchestration must not mutate Shared Action lifecycle into:
- completed;
- resolved;
- verified;
- executed;
- approved;
- externally_exposed;
- solved;
- cancelled;
- failed.

Core invariant:

WAITING orchestration ≠ Shared Action completion

---

## Temporary State Mutation Restriction

Temporary orchestration state may support lifecycle visibility.

Temporary orchestration state must not become lifecycle authority.

Temporary orchestration state may be:
- created;
- updated;
- expired;
- cleaned up;
- marked unresolved;
- made retry-visible.

But temporary orchestration state must not directly cause durable lifecycle mutation.

temporary orchestration state ≠ durable coordination truth

---

## Cleanup and Expiration Mutation Boundary

Cleanup is operational hygiene only.

Expiration means temporary orchestration state is no longer valid for continued use without renewed evaluation.

cleanup ≠ cancellation  
expiration ≠ failure  
TTL expiry ≠ task rejection  
temporary state deletion ≠ Shared Action deletion  
orchestration cleanup ≠ lifecycle resolution  

Cleanup and expiration may generate visibility or review needs.

They must not directly mutate durable lifecycle truth.

---

## Timeout Mutation Boundary

Timeout observation is not failure.

timeout observed ≠ failed  
timeout observed ≠ completed  
timeout observed ≠ cancelled  
timeout observed ≠ human declined  

Timeout may produce:
- unresolved visibility;
- retry availability;
- review request;
- authorized timeout policy event.

Only an explicit authorized timeout policy event may produce lifecycle mutation.

---

## Inbound Result Mutation Boundary

Inbound result presence is not verified truth.

inbound_result ≠ verified_truth  
source response ≠ task solved  
source response ≠ human approval  
source response ≠ execution authority  

Inbound result may be routed to:
- Analyzer;
- verification layer;
- Governance;
- Runtime review path;
- human confirmation path;
- Shared Action review path.

Runtime must not mutate lifecycle truth from inbound result presence alone.

---

## Prepared Artifact Mutation Boundary

Prepared artifact does not equal exposed artifact.

prepared ≠ externally_exposed  
prepared ≠ sent  
prepared ≠ approved  
prepared ≠ published  
prepared ≠ delivered  

Prepared artifact may become externally exposed only through:
- explicit exposure event;
- proper authority;
- Governance approval where required;
- observable delivery result.

Prepared state must not silently become exposed state.

---

## Helper / Coordinator Boundary

Helper outputs and Coordinator readiness flags are not lifecycle authority.

helper output ≠ lifecycle mutation  
coordinator readiness ≠ lifecycle truth  
acquisition needed ≠ acquisition completed  
not ready ≠ acquisition needed  
ready_for_next_route ≠ task solved  

Helper outputs may support routing decisions.

They must not directly mutate durable lifecycle state.

---

## Mutation Observability Requirements

Every lifecycle mutation must be observable.

A valid lifecycle mutation should record:
- previous state;
- target state;
- explicit lifecycle event;
- authority source;
- actor or system component;
- reason code;
- timestamp;
- boundary checks applied.

If mutation cannot be observed or reviewed, it should not occur.

---

## Mutation Auditability Requirements

Every lifecycle mutation must be reviewable after the fact.

Auditability requires:
- explicit event record;
- transition source;
- target state;
- reason code;
- authority source;
- failure/rollback visibility where applicable.

No hidden mutation is allowed.

No silent lifecycle progression is allowed.

---

## Cross-Layer Mutation Restrictions

Runtime must not mutate lifecycle truth on behalf of:
- Governance;
- Analyst;
- Planner;
- Memory;
- external systems;
- human approval;
- verification layer.

Runtime may route requests to those layers.

Runtime may receive authorized events from those layers.

Runtime must not impersonate their authority.

Governance decision ≠ Runtime execution  
Analyst recommendation ≠ lifecycle mutation  
Planner proposal ≠ lifecycle mutation  
Memory record ≠ lifecycle truth  
external response ≠ verified truth  
human message presence ≠ human approval  

---

## Human Approval Boundary

Human approval requires explicit approval semantics.

Human message presence is not approval.

human message received ≠ human approved  
human silence ≠ human declined  
human silence ≠ human approved  
ambiguous response ≠ approval  
partial response ≠ full authorization  

Runtime must not infer human approval from:
- inbound message presence;
- silence;
- timeout;
- incomplete response;
- unrelated reply;
- continued conversation;
- prior general preference.

---

## Failure / Cancellation Boundary

Failure and cancellation require explicit lifecycle events.

failure ≠ timeout  
failure ≠ cleanup  
failure ≠ expiration  
failure ≠ unresolved  
cancellation ≠ cleanup  
cancellation ≠ temporary deletion  
cancellation ≠ missing response  

A task may remain unresolved without being failed or cancelled.

Unresolved is a valid lifecycle condition when truth is unknown.

---

## Valid Mutation Direction Principle

Lifecycle mutation must move state only through valid transitions.

A mutation must not skip required authority gates.

Forbidden examples:
- waiting → completed without verified completion event;
- prepared → externally_exposed without exposure event;
- answered → solved without verification or resolution event;
- timeout → failed without authorized timeout policy event;
- cleanup → cancelled without explicit cancellation event;
- inbound_result → verified without verification authority;
- analyst_recommendation → executed without Governance/Runtime execution path.

---

## Anti-Fake-Progress Rule

Runtime must prefer unresolved truth over fake lifecycle progress.

Unknown must remain unknown.

Unanswered must remain unanswered.

Unverified must remain unverified.

Unexecuted must remain unexecuted.

Unexposed must remain unexposed.

If evidence is insufficient, Runtime must not “helpfully” advance lifecycle state.

---

## Final Contract Summary

Lifecycle mutation is explicit.

Lifecycle mutation is bounded.

Lifecycle mutation is observable.

Lifecycle mutation is reviewable.

Lifecycle mutation requires authority.

Lifecycle mutation requires an event.

Runtime orchestration may support lifecycle visibility.

Runtime orchestration must not silently mutate lifecycle truth.

Final invariant:

lifecycle mutation ≠ orchestration side-effect