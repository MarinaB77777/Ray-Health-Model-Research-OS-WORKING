# Standard Method Data Contract

## Purpose

This document defines the data boundaries, ownership rules, lifecycle, and interpretation limits for Standard Method Data within the psychophysical research ecosystem.

The purpose of this contract is:

- preserve Standard Method domain independence;
- preserve provenance;
- prevent authority collapse;
- prevent truth-source collapse;
- support research-safe comparison;
- support future extensibility.

This document governs:

- Standard Method Data;
- Standard Method lifecycle;
- Standard Method ownership;
- comparison boundaries;
- validation boundaries;
- interpretation boundaries.

This document does NOT:

- define Health Model calculations;
- define Decision Research tasks;
- define Runtime behavior;
- define Governance authority;
- define Ground Truth;
- define medical diagnosis.

---

# Standard Method Domain

Standard Method Data is an independent research domain.

Examples may include:

- questionnaires;
- scales;
- inventories;
- psychometric instruments;
- future standardized assessment methods.

Standard Method Data remains independent from:

- Health Model Data;
- Decision Research Data;
- Runtime Data;
- Governance Data;
- Research Findings.

---

# Core Principle

Standard methods are research instruments.

Standard methods are not authority sources.

---

# Standard Method Data

Standard Method Data may include:

- method metadata;
- method version;
- task definitions;
- participant responses;
- scoring outputs;
- derived observations;
- research-safe interpretations.

The list above is illustrative, not exhaustive.

Future Standard Method outputs remain part of the Standard Method domain.

Future outputs
≠
new domain ownership.

---

# Standard Method Lifecycle

Standard Method Task
↓
Standard Method Result
↓
Standard Method Observation
↓
Standard Method Pattern

Lifecycle Boundary

Standard Method Task
≠
Standard Method Observation

Standard Method Result
≠
Standard Method Pattern

Standard Method Pattern
≠
Participant Identity

---

# Observation Boundary

Standard Method Observation
≠
Standard Method Pattern

Standard Method Observation
≠
Participant Truth

Standard Method Observation
≠
Ground Truth

Observation
≠
Pattern

Observation
≠
Conclusion

---

# Result Boundary

Standard Method Result
≠
Participant Truth

Standard Method Result
≠
Health Model State

Standard Method Result
≠
Decision Research Result

Standard Method Result
≠
Authority Source

---

# Ground Truth Boundary

Standard Method Result
≠
Ground Truth

Standard Method Observation
≠
Ground Truth

Standard Method Pattern
≠
Ground Truth

Ground Truth
≠
Method Agreement

Method Agreement
≠
Ground Truth

---

# Health Model Boundary

Standard Method Data
≠
Health Model Data

Standard Method Result
≠
Health Model State

Health Model State
≠
Standard Method Result

Standard Method Data may be compared with Health Model Data.

Comparison
≠
validation.

---

# Decision Research Boundary

Standard Method Data
≠
Decision Research Data

Standard Method Task
≠
Decision Task

Standard Method Result
≠
Decision Result

Standard Method Pattern
≠
Decision Pattern

Standard Method Data may be analyzed alongside Decision Research Data.

Joint analysis
≠
domain merge.

---

# Method Independence Boundary

One Standard Method
≠
Another Standard Method

Method A Result
≠
Method B Result

Method disagreement
≠
method failure

Method agreement
≠
method equivalence

---

# Comparison Boundary

Standard Method Data may be used for:

- comparison;
- correlation;
- validation studies;
- calibration studies.

Comparison
≠
Validation

Correlation
≠
Validation

No Correlation Found
=
Valid Outcome

No Agreement Found
=
Valid Outcome

---

# Validation Boundary

Validation Attempt
≠
Validation Success

Validation Study
≠
Validation Result

Validation Result
≠
Ground Truth

Validation Success
≠
Permanent Validation

Agreement
≠
Proof

Disagreement
≠
Refutation

Agreement between methods
≠
Validation

Disagreement between methods
≠
Model Failure

---

# Missing Data Boundary

Unknown
≠
0

No Answer
≠
Failure

Missing Standard Method Data
≠
Negative Result

Missing Standard Method Data
≠
Invalid Health Model

Missing Health Model Data
≠
Invalid Standard Method

Not Enough Data
=
Valid State

Incomplete Method Result
≠
Participant Characteristic

---

# Provenance Preservation

All Standard Method Data must preserve provenance.

The system must be able to determine:

- method identity;
- method version;
- collection context;
- session reference;
- source domain;
- scoring source.

Loss of provenance is considered architectural degradation.

---

# Authority Boundary

Standard Method Data
≠
Authority

Standard Method Result
≠
Governance Verdict

Standard Method Result
≠
Runtime Authority

Standard Method Result
≠
Action Permission

Research interpretation
≠
Authority

---

# Architectural Foundation

The architecture follows:

Standard Method Task
→ Standard Method Result
→ Standard Method Observation
→ Standard Method Pattern

The architecture does NOT follow:

Standard Method Result
→ Truth

Standard Method Result
→ Authority

Standard Method Result
→ Participant Identity

---

# Core Invariants

Source is not truth.

Analysis is not authority.

Standard methods are research instruments.

Standard methods are not authority sources.

Standard Method Result
≠
Participant Truth

Standard Method Result
≠
Ground Truth

Agreement
≠
Proof

Disagreement
≠
Refutation

Unknown
≠
0

Not Enough Data
=
Valid State