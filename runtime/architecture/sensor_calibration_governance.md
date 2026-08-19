# Sensor Calibration Governance — v2.0

Status: ACTIVE ARCHITECTURE CONTRACT

## Core principle

Calibration exists to make interpretation scientifically more valid, not to manufacture certainty or authority.

Calibration validity is evidence-driven, parameter-specific, context-specific, freshness-aware, and uncertainty-aware.

Elapsed time alone != valid calibration.
Calibration != certainty.
Calibration != permission.
Calibration != identity truth.

## 1. Subject separation

Calibration records must identify their subject.

At minimum:
- `human_health.*` — human psychophysical/health calibration;
- `ray_self_health.*` — Ray hardware/software self-health calibration.

These domains must not be merged merely because they use similar statistical methods or share transport hardware.

## 2. Human calibration purpose

Human calibration may support:
- sensor interpretation;
- baseline comparison;
- readiness/uncertainty evaluation;
- false-alarm reduction;
- context-aware coordination;
- Health Model inputs where contractually appropriate.

Human sensor/calibration data must not silently become:
- personality truth;
- stable values;
- motivation certainty;
- Human Heart content;
- permission to act.

## 3. Ray Self-Health calibration purpose

Ray Self-Health calibration may support:
- thermal baselines;
- power/battery/UPS baselines;
- memory/storage health interpretation;
- compute-load baselines;
- sensor/driver reliability;
- cooling behavior;
- component aging/degradation detection;
- integrity monitoring.

Ray Self-Health calibration is technical integrity evidence, not Human Health data and not Heart of Ray identity content.

## 4. Scientific calibration validity

Calibration validity may depend on:
- sufficient observations;
- independence/repetition where relevant;
- baseline strength;
- baseline stability;
- context diversity;
- context match;
- calibration freshness;
- sensor reliability;
- signal quality;
- artifact level;
- environmental stability;
- cross-source consistency/contradiction;
- reference measurement quality;
- subject self-report where scientifically relevant for human calibration.

No fixed number of days is sufficient by itself.

Different parameters may reach adequate validity at different times.

## 5. Baselines

Baselines are parameter/context-specific.

Human examples may include resting, physical-load, cognitive-load, recovery, illness, sleep-deprivation, social-load, or other scientifically justified baselines.

Ray examples may include idle/load thermal, normal power draw, cooling response, memory pressure, storage health, sensor noise, or other component-specific baselines.

A baseline valid in one context != universal baseline truth.

## 6. Missing or weak calibration

Missing/weak calibration must preserve uncertainty.

No baseline != normal.
No baseline != zero.
Weak calibration != confident interpretation.

Weak calibration may require:
- additional observation;
- reference measurement;
- clarification;
- uncertainty increase;
- interpretation limitation;
- forecast/escalation limitation.

## 7. Sensor reliability and artifacts

Reliability assessment may include hardware quality, placement, battery/power state, signal integrity, environmental interference, motion, synchronization, driver state, calibration drift, and measurement corruption.

Artifacts must remain visible to interpretation and uncertainty handling.

For human sensors, physical activation must not automatically be interpreted as emotional activation.

For Ray Self-Health sensors, a single anomalous measurement must not automatically become component-failure certainty unless the hardware protection contract requires immediate protective action.

## 8. Freshness and decay

Calibration may become stale through time, context change, hardware replacement, firmware/driver change, illness/recovery, environmental change, or other relevant state changes.

Old calibration != current calibration truth.

Component replacement may invalidate Ray Self-Health baselines for the replaced component without changing Heart of Ray identity.

## 9. Calibration memory

Calibration/evidence records belong to the governed multi-memory architecture.

Calibration Memory != Heart of Human.
Calibration Memory != Heart of Ray.

Records should preserve provenance, context, uncertainty, validity, freshness, correction lineage, and subject identity.

## 10. Promotion boundary

A repeatedly validated human pattern may become a candidate for deeper interpretation, but:

validated pattern != Human Heart truth.

Potential promotion toward a practically invariant Human Heart declaration requires the separately protected evidence -> validation -> interpretation -> human confirmation pathway.

Ray Self-Health calibration never promotes into Heart of Human.

Technical self-health state does not silently rewrite Heart of Ray.

## 11. Calibration and escalation

Sensor interpretation does not automatically grant interruption, emergency, disclosure, or execution authority.

Weak calibration should reduce confidence in escalation where additional evidence is required.

Emergency hardware safety mechanisms for Ray may still perform narrowly defined protective actions based on validated device-safety contracts; those mechanisms do not create general authority.

## 12. External processing

External AI/services may assist bounded signal processing or anomaly analysis only with permitted data.

External processing is not calibration authority and must not receive raw Inner Core.

External output requires provenance and appropriate validation before becoming internal calibration evidence.

## 13. Hardware adapter boundary

Until physical sensors are installed, adapter stubs must report honest availability states such as:
- `NOT_CONNECTED`;
- `NO_DEVICE`;
- `NO_DATA`;
- `DRIVER_UNAVAILABLE`.

Stubs must not manufacture plausible measurements.

The full calibration architecture remains present even when the physical sensor is absent.

## 14. Research and validation transparency

For calibration-derived material decisions, Ray should be able to explain the relevant calibration quality, evidence limitations, context match, and whether additional calibration could materially change the interpretation.

## Final invariants

- calibration validity is evidence-driven
- time alone != calibration validity
- calibration != certainty
- calibration != authority
- sensor data != identity truth
- missing baseline preserves uncertainty
- human health calibration != Ray Self-Health calibration
- validated pattern != Human Heart truth
- hardware replacement != automatic Ray identity replacement
- absent sensor != fake measurement
