# Runtime Lifecycle Recovery Contract

## Core Principle

Recovery may restore visibility, trace, and review context.

Recovery must not restore execution legitimacy by itself.

Core invariants:

recovery  
≠ execution resumption

recovery visibility  
≠ recovery authority

recovered state  
≠ current valid state

---

## Purpose

This document defines the contract for Runtime lifecycle recovery.

It protects Runtime architecture from:
- hidden resume;
- zombie execution;
- restored stale authority;
- fake operational continuity;
- replay-based recovery drift;
- reconnect authority resurrection;
- partial recovery being treated as full recovery;
- restored visibility being treated as current validity.

---

## Recovery Definition

Recovery is the process of restoring bounded operational visibility after interruption, reconnect, retry preparation, restart, or partial state loss.

Recovery may restore:
- visibility;
- trace;
- review context;
- unresolved continuity;
- retry visibility;
- recovery candidate state;
- audit context;
- bounded orchestration context.

Recovery does not restore:
- execution authority;
- retry authority;
- external exposure authority;
- lifecycle mutation authority;
- human approval;
- Governance approval;
- verification authority;
- current validity.

---

## Recovery Is Not Execution Resumption

Recovery must not silently resume execution.

Core invariant:

recovery ≠ execution resumption

Recovery may show what was happening.

Recovery may show what was unresolved.

Recovery may show what may need review.

But recovery must not:
- restart execution;
- resume external calls;
- retry acquisition;
- mutate lifecycle state;
- mark action in progress;
- mark action completed;
- mark action failed;
- mark action cancelled;
- expose information externally.

Execution resumption requires explicit current authority, valid transition, and appropriate lifecycle event.

---

## Recovery Visibility Is Not Recovery Authority

Recovered visibility does not create authority.

Core invariant:

recovery visibility ≠ recovery authority

Runtime may recover visibility into:
- previous orchestration state;
- previous lifecycle state;
- previous authority references;
- previous retry context;
- previous external dependency context;
- previous event history.

But visibility into previous state must not be treated as permission to act.

Recovery visibility supports:
- review;
- validation;
- audit;
- replanning;
- renewed authorization.

It does not authorize execution.

---

## Recovered State Is Not Current Valid State

Recovered state may be stale, partial, inconsistent, or authority-invalid.

Core invariant:

recovered state ≠ current valid state

Recovered state may require:
- freshness validation;
- authority validation;
- transition validation;
- event validation;
- replay protection;
- scope validation;
- context validation;
- dependency validation;
- Governance validation where applicable.

Recovered state must not be treated as current valid state until required validation passes.

---

## Recovery Scope Boundary

Recovery must be bounded to its proper scope.

Recovered context must not be reused across:
- unrelated action_id;
- unrelated lifecycle object;
- unrelated operation scope;
- unrelated human confirmation scope;
- unrelated Governance scope;
- unrelated external exposure scope;
- unrelated memory scope.

Core invariant:

recovery in one scope  
≠ recovery authority in another scope

Recovery must not borrow authority, validity, or continuity from another action, branch, event chain, or orchestration context.

---

## Recovery Freshness Boundary

Recovered information may be historically accurate but operationally stale.

Core invariant:

historically accurate recovery  
≠ currently actionable recovery

Recovery freshness may be invalidated by:
- time passing;
- changed Governance state;
- changed human permission;
- changed risk level;
- changed operational context;
- changed external dependency;
- changed lifecycle state;
- expired authority;
- consumed event;
- replayed event;
- partial data loss.

If freshness is uncertain, Runtime must preserve unresolved recovery semantics.

---

## Recovery Replay Protection

Recovery must not replay old events into new authority.

Core invariant:

recovered event history  
≠ replay-authorized mutation

Recovered event history may support:
- audit;
- explanation;
- duplicate detection;
- recovery review;
- transition validation.

Recovered event history must not silently:
- re-apply consumed events;
- replay lifecycle mutations;
- recreate execution authority;
- retry external calls;
- re-expose information;
- re-run event chains.

Replay after recovery requires explicit policy, valid scope, and current authority.

---

## Recovery and Lifecycle Events

Recovered lifecycle events remain lifecycle events.

Recovered lifecycle events are not automatically trusted, applicable, or current.

Core invariants:

recovered event  
≠ trusted event

recovered event  
≠ applicable event

recovered event  
≠ fresh event

Recovered events may require:
- source validation;
- scope validation;
- freshness validation;
- replay validation;
- consumption validation;
- authority validation;
- transition validation.

Recovery must not convert event history into current mutation path.

---

## Recovery and Transition Validation

Recovery may provide input for transition validation.

Recovery does not validate transitions by itself.

Core invariant:

recovery context  
≠ transition eligibility

A recovered transition path may have been valid before interruption.

That does not mean it is valid now.

Recovered transition candidates require:
- current source state check;
- current target state check;
- current authority check;
- current event check;
- freshness check;
- replay check;
- blocker check.

Recovery must not smooth invalid transition continuity into valid operational continuity.

---

## Recovery and Shared Action Lifecycle

Recovery may restore Shared Action visibility.

Recovery must not mutate Shared Action lifecycle.

Core invariant:

recovered Shared Action visibility  
≠ Shared Action lifecycle mutation

Recovery may show:
- previous Shared Action state;
- unresolved state;
- pending review;
- previous retry context;
- previous event history.

Recovery must not infer:
- completion;
- cancellation;
- failure;
- approval;
- verification;
- execution;
- external exposure.

Shared Action lifecycle mutation still requires explicit event, valid transition, and current authority.

---

## Recovery and Orchestration State

Recovery may restore temporary orchestration visibility.

Recovery must not restore orchestration authority.

Core invariant:

recovered orchestration state  
≠ restored orchestration authority

Recovered orchestration state may support:
- review;
- unresolved continuity;
- retry visibility;
- reconnect awareness;
- recovery planning.

Recovered orchestration state must not:
- restart execution;
- recreate authority;
- retry automatically;
- expose externally;
- mutate durable lifecycle truth;
- become memory;
- become current validity without validation.

---

## Recovery and Authority

Recovered authority reference is not current authority.

Core invariant:

recovered authority reference  
≠ current authority

Recovery may show:
- previous authority;
- previous approval;
- previous Governance result;
- previous human confirmation;
- previous retry permission.

But Runtime must validate whether authority is:
- current;
- scoped;
- unexpired;
- unconsumed;
- unreplayed;
- compatible with current context;
- compatible with current lifecycle state.

Recovered authority must not be inherited silently.

---

## Recovery and Human Intent

Recovered human message or prior approval is not current human intent.

Core invariant:

recovered human signal  
≠ current human approval

Recovery must not infer current human approval from:
- previous message;
- prior silence;
- prior ambiguous response;
- prior consent;
- previous conversation continuity;
- historical preference.

Human intent after recovery may require renewed confirmation when scope, freshness, risk, or context is uncertain.

---

## Recovery and External Systems

Recovered external status is not verified current external truth.

Core invariant:

recovered external status  
≠ current verified external state

Recovered external data may be stale because:
- external system changed;
- callback was delayed;
- delivery was partial;
- dependency failed;
- status was superseded;
- operation was retried elsewhere;
- state was never verified.

Recovered external status may require:
- source validation;
- freshness check;
- verification;
- human review;
- Governance review;
- external re-check where allowed.

---

## Partial Recovery Boundary

Partial recovery must remain partial.

Core invariant:

partial recovery  
≠ full operational recovery

Partial recovery may restore some:
- visibility;
- trace;
- events;
- context;
- unresolved state.

Partial recovery must not infer missing:
- authority;
- current validity;
- event trust;
- transition eligibility;
- execution continuity;
- external status;
- human approval.

If recovery is incomplete, Runtime must preserve partial/unresolved semantics.

---

## Recovery Completion Boundary

Recovery completion does not mean task completion.

Core invariant:

recovery completed  
≠ lifecycle completed

Recovery may complete restoration of visibility or trace.

It does not mean:
- task completed;
- action executed;
- acquisition completed;
- external exposure completed;
- lifecycle resolved;
- human approved;
- Governance approved.

Recovery completion only means recovery process reached its own bounded endpoint.
Recovery completion does not authorize operational continuation.

Core invariant:

recovery completed  
≠ recovery authorized continuation

Recovery completion may indicate:
- visibility restored;
- trace restored;
- recovery flow finished;
- unresolved continuity restored;
- validation pending;
- review pending.

Recovery completion must not silently:
- resume execution;
- retry operation;
- restore authority;
- continue transition chain;
- continue external calls;
- resume lifecycle mutation.

Operational continuation after recovery requires:
- current authority;
- valid transition;
- fresh validation;
- replay protection;
- explicit continuation semantics where applicable.

---

## Recovery Result Boundary

Recovery result is not lifecycle truth.

Core invariant:

recovery result  
≠ lifecycle truth

Recovery result may indicate:
- restored visibility;
- partial restoration;
- unresolved restoration;
- recovery failure;
- recovery needs review;
- recovery needs revalidation.

Recovery result must not directly mutate lifecycle truth.

---

## Recovery Failure Boundary

Recovery failure does not mean task failure.

Core invariant:

recovery failure  
≠ task failure

Recovery failure may mean:
- trace unavailable;
- context incomplete;
- state corrupted;
- dependency unavailable;
- authority unknown;
- event history incomplete;
- validation impossible.

Recovery failure may require:
- unresolved state;
- manual review;
- re-acquisition;
- renewed authorization;
- fallback path;
- audit note.

Recovery failure must not automatically fail, cancel, or complete the task.

---

## Recovery Anti-Zombie Rules

Runtime must prevent zombie execution after recovery.

Zombie execution includes:
- resumed stale execution;
- repeated external call;
- stale retry;
- stale approval continuation;
- replayed mutation;
- hidden lifecycle progression;
- restored authority without validation.

Core invariant:

recovery must not resurrect execution authority

Recovered continuity may support review.

Recovered continuity must not resurrect operational authority.

---

## Recovery Anti-Optimism Rules

Runtime must not optimize recovery smoothness over truthful recovery state.

Core invariant:

smooth recovery  
≠ valid recovery

Runtime must not present:
- partial recovery as full recovery;
- stale recovery as current recovery;
- recovered visibility as recovered authority;
- recovered trace as recovered execution legitimacy;
- recovered event history as current transition path.

If recovery truth is uncertain, Runtime must preserve unresolved recovery semantics.

---

## Recovery Observability Requirements

Recovery must be observable and reviewable.

A recovery result should record:
- recovery id;
- recovered action_id where applicable;
- recovered lifecycle object;
- recovered orchestration state;
- recovered event references;
- recovered authority references;
- freshness status;
- replay status;
- scope status;
- validation status;
- partial recovery status;
- blockers;
- timestamp;
- reason codes.

No hidden recovery.

No hidden resume.

No hidden authority restoration.

---

## Recovery Auditability Requirements

Recovery must support audit.

Auditability should show:
- what was recovered;
- what was not recovered;
- what remains unresolved;
- what requires validation;
- what authority is missing or stale;
- what events are consumed or replay-risky;
- what execution remains blocked;
- what lifecycle mutations did not occur.

Recovery audit must make clear:

visibility restored  
≠ execution resumed

---

## Final Contract Summary

Recovery may restore visibility, trace, and review context.

Recovery may preserve unresolved continuity.

Recovery may support validation, replanning, and renewed authorization.

Recovery does not restore execution legitimacy.

Recovery does not restore authority.

Recovery does not make recovered state currently valid.

Recovery does not mutate lifecycle truth.

Final invariants:

recovery  
≠ execution resumption

recovery visibility  
≠ recovery authority

recovered state  
≠ current valid state