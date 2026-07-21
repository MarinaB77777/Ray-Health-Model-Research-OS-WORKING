# Retention Governance Contract

Policy document version: retention-governance-contract-1

## Purpose

This document defines governance rules for research data retention within the university pilot research system.

The purpose of this contract is:
- define retention validity;
- define storage validity boundaries;
- define retention expiration semantics;
- define retention review boundaries;
- prevent silent ungoverned retention;
- preserve auditability;
- preserve future compatibility.

This document governs:
- retention status semantics;
- retention validity;
- retention expiration;
- retention restrictions;
- retention review visibility;
- retention-related governance decisions.

This document does NOT:
- define participant consent;
- define research export approval;
- define dataset admission;
- define deletion execution;
- define participant identity;
- define institutional review authority.

---

# Non-Purpose

Retention governance is not intended to:
- authorize research use;
- authorize export;
- authorize reuse;
- authorize longitudinal linkage;
- determine participant value;
- determine participant reliability;
- determine participant truthfulness.

Retention status
≠
participant status.

Retention status
≠
participant classification.

Retention governance
≠
research authority.

---

# Core Principle

Retention governance defines whether stored research data remains within the approved research scope.

retention governance
=
approved-scope storage/use-validity boundary

Retention governance does NOT define:
- consent authority;
- export authority;
- dataset authority;
- deletion execution authority.

retention governance
≠
deletion engine

retention governance
≠
export authority

retention governance
≠
consent authority

retention governance
≠
dataset assembler

---

# Retention Statuses

Allowed retention statuses:
- not_evaluated
- active
- expired
- deleted
- deletion_requested
- retention_blocked
- policy_restricted

Retention status must remain explicit.

missing retention status
≠
active

unknown retention status
≠
retention allowed

---

# Retention Evaluation Boundary

Retention evaluation must remain explicit.

not_evaluated
≠
active

not_evaluated
≠
expired

active
=
retention remains valid within the originally approved research scope

expired
≠
deleted

deletion_requested
≠
deleted

retention_blocked
≠
deleted

policy_restricted
≠
deleted

Retention uncertainty must remain visible.

Unknown retention state
≠
permission to continue reuse.

---

# Retention Record Shape

Retention records should include:
- retention_status
- retention_version
- retention_class
- retention_basis
- retention_reviewed_at
- expiration_at
- deletion_requested_at
- deleted_at
- notes

notes may exist for audit purposes.

notes
≠
research export permission

notes must not silently enter research exports.

Retention record
≠
participant profile.

Retention record
≠
research approval.

---

# Retention Class Boundary

Retention classes may define:
- retention duration;
- review requirements;
- expiration requirements;
- reuse limitations;
- storage limitations.

Retention class
≠
research permission.

Retention class
≠
dataset permission.

Retention class
≠
consent scope.

---

# Expiration Boundary

Retention expiration is a governance state.

expired
=
retention validity ended

Retention expiration does not automatically imply:
- deletion completed;
- export invalidation;
- historical artifact destruction.

retention expired
≠
immediate physical deletion

expired retention
≠
participant failure

---

# Deletion Boundary

Deletion governance and retention governance are separate.

Retention governance may indicate:
- deletion requested;
- deletion pending;
- retention no longer valid.

Retention governance does not perform deletion.

deletion requested
≠
deletion completed

deleted status
≠
active retention authority

Retention governance
≠
deletion engine

---

# Consent / Retention Separation

Consent and retention are separate governance layers.

Consent governance answers:

does participant permission exist for a bounded scope?

Retention governance answers:

is continued storage/use-validity still allowed under retention rules?

consent granted
≠
indefinite retention

consent granted
≠
active retention

consent revoked
≠
automatic deletion

retention active
≠
consent granted
Consent for a new session controls future collection.

Refusal or absence of consent for a new session
does not automatically invalidate previously collected,
properly consented, anonymized research data.

Previously completed sessions may remain usable
within the originally approved research scope
unless retention status, withdrawal rules,
institutional requirements, or policy restrictions say otherwise.

---

# Export Boundary

Retention governance does not authorize export.

retention active
≠
export allowed

retention allowed
≠
export allowed

export_valid=True
≠
retention valid

research export exists
≠
retention active

retention expired after export
≠
proof that export was invalid when generated

historical export existence
≠
current retention validity

---

# Reuse Boundary

Retention governance does not authorize reuse.

retention active
≠
reuse approved

retention valid
=
continued use is allowed only within the originally approved research scope

stored data
≠
unrestricted reusable data

Reuse governance may later impose additional restrictions.

Retention validity
≠
reuse permission.

---

# Snapshot Boundary

Research snapshot existence does not determine retention validity.

snapshot exists
≠
retention valid

snapshot exists
≠
reuse permission

research snapshot exists
≠
snapshot may continue to be reused

historical artifact existence
≠
active retention permission

historical export exists
≠
retention active

---

# Dataset Boundary

Retention governance does not determine dataset admission.

retention active
≠
dataset admissible

dataset admitted
≠
retention active

dataset admissible
≠
retention valid by itself

retention unknown
≠
safe dataset admission

retention not_evaluated
≠
safe dataset admission

---

# Existing MVP Compatibility Boundary

Current MVP components may contain retention-related placeholders.

Presence of retention-related fields does not imply that retention governance exists.

existing retention placeholder
≠
implemented retention governance

placeholder retention status
≠
implemented retention evaluation

retention field presence
≠
retention approval

retention field presence
≠
retention reviewed

aggregation retention status
≠
retention authority

Runtime intake retention policy
≠
research retention governance.

IntakeRetentionPolicy.allow_cleanup
≠
research retention validity.

Runtime soft delete / purge
≠
research deletion governance.

Runtime cleanup retention
≠
research data retention.

Research retention components must not import Runtime intake retention policy.

Runtime intake cleanup components must not import Research Retention Governance.

---

# Audit Boundary

Retention governance should preserve:
- retention status;
- retention reason;
- retention review history;
- expiration visibility;
- deletion-request visibility;
- policy restrictions.

Auditability
≠
surveillance authority.

Retention review
≠
participant scoring.

Retention review
≠
automatic renewal

Retention review
≠
automatic retention extension

review completed
≠
retention approved

---

# Future Implementation Boundary

Future implementation may introduce:
- retention registry;
- retention validator;
- retention policy engine;
- expiration workflows;
- deletion request workflows;
- retention audit trail;
- retention review scheduling.

Future implementation
≠
automatic retention approval.

Unimplemented retention feature
≠
active retention.

---

# Final Principle

Retention governance exists to define bounded storage validity.

Retention governance must never become:
- unrestricted storage authority;
- hidden profiling infrastructure;
- silent ungoverned retention mechanism;
- participant scoring system;
- unrestricted reuse authority.

stored data
≠
unrestricted reusable data

retention allowed
=
continued use allowed only within the originally approved research scope

retention allowed
≠
new research purpose approval

research usefulness
≠
retention justification
