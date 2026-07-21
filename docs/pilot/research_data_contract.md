# Research Data Contract

## Purpose

This document defines:
- research data boundaries;
- participant/session data handling;
- research export rules;
- retention boundaries;
- uncertainty preservation rules;
- bounded research interpretation principles.

The purpose of this contract is:
- research-safe data handling;
- anti-profiling protection;
- anti-hidden-authority protection;
- explainable research governance;
- bounded operational storage.

This document governs:
- pilot research data;
- participant/session records;
- operational readiness outputs;
- bounded research exports.

This document does NOT:
- define medical records;
- define psychiatric truth;
- authorize unrestricted profiling;
- authorize unrestricted retention;
- authorize unrestricted behavioral inference.

---

# Core Principles

## Constitutional Principles

Research data handling preserves:
- uncertainty visibility;
- bounded interpretation;
- participant autonomy;
- operational explainability;
- anti-fabrication behavior.

Core invariants:
- Unknown ≠ 0
- NOT_ENOUGH_DATA = valid state
- contradiction ≠ invalid participant
- operational assessment ≠ diagnosis
- operational output ≠ psychological truth
- research usefulness ≠ retention justification
- potential future usefulness ≠ automatic retention justification
- research participant ≠ research object owned by the system
- access ≠ permission
- visibility ≠ authority
- institutional usefulness ≠ permission expansion

---

## Research Scope Principle

Pilot research data exists only within:
- approved pilot scope;
- approved participant consent boundaries;
- bounded operational interpretation scope.

Research expansion requires:
- explicit review;
- explicit approval;
- explicit governance update.

Research pressure must not override participant boundaries.

---

# Participant Data Model

## Participant Identity

Participants receive:
- participant_id
- pilot-scoped session linkage identifier

For longitudinal trajectory analysis, the system may also use:

- subject_link_id

subject_link_id is a consent-bound pseudonymous linkage identifier
used only to determine that multiple sessions belong to the same participant
within an approved longitudinal research or personal-account context.

subject_link_id does NOT represent:
- legal identity;
- real-world identity;
- psychological identity;
- unrestricted behavioral identity;
- permission for hidden profiling.

subject_link_id may be used only when:
- the participant has an active consent/agreement for longitudinal tracking;
- the linkage purpose is explicit;
- the linkage scope is bounded;
- the linkage can be reviewed, revoked, or governed according to retention rules.

The pilot should minimize:
- personally identifying information;
- unnecessary identity linkage;
- unrestricted identity persistence.

Participant identifiers, including subject_link_id,
must not silently become cross-context behavioral identity infrastructure.

Longitudinal linkage is allowed only as an explicit,
consent-bound, scope-limited trajectory analysis mechanism.

---

## Participant Identity Boundaries

The pilot must NOT:
- reconstruct hidden identity;
- infer psychological identity;
- generate covert participant profiles;
- synthesize hidden participant traits.

Participant operational profile
≠ participant identity

---

# Session Data Model

## Session Structure

Each session may contain:
- session_id
- timestamps
- questionnaire answers
- readiness outputs
- uncertainty states
- warnings
- clarification requests
- next_questions
- acquisition requests
- clarification statistics
- bounded operational recommendations

Timestamp granularity
must remain limited
to operational and approved research necessity.

Each session may also contain:
- subject_link_id when longitudinal tracking is explicitly consented;
- study_id;
- participant_role;
- synchronization_reference;
- global_time_utc event timestamps.

synchronization_reference links events collected within the same synchronized session or collection window.

synchronization_reference does NOT imply causation, correlation, or participant identity expansion.

Questionnaire completeness
≠ participant reliability

---

## Session State and Event History Boundary

Session stores the current operational state of an interaction.

Session may include:
- session_id;
- participant_id;
- subject_link_id when consented;
- study_id;
- synchronization_reference;
- created_at;
- updated_at;
- closed_at;
- current status;
- current knowledge snapshot;
- current block;
- turn summaries.

ResearchEventRecord stores immutable event history.

Each event records:
- what happened;
- when it happened on the global UTC time axis;
- what input was received;
- what was extracted;
- what the knowledge/status/output snapshots were at that moment;
- which model, logic, and extraction versions produced the result.

Session
≠
Event History

Session is current state.
Event History is reproducible record.

Session may be reconstructed from events.
Events must not be rewritten to match later session state.

Corrections, recalculations, or reinterpretations must create new events or derived records,
not silently overwrite historical events.

---

## Session Boundaries

Session data represents:
- bounded operational interaction;
- readiness-oriented interpretation;
- uncertainty-aware processing.

Session data does NOT represent:
- complete participant identity;
- permanent psychological truth;
- unrestricted behavioral understanding.

---

# Questionnaire Data

## Questionnaire Handling

Questionnaire responses may include:
- contextual information;
- operational load indicators;
- readiness-related answers;
- uncertainty-relevant gaps.

Questionnaire uncertainty remains valid.

Participant uncertainty
≠ invalid participation

---

## Questionnaire Restrictions

Questionnaire responses must NOT be transformed into:
- hidden psychological diagnosis;
- covert personality scoring;
- unrestricted participant classification;
- deterministic future interpretation.

---

# Clarification Data

## Clarification Purpose

Clarification exists to:
- reduce operational uncertainty;
- resolve important ambiguity;
- improve readiness interpretation quality.

Clarification does NOT exist to:
- pressure coherence;
- force completion;
- interrogate participants;
- extract hidden identity.

---

## Clarification Boundaries

Participant refusal to answer clarification requests is valid.

Missing clarification must preserve uncertainty,
not force inferred interpretation.

Clarification pressure
≠ improved research quality

Clarification refusal
≠ participant non-cooperation

Clarification frequency,
delay,
or refusal
must not silently become:
- participant quality scoring;
- participant compliance scoring;
- participant reliability scoring;
- participant cooperativeness scoring.

---

# Readiness Output Handling

## Readiness Output Purpose

Readiness outputs are:
- operational estimates;
- uncertainty-aware interpretations;
- bounded research-oriented outputs.

Readiness outputs are NOT:
- psychiatric truth;
- medical diagnosis;
- hidden participant identity;
- definitive psychological interpretation.

Recommendation
≠ obligation

Participant non-compliance
≠ participant failure

Operational recommendation
≠ behavioral authority

---

## Output Uncertainty Preservation

Research handling must preserve:
- uncertainty visibility;
- contradiction visibility;
- incomplete-data visibility;
- forecast limitations.

Blocked forecast
≠ system failure

Forecast uncertainty
must remain visible
in exported research artifacts.

---

# Forecast Data Boundaries

## Forecast Governance

Forecasts may exist only when:
- uncertainty acceptable;
- coverage sufficient;
- consistency acceptable;
- no critical forecast block present.

Forecasts remain:
- probabilistic;
- bounded;
- uncertainty-aware.

Forecast
≠ deterministic human prediction

Forecast
≠ participant future determination

---

# Human Profiles

## Operational Profiles

Operational Human Profiles may support:
- contextual routing;
- clarification prioritization;
- operational interaction adaptation.

Profile use must remain uncertainty-aware.

Profiles remain:
- revisable;
- probabilistic;
- uncertainty-aware;
- bounded operational heuristics.

Operational profile
must remain:
- task-scoped;
- revisable;
- non-identity-forming.

Profiles must NOT silently evolve into:
- longitudinal identity models;
- covert participant classification systems;
- hidden behavioral continuity models.

Operational adaptation
must not silently become:
- behavioral steering;
- psychological optimization;
- covert behavioral shaping.

Profiles are NOT:
- psychological identities;
- deterministic participant classifications;
- permanent participant labels.

---

# Research Export

## Export Scope

Research exports may include:
- anonymized participant_id;
- session_id;
- timestamps;
- questionnaire responses;
- readiness outputs;
- uncertainty states;
- warnings;
- clarification statistics;
- bounded operational metadata.

---

## Export Restrictions

Research exports must NOT include:
- Inner Core data;
- unrestricted dialogue history;
- unrestricted memory;
- hidden profile reconstruction;
- unrestricted behavioral inference;
- covert identity synthesis.

Research exports must NOT enable:
- cross-session hidden identity stitching;
- covert longitudinal participant reconstruction;
- hidden behavioral continuity inference.

---

## Export Governance

Research export must preserve:
- participant consent boundaries;
- uncertainty visibility;
- bounded interpretation semantics;
- operational context limitations.

Research export
≠ unrestricted truth export

Exported data
≠ unrestricted reuse permission

Research usefulness
≠ justification for deeper extraction

---

# Retention Principles

## Retention Boundaries

Research data retention must remain:
- bounded;
- purpose-limited;
- reviewable;
- consent-aware.

Retention duration
must remain bounded by:
- approved research scope;
- institutional requirements;
- operational necessity.

---

## Retention Restrictions

Persistent storage must NOT silently become:
- hidden participant surveillance;
- unrestricted profiling archive;
- permanent behavioral authority system.

Memory persistence
≠ retention justification

---

# Research Interpretation Boundaries

## Interpretation Principles

Research interpretation must remain:
- probabilistic;
- uncertainty-aware;
- operationally bounded;
- non-deterministic.

Operational interpretation
≠ clinical truth

Operational interpretation
≠ identity determination

---

## Contradiction Handling

Contradictions remain:
- legitimate;
- uncertainty-relevant;
- operationally meaningful.

Contradiction
≠ deception

Contradiction
≠ participant invalidity

---

# Future-Compatible Extensions

## Future-Compatible Sources

The pilot architecture may later support:
- sensor integrations;
- calibration games;
- bounded external devices;
- additional acquisition sources.

Future integrations must remain:
- governed;
- bounded;
- uncertainty-aware;
- consent-aware.

Additional acquisition capability
≠ increased authority

Additional sensors
≠ unrestricted participant visibility

---

## Extension Restrictions

Future integrations must NOT silently introduce:
- unrestricted surveillance;
- hidden profiling;
- covert authority escalation;
- unrestricted adaptive interpretation.

Capability
≠ permission

Inference
≠ authority

---

# Session Closure

## Closure Boundaries

Closed sessions remain:
- bounded historical operational records;
- uncertainty-aware research artifacts.

Closed session
≠ permanent participant truth

Closed session
≠ unrestricted future authority

---

# Pilot Research Position

The university pilot operates as:

bounded uncertainty-aware operational readiness research system

with:
- explainable outputs;
- governed interaction;
- bounded operational interpretation;
- anti-fabrication principles;
- uncertainty visibility.

The pilot is NOT:
- hidden diagnostic infrastructure;
- covert psychological profiling system;
- unrestricted adaptive surveillance architecture;
- autonomous behavioral authority engine.
