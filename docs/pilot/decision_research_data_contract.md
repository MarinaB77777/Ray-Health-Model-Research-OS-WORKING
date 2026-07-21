# Decision Research Data Contract

## Purpose

This document defines the ownership, boundaries, lifecycle, and separation rules for Decision Research Data.

The purpose of this contract is:

- define Decision Research Data;
- define Decision Research ownership boundaries;
- preserve provenance;
- preserve separation from Health Model Data;
- prevent hidden profiling;
- prevent identity inference;
- support explainable research analysis;
- support future research extensibility.

This document governs:

- decision research data;
- decision tasks;
- decision responses;
- decision observations;
- decision hypotheses and patterns.

This document does NOT:

- define Health Model calculations;
- define Runtime behavior;
- define Governance authority;
- define personality models;
- define participant identity;
- define psychological truth.

---

# Decision Research Domain

Decision Research is an independent research domain.

Decision Research Data
≠
Health Model Data

Decision Research Data
≠
Standard Method Data

Decision Research Data
≠
Runtime Data

Decision Research Data
≠
Governance Data

Decision Research remains a separate domain.

---

# Core Principle

Decision-related information may be analyzed.

Decision-related information must preserve provenance.

Analysis
≠
authority

Observation
≠
truth

Pattern
≠
identity

---

# Decision Research Data

Decision Research Data includes:

- decision tasks;
- decision scenarios;
- decision responses;
- decision observations;
- decision context references;
- decision hypotheses;
- decision patterns.

The list above is illustrative, not exhaustive.

Future Decision Research outputs remain part of the Decision Research domain.

Future outputs
≠
new domain ownership.

---

# Decision Research Lifecycle

Decision Task
↓
Decision Response / Result
↓
Decision Observation
↓
Candidate Hypothesis
↓
Decision Pattern

These levels must remain separated.

---

# Candidate Hypothesis Boundary

Candidate Hypothesis
≠
Validated Pattern

Candidate Hypothesis
≠
Decision Pattern

Candidate Hypothesis
≠
Research Finding

Candidate Hypothesis
≠
Participant Characteristic

Candidate Hypothesis remains provisional.

Candidate Hypothesis requires validation before becoming a Decision Pattern.

---

# Decision Task Boundary

Decision Task
≠
Decision Result

Decision Task
≠
Participant State

Decision Task
≠
Personality Test

Decision Task represents a research instrument.

Task completion does not automatically generate conclusions.

---

# Decision Result Boundary

Decision Result
≠
Decision Observation

Decision Result
≠
Participant Truth

Decision Result
≠
Personality Label

Decision Result represents a recorded response to a task.

---

# Decision Observation Boundary

Decision Observation
≠
Decision Pattern

Decision Observation
≠
Identity Label

Decision Observation
≠
Psychological Truth

Observations remain observations.

Observations may support future hypotheses.

Observations do not automatically become findings.

---

# Single Observation Boundary

Single Decision Result
≠
Decision Pattern

Single Observation
≠
Decision Pattern

Single Task Result
≠
Participant Characteristic

Single Task Result
≠
Participant Identity Signal

---

# Pattern Boundary

Decision Pattern
≠
Fact

Decision Pattern
≠
Identity Label

Decision Pattern
≠
Stable Personality

Decision Pattern
≠
Future Behavior Guarantee

Decision Pattern
≠
Participant Truth

Repeated Observation
≠
Permanent Trait

Pattern persistence
≠
Pattern permanence

Patterns remain research constructs.

Patterns remain revisable.

Patterns remain uncertainty-aware.

---

# Health Model Boundary

Decision Research may analyze Health Model outputs.

Decision Research may reference Health Model state.

Decision Research must not overwrite Health Model state.

Decision Research must not own Health Model state.

Decision Research findings
≠
Health Model state.

Decision Research findings
≠
Health Model truth.

Consumption
≠
ownership transfer.

Reference
≠
ownership transfer.

---

# Analyzer Boundary

Decision Research Data
≠
Analyzer Output

Analyzer Output
≠
Decision Research Source Data

Analyzer may consume Decision Research Data.

Analyzer may analyze Decision Research Data.

Analyzer does not own Decision Research Data.

Analyzer findings
≠
Decision Research source records.

---

# Standard Method Boundary

Standard Method Data
≠
Decision Research Data

Standard Method Data may be used for:

- comparison;
- validation;
- correlation studies;
- research analysis.

Standard Method Data does not become Decision Research Data.

Decision Research Data does not become Standard Method Data.

---

# Research Method Independence

Decision Research is not tied to a specific implementation.

Examples may include:

- questionnaires;
- games;
- social scenarios;
- simulations;
- decision exercises;
- future research instruments.

Research methods may change.

Domain ownership does not change.

---

# Game Boundary

Games may be used as research acquisition instruments.

Game
≠
Participant Truth

Game Result
≠
Identity

Game Result
≠
Personality Label

Game Result
≠
Psychological Diagnosis

Game Result may contribute to observations.

Game Result does not automatically become a pattern.

---

# Missing Data Boundary

Unknown ≠ 0

Missing Data
≠
Negative Result

Missing Data
≠
Failure

Missing Data
≠
Participant Refusal

No Answer
≠
Confirmation

No Answer
≠
Pattern

No Answer
≠
Identity Signal

Not Enough Data
=
Valid State

When information is missing:

the system should request clarification;
the system should request additional acquisition;
the system should preserve uncertainty.

Missing information must not be invented.

---

# State Stability Boundary

State Unchanged
=
Valid Outcome

No Pattern Found
=
Valid Outcome

No Correlation Found
=
Valid Outcome

No Change Detected
=
Valid Outcome

Research systems must not fabricate findings.

---

# Provenance Preservation

Decision results must preserve provenance.

Examples include:

- task_id;
- task_version;
- collection_context;
- session_id;
- snapshot_reference;
- source_domain.

Loss of provenance is considered architectural degradation.

---

# Longitudinal Boundary

Repeated Decision Pattern
≠
Longitudinal Identity Model

Repeated Observation
≠
Stable Personality

Repeated Observation
≠
Participant Identity

Repeated Behavior
≠
Participant Truth

Longitudinal conclusions require separate justification.

Longitudinal conclusions must remain uncertainty-aware.

---

# Authority Boundary

Decision Research Finding
≠
Governance Verdict

Decision Research Finding
≠
Runtime Authority

Decision Research Finding
≠
Operational Permission

Research findings must not automatically authorize actions.

---

# Memory Boundary

Decision Research Data
≠
Memory State

Decision Pattern
≠
Stored Identity Fact

Research observations
≠
Personal Identity Record

Decision Research does not automatically create memory facts.

---

# Architectural Foundation

The architecture follows:

Decision Task
→ Decision Result
→ Decision Observation
→ Decision Hypothesis / Pattern

The architecture does NOT follow:

Decision Task
→ Identity Label

Decision Task
→ Personality Truth

Decision Task
→ Governance Authority

Decision Task
→ Runtime Permission

---

# Uncertainty Preservation

Uncertainty
≠
Error

Missing evidence
≠
Negative evidence

Missing evidence
≠
Pattern

Missing evidence must not be replaced by assumptions.

Uncertainty must remain visible.

Not Enough Data
=
Valid State

---

# Core Invariants

Source is not truth.

Unknown ≠ 0.

Not enough data = valid state.

State unchanged = valid outcome.

No pattern found = valid outcome.

No answer ≠ confirmation.

No answer ≠ refusal.

Observation ≠ truth.

Pattern ≠ fact.

Pattern ≠ identity.

Analysis ≠ authority.

Decision Research remains an independent domain.