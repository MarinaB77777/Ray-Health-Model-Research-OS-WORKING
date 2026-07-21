# Research Analysis Layer Contract

## Purpose

This document defines the bounded architecture and governance rules for the Research Analysis Layer used in the university pilot.

The purpose of this layer is:
- scientific analysis;
- hypothesis validation;
- psychophysical pattern research;
- decision-pattern research;
- comparison against standard methods;
- uncertainty-aware model validation.

This layer exists to support:
- scientific rigor;
- bounded research;
- explainable analysis;
- reproducibility;
- anti-fabrication principles.

This layer does NOT:
- define personal truth;
- define diagnosis;
- define hidden profiling authority;
- replace participant autonomy;
- replace clinical evaluation;
- replace Runtime/Governance/Analyzer layers.

---

# Core Principle

Research Analysis Layer is:

- optional;
- pluggable;
- governed;
- uncertainty-aware;
- scientifically bounded;
- separated from Pilot Session lifecycle.

Research Layer must not contaminate:
- Pilot Session;
- Runtime;
- participant-facing outputs;
- Governance authority;
- operational state machine.

---

# Architectural Separation

Research Layer is separated from:

Pilot Session
Runtime
Governance
Analyzer
Sensor Layer
Decision Support Layer

Research Layer consumes governed research snapshots only.

Research Layer does NOT directly operate on:
- live Runtime state;
- raw participant lifecycle state;
- unrestricted internal memory;
- Inner Core;
- unrestricted sensor streams.

---

# Research Inputs

Research Layer may receive:

- participant-safe research snapshots;
- anonymized session exports;
- uncertainty-aware outputs;
- bounded sensor snapshots;
- standard-method results;
- decision-pattern observations;
- validated contextual metadata.

Research Layer inputs must remain governed.

---

# Unknown And Insufficient States

The following are valid research outcomes:

- UNKNOWN
- NOT_ENOUGH_DATA
- NOT_CALCULATED
- FORECAST_BLOCKED
- HIGH_UNCERTAINTY
- INSUFFICIENT_READINESS

Research Layer must never fabricate conclusions from missing data.

Absence of evidence is NOT evidence.

Missing information must not silently become:
- inferred personality;
- inferred diagnosis;
- inferred intent;
- inferred stability;
- inferred behavioral truth.

---

# Correlation Boundary

Research correlations do NOT automatically imply:
- causation;
- psychological mechanism;
- behavioral inevitability;
- stable personal traits.

Observed associations may be:
- contextual;
- temporary;
- indirect;
- confounded;
- non-generalizable.

Research Layer must preserve:
- causal uncertainty;
- alternative explanations;
- model limitations.

---

# Pattern Discovery

Pattern discovery is allowed.

Pattern discovery must remain:
- governed;
- uncertainty-aware;
- evidence-based;
- revisable;
- context-aware.

Patterns are:
- hypotheses;
- probabilistic observations;
- bounded research findings.

Patterns are NOT:
- immutable truth;
- identity labels;
- hidden psychological profiles.

Research Layer must support:
- failed hypotheses;
- conflicting evidence;
- uncertainty propagation;
- negative results;
- revalidation.

---

# Temporal Stability Boundary

Research observations are time-bound.

Patterns may:
- weaken;
- disappear;
- reverse;
- become context-specific.

Historical observations must not automatically define current participant state.

Past observations must not silently become:
- stable identity assumptions;
- permanent behavioral labels;
- irreversible classifications.

---

# Generalization Boundary

Research findings must not automatically generalize:
- across populations;
- across cultures;
- across professions;
- across neurotypes;
- across environments.

Generalization requires:
- explicit validation;
- uncertainty analysis;
- population/context review;
- reproducibility review.

Small-sample observations must remain explicitly bounded.

---

# Decision Pattern Research

Research Layer may analyze:
- decision behavior;
- overload decisions;
- fatigue-related decisions;
- uncertainty handling;
- conflict behavior;
- avoidance patterns;
- impulsive decisions;
- delayed decisions;
- decision inconsistency.

Decision patterns are:
- research objects;
- contextual observations.

Decision patterns are NOT:
- personality labels;
- authority classifications;
- autonomous governance decisions.

Research Layer must preserve:
- context;
- uncertainty;
- evidence quality;
- limitations;
- temporal boundaries.

---

# Anti-Manipulation Boundary

Decision-pattern research must not be used for:
- covert behavioral steering;
- hidden optimization of participant choices;
- psychological pressure strategies;
- autonomy erosion;
- silent recommendation shaping.

Research exists for:
- understanding;
- validation;
- bounded scientific analysis.

Research does NOT exist for covert influence.

---

# Standard Method Comparison

Research Layer may compare model outputs against:
- validated questionnaires;
- validated psychometric scales;
- workload scales;
- stress scales;
- fatigue scales;
- decision-making assessments;
- cognitive-load methods.

Comparison exists for:
- validation;
- calibration;
- scientific analysis;
- divergence analysis;
- predictive usefulness evaluation.

Comparison does NOT imply:
- replacement of validated methods;
- clinical equivalence;
- medical authority.

Research Layer must support:
- weak correlation;
- failed correlation;
- contradictory findings;
- model limitations.

Negative results are valid scientific outcomes.

---

# Sensor Integration

Sensor systems are separate pluggable modules.

Research Layer may consume:
- governed sensor snapshots;
- bounded sensor summaries;
- validated baseline comparisons;
- contextual sensor interpretations.

Research Layer must NOT:
- assume sensor truth automatically;
- ignore calibration quality;
- ignore context;
- ignore artifacts.

Sensor interpretation must remain:
- uncertainty-aware;
- baseline-aware;
- context-aware;
- individually calibrated when possible.

Lack of sensor data is valid.

Sensor disagreement with self-report is valid.

Research Layer must not silently resolve contradictions by invention.

---

# Research Sandbox Boundary

Experimental hypotheses may exist inside bounded research sandboxes.

Sandbox findings:
- are not operational truth;
- are not Runtime authority;
- are not participant truth;
- are not Governance authority;
- require validation before broader research usage.

Exploratory observations must remain explicitly marked as experimental.

---

# Research Export Boundaries

Research exports must remain:
- anonymized or pseudonymous;
- governed;
- retention-aware;
- consent-aware;
- uncertainty-preserving.

Invalidated sessions must not silently enter research aggregation.

Research exports must contain:
- schema versions;
- engine versions;
- export policy versions;
- uncertainty metadata;
- evidence limitations.

Research exports must not expose:
- unrestricted internal state;
- raw Runtime internals;
- Inner Core information;
- hidden routing/debug structures.

---

# Re-identification Risk Boundary

Research exports must minimize re-identification risk.

Rare combinations of:
- timestamps;
- professions;
- contextual metadata;
- sensor signatures;
- behavioral sequences;
- unusual event patterns

must be evaluated before export.

Pseudonymous exports may still carry re-identification risk.

Research governance must treat re-identification risk as a valid uncertainty and safety concern.

---

# Reproducibility And Research Metadata

Research exports should preserve:
- calculation versions;
- preprocessing versions;
- exclusion rules;
- calibration state;
- uncertainty assumptions;
- missing-data handling strategy;
- schema versions;
- export policy versions.

Research findings should remain reproducible when possible.

---

# Consent And Governance

Research participation must remain consent-aware.

Research Layer must support:
- consent versioning;
- consent withdrawal;
- exclusion from aggregation;
- retention governance;
- anonymization policies.

Research analysis authority is bounded.

Research findings must not silently become:
- Runtime authority;
- Governance authority;
- participant truth;
- medical conclusions.

---

# Decision Support Boundary

Research findings may inform Decision Support.

Research findings must not automatically become:
- autonomous decisions;
- hidden recommendations;
- participant authority overrides.

Decision Support remains separate from:
- Research Layer;
- Runtime;
- Governance;
- participant identity.

---

# Final Principle

Research Analysis Layer exists to support:
- scientific rigor;
- uncertainty-aware analysis;
- bounded psychophysical research;
- explainable model validation.

Research Analysis Layer must never become:
- hidden profiling infrastructure;
- autonomous authority;
- silent behavioral scoring system;
- fabricated certainty engine.

