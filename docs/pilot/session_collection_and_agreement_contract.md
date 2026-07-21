# Session Collection and Agreement Contract

Policy document version: session-collection-contract-1

## Purpose

This document defines collection-session governance rules for the university pilot.

The purpose of this contract is:

- define agreement-before-collection requirements;
- define session creation boundaries;
- define collection lifecycle rules;
- define persistence requirements;
- define minimum analyzable threshold requirements;
- define incomplete-attempt handling;
- preserve auditability;
- preserve future compatibility.

This document governs:

- collection session initiation;
- agreement gating;
- session persistence;
- incomplete collection attempts;
- analyzable session creation;
- collection lifecycle boundaries.

This document does NOT:

- define retention governance;
- define export approval;
- define dataset admission;
- define research interpretation;
- define participant identity authority;
- define research correctness.

---

# Core Principle

Collection requires agreement acceptance.

No agreement
=
No collection.

Agreement acceptance
=
permission to start collection.

Agreement acceptance
≠
guarantee of session persistence.

---

# Session-Level Agreement

Every collection session must present the current agreement before collection begins.

Agreement acceptance must occur before:

- answer collection;
- sensor collection;
- diagnostic collection;
- standard method collection;
- acquisition requests.

Declined agreement
=
collection blocked.

Declined agreement
=
no new session.

Declined agreement
=
no new data.

---

# Session Independence

Each collection session is independent.

New session
=
new agreement record.

New session
=
new signed_at timestamp.

New session
=
new collected data.

New session
≠
overwrite previous session.

Previous valid sessions remain unchanged.

---

# Single-Pass Collection

Pilot v1 uses single-pass collection.

Pilot v1 does not support:

- draft sessions;
- save and continue later;
- session resume;
- partial collection restoration.

No Resume
=
Pilot v1 rule.

No Continue Later
=
Pilot v1 rule.

---

# Minimum Analyzable Threshold

Collection attempts must reach a minimum analyzable threshold before persistence.

Agreement acceptance alone does not create a persisted research session.

Collection data must be sufficient for analysis.

Minimum analyzable threshold determination is implementation-specific.

Implementation-specific
≠
arbitrary.

Threshold determination must remain documented and reviewable.

---

# Incomplete Attempt Boundary

Incomplete attempt
≠
research session.

Incomplete attempt
≠
research snapshot.

Incomplete attempt
≠
dataset admission candidate.

Incomplete attempt
≠
exportable artifact.

If the participant exits before reaching the minimum analyzable threshold:

- the attempt is discarded;
- no analyzable session is created;
- no snapshot is created;
- no dataset admission is allowed.

---

# Previously Accepted Sessions

Failure to start a new session does not invalidate previous valid sessions.

Declined new agreement
≠
invalidation of previous sessions.

Missing new agreement
≠
invalidation of previous sessions.

Previous valid session data remains usable within the originally agreed scope.

---

# Collection Mode Boundary

Pilot v1 applies the same collection lifecycle rule to:

- questionnaires;
- sensor collection;
- diagnostic games;
- standard methods;
- mixed collection modes.

All collection modes follow:

single-pass collection

and

no resume.

---

# Existing MVP Compatibility Boundary

Current MVP implementation may create sessions before agreement gating exists.

Current MVP behavior
≠
final collection governance architecture.

Current MVP implementation behavior
must not be interpreted as governance approval.

Future implementation may move session creation behind agreement validation.

---

# Future Compatibility Boundary

Future versions may introduce:

- resumable collection;
- draft collection;
- staged collection workflows;
- collection-mode-specific lifecycle rules.

Future capability
≠
Pilot v1 behavior.

Pilot v1 remains:

single-pass collection only.

---

# Final Principle

Agreement governs collection permission.

Collection permission
≠
session persistence.

Session persistence
requires
minimum analyzable data.

Collected data
≠
research-ready data.

Agreement accepted
≠
research-ready session.

Pilot v1 prioritizes:

- simplicity;
- auditability;
- bounded collection;
- reproducibility;
- governance clarity.