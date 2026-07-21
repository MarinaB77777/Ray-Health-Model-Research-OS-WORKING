# Pilot Implementation Plan

## Purpose

This document defines the implementation plan for Pilot v1 of the psychophysical readiness system.

This document exists to:
- prevent architectural drift;
- separate executable reality from documentation;
- define implementation order;
- define pilot boundaries;
- define operational priorities;
- prevent fake implementation feeling.

This document is:
- an implementation plan;
- an operational audit;
- a bounded roadmap.

This document is NOT:
- a constitutional architecture rewrite;
- a speculative AGI roadmap;
- unrestricted future planning.

---

# Current Honest Status

Current system status:

Remote executable pilot skeleton ✅

Real university pilot system ❌ not yet.

Currently operational:
- FastAPI backend;
- /run endpoint;
- Render deployment;
- psychophysical engine foundation;
- readiness logic foundation;
- uncertainty routing foundation;
- forecast governance foundation;
- next_questions foundation;
- data_acquisition_requests foundation;
- pilot_session MVP endpoints;
- bounded export foundation.

Currently verified:
- create session;
- submit answers;
- run engine;
- export session;
- Render deployment;
- remote end-to-end pilot loop.

---

# Critical Operational Truths

The following are valid operational states:

- NOT_ENOUGH_DATA = valid state
- UNKNOWN = valid status
- no data ≠ failure
- missing answer ≠ invented conclusion

The following architectural separations must remain true:

- pilot session ≠ analyst
- pilot export ≠ medical truth
- session persistence ≠ orchestration authority
- export_generated ≠ export_valid
- stored uncertainty ≠ resolved uncertainty

---

# Current Critical Gaps

Current critical missing areas:

1. No persistent storage layer.
   Sessions disappear after restart.

2. No consent persistence.
   consent_version is not stored.

3. No schema/engine/export version persistence.

4. No audit trail persistence.

5. No retention/deletion/anonymization implementation.

6. No participant-facing bounded flow.

7. No controlled API error layer.

8. No participant export vs research export separation.

9. No session validity lifecycle semantics.

10. No bounded clarification loop.

11. No persistent research-safe export storage.

12. No operational invalidation semantics.

13. No explicit export validity model.

14. No pseudonymous participant governance model.

---

# What Pilot v1 Explicitly Does NOT Do

Pilot v1 does NOT implement:

- Inner Core
- Projection Layer
- adaptive personality learning
- hidden longitudinal profiling
- unrestricted Runtime orchestration
- Domain Rays
- autonomous coordination
- psychological authority
- medical diagnosis
- unrestricted forecasting
- automatic forecast if readiness blocked
- hidden participant scoring
- real identity storage by default
- unrestricted sensor integration
- unrestricted memory accumulation

Pilot v1 remains:

bounded uncertainty-aware operational research infrastructure

NOT:
- AGI;
- therapist;
- hidden adaptive agent;
- unrestricted profiling system.

---

# Pilot v1 Target

Pilot v1 target:

bounded executable university pilot system

The minimum Pilot v1 must support:

- participant session lifecycle;
- persistent sessions;
- bounded questionnaire flow;
- bounded clarification flow;
- engine execution;
- uncertainty-aware outputs;
- research-safe exports;
- operational invalidation;
- retention/deletion handling;
- bounded participant-facing interaction.

---

# Required Lifecycle Semantics

The following semantics must remain separated:

CLOSED
= operationally finalized

INVALIDATED
= excluded / not reliable / not usable for research output

DELETED / ANONYMIZED
= removed or anonymized according to retention policy

These states must NOT collapse into a single status transition.

---

# Export Validity Rules

The following invariant must remain true:

export_generated ≠ export_valid

An export may become invalid because of:
- export policy changes;
- schema changes;
- engine version changes;
- invalidated session;
- retention rules;
- governance restrictions.

Export generation does NOT guarantee eternal validity.

---

# Phase Plan

## Phase 1 — Persistent Storage Foundation

Goal:
session survives restart.

Implement:
- pilot_session/persistent_store.py
- persistence serialization
- persistence deserialization
- persistence tests

Persistence must preserve:
- session lifecycle state;
- answers;
- public output;
- uncertainty;
- acquisition snapshots;
- clarification snapshots;
- schema versions;
- consent version.

No hidden recalculation allowed.

---

## Phase 2 — Lifecycle Semantics

Implement:
- CLOSED semantics
- INVALIDATED semantics
- DELETED/ANONYMIZED semantics

Add:
- explicit session validity model;
- export validity rules;
- operational invalidation handling.

---

## Phase 3 — Controlled API Errors

Implement controlled HTTP responses:

- SESSION_NOT_FOUND
- INVALID_STATUS_TRANSITION
- EXPORT_BLOCKED
- SESSION_INVALIDATED
- SESSION_DELETED
- RUN_FAILED

No raw traceback exposure.

---

## Phase 4 — Export Separation

Separate:
- participant export
- research export

Participant export:
- bounded public output only.

Research export:
- research-safe structured data only.

No hidden profiling exports.

---

## Phase 5 — Retention / Deletion / Anonymization

Implement:
- retention policy;
- anonymization rules;
- deletion handling;
- invalidation handling.

No silent retention drift.

---

## Phase 6 — Bounded Clarification Loop

Implement:

answers
→ run
→ clarification questions
→ additional answers
→ rerun
→ bounded export

No autonomous endless questioning.

---

# Exact Coding Order

1. persistent_store.py
2. persistence tests
3. lifecycle semantics
4. controlled API errors
5. close / invalidate / get endpoints
6. participant export vs research export
7. retention / deletion / anonymization
8. bounded clarification loop

No DB shortcuts before lifecycle semantics.

No UI-first implementation before persistence.

No export expansion before validity rules.

---

# Test Gates

Each phase must include:
- isolated tests;
- lifecycle tests;
- serialization tests;
- regression tests;
- deployment-safe validation.

No phase proceeds before:
- pytest passes;
- lifecycle invariants remain valid;
- uncertainty handling remains intact.

---

# Deployment Gate

Deployment is allowed only if:
- tests pass;
- no hidden Runtime drift detected;
- no public/internal leakage detected;
- no lifecycle collapse detected;
- no persistence reinterpretation introduced.

---

# Current Strategic Position

Current position is strong because:
- executable backend exists;
- uncertainty legitimacy exists;
- bounded Runtime exists;
- remote pilot loop works;
- architecture drift has reduced;
- anti-fabrication direction stabilized.

However:

Current system is still a bounded executable pilot skeleton,
not yet a full university pilot system.

The next implementation priority is:
persistent operational foundation,
not architectural expansion.