# Consent Governance Contract

## Purpose

This document defines governance rules for participant consent within the university pilot research system.

The purpose of this contract is:
- bounded consent handling;
- research participation governance;
- participant autonomy protection;
- consent-aware research export;
- consent-aware dataset admission.

This document governs:
- consent status semantics;
- consent scope semantics;
- consent records;
- consent revocation;
- research export eligibility.

This document does NOT:
- define participant identity;
- define research approval;
- define retention policy;
- define dataset governance;
- define institutional review authority.

---

# Non-Purpose

Consent governance is not intended to:
- determine participant value;
- determine participant reliability;
- determine participant truthfulness;
- authorize unrestricted research use;
- replace ethics review.

Consent status
≠
participant classification.

Consent record
≠
participant identity.

---

# Core Principle

Consent must be:
- explicit where required;
- bounded;
- reviewable;
- revocable;
- purpose-limited.

consent granted
≠
unrestricted future use.

consent scope
≠
global permission.

research participation
≠
unrestricted data use.

---

# Runtime Governance Boundary

Runtime governance and consent governance are separate layers.

Runtime governance controls operational action boundaries, including:
- proposed action evaluation;
- external communication;
- memory write;
- autonomy;
- emergency handling;
- sensitive domain restrictions;
- visibility and target audience;
- confirmation requirements.

Consent governance controls participant research permission boundaries, including:
- research participation consent;
- research snapshot export consent;
- dataset inclusion consent;
- future contact consent;
- future study consent;
- consent revocation visibility;
- consent expiration visibility.

Runtime governance verdict
≠
participant research consent.

Runtime permission
≠
research export consent.

GovernanceDecisionStatus.ALLOWED
≠
consent_status.granted.

GovernanceDecisionStatus.BLOCKED
≠
consent_status.denied.

GovernanceDecisionStatus.NOT_ENOUGH_DATA
≠
consent_status.not_evaluated.

Consent status
≠
Runtime execution permission.

Consent governance must not replace Runtime governance.

Runtime governance must not infer participant research consent.

---

# Consent Decision Boundary

Consent decision and Runtime governance verdict are different artifacts.

Consent decision may describe:
- whether consent exists;
- what scope consent covers;
- whether consent is pending;
- whether consent was revoked;
- whether consent expired.

Runtime GovernanceVerdict may describe:
- whether an operational action is allowed;
- whether a Runtime action is blocked;
- whether action scope is restricted;
- whether confirmation is required;
- whether operational information is insufficient.

Consent decision
≠
GovernanceVerdict.

ConsentRecord
≠
GovernanceVerdict.

consent_status.granted
≠
GovernanceDecisionStatus.ALLOWED.

consent_status.denied
≠
GovernanceDecisionStatus.BLOCKED.

Consent governance may later inform research export eligibility.

Consent governance must not become Runtime action authority.

Runtime governance may later read consent status as one input for research export actions, but must not rewrite consent status.

---

# Consent Statuses

Allowed consent statuses:

- not_evaluated
- pending
- granted
- denied
- revoked
- expired

Consent status must remain explicit.

missing consent status
≠
granted.

silence
≠
consent.

---

# Consent Evaluation Boundary

Consent evaluation must remain explicit.

not_evaluated
≠
denied.

not_evaluated
≠
granted.

pending
≠
granted.

expired
≠
revoked.

expired
≠
denied.

Consent status uncertainty must remain visible.

Unknown consent state
≠
permission to proceed.

Consent evaluation
≠
participant classification.

For research export and dataset admission:

not_evaluated
=
blocked until consent evaluation occurs.

---

# Consent Record Shape

Consent records should include:

- consent_status;
- consent_version;
- consent_scope;
- granted_at;
- revoked_at;
- expiration_at;
- consent_basis;
- notes.

Consent record
≠
participant profile.

---

Consent records may evolve over time.

Future implementations may preserve:
- consent history;
- consent revisions;
- consent renewals;
- consent revocations.

Current consent status
≠
entire consent history.

Consent history
≠
permission to ignore current consent state.

---

# Consent Scope Boundary

Consent must remain scoped.

Examples of scope may include:
- pilot participation;
- research snapshot export;
- dataset inclusion;
- future contact;
- future studies.

Consent granted for one scope
≠
consent granted for all scopes.

dataset consent
≠
future contact consent.

future contact consent
≠
future studies consent.

---

Broad scope
≠
unbounded scope.

Consent scope must remain:
- explicit;
- reviewable;
- purpose-limited.

Future consent expansion
≠
implicit consent expansion.

---

# Missing Consent Boundary

Missing consent must not be interpreted as consent.

missing consent
≠
implied approval.

missing consent
≠
denied consent.

missing consent
≠
participant failure.

For research export purposes:

missing consent
=
export blocked.

---

Missing consent
≠
not_evaluated consent.

Missing consent indicates absence of a consent record.

not_evaluated indicates that consent evaluation has not yet completed.

These states must remain distinguishable.

Different blocked states
≠
equivalent states.

---

# Revocation Boundary

Participants may revoke consent.

Revocation must remain:
- explicit;
- auditable;
- reviewable.

revocation
≠
participant failure.

revocation
≠
participant inconsistency.

Future exports must respect revocation rules.

---

# Consent Expiration Boundary

Consent may expire when an explicit expiration condition exists.

Expiration must remain:
- explicit;
- reviewable;
- auditable.

expired
≠
revoked.

expired
≠
denied.

Expiration may require:
- explicit renewal;
- participant notification;
- institutional review requirements.

silence
≠
consent renewal.

missing renewal
≠
consent renewal.

Future implementation may support consent renewal workflows.

Automatic renewal by participant inactivity must not be assumed.

---

Revocation handling may depend on:
- retention governance;
- dataset governance;
- legal obligations;
- institutional requirements.

Revocation
≠
automatic historical deletion.

Revocation
≠
permission to ignore retention obligations.

---

# Research Export Boundary

Research export eligibility depends on more than consent.

consent granted
≠
research export approved.

Research export may additionally depend on:
- consent governance;
- answer policy;
- retention policy;
- governance review;
- export scope.

---

Consent denied
≠
participant exclusion from pilot.

Research export denial
≠
participation denial.

Participation status and export eligibility must remain separate.

---

# Snapshot Integration Boundary

Snapshot inclusion must not infer consent.

included answer
≠
consent resolved.

snapshot inclusion
≠
future reuse permission.

Snapshots must preserve consent status visibility.

---

# Dataset Boundary

Research dataset eligibility is separate from research snapshot eligibility.

research export allowed
≠
dataset allowed.

snapshot inclusion
≠
dataset admission.

dataset admission
≠
future longitudinal permission.

dataset allowed
≠
future dataset reuse.

---

# Participant Transparency Boundary

Participants should be able to understand:
- whether consent exists;
- what scope it covers;
- whether consent may be revoked;
- whether export is blocked without consent.

Transparency
≠
participant burden.

---

Participant visibility
≠
internal governance disclosure.

Transparency should explain:
- participant-facing effects;
- consent implications;
- consent scope.

Transparency does not require disclosure of:
- internal implementation details;
- governance internals;
- institutional review procedures.

---

# Future Implementation Boundary

Future implementation may introduce:
- consent registry;
- consent validator;
- consent revocation workflow;
- consent renewal workflow;
- consent expiration handling;
- dataset-level consent checks;
- consent audit trail.

Future implementation
≠
automatic approval.

Unimplemented consent feature
≠
consent granted.

---

# Final Principle

Consent governance exists to protect participant autonomy and bounded research use.

Consent governance must never become:
- a hidden profiling system;
- unrestricted research authority;
- implicit permission infrastructure;
- participant scoring mechanism.

silence
≠
consent.

consent granted
≠
unrestricted future use.

consent status
≠
research approval.

