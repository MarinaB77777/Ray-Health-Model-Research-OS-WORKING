# Domain Data Preparation Contract

## Purpose

This document defines the ownership, responsibilities, boundaries, preparation rules, and output requirements for Domain Data Preparation within the psychophysical research ecosystem.

The purpose of this layer is:

- prepare raw domain data for analysis;
- preserve scientific provenance;
- preserve calibration traceability;
- preserve synchronization integrity;
- preserve data quality visibility;
- support reproducible research;
- provide analysis-ready domain outputs;
- prevent preparation-analysis collapse.

This document governs:

- domain data preparation;
- preparation ownership;
- calibration boundaries;
- normalization boundaries;
- synchronization boundaries;
- prepared output requirements;
- provenance preservation;
- preparation metadata requirements.

This document does NOT:

- define scientific analysis;
- define hypotheses;
- define patterns;
- define correlations;
- define validation studies;
- define Health Model calculations;
- define Runtime authority;
- define Governance authority;
- define research conclusions.

---

# Domain Data Preparation Domain

Domain Data Preparation is an independent layer.

Domain Data Preparation
≠
Data Analysis

Domain Data Preparation
≠
Research Management

Domain Data Preparation
≠
Health Model

Domain Data Preparation
≠
Runtime

Domain Data Preparation
≠
Governance

The purpose of this layer is to prepare data for downstream analysis.

---

# Core Principle

Prepared Output
=
Analysis-Ready Data

Prepared Output
≠
Analysis Result

Prepared Output
≠
Research Finding

Prepared Output
≠
Scientific Conclusion

Prepared Output
≠
Health State

Prepared Output
≠
Readiness State

Preparation
≠
Analysis

---

# Raw Data Boundary

Raw Data
≠
Prepared Data

Raw Data remains original collected information.

Prepared Data is derived from Raw Data through governed preparation procedures.

Raw Data provenance must remain recoverable.

---

# Domain Independence Boundary

Prepared Domain Output must remain domain-owned.

Cross-domain analysis is optional.

Domain validity does not depend on cross-domain availability.

Missing linked domain
≠
Invalid Prepared Output

Sensor Prepared Output
≠
Health Model Dependency

Health Model Output
≠
Sensor Dependency

Decision Task Output
≠
Health Model Dependency

Standard Method Output
≠
Decision Research Dependency

---

# Sensor Independence

Each sensor may have:

- its own data format;
- its own calibration requirements;
- its own baseline requirements;
- its own preparation pipeline.

Sensor A
≠
Sensor B

Sensor A Calibration
≠
Sensor B Calibration

Sensor A Baseline
≠
Sensor B Baseline

Preparation pipelines may differ.

Prepared output requirements remain governed.

---

# Calibration Boundary

Calibration Data
≠
Raw Data

Calibration Data
≠
Research Finding

Calibration
≠
Truth

Calibration may be used for:

- normalization;
- baseline comparison;
- transformation;
- quality assessment.

Calibration references must remain preserved.

Calibration provenance must remain recoverable.

---

# Calibration Memory Boundary

Calibration Memory
≠
Prepared Output

Calibration Memory
≠
Research Finding

Calibration Memory
≠
Analysis Result

Preparation Memory
≠
Research Data

Preparation Memory
≠
Analysis Output

Prepared outputs may reference calibration.

Prepared outputs do not become calibration storage.

---

# Noise Cleaning Boundary

Noise Cleaning
≠
Interpretation

Noise Cleaning
≠
Analysis

Noise Cleaning
≠
Validation

Preparation may remove:

- artifacts;
- corrupted samples;
- invalid measurements;
- known noise sources.

Removed data must preserve exclusion metadata.

---

# Normalization Boundary

Normalization
≠
Analysis

Normalization
≠
Validation

Normalization
≠
Scientific Finding

Normalization may transform values relative to:

- calibration data;
- baseline data;
- instrument-specific references.

Normalization provenance must remain preserved.

Raw-unit reconstruction may remain possible through calibration and transformation metadata.

---

# Time Synchronization Boundary

Time Synchronization
≠
Correlation

Time Synchronization
≠
Causation

Prepared outputs must preserve synchronized time references.

Prepared outputs must preserve absolute time references when available.

Synchronization references must remain recoverable.

---

# Background Context Boundary

Background Context
≠
Sensor Signal

Context Reference
≠
Signal Value

Context may be synchronized with prepared outputs.

Context must not be silently merged into signal values.

Prepared outputs must preserve separation between signal and context.

---

# Prepared Domain Output Contract

Prepared Domain Output
=
Common Scientific Metadata Container
+
Domain-Specific Prepared Payload

Common Metadata
≠
Common Payload Format

Prepared outputs may use different payload structures.

Prepared outputs must preserve common scientific metadata.

---

# Prepared Payload Ownership Boundary

Domain-Specific Payload
≠
Domain Ownership Transfer

Prepared payload format does not change domain ownership.

Prepared payload normalization
≠
Domain Merge

Prepared payload standardization
≠
Ownership Transfer

---

# Common Scientific Metadata Requirements

Prepared Domain Outputs should preserve:

- source_domain;
- source_type;
- source_id / instrument_id;
- research_session_reference;
- participant_reference;
- time_reference;
- synchronization_reference;
- pipeline_version;
- calibration_reference when applicable;
- device_metadata when applicable;
- quality_metadata;
- missing_data_metadata;
- exclusion_metadata;
- provenance metadata.

Loss of provenance is considered architectural degradation.

---

# Scientific Reproducibility Boundary

Prepared outputs should preserve enough information to reproduce preparation steps.

Preparation reproducibility
≠
Result reproducibility

Reproducible preparation
≠
Scientific validation

Pipeline provenance must remain recoverable.

---

# Measurement Device Metadata

Measurement devices may preserve:

- device_type;
- manufacturer;
- model;
- hardware version;
- firmware version;
- sampling rate;
- measurement resolution;
- measurement range;
- measurement unit;
- known limitations.

Measurement Device
≠
Measurement Result

Device Quality
≠
Data Quality

Device Specification
≠
Measurement Validity

---

# Quality Boundary

Prepared outputs must preserve quality visibility.

Quality metadata may include:

- quality flags;
- confidence indicators;
- missing samples;
- signal artifacts;
- quality exclusions;
- preparation warnings.

Quality metadata must remain visible to downstream analysis.

---

# Missing Data Boundary

Unknown
≠
0

Missing Data
≠
Negative Result

Missing Data
≠
Failure

Not Enough Data
=
Valid State

Prepared outputs should preserve missing-data reasons.

Examples include:

- sensor unavailable;
- participant skipped response;
- corrupted data;
- rejected by quality filter;
- not collected.

Missing information must not be invented.

---

# Exclusion Metadata Boundary

Excluded Data
≠
Nonexistent Data

Prepared outputs should preserve exclusion reasons.

Examples include:

- artifact removal;
- quality rejection;
- manual exclusion;
- preprocessing exclusion.

Exclusion provenance must remain recoverable.

---

# Human Intervention Boundary

Human Intervention
≠
Automatic Processing

Manual Correction
≠
Ground Truth

Human Intervention
≠
Validation

Human intervention metadata must remain visible.

Prepared outputs should preserve intervention visibility.

Examples include:

- fully automatic;
- semi-automatic;
- manually corrected.

Human intervention metadata supports reproducibility.

---

# Coverage Boundary

Prepared outputs should preserve preparation coverage.

Examples include:

- raw samples;
- valid samples;
- excluded samples;
- retained samples.

Coverage metadata supports downstream quality assessment.

---

# Analyzer Boundary

Prepared Output
≠
Analysis Result

Prepared Output
≠
Observation

Prepared Output
≠
Hypothesis

Prepared Output
≠
Pattern

Prepared Output
≠
Validation Result

Prepared outputs are inputs to analysis.

Prepared outputs are not analytical outputs.

---

# Research Boundary

Prepared Output
≠
Research Finding

Prepared Output
≠
Research Conclusion

Prepared Output
≠
Publication Result

Prepared Output
≠
Scientific Validation

Preparation Pipeline
≠
Scientific Method

Prepared Data
≠
Validated Data

---

# Authority Boundary

Preparation
≠
Authority

Prepared Output
≠
Permission

Prepared Output
≠
Governance Verdict

Prepared Output
≠
Runtime Authority

Prepared Output does not authorize actions.

---

# Architectural Foundation

The architecture follows:

Raw Data
↓
Domain Preparation
↓
Prepared Domain Output
↓
Data Analysis
↓
Research Management

The architecture does NOT follow:

Raw Data
↓
Scientific Finding

Preparation
↓
Research Truth

Preparation
↓
Authority

---

# Core Invariants

Preparation ≠ Analysis.

Raw Data ≠ Prepared Data.

Prepared Output = Analysis-Ready Data.

Prepared Output ≠ Analysis Result.

Prepared Output ≠ Research Finding.

Prepared Output ≠ Scientific Conclusion.

Prepared Output ≠ Health State.

Prepared Output ≠ Readiness State.

Calibration ≠ Truth.

Normalization ≠ Validation.

Synchronization ≠ Correlation.

Correlation ≠ Causation.

Device Quality ≠ Data Quality.

Prepared Data ≠ Validated Data.

Cross-domain analysis is optional.

Domain validity does not depend on cross-domain availability.

Reproducibility requires provenance.

Loss of provenance = Architectural degradation.