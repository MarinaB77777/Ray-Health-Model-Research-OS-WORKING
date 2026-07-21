Research Snapshot Answer Integration Contract

Purpose

This document defines the bounded integration contract between answer export filtering and research snapshot construction.

The purpose of this contract is:
 • safe answer inclusion in research snapshots;
 • clear separation between answer policy and snapshot building;
 • audit-preserving answer export semantics;
 • prevention of raw answer leakage;
 • prevention of builder-side policy authority.

This document governs:
 • how filtered answer export results may enter research snapshots;
 • what snapshot_builder may consume;
 • what snapshot_builder must not decide;
 • how included and excluded answers must remain represented.

This document does NOT:
 • define answer policy categories;
 • define consent governance;
 • define retention governance;
 • define dataset aggregation;
 • authorize raw answer export;
 • authorize research analytics.

⸻

Core Principle

Research snapshot builder may consume only bounded answer export filter output.

Research snapshot builder must not directly consume raw answers.

snapshot_builder
≠
policy authority.

answer_export_filter output
≠
final research permission.

included answer
≠
consent/retention approved.

excluded answer
≠
deleted answer.

excluded metadata
≠
safe by default.

⸻

Integration Pipeline

The bounded pipeline is:

session.answers
↓
answer_export_filter
↓
bounded answer_export_result
↓
research snapshot builder

Research snapshot builder may include:
 • included_answers;
 • excluded_answers audit;
 • answer_policy_version;
 • filter_version;
 • filter_method;
 • filter_scope;
 • count metadata;
 • explicit limitations.

Research snapshot builder must not include:
 • raw session.answers;
 • unfiltered answer values;
 • excluded answer values;
 • builder-side variable classifications;
 • hidden policy overrides.

⸻

Included / Excluded Answer Boundary

Research snapshot builder may consume only bounded answer export filter output.

Included answers are:
 • bounded export candidates;
 • policy-filtered export candidates;
 • uncertainty-preserving payload elements.

Included answers are NOT:
 • final export authorization;
 • consent-resolved artifacts;
 • retention-approved artifacts;
 • unrestricted research permissions.

included answer
≠
consent approved.

included answer
≠
retention approved.

included answer
≠
dataset admission approved.

Excluded answers remain bounded audit artifacts.

Excluded answers are NOT:
 • deleted answers;
 • safe-to-ignore answers;
 • unrestricted metadata.

Excluded answers must not contain:
 • raw values;
 • transformed values;
 • hidden summaries;
 • indirect value leakage.

Excluded answer metadata must remain bounded.

excluded answer metadata
≠
safe by default.

⸻

Aggregate-Only Integration Boundary

Aggregate-only answers must never appear inside individual research snapshots.

aggregate_only
≠
individual snapshot exportable.

Aggregate-only variables may later participate only through:
 • governed aggregation;
 • cohort-level processing;
 • re-identification-aware review;
 • explicit aggregation governance.

Research snapshot builder must not:
 • include aggregate-only raw values;
 • silently downgrade aggregate-only restrictions;
 • create pseudo-individual exports from aggregate-only variables.

⸻

Transform Boundary

Research snapshot builder must not create transforms.

snapshot_builder
≠
transform engine.

Research-safe transforms require:
 • explicit transform governance;
 • explicit transform review;
 • explicit transform policy;
 • explicit transform versioning.

Transformed value
≠
source answer value.

Derived transform
≠
source export permission.

Transform outputs must preserve:
 • uncertainty semantics;
 • policy traceability;
 • transform provenance;
 • transform version visibility.

⸻

Duplicate Variable Boundary

Duplicate normalized variable codes must not silently merge.

duplicate normalized variable codes
≠
safe merge.

If duplicate normalized variables are detected:
 • silent overwrite is forbidden;
 • silent merge is forbidden;
 • silent precedence selection is forbidden.

Duplicate handling must remain:
 • explicit;
 • reviewable;
 • audit-visible.

Duplicate exclusion
≠
policy failure.

⸻

Fail-Closed Integration Rule

Research snapshot builder must fail closed when answer integration state is unclear.

If:
 • filter output is malformed;
 • policy state is malformed;
 • inclusion state is ambiguous;
 • scope resolution is ambiguous;
 • transform provenance is unclear;
 • policy version is missing;
 • answer export result is structurally invalid;

then answer inclusion must remain blocked.

Malformed filter result

deny answer integration.

Partial malformed payload
≠
safe partial inclusion.

Fail-closed behavior
≠
system failure.

⸻

Builder Non-Authority Boundary

Research snapshot builder must not:
 • invent export rules;
 • infer exportability;
 • auto-classify answers;
 • create fallback export semantics;
 • silently broaden export scope;
 • silently override policy restrictions.

NO builder-side default export rules.

NO builder-side implicit exportability.

NO builder-side inference.

snapshot_builder
≠
policy engine.

snapshot_builder
≠
consent authority.

snapshot_builder
≠
retention authority.

⸻

Consent / Retention Unresolved Boundary

Included-by-policy answers may still remain unresolved for:
 • consent;
 • retention;
 • deletion;
 • linkage;
 • aggregation;
 • institutional review.

included_by_policy
≠
consent_resolved.

included_by_policy
≠
retention_resolved.

included_by_policy
≠
institutionally_approved.

Research snapshot inclusion must preserve unresolved governance visibility.

Unresolved governance state
≠
permission to proceed silently.

⸻

Audit Preservation Boundary

Answer integration must preserve:
 • policy version;
 • filter version;
 • inclusion reasons;
 • exclusion reasons;
 • exclusion visibility;
 • duplicate detection visibility;
 • uncertainty visibility.

Audit preservation
≠
surveillance authority.

Exclusion trace
≠
answer export.

Builder integration must not silently remove:
 • exclusion semantics;
 • governance limitations;
 • uncertainty markers;
 • blocked states.

⸻

Answer Export Result Boundary

answer_export_result is a bounded governance artifact.

answer_export_result
≠
final research dataset row.

answer_export_result
≠
participant model.

answer_export_result
≠
consent artifact.

answer_export_result
≠
retention artifact.

answer_export_result
≠
research analytics output.

Filter output remains:
 • bounded;
 • reviewable;
 • uncertainty-aware;
 • governance-scoped;
 • non-authoritative.

⸻

Answer Export Filter Output Boundary

answer_export_filter output is a bounded intermediate artifact.

It is NOT:
 • final research export approval;
 • consent resolution;
 • retention approval;
 • dataset admission approval;
 • ethics approval;
 • participant truth;
 • research analytics.

answer_export_filter
≠
export authority.

answer_export_filter
≠
consent engine.

answer_export_filter
≠
retention engine.

answer_export_filter
≠
research intelligence.

⸻

Included Answer Semantics

Included answers may enter research snapshots only as part of bounded filter output.

Included answers must preserve:
 • variable_code;
 • value;
 • policy_category;
 • reason_code;
 • policy_version;
 • review_status;
 • allowed_export_scope.

Included answer
≠
final export authorization.

Included answer
≠
longitudinal linkage permission.

Included answer
≠
dataset eligibility.

Included answer
≠
research correctness.

⸻

Excluded Answer Semantics

Excluded answers must preserve audit without exposing excluded values.

Excluded answer audit may include:
 • variable_code;
 • policy_category;
 • reason_code;
 • policy_version;
 • review_status;
 • allowed_export_scope.

Excluded answer audit must not include:
 • excluded answer value;
 • hidden derived equivalent;
 • free-text substitute;
 • indirect reconstruction path.

Excluded answer
≠
deleted answer.

Excluded metadata
≠
safe by default.

Excluded answer audit should remain bounded and reviewable.

⸻

Snapshot Builder Consumption Rules

snapshot_builder may consume answer_export_result only after it has been produced by answer_export_filter.

snapshot_builder must consume answer_export_result as immutable bounded governance output.

snapshot_builder must treat answer_export_result as:
 • bounded;
 • policy-filtered;
 • still not consent-final;
 • still not retention-final;
 • still not dataset-final.

snapshot_builder must not:
 • call answer policy logic directly to decide inclusion;
 • classify variables;
 • infer consent;
 • infer retention;
 • infer dataset eligibility;
 • override filter exclusions;
 • reconstruct excluded answers.

Builder consumption
≠
policy decision.

Builder inclusion
≠
research approval.

⸻

Prohibited Integration Patterns

The following are prohibited:
 • raw answers directly into research snapshot;
 • snapshot_builder deciding variable exportability;
 • snapshot_builder overriding answer_export_filter;
 • aggregate_only answers appearing as individual answers;
 • transient_only answers appearing in snapshots;
 • not_exportable answers appearing in snapshots;
 • excluded values leaking through summaries;
 • excluded values leaking through public reasons;
 • excluded values leaking through warnings;
 • excluded values leaking through derived fields;
 • consent inference from filter inclusion;
 • retention inference from filter inclusion.

⸻

Aggregate-Only Boundary

aggregate_only answers must not enter individual-level research snapshots as values.

aggregate_only
≠
individual snapshot export.

Future aggregate-only handling requires:
 • aggregation governance;
 • cohort-size review;
 • re-identification review;
 • small-n suppression;
 • explicit dataset assembly rules.

⸻

Transform Boundary

Transformed answer values may enter snapshots only if:
 • the transform has its own explicit policy record;
 • the source answer policy allows such transform;
 • the transform does not reconstruct the blocked source value;
 • governance marks the value as transformed.

Transform output
≠
source answer export permission.

Research-safe transform
≠
safe by default.

⸻

Consent And Retention Boundary

answer_export_result does not resolve consent or retention.

Snapshot builder must preserve that:
 • consent_evaluated may be false;
 • retention_evaluated may be false;
 • included_answers_are_not_final_export_authorization may be true.

Consent not evaluated
≠
consent granted.

Retention not evaluated
≠
retention permitted.

⸻

Integration Metadata

Research snapshots that include answer export results should preserve:
 • answer_policy_version;
 • filter_version;
 • filter_method;
 • filter_scope;
 • answer_count;
 • included_count;
 • excluded_count;
 • count_basis;
 • duplicate_variable_codes_detected;
 • unknown_policy_default_deny;
 • answer_values_filtered;
 • included_answers_are_not_final_export_authorization.

These metadata fields support auditability.

Auditability
≠
surveillance authority.

⸻

Future Governance Compatibility

This contract must remain compatible with future:
 • consent governance;
 • retention governance;
 • deletion governance;
 • transform governance;
 • aggregation governance;
 • institutional review workflows;
 • participant revocation workflows.

Compatibility
≠
pre-approval for future integration.

Future governance compatibility
≠
future permission granted.

Unimplemented governance layer
≠
safe implicit approval.

⸻

MVP Integration Rule

Current MVP rule:

Do not wire answer_export_filter into snapshot_builder until this contract is stable and tests are added.

When integration begins:
 • add answer section to snapshot;
 • consume only answer_export_result;
 • do not consume raw session.answers directly;
 • test that raw excluded values do not leak;
 • test that unknown answers remain excluded;
 • test that filter metadata is preserved;
 • test that builder does not classify variables.

⸻

Excluded Metadata Leakage Boundary

Excluded answer metadata may itself create indirect leakage risk.

Even without raw values, excluded metadata combinations may reveal:
 • sensitive categories;
 • refusal patterns;
 • operational state;
 • rare participant context;
 • hidden linkage opportunities.

Excluded metadata
≠
automatically safe metadata.

Excluded metadata exports may later require:
 • bounded reduction;
 • aggregation-only handling;
 • cohort-size review;
 • metadata minimization;
 • re-identification review.

Audit visibility
≠
unrestricted metadata visibility.

⸻

Small-N And Rare Context Boundary

Rare answer combinations may increase re-identification risk even when:
 • values are pseudonymized;
 • identifiers are removed;
 • answers are policy-filtered.

Small cohort safety
≠
automatic safety.

Rare context
≠
safe because exportable.

Future dataset assembly layers must support:
 • small-n suppression;
 • cohort-size thresholds;
 • rare-combination review;
 • linkage-risk review.

snapshot_builder
≠
small-n protection engine.

⸻

Policy Version Compatibility Boundary

answer_export_result and snapshot_builder must preserve policy-version compatibility visibility.

Mismatched policy versions must not silently proceed.

policy_version mismatch
≠
safe fallback behavior.

If:
 • answer_policy_version is missing;
 • filter_version is missing;
 • incompatible policy semantics are detected;

then integration must fail closed.

Backward compatibility
≠
silent semantic reinterpretation.

⸻

Unknown Future Policy Boundary

Future policy categories must default to deny integration unless explicitly supported.

Unknown future category
≠
implicitly exportable.

Future policy expansion
≠
automatic builder compatibility.

snapshot_builder must not:
 • silently reinterpret unknown categories;
 • silently downgrade unknown restrictions;
 • silently map future categories into existing categories.

Unsupported policy category

deny integration.

⸻

Intermediate Artifact Retention Boundary

Intermediate artifacts such as:
 • answer_export_result;
 • exclusion audit objects;
 • temporary integration payloads;
 • pre-snapshot filtered answer sets;

must remain bounded and reviewable.

Intermediate artifact
≠
permanent retention permission.

Temporary governance artifact
≠
dataset artifact.

Retention of intermediate artifacts requires separate governance decisions.

⸻

Snapshot Mutation Boundary

Once a research snapshot is generated, answer integration results must not be silently mutated.

Post-generation mutation
≠
safe correction.

Corrections require:
 • explicit revision;
 • explicit version visibility;
 • audit traceability;
 • preserved historical interpretation boundaries.

Historical snapshot
≠
current policy state.

Updated answer policy
≠
retroactive snapshot reinterpretation.

⸻

Integration Failure Visibility

Answer integration failures must remain visible.

Silent answer dropping is forbidden when:
 • integration failed;
 • policy resolution failed;
 • malformed filter output was detected;
 • policy compatibility failed.

Failure visibility
≠
system instability.

Visible blocked state
≠
pipeline failure.

Research systems must preserve:
 • blocked visibility;
 • failure visibility;
 • uncertainty visibility;
 • exclusion visibility.
 
 ⸻
 
Final Principle

Research snapshot answer integration exists to allow bounded, audited answer inclusion without turning snapshot_builder into a policy authority.

This integration must never become:
 • raw answer serialization;
 • hidden answer profiling;
 • builder-side policy classification;
 • consent inference;
 • retention inference;
 • dataset eligibility inference;
 • longitudinal participant modeling.

