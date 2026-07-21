# Runtime Transition Validation Contract

## Core Principle

Valid lifecycle mutation requires valid lifecycle transition.

Runtime must validate transition eligibility before any lifecycle mutation may occur.

Transition validation determines whether a transition is structurally and contextually eligible.

Transition validation does not execute the transition.

Core invariants:

valid lifecycle mutation  
requires valid lifecycle transition

transition eligibility  
≠ transition execution

---

## Purpose

This document defines the contract for Runtime transition validation.

It protects Runtime architecture from:
- illegal lifecycle transitions;
- skipped authority gates;
- replayed transitions;
- stale-state mutation;
- optimistic progression;
- hidden transition smoothing;
- validation becoming execution;
- invalid transitions being normalized into fake operational continuity.

---

## Transition Validation Definition

Transition validation is the process of checking whether a proposed lifecycle transition is eligible.

A transition validation check may evaluate:
- source state;
- target state;
- lifecycle event;
- authority source;
- scope;
- freshness;
- replay risk;
- current context;
- boundary rules;
- required gates;
- blocking conditions.

Transition validation does not:
- perform the transition;
- grant authority;
- execute the action;
- verify truth;
- complete the task;
- cancel the task;
- fail the task;
- resolve unresolved lifecycle state.

---

## Transition Eligibility vs Execution

Transition eligibility means a transition may be considered valid if all required checks pass.

Transition execution means the lifecycle state is actually mutated.

These are separate operations.

Core invariant:

transition allowed  
≠ transition performed

A valid transition may still require:
- execution path;
- authorized mutation call;
- current Governance permission;
- human confirmation;
- verification result;
- runtime execution flow;
- external exposure authority;
- audit record creation.

Runtime must not treat transition eligibility as permission to execute.

---

## Transition Validation Is Not Authority Grant

Transition validation checks whether a proposed transition is structurally valid.

It does not create authority.

Core invariant:

transition validation  
≠ authority grant

A transition may be structurally valid but still blocked because:
- authority is missing;
- authority is stale;
- Governance approval is absent;
- human confirmation is required;
- scope is invalid;
- context changed;
- risk level changed;
- execution path is unavailable;
- verification is pending.

Validation may say “eligible.”

It must not say “authorized to execute” unless authority is separately provided.

---

## Required Transition Validation Standard

Every lifecycle transition validation must check:
- previous lifecycle state;
- proposed target lifecycle state;
- explicit lifecycle event;
- event source;
- authority source;
- transition scope;
- freshness;
- replay status;
- boundary restrictions;
- required gates;
- blocking conditions.

A valid transition must answer:

1. What state is changing?
2. What target state is proposed?
3. What explicit lifecycle event supports it?
4. Is the transition allowed from the current state?
5. Is the authority current and scoped?
6. Is the event fresh and not replayed?
7. Are required Governance or human gates satisfied?
8. Are there unresolved blockers?
9. Is the mutation observable and reviewable?

---

## Explicit Lifecycle Event Requirement

A transition cannot be valid without an explicit lifecycle event.

state observation ≠ transition event  
WAITING observed ≠ answered event  
timeout observed ≠ failure event  
cleanup observed ≠ cancellation event  
inbound result observed ≠ verification event  
prepared artifact observed ≠ exposure event  

Observed state may inform transition review.

Observed state must not become transition event by itself.

---

## Transition Authority Validation

A transition requires current bounded authority.

Authority must be:
- explicit;
- scoped;
- current;
- validated;
- reviewable.

Authority must not be inferred from:
- visibility;
- persistence;
- replay;
- unresolved continuity;
- retry availability;
- historical approval;
- cached approval;
- route availability;
- prepared artifact presence.

Core invariant:

visible authority  
≠ transition authority

Authority visibility may support validation.

Authority visibility does not satisfy validation by itself.

---

## Transition Freshness Validation

A transition must be fresh enough for the current operational context.

Historical validity does not guarantee current validity.

Core invariant:

historically valid transition  
≠ currently valid transition

Freshness validation may be required when:
- time passed;
- Governance state changed;
- human permission changed;
- context changed;
- risk level changed;
- dependency changed;
- action scope changed;
- lifecycle state changed;
- authority may have expired.

If freshness is uncertain, transition must remain unresolved or require renewed validation.

---

## Transition Replay Protection

A replayed lifecycle event must not silently authorize a new transition.

Core invariant:

replayed transition event  
≠ re-authorized transition

Replay protection must check:
- whether event was already consumed;
- whether transition was already applied;
- whether authority is still valid;
- whether scope still matches;
- whether target state is still valid;
- whether Governance is still valid where applicable;
- whether replay is explicitly allowed by policy.

Replay may support audit or recovery review.

Replay must not silently mutate lifecycle truth.

---

## Transition Scope Validation

A transition must be valid for the specific action, lifecycle object, and operation scope.

Core invariant:

valid authority in one scope  
≠ valid transition authority in another scope

Scope validation must check:
- action_id;
- lifecycle object identity;
- target state;
- operation type;
- target audience where applicable;
- external exposure boundary where applicable;
- memory boundary where applicable;
- Governance scope where applicable;
- human confirmation scope where applicable.

A transition must not borrow authority from another action, route, object, or scope.

---

## Forbidden Transition Sources

A transition must not be considered valid solely because of:
- WAITING persistence;
- timeout observation;
- cleanup execution;
- TTL expiration;
- retry visibility;
- route availability;
- route preparation;
- helper output;
- Coordinator readiness flag;
- acquisition request existence;
- inbound result presence;
- external response presence;
- prepared artifact presence;
- persisted orchestration state;
- replayed orchestration state;
- unresolved continuity.

Forbidden examples:

WAITING → completed is forbidden without explicit completion event.  
timeout → failed is forbidden without authorized timeout policy event.  
cleanup → cancelled is forbidden without explicit cancellation event.  
inbound_result → verified is forbidden without verification authority.  
prepared → externally_exposed is forbidden without exposure authority.  
persisted_unresolved → in_progress is forbidden without current resume authority.  

---

## Transition Failure Boundary

Transition failure means the proposed transition is invalid or cannot currently be applied.

Transition failure does not mean task failure.

Core invariant:

transition failure  
≠ task failure

A failed validation may result in:
- blocked transition;
- unresolved lifecycle state;
- request for renewed authority;
- request for clarification;
- recovery route;
- review route.

A failed transition validation must not automatically:
- fail the task;
- cancel the task;
- complete the task;
- retry execution;
- resolve lifecycle truth.

---

## Transition Blocked Boundary

A blocked transition means mutation is not allowed under current conditions.

A blocked transition does not mean task cancellation.

Core invariant:

transition blocked  
≠ task cancelled

Blocked transition may mean:
- missing authority;
- stale event;
- invalid scope;
- unresolved dependency;
- Governance restriction;
- human confirmation required;
- replay detected;
- context changed.

Blocked transition must preserve truthful unresolved or blocked semantics.

It must not be smoothed into completion, failure, or cancellation.

---

## Invalid Transition Handling

Invalid transition must not be normalized into valid operational continuity.

Core invariant:

invalid transition  
must not be normalized  
into valid operational continuity

Runtime must not “smooth over” invalid transitions by:
- skipping states;
- inventing authority;
- treating stale context as current;
- treating replay as fresh;
- converting unresolved into completed;
- converting blocked into failed;
- converting failed validation into task failure;
- auto-selecting a nearby valid state.

Invalid transition should remain invalid, blocked, or unresolved until an explicit valid route exists.

---

## Unresolved-State Preservation

Unresolved is a valid lifecycle condition.

If transition validation cannot determine eligibility, Runtime must preserve unresolved truth.

Core invariant:

uncertain transition eligibility  
must preserve unresolved semantics

Runtime must not force:
- completion;
- failure;
- cancellation;
- execution;
- exposure;
- verification;

when transition eligibility is unknown.

Unknown must remain unknown.

---

## Transition Observability Requirements

Every transition validation result should be observable.

A transition validation result should record:
- proposed transition;
- source state;
- target state;
- explicit event;
- authority source;
- validation result;
- reason codes;
- blockers;
- freshness status;
- replay status;
- scope status;
- timestamp.

Unobservable transition validation must not silently cause lifecycle mutation.

---

## Transition Auditability Requirements

Every transition validation must be reviewable after the fact.

Auditability requires:
- transition proposal record;
- validation checks performed;
- reason codes;
- authority source;
- event source;
- blocker list;
- final validation result.

No hidden transition validation.

No hidden lifecycle progression.

---

## Transition Rollback Boundary

Rollback is not automatic lifecycle correction.

Rollback requires explicit rollback semantics.

rollback intent ≠ rollback authority  
failed transition ≠ automatic rollback  
invalid transition ≠ previous state restoration  
blocked transition ≠ cancellation  

Rollback may require:
- explicit rollback event;
- valid authority;
- reviewable reason;
- safe target state;
- Governance approval where applicable.

Runtime must not use rollback to hide invalid transition handling.

---

## Runtime Anti-Optimistic Transition Rules

Runtime must not optimize lifecycle smoothness over truthful transition state.

Runtime must not prefer:
- smooth progress;
- clean closure;
- optimistic state advance;
- reduced visible uncertainty;
- fake continuity;

over:
- valid transition;
- current authority;
- verified event;
- unresolved truth;
- explicit mutation discipline.

Core invariant:

transition smoothness  
≠ transition validity

---

## Final Contract Summary

Transition validation checks eligibility.

Transition validation does not execute.

Transition validation does not grant authority.

Transition allowed does not mean transition performed.

Transition failure does not mean task failure.

Transition blocked does not mean task cancelled.

Invalid transitions must not be normalized into fake continuity.

Valid lifecycle mutation requires valid lifecycle transition.

Final invariant:

transition eligibility  
≠ transition execution