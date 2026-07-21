# Bounded Answer Export Policy

## Purpose

Policy document version: bounded-answer-export-policy-1

This document defines semantic governance rules for exporting questionnaire answers into research snapshots and research datasets.

The purpose of this policy is:
- bounded answer export;
- variable-level export classification;
- anti-profiling protection;
- retention-aware answer handling;
- consent-aware research data governance;
- uncertainty-preserving answer semantics.

This document governs:
- questionnaire answer export decisions;
- answer-level research admissibility;
- bounded answer retention semantics;
- answer linkage boundaries.

This document does NOT:
- define participant identity;
- define diagnosis;
- define scoring;
- define research analytics;
- define participant modeling;
- authorize unrestricted answer retention.

---

# Core Principle

Answer variables are research data candidates.

Answer variables are NOT:
- participant identity;
- participant truth;
- hidden personality labels;
- unrestricted behavioral profiles.

Answer variable
≠
participant identity.

Answer sensitivity
≠
participant sensitivity.

Research usefulness
≠
export permission.

---

# Answer Policy Categories

Each answer variable should have an explicit export classification.

Allowed policy categories:

- exportable
- aggregate_only
- requires_additional_consent
- transient_only
- not_exportable
- not_yet_classified

These categories define export admissibility.

They do NOT define:
- participant value;
- participant reliability;
- participant quality;
- psychological identity.

---

# Default Deny Rule

Unknown answer policy defaults to not exportable.

If an answer variable has no explicit classification, it must not enter:
- research snapshot;
- research export;
- research dataset;
- aggregation pipeline.

not_yet_classified
≠
exportable.

Unknown answer policy
=
not exportable by default.

---

# Variable-Level Classification

Answer export policy applies at variable level.

Variable-level classification should define:
- variable_code;
- export category;
- allowed export scope;
- retention sensitivity;
- consent requirements;
- linkage limitations;
- aggregation limitations.

Variable classification
≠
participant classification.

Sensitive variable
≠
sensitive participant.

---

# Exportable Semantics

Exportable answers may enter bounded research snapshots when:
- the variable is explicitly classified as exportable;
- participant consent allows it;
- retention policy allows it;
- export governance allows it;
- uncertainty semantics remain preserved.

exportable
≠
unrestricted retention.

exportable
≠
longitudinal permission.

exportable
≠
unrestricted reuse.

---

# Aggregate-Only Semantics

Aggregate-only answers must not appear as individual-level research snapshot fields.

Aggregate-only answers may be used only when:
- aggregation governance allows it;
- cohort size and re-identification risk are acceptable;
- individual-level reconstruction is prevented;
- consent permits aggregate use.

aggregate_only
≠
individual export.

aggregate_only
≠
longitudinal individual linkage.

aggregate_only
≠
covert participant profiling.

---

# Additional Consent Semantics

Some answers may require additional consent before export.

Additional consent may be required when answers involve:
- sensitive context;
- high re-identification risk;
- longitudinal linkage risk;
- sensitive behavioral or physiological meaning;
- external research sharing;
- future reuse beyond original pilot scope.

requires_additional_consent
≠
exportable by default.

Additional consent
≠
broad future consent.

Consent
≠
unlimited future use.

---

# Transient-Only Semantics

Transient-only answers may be used during operational processing but must not be stored in research snapshots or research datasets.

Transient-only answers may support:
- immediate model calculation;
- immediate clarification;
- temporary operational routing.

Transient-only answers must not become:
- persistent research data;
- hidden memory;
- longitudinal evidence;
- participant profile material.

transient_only
≠
snapshot storage.

transient_only
≠
research retention.

---

# Not Exportable Semantics

Not-exportable answers must not enter research snapshots, research exports, or research datasets.

Not-exportable answers may exist only within their approved operational context.

not_exportable
≠
hidden discard without trace.

Systems may record that a variable was excluded by policy without exporting its value.

Not-exportable values must not be reconstructed through:
- derived fields;
- hidden summaries;
- indirect identifiers;
- debug traces.

---

# Unknown / Not Yet Classified Semantics

Not-yet-classified answers are blocked from export.

They may later become classified only through explicit policy review.

not_yet_classified
≠
temporary export permission.

not_yet_classified
≠
safe default.

Classification absence
≠
low sensitivity.

---

# Longitudinal Linkage Boundary

Answer export permission does not automatically allow longitudinal linkage.

Longitudinal linkage requires:
- explicit permission;
- explicit scope;
- explicit retention boundary;
- re-identification risk review;
- aggregation governance review.

exportable
≠
longitudinally linkable.

pseudonymous linkage
≠
unrestricted longitudinal tracking.

---

# Research Snapshot Integration Boundary

Research snapshots must include answer values only when answer policy explicitly allows it.

Research snapshot builder must not silently include:
- unrestricted answers;
- unclassified answers;
- transient-only answers;
- not-exportable answers;
- aggregate-only answers at individual level.

Answer exclusion should preserve:
- policy traceability;
- uncertainty visibility;
- missing-data visibility.

Answer exclusion
≠
model failure.

No answer export
≠
no research value.

---

# Sensitive / High-Risk Answers

High-risk answers include variables that may reveal:
- identity;
- rare context;
- sensitive behavioral patterns;
- health-related interpretation;
- social vulnerability;
- financial vulnerability;
- spiritual or values-related vulnerability;
- decision vulnerability;
- physiological or sensor-linked sensitivity.

High-risk answer handling must remain:
- consent-aware;
- retention-aware;
- re-identification-aware;
- aggregation-aware.

High-risk variable
≠
high-risk participant.

---

# Prohibited Uses

Answer export policy must not be used for:
- participant scoring;
- compliance scoring;
- hidden reliability scoring;
- hidden personality inference;
- covert behavioral profiling;
- unrestricted longitudinal modeling.

Answer policy
≠
participant model.

Answer category
≠
participant category.

---

# Policy Object Shape

Answer policy records should include:

- variable_code;
- policy_category;
- allowed_export_scope;
- requires_consent;
- consent_scope;
- retention_class;
- linkage_allowed;
- aggregation_allowed;
- individual_snapshot_allowed;
- dataset_allowed;
- policy_version;
- review_status;
- rationale.

Policy object
≠
consent record.

Answer policy classification
≠
permission to collect answer.

Answer export permission
≠
model input permission.

---

# Policy Versioning And Revision

Answer export policy must remain versioned.

Policy changes must be:
- explicit;
- reviewable;
- documented;
- non-silent.

answer_policy_version must be preserved when policy decisions affect exports.

Policy change
≠
retroactive export permission.

Previously exported answer
≠
currently valid retention.

Classification may be revised.

Classification revision
≠
participant inconsistency.

---

# Precedence Rules

When multiple classifications or risks apply, the most restrictive applicable category wins.

Mixed or compound variables should inherit the most restrictive category among their components.

High-risk status overrides ordinary exportability unless explicit review allows bounded export.

Most restrictive category wins
≠
data loss.

Variable ambiguity
≠
permission to export.

---

# Derived Field Boundary

Derived values must not be used to bypass answer export restrictions.

Derived value
≠
safe substitute for blocked answer.

Model-calculated feature
≠
original answer export permission.

Blocked answers must not leak through:
- derived fields;
- public reasons;
- warnings;
- summaries;
- domain summaries;
- debug traces;
- aggregate labels.

---

# Answer Presence / Absence Boundary

Answer value and answer presence metadata are separate.

Presence, absence, refusal, delay, or skip metadata may itself be sensitive.

Skip/refusal metadata
≠
participant non-cooperation.

Missing answer metadata
≠
participant unreliability.

Presence metadata export requires explicit policy classification.

---

# Free-Text Answer Boundary

Free-text answers are high-risk by default.

Free-text answers are not_exportable by default unless an explicit reviewed policy says otherwise.

Free-text answer
≠
ordinary structured answer.

Free-text usefulness
≠
export permission.

Free-text content must not silently enter research snapshots, summaries, or datasets.

---

# Safety-Critical Answer Boundary

Some answers may be required for immediate safety or Runtime handling.

Safety-critical answer
≠
research-exportable answer.

Operational safety use
≠
research export permission.

Safety-critical variables default to:
- transient-only;
or
- not_exportable;

unless an explicit reviewed policy says otherwise.

# Snapshot Versus Dataset Boundary

Answer policy must distinguish:
- research snapshot eligibility;
- research dataset eligibility;
- aggregate-only dataset eligibility;
- longitudinal linkage eligibility.

Snapshot eligibility
≠
dataset eligibility.

Dataset eligibility
≠
longitudinal linkage permission.

Aggregate-only
≠
small cohort export.

Small cohort export requires re-identification review.

---

# Consent Separation

Answer policy does not replace participant consent.

Consent must remain:
- explicit where required;
- scoped;
- versioned;
- revocable;
- purpose-limited.

Additional consent
≠
consent by silence.

Consent granted
≠
unrestricted future use.

---

# Audit Semantics

Answer export decisions should preserve auditability.

Systems should record:
- why an answer was exported;
- why an answer was excluded;
- policy version used;
- consent basis if applicable;
- retention class;
- linkage restriction.

Export auditability
≠
surveillance authority.

Answer exclusion
≠
answer deletion.

Export exclusion trace
≠
export of the answer value.

---

# Operational Runtime Boundary

Operational Runtime may temporarily use answers that are not exportable.

Operational necessity
≠
research export permission.

Collection permission
≠
storage permission.

Storage permission
≠
export permission.

Export permission
≠
future reuse permission.

Runtime processing
≠
research admissibility.

Answers required for:
- safety;
- clarification;
- temporary routing;
- operational state handling;
may still remain:
- transient-only;
- not-exportable;
- excluded from datasets.

---

# Collection / Storage / Export Separation

Answer governance must separate:
- collection permission;
- operational use permission;
- storage permission;
- export permission;
- reuse permission;
- linkage permission.

Permission in one layer does not automatically authorize another layer.

Allowed collection
≠
allowed retention.

Allowed retention
≠
allowed export.

Allowed export
≠
allowed reuse.

Allowed reuse
≠
allowed longitudinal linkage.

---

# Extended Policy Object Shape

Answer policy records may additionally include:

- collection_allowed;
- storage_allowed;
- export_allowed;
- reuse_allowed;
- derived_feature_allowed;
- free_text_allowed;
- longitudinal_linkage_allowed;
- cross_dataset_linkage_allowed;
- review_required;
- export_review_required;
- ethics_scope;
- deletion_policy_class.

Policy fields must remain:
- explicit;
- reviewable;
- versioned;
- bounded.

Policy engine
≠
autonomous policy generator.

---

# Deletion And Retention Boundary

Answer export policy does not fully define deletion policy.

Retention handling and deletion handling are related but separate governance layers.

Answer exclusion
≠
answer deletion.

Retention expiration
≠
immediate deletion guarantee.

Deletion policy
≠
export policy.

Systems must avoid silent indefinite retention of:
- transient-only answers;
- not-exportable answers;
- revoked-consent answers.

---

# Research-Safe Transform Boundary

Research-safe transforms may exist for some answers.

Examples:
- coarse ranges;
- capped values;
- normalized bins;
- aggregate-safe transforms;
- uncertainty-preserving abstractions.

Research-safe transform
≠
original answer export.

Derived research-safe value
≠
permission to export source answer.

Transforms must not silently bypass:
- consent boundaries;
- export restrictions;
- linkage restrictions;
- retention restrictions.

---

# Inference Boundary

Inferred or model-derived features are separate from collected answers.

Inference
≠
collected answer.

Derived interpretation
≠
participant-confirmed truth.

Probabilistic feature
≠
verified participant attribute.

Model inference must not silently inherit export permission from source answers.

Inferred features require:
- explicit governance;
- explicit review;
- bounded retention;
- bounded linkage policy.

---

# Ambiguity And Deny Rule

Policy ambiguity defaults to deny export.

If:
- classification is unclear;
- consent scope is unclear;
- linkage scope is unclear;
- retention scope is unclear;
- transform safety is unclear;
- inference status is unclear;

then export must remain blocked until reviewed.

Ambiguity
≠
permission.

Missing governance
≠
safe export.

---

# Derived Risk Boundary

Combined or derived variables may create higher sensitivity than original variables alone.

Derived risk may exceed source variable risk.

Low-risk variables in combination
≠
low-risk dataset.

Pseudonymized data
≠
immune to re-identification.

Combination safety requires:
- aggregation governance;
- linkage review;
- re-identification review;
- cohort-size awareness.

Derived aggregate
≠
impossible re-identification.

---

# Cross-Dataset Linkage Boundary

Cross-dataset linkage requires explicit governance.

Pseudonymization alone does not authorize:
- cross-study linkage;
- cross-dataset identity matching;
- hidden participant tracking;
- longitudinal reconstruction.

Cross-dataset linkage
≠
allowed because pseudonymized.

Export-scoped identity
≠
global research identity.

---

# Research Ethics Boundary

Answer export policy does not replace:
- ethics review;
- institutional approval;
- legal compliance;
- participant protections.

Policy compliance
≠
ethical approval.

Technical admissibility
≠
ethical admissibility.

Research governance must remain:
- human-reviewable;
- institution-aware;
- ethics-aware.

---

# Participant Transparency Boundary

Participants should be able to understand:
- whether answers are exportable;
- whether answers are retained;
- whether answers are aggregate-only;
- whether answers are transient-only;
- whether additional consent is required.

Participant visibility
≠
participant burden.

Transparency
≠
unrestricted disclosure of internal governance logic.

Participants may later require:
- export review;
- revocation pathways;
- bounded exclusion requests.

---

# AI-Generated Text Boundary

AI-generated summaries, interpretations, or free-text abstractions are high-risk outputs.

AI-generated free-text
≠
safe structured answer.

Generated summary
≠
safe export artifact.

AI-generated text may unintentionally leak:
- blocked answers;
- sensitive context;
- inferred attributes;
- hidden linkage information.

AI-generated research text requires:
- explicit review;
- bounded export policy;
- leakage-aware governance.

---

# Policy Engine Boundary

Future answer policy engines must remain bounded governance layers.

Policy engine
≠
participant scoring system.

Policy engine
≠
hidden sensitivity inference engine.

Policy engine
≠
autonomous classifier authority.

Policy engines must not:
- silently invent classifications;
- silently escalate retention;
- silently broaden export scope;
- silently authorize linkage;
- silently override consent.

---

# Review Boundary

Policy review and policy revision must remain bounded governance actions.

Policy review
≠
automatic reclassification.

Manual review
≠
automatic permission escalation.

Review tooling
≠
hidden policy authority.

Changes to answer classification require:
- explicit review;
- explicit versioning;
- documented rationale;
- bounded scope.

---

# Emergency Access Boundary

Temporary operational or emergency access does not automatically authorize research export.

Emergency access
≠
persistent export permission.

Temporary operational visibility
≠
retention approval.

Safety handling
≠
research admissibility.

Emergency-related answers may still remain:
- transient-only;
- excluded from snapshots;
- excluded from datasets;
- excluded from longitudinal linkage.

---

# Historical Export Boundary

Policy evolution must not silently redefine historical exports.

Updated classification
≠
retroactive historical reinterpretation.

Historical exports must preserve:
- policy version;
- consent basis;
- export scope;
- retention context.

---

# MVP Implementation Rules

This policy governs answer export classification only.

It does NOT replace:
- consent governance;
- retention governance;
- deletion governance;
- ethics approval;
- institutional review.

Referential fields such as collection_allowed, storage_allowed, deletion_policy_class, and ethics_scope are included for traceability only.

Final authority for collection, storage, deletion, consent, and ethics remains in their respective governance layers.

Current MVP rule:

Research snapshot builder excludes all raw answers until explicit answer policy implementation exists.

Answer policy must be applied before any answer value enters a research snapshot.

Policy lookup failure
=
deny export.

Malformed policy record
=
deny export.

Conflicting policy fields
=
most restrictive outcome wins.

allowed_export_scope must be explicit.

Empty allowed_export_scope
=
no export.

export_allowed=True alone is insufficient without compatible:
- allowed_export_scope;
- consent requirements;
- retention class;
- linkage restrictions;
- policy version.

answer_policy.py must not auto-classify unknown variables.

Static policy registry
≠
reviewed institutional approval.

Policy registry mutation must be:
- explicit;
- reviewed;
- versioned;
- documented.

Transform outputs must have their own policy record.

Research-safe transform
≠
permission to export source answer.

Free-text answers are not_exportable by default unless an explicit reviewed policy says otherwise.

Safety-critical answers default to transient_only or not_exportable unless an explicit reviewed policy says otherwise.

not_yet_classified is blocked from export like not_exportable, but remains distinct for audit.

not_exportable by policy
≠
not_yet_classified pending review.

Absence/refusal metadata may be more restrictive than the answer value itself.

Small-n aggregate cells must not be exported without re-identification review.

Aggregate output
≠
safe output by default.

---

# Final Principle

Bounded answer export policy exists to support:
- safe research data handling;
- anti-profiling protection;
- uncertainty-aware research;
- consent-aware governance;
- bounded scientific analysis.

Bounded answer export policy must never become:
- hidden participant classification system;
- unrestricted answer retention authority;
- behavioral profiling infrastructure;
- covert identity reconstruction layer.