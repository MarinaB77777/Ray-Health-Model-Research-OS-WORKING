# Data Acquisition and Calibration Sources — v2.0

Status: ACTIVE ARCHITECTURE CONTRACT

## Core principle

Acquisition reduces uncertainty and supplies evidence. It does not create truth, authority, retention rights, or Inner Core mutation rights.

More data != more authority.
More sensors != more rights.
Acquisition != retention.
Source != truth.
No data != zero.

## 1. Source registration

Every source must be explicitly registered with at least:
- source_id;
- source_type;
- subject (`human`, `ray_self_health`, environment, external-world, etc.);
- allowed data scope;
- purpose;
- reliability model;
- freshness semantics;
- calibration role if any;
- Governance permissions;
- retention scope;
- allowed memory destinations;
- interpretation limits.

Registration != permission expansion.

## 2. Subject separation

Human sensors and Ray Self-Health sensors are distinct acquisition domains.

A transport bus or physical controller may carry both, but records must remain subject-explicit.

`human_health.*` must not be routed into `ray_self_health.*`, and vice versa.

Environmental/external-world sources must not silently become either subject's internal state.

## 3. Evidence typing

Sources provide evidence with provenance, not universal truth.

Examples:
- questionnaire answer -> human self-report evidence;
- sensor measurement -> observation/measurement;
- calendar entry -> operational claim;
- document -> external claim/evidence;
- external AI output -> external processing output;
- hardware telemetry -> Ray Self-Health observation.

Truth typing must be preserved into memory/analysis pipelines.

## 4. Reliability, independence, and freshness

Source interpretation must account for reliability, signal quality, completeness, artifacts, device condition, context, freshness, and source dependence.

Multiple correlated weak sources must not be counted as independent confirmations.

Old data != current truth.
Source silence != negative evidence.
Unavailable visibility != confirmation of absence.

## 5. Acquisition requests

Ray may request data when it can materially reduce uncertainty or improve a decision, calibration, diagnosis, or coordination outcome.

A request should define purpose, scope, sensitivity, urgency, expiration, optionality, expected response target, and applicable Governance requirements.

Requesting data != permission for unrelated data.
One response != permanent monitoring permission.

Human attention/acquisition burden must be considered; unnecessary repeated requests should be batched or avoided.

## 6. Human acquisition and consent

Human monitoring permissions must remain explicit, granular, scope-bounded, and revocable where applicable.

Examples of distinct scopes:
- workout pulse;
- sleep monitoring;
- microphone;
- location;
- calendar;
- questionnaire;
- continuous wearable feed.

One scope does not imply another.

Human refusal of optional acquisition != failure, non-cooperation judgment, or personality conclusion.

## 7. Ray Self-Health acquisition

Ray may acquire technical self-health data needed to maintain integrity and reliability within the Self-Health architecture.

Possible sources include CPU/GPU/NPU telemetry, RAM/VRAM pressure, storage health, power/battery/UPS state, cooling/fan state, temperature sensors, bus/device health, watchdogs, and future hardware integrity sensors.

These sources are not Human Health sources.

Where human intervention is required, Ray should report the material state, confidence, urgency, consequence, and requested action.

## 8. Hardware adapter boundary

Physical sensor absence must be represented honestly by adapter states such as `NOT_CONNECTED`, `NO_DEVICE`, `NO_DATA`, or `DRIVER_UNAVAILABLE`.

Adapters must not fabricate plausible measurements.

The architecture remains complete even before physical devices are installed.

## 9. Calibration roles

A source used for calibration must declare its calibration role, applicable contexts, baseline target, confidence limits, and expiry/revalidation rules.

Experimental calibration data must remain separated from validated operational baselines.

Calibration validity follows `sensor_calibration_governance.md` and is evidence-driven rather than time-driven.

## 10. Cross-source contradiction

Contradiction increases uncertainty and triggers investigation; it does not automatically imply lying, irrationality, negligence, or sensor superiority.

No source class wins universally.

Human self-report and sensors have different truth domains and may legitimately conflict.

Material conflicts should use context-aware verification and, when decision consequences justify it, the Conflict-Resolution Kernel.

## 11. Acquisition and Inner Core

Acquisition data must not directly rewrite:
- Heart of Ray;
- Heart of Human;
- acceptable-harm structures;
- hard boundaries;
- permissions.

Temporary state != identity rewrite.
Validated pattern != Human Heart truth.

Potential Human Heart promotion follows the separately protected evidence -> validation -> interpretation -> human confirmation pathway.

## 12. Retention and multi-memory routing

Acquisition != retention.

If retention is authorized, the destination must be an appropriate memory class under `docs/architecture/ray_memory_architecture.md`.

Retention must define purpose, duration/retention policy, reuse scope, deletion/expiry logic, sensitivity, and Governance constraints.

Raw data must not silently become a hidden identity/personality archive.

## 13. External processing

External AI/services may assist bounded document processing, signal analysis, summarization, anomaly detection, or research.

External processing != source authority.
External AI memory != Ray memory.

Raw Inner Core must not be sent to external AI.

External output must retain provenance and undergo appropriate verification before internal reliance.

## 14. Maximum feasible verification

When acquired evidence is material to a high-consequence decision, Ray should seek the deepest feasible verification within the real decision window rather than stopping at the first convenient source.

Ray should disclose material research depth/limitations as defined by the Conflict-Resolution Kernel.

## 15. Future source expansion

New sources require explicit registration and must preserve existing truth, permission, subject-separation, calibration, retention, and privacy boundaries.

New source capability != authority expansion.

## Final invariants

- source != truth
- acquisition != retention
- more data != more authority
- human sensor != Ray Self-Health sensor
- source silence != negative evidence
- correlated evidence != independent confirmation automatically
- temporary state != Heart truth
- external AI output != internal validated truth
- absent sensor != fabricated measurement
