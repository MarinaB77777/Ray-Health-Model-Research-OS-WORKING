# Research Snapshot Contract

## Purpose

This document defines the bounded snapshot contract between operational pilot systems and the Research Analysis Layer.

The purpose of this contract is:
- governed research ingestion;
- bounded research exports;
- uncertainty-preserving research snapshots;
- anti-contamination separation;
- reproducible research inputs.

This document defines:
- what operational systems may expose to research;
- what research may consume;
- snapshot boundaries;
- snapshot validity semantics;
- anonymization rules;
- uncertainty propagation rules.

This document does NOT:
- define Runtime authority;
- define participant truth;
- define unrestricted analytics;
- define unrestricted historical profiling;
- define unrestricted sensor export.

---

# Core Principle

Research Layer consumes bounded research snapshots only.

Research snapshots are:
- governed;
- immutable once generated;
- uncertainty-aware;
- bounded by export policy;
- separate from Runtime state.

Research snapshots are NOT:
- live Runtime state;
- unrestricted internal memory;
- unrestricted session dumps;
- unrestricted sensor streams.

---

# Export Governance Boundary

Research snapshots must only be generated through approved export governance pathways.

Research snapshots must not originate from:
- unrestricted Runtime dumps;
- unrestricted database exports;
- unrestricted debug exports;
- unrestricted memory extraction;
- unrestricted sensor extraction.

Snapshot generation must remain:
- governed;
- policy-aware;
- consent-aware;
- export-scoped.

⸻

# Snapshot Separation

Research snapshots are separate from:
- participant exports;
- Runtime state;
- Governance state;
- operational orchestration;
- Analyzer internals;
- Inner Core;
- unrestricted sensor history.

Participant export
≠
Research snapshot.

---

# Allowed Snapshot Inputs

Research snapshots may contain:
- bounded public-safe outputs;
- uncertainty summaries;
- next-question summaries;
- bounded readiness summaries;
- bounded sensor summaries;
- validated contextual metadata;
- decision-pattern observations;
- comparison metadata for standard methods.

Research snapshots may contain:
- schema versions;
- engine versions;
- export policy versions;
- calibration metadata;
- preprocessing metadata;
- exclusion metadata.

---

# Forbidden Snapshot Inputs

Research snapshots must NOT contain:
- Inner Core information;
- unrestricted Runtime internals;
- hidden routing structures;
- unrestricted debug data;
- unrestricted chain-of-thought;
- unrestricted sensor streams;
- unrestricted dialogue history;
- unrestricted memory state;
- unrestricted governance state.

Research snapshots must not silently expose:
- hidden participant profiling;
- hidden scores;
- hidden behavioral labels;
- hidden authority classifications.

---

# Snapshot Immutability

Research snapshots are immutable once generated.

Later changes to:
- Runtime;
- Governance;
- model versions;
- participant state;
- sensor baselines;
- export policy;
- consent status

must not silently rewrite historical snapshots.

Historical snapshots may later become:
- invalidated;
- excluded;
- deprecated;
- policy-restricted.

Generated snapshot
≠
currently valid research artifact.

---

# Snapshot Validity

Research snapshots must preserve:
- export validity status;
- invalidation state;
- exclusion state;
- uncertainty level;
- readiness limitations;
- missing-data limitations.

Research systems must not silently treat:
- missing fields;
- blocked calculations;
- invalidated sessions;
- excluded participants

as valid research truth.

UNKNOWN remains valid.

NOT_ENOUGH_DATA remains valid.

---

# Retention And Revocation Boundary

Research snapshot existence does not override:
- consent withdrawal;
- exclusion requests;
- retention policies;
- governance restrictions;
- invalidation semantics.

Previously generated research snapshots may later become:
- excluded;
- deprecated;
- policy-restricted;
- retention-expired.

Historical existence
≠
permanent research authorization.

⸻

# Uncertainty Propagation

Research snapshots must preserve uncertainty.

Research export systems must not:
- remove uncertainty;
- silently normalize ambiguity;
- convert blocked states into estimates;
- replace missing data with fabricated values.

Uncertainty metadata should remain attached to:
- outputs;
- patterns;
- correlations;
- comparisons;
- decision observations.

---

# Research Identity Boundary

Research snapshots should remain:
- anonymized;
- pseudonymous;
- retention-aware;
- consent-aware.

Direct participant identity should remain outside research snapshots whenever possible.

Research systems must evaluate:
- re-identification risk;
- rare metadata combinations;
- temporal linkage risk;
- sensor-pattern uniqueness.

---

# Sensor Snapshot Boundary

Sensor snapshots are bounded research summaries.

Research snapshots must preserve:
- calibration quality;
- baseline quality;
- artifact uncertainty;
- contextual limitations;
- missing-sensor states.

Sensor disagreement with self-report is valid.

Sensor absence is valid.

Research systems must not silently resolve contradictions by invention.

---

# Standard Method Boundary

Research snapshots may contain:
- standard-method comparison summaries;
- bounded validation metadata;
- comparison uncertainty.

Research snapshots must not silently imply:
- diagnostic equivalence;
- medical authority;
- replacement of validated methods.

Correlation
≠
causation.

---

# Decision Pattern Boundary

Research snapshots may contain:
- bounded decision-pattern observations;
- contextual decision metadata;
- uncertainty-aware behavioral summaries.

Decision-pattern observations are:
- contextual;
- probabilistic;
- revisable;
- time-bound.

Decision-pattern observations are NOT:
- personality truth;
- permanent traits;
- hidden governance scores.

---

# Sandbox Boundary

Experimental research findings must remain sandboxed until validated.

Sandbox outputs:
- are not Runtime authority;
- are not participant truth;
- are not Governance authority;
- are not operational policy.

Exploratory findings must remain explicitly marked as experimental.

⸻

# Operational Non-Feedback Boundary

Research findings must not silently feed back into:
- Runtime;
- Governance;
- participant evaluation;
- operational scoring;
- decision authority;
- recommendation authority.

Research findings require:
- explicit validation;
- explicit governance approval;
- bounded operational review

before any operational usage.

Exploratory findings
≠
operational truth.

---

# Operational Event Boundary

Operational event records may exist before a research snapshot is generated.

Operational event records support:
- auditability;
- provenance preservation;
- session reconstruction;
- processing traceability.

Operational event records are NOT:
- research snapshots;
- dataset admission artifacts;
- research exports;
- participant profiles.

Incomplete collection attempts may generate operational event records.

Incomplete collection attempts must NOT automatically generate:
- research snapshots;
- dataset admission records;
- research exports.

Research snapshot generation requires explicit snapshot eligibility evaluation.

ResearchEventRecord
≠
Research Snapshot

---

# Final Principle

Research snapshots exist to support:
- bounded scientific analysis;
- uncertainty-aware validation;
- reproducibility;
- explainable research workflows.

Research snapshots must never become:
- unrestricted participant mirrors;
- hidden profiling infrastructure;
- silent authority systems;
- fabricated certainty engines.
