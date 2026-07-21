# Research Layer Separation Principles

## Purpose

This document defines the foundational separation principles for research-related layers within the psychophysical model ecosystem.

The purpose of this document is:

- preserve architectural clarity;
- preserve data provenance;
- prevent hidden authority accumulation;
- prevent truth-source collapse;
- support explainable cross-domain analysis;
- support future extensibility.

This document governs:

- research-layer boundaries;
- data-domain separation;
- cross-domain analysis rules;
- hypothesis boundaries;
- provenance preservation.

This document does NOT:

- define Health Model calculations;
- define Decision Research tasks;
- define Standard Method implementations;
- define Sensor processing;
- define Runtime behavior;
- define Governance authority.

---

# Core Principle

Data may be analyzed together.

Data must not be stored together.

---

# Domain Separation Invariant

Research domains remain separate.

Examples include:

- Health Model Data;
- Decision Research Data;
- Standard Method Data;
- Sensor Data;
- Context Data;
- Future Research Domains.

Domain separation must be preserved even when multiple domains participate in the same study.

---

# Storage Separation Invariant

Each domain stores its own data.

Domain storage must not be merged into a single truth source.

Examples:

Health Model Data
≠
Decision Research Data

Decision Research Data
≠
Standard Method Data

Sensor Data
≠
Questionnaire Data

Context Data
≠
Health State

---

# Provenance Preservation Invariant

All data must preserve origin information.

The system must be able to determine:

- where data originated;
- how data was collected;
- which domain owns the data;
- which layer produced the output.

Loss of provenance is considered architectural degradation.

---

# Analysis Integration Invariant

Analytical layers may compare domains.

Analytical layers may correlate domains.

Analytical layers may investigate relationships between domains.

Analytical layers may generate findings and hypotheses.

Analytical layers must not collapse domains into a single truth source.

---

# Hypothesis Boundary

Hypothesis
≠
Fact

Pattern
≠
Fact

Correlation
≠
Reality

Finding
≠
Truth

Analytical outputs remain analytical constructs.

Analytical outputs must not overwrite source data.

---

# Source Data Boundary

Source Data
≠
Analytical Output

Analytical Output
≠
Source Data

Analytical Output
≠
Domain Storage

Research findings must not silently replace source records.

Research findings must remain separated from collected observations.

---

# Feedback Boundary

Research outputs may reference source domains.

Research outputs must not overwrite source domains.

Research outputs must not silently modify source-domain records.

Finding generated
≠
source data updated

Hypothesis generated
≠
model updated

Pattern candidate generated
≠
domain storage updated

---

# Authority Boundary

Analysis
≠
Authority

Research Layer
≠
Governance Layer

Research Layer
≠
Runtime Authority

Research findings must not automatically authorize actions.

---

# Optional Layer Principle

Research layers are optional.

Examples:

Decision Research Layer may be absent.

Standard Method Layer may be absent.

Sensor Layer may be absent.

Context Layer may be absent.

Absence of a layer does not invalidate remaining layers.

---

# Health Model Independence

Health Model remains an independent domain.

Optional research layers may analyze Health Model outputs.

Optional research layers may reference Health Model outputs.

Optional research layers must not overwrite Health Model outputs.

Health Model remains the source of its own state calculations.

---

# Acquisition Mode Independence

The system may support multiple acquisition modes.

Examples:

- Questionnaire Mode;
- Adaptive Dialogue Mode.

Acquisition mode does not change domain ownership.

Acquisition mode does not remove provenance requirements.

Acquisition mode does not merge domains.

Core invariant:

Acquisition mode
≠
Data domain

Dialogue collection
≠
Health Model domain

Questionnaire collection
≠
Standard Method domain

---

# Architectural Foundation

The architecture follows:

Source Data
→ Domain Storage
→ Analytical Layer
→ Findings / Hypotheses

The architecture does NOT follow:

Source Data
→ Analytical Layer
→ New Truth Source

---

# Core Invariants

Source is not truth.

Unknown ≠ 0.

More data is not more authority.

Stored data ≠ reusable data.

Analysis ≠ authority.

Pattern ≠ fact.

Hypothesis ≠ reality.

Domains remain separated.

Analytical layers may compare domains.

Analytical layers may not collapse domains.

Data may be analyzed together.

Data must not be stored together.