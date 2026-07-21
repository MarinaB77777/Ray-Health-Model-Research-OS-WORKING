from __future__ import annotations

from copy import deepcopy
from typing import Any


SENSOR_HYPOTHESIS_SCHEMA_VERSION = "health-model-sensor-hypothesis-1"

VALIDATION_AIMS = {
    "device_verification": "Device verification: accuracy, precision, repeatability and drift",
    "analytical_validation": "Analytical validation against a reference measurement",
    "clinical_construct_validation": "Clinical/construct validation against physical state, questionnaire or parameter",
    "sensor_questionnaire_discrepancy": "Sensor–questionnaire/parameter discordance",
    "temporal_dynamics": "Temporal, lagged and within-person dynamics",
    "prediction": "Prediction of state, event or parameter from sensor measurements",
}

SOURCE_ROLES = {
    "sensor_candidate": "Candidate sensor signal or feature",
    "criterion_reference": "Reference instrument or criterion measurement",
    "questionnaire_anchor": "Questionnaire response or score",
    "physical_state_anchor": "Physical/clinical state measurement",
    "model_parameter_anchor": "Calculated model parameter",
    "event_annotation": "Event or state annotation",
    "covariate": "Covariate / condition",
    "time_axis": "Unified time axis",
}

SOURCE_ROLE_ENTITY_TYPES = {
    "sensor_candidate": {"measurement_dataset", "image_processing_run", "image_video_dataset"},
    "criterion_reference": {"measurement_dataset", "analysis_result", "image_processing_run", "image_video_dataset", "event_annotation", "measurement_instrument", "trained_model"},
    "questionnaire_anchor": {"questionnaire_result"},
    "physical_state_anchor": {"measurement_dataset", "parameter_result", "analysis_result", "game_result", "observable_marker"},
    "model_parameter_anchor": {"parameter_result", "model_parameter"},
    "event_annotation": {"event_annotation", "game_result"},
    "covariate": {"measurement_dataset", "questionnaire_result", "parameter_result", "analysis_result", "image_processing_run", "image_video_dataset", "game_result", "observable_marker", "model_parameter", "trained_model", "model_training_run"},
    "time_axis": {"time_variable"},
}

DATA_KINDS = {
    "continuous_signal": "Continuous signal / numeric feature",
    "ordinal_score": "Ordinal score",
    "binary_state": "Binary state",
    "multiclass_state": "Multiclass state",
    "event_time": "Event time / time-to-event",
    "image_video_feature": "Feature extracted from image or video",
}

PAIRING_STRATEGIES = {
    "exact_utc": "Exact UTC timestamp",
    "nearest_within_tolerance": "Nearest timestamp within a prespecified tolerance",
    "window_aggregate": "Aggregate sensor values within a questionnaire/measurement window",
    "event_anchored": "Event-anchored window",
    "lagged_window": "Prespecified lagged window",
}

DISCREPANCY_METRICS = {
    "raw_difference": "Signed raw difference after unit harmonization",
    "absolute_difference": "Absolute difference after unit harmonization",
    "standardized_difference": "Difference after prespecified standardization",
    "reference_residual": "Residual from a prespecified reference/calibration model",
    "dynamic_divergence": "Time-varying divergence between aligned trajectories",
    "classification_disagreement": "Disagreement between prespecified state classifications",
}

METHODS = [
    {"method_id": "pearson_association", "title": "Pearson association with confidence interval", "aims": ["clinical_construct_validation"], "data_kinds": ["continuous_signal", "image_video_feature"], "requires_reference": False, "supports_repeated": False, "purpose": "linear_association_not_agreement", "execution_status": "registered_without_validated_runner"},
    {"method_id": "spearman_association", "title": "Spearman rank association with confidence interval", "aims": ["clinical_construct_validation"], "data_kinds": ["continuous_signal", "ordinal_score", "image_video_feature"], "requires_reference": False, "supports_repeated": False, "purpose": "monotonic_association_not_agreement", "execution_status": "registered_without_validated_runner"},
    {"method_id": "bland_altman_repeated", "title": "Repeated-measures limits of agreement", "aims": ["analytical_validation", "sensor_questionnaire_discrepancy"], "data_kinds": ["continuous_signal", "image_video_feature"], "requires_reference": True, "supports_repeated": True, "purpose": "absolute_agreement_bias_and_limits", "execution_status": "registered_without_validated_runner"},
    {"method_id": "deming_regression", "title": "Deming regression", "aims": ["analytical_validation"], "data_kinds": ["continuous_signal", "image_video_feature"], "requires_reference": True, "supports_repeated": False, "purpose": "calibration_with_error_in_both_methods", "execution_status": "registered_without_validated_runner"},
    {"method_id": "concordance_correlation", "title": "Lin concordance correlation coefficient", "aims": ["analytical_validation"], "data_kinds": ["continuous_signal", "image_video_feature"], "requires_reference": True, "supports_repeated": False, "purpose": "precision_and_accuracy_concordance", "execution_status": "registered_without_validated_runner"},
    {"method_id": "intraclass_correlation", "title": "Intraclass correlation coefficient with declared form", "aims": ["device_verification", "analytical_validation"], "data_kinds": ["continuous_signal", "ordinal_score", "image_video_feature"], "requires_reference": False, "supports_repeated": True, "purpose": "reliability_or_absolute_agreement_as_prespecified", "execution_status": "registered_without_validated_runner"},
    {"method_id": "repeatability_measurement_error", "title": "Repeatability, within-device SD and measurement error", "aims": ["device_verification"], "data_kinds": ["continuous_signal", "image_video_feature"], "requires_reference": False, "supports_repeated": True, "purpose": "precision_repeatability_and_error", "execution_status": "registered_without_validated_runner"},
    {"method_id": "sensor_drift_analysis", "title": "Sensor drift and stability analysis", "aims": ["device_verification", "temporal_dynamics"], "data_kinds": ["continuous_signal", "image_video_feature"], "requires_reference": False, "supports_repeated": True, "purpose": "systematic_drift_change_points_and_stability", "execution_status": "registered_without_validated_runner"},
    {"method_id": "calibration_bias_rmse", "title": "Calibration curve, bias, MAE and RMSE", "aims": ["device_verification", "analytical_validation", "prediction"], "data_kinds": ["continuous_signal", "image_video_feature"], "requires_reference": True, "supports_repeated": True, "purpose": "error_and_calibration", "execution_status": "registered_without_validated_runner"},
    {"method_id": "mixed_effects_regression", "title": "Mixed-effects regression", "aims": ["clinical_construct_validation", "sensor_questionnaire_discrepancy", "temporal_dynamics"], "data_kinds": list(DATA_KINDS), "requires_reference": False, "supports_repeated": True, "purpose": "within_and_between_person_association", "execution_status": "registered_without_validated_runner"},
    {"method_id": "generalized_mixed_model", "title": "Generalized mixed-effects model", "aims": ["clinical_construct_validation", "prediction", "temporal_dynamics"], "data_kinds": ["binary_state", "multiclass_state", "ordinal_score"], "requires_reference": False, "supports_repeated": True, "purpose": "non_gaussian_repeated_outcomes", "execution_status": "registered_without_validated_runner"},
    {"method_id": "cross_correlation_lag", "title": "Cross-correlation with prespecified lag search", "aims": ["temporal_dynamics", "sensor_questionnaire_discrepancy"], "data_kinds": ["continuous_signal", "image_video_feature"], "requires_reference": False, "supports_repeated": True, "purpose": "lead_lag_association_not_agreement", "execution_status": "registered_without_validated_runner"},
    {"method_id": "state_space_model", "title": "State-space / dynamic latent-state model", "aims": ["temporal_dynamics", "sensor_questionnaire_discrepancy"], "data_kinds": ["continuous_signal", "ordinal_score", "binary_state", "image_video_feature"], "requires_reference": False, "supports_repeated": True, "purpose": "latent_state_and_dynamic_measurement_error", "execution_status": "registered_without_validated_runner"},
    {"method_id": "roc_pr_calibration", "title": "ROC/PR analysis and probability calibration", "aims": ["clinical_construct_validation", "prediction"], "data_kinds": ["binary_state", "multiclass_state"], "requires_reference": True, "supports_repeated": False, "purpose": "classification_discrimination_and_calibration", "execution_status": "registered_without_validated_runner"},
    {"method_id": "cohens_kappa", "title": "Cohen kappa with prevalence-aware interpretation", "aims": ["analytical_validation", "sensor_questionnaire_discrepancy"], "data_kinds": ["binary_state", "multiclass_state", "ordinal_score"], "requires_reference": True, "supports_repeated": False, "purpose": "categorical_agreement", "execution_status": "registered_without_validated_runner"},
    {"method_id": "equivalence_prespecified_margin", "title": "Equivalence test against a prespecified meaningful margin", "aims": ["analytical_validation", "sensor_questionnaire_discrepancy"], "data_kinds": ["continuous_signal", "ordinal_score", "image_video_feature"], "requires_reference": True, "supports_repeated": True, "purpose": "evidence_for_equivalence_with_declared_margin", "execution_status": "registered_without_validated_runner"},
    {"method_id": "nested_grouped_validation", "title": "Nested participant-grouped validation", "aims": ["prediction"], "data_kinds": list(DATA_KINDS), "requires_reference": True, "supports_repeated": True, "purpose": "leakage_resistant_external_performance_estimation", "execution_status": "registered_without_validated_runner"},
]


def sensor_hypothesis_contract() -> dict[str, Any]:
    return {
        "schema_version": SENSOR_HYPOTHESIS_SCHEMA_VERSION,
        "validation_aims": deepcopy(VALIDATION_AIMS),
        "source_roles": deepcopy(SOURCE_ROLES),
        "source_role_entity_types": {key: sorted(value) for key, value in SOURCE_ROLE_ENTITY_TYPES.items()},
        "data_kinds": deepcopy(DATA_KINDS),
        "pairing_strategies": deepcopy(PAIRING_STRATEGIES),
        "discrepancy_metrics": deepcopy(DISCREPANCY_METRICS),
        "methods": deepcopy(METHODS),
        "time_contract": {"axis": "UTC", "contract_version": "measurement-time-contract-1", "raw_and_derived_timestamps_preserved": True},
        "scientific_basis": [
            {"title": "FDA Digital Health Technologies for Remote Data Acquisition in Clinical Investigations", "url": "https://www.fda.gov/regulatory-information/search-fda-guidance-documents/digital-health-technologies-remote-data-acquisition-clinical-investigations"},
            {"title": "Bland & Altman: Measuring agreement in method comparison studies", "doi": "10.1177/096228029900800204"},
            {"title": "V3 framework: verification, analytical validation and clinical validation", "doi": "10.1177/20552076221144858"},
        ],
        "invariants": [
            "correlation_is_not_agreement",
            "sensor_verification_is_distinct_from_clinical_validation",
            "questionnaire_anchor_is_not_automatically_a_gold_standard",
            "repeated_measurements_preserve_participant_clustering",
            "prediction_split_preserves_participant_independence",
            "raw_sensor_data_and_processing_provenance_are_preserved",
            "all_cross_domain_pairing_uses_utc_and_declared_windows",
            "registered_without_validated_runner_is_not_executable",
        ],
    }


def compatible_sensor_methods(*, validation_aim: str, outcome_data_kind: str,
                              repeated_measurements: bool, has_reference: bool) -> list[dict[str, Any]]:
    if validation_aim not in VALIDATION_AIMS:
        raise ValueError("SENSOR_VALIDATION_AIM_UNSUPPORTED")
    if outcome_data_kind not in DATA_KINDS:
        raise ValueError("SENSOR_DATA_KIND_UNSUPPORTED")
    result = []
    for method in METHODS:
        reasons = []
        if validation_aim not in method["aims"]:
            reasons.append("VALIDATION_AIM_INCOMPATIBLE")
        if outcome_data_kind not in method["data_kinds"]:
            reasons.append("DATA_KIND_INCOMPATIBLE")
        if repeated_measurements and not method["supports_repeated"]:
            reasons.append("REPEATED_MEASUREMENTS_UNSUPPORTED")
        if method["requires_reference"] and not has_reference:
            reasons.append("REFERENCE_SOURCE_REQUIRED")
        item = deepcopy(method)
        item["compatible"] = not reasons
        item["incompatibility_reasons"] = reasons
        result.append(item)
    return result


def build_sensor_validation_plan(raw: dict[str, Any]) -> dict[str, Any]:
    aim = str(raw.get("validation_aim") or "")
    data_kind = str(raw.get("outcome_data_kind") or "")
    repeated = bool(raw.get("repeated_measurements"))
    if aim not in VALIDATION_AIMS:
        raise ValueError("SENSOR_VALIDATION_AIM_UNSUPPORTED")
    if data_kind not in DATA_KINDS:
        raise ValueError("SENSOR_DATA_KIND_UNSUPPORTED")
    sources = []
    source_role_issues = []
    for source in raw.get("data_sources") or []:
        role = str(source.get("source_role") or "")
        if role not in SOURCE_ROLES:
            raise ValueError("SENSOR_SOURCE_ROLE_UNSUPPORTED")
        entity_type = str(source.get("entity_type") or "").strip()
        if entity_type not in SOURCE_ROLE_ENTITY_TYPES[role]:
            source_role_issues.append(f"SOURCE_ENTITY_TYPE_INCOMPATIBLE_WITH_ROLE:{role}:{entity_type or 'missing'}")
        sources.append({
            "source_role": role,
            "entity_ref": str(source.get("entity_ref") or "").strip(),
            "display_name": str(source.get("display_name") or "").strip(),
            "entity_type": entity_type,
            "version": source.get("version"),
            "measurement_scale_ref": str(source.get("measurement_scale_ref") or "").strip(),
            "unit": str(source.get("unit") or "").strip(),
            "time_contract": deepcopy(source.get("time_contract") or {}),
        })
    has_reference = any(x["source_role"] == "criterion_reference" for x in sources)
    methods = compatible_sensor_methods(
        validation_aim=aim, outcome_data_kind=data_kind,
        repeated_measurements=repeated, has_reference=has_reference,
    )
    method_map = {item["method_id"]: item for item in methods}
    selected = []
    for method_id in dict.fromkeys(raw.get("selected_method_ids") or []):
        if method_id not in method_map:
            raise ValueError("SENSOR_METHOD_UNKNOWN")
        selected.append(deepcopy(method_map[method_id]))
    issues = list(source_role_issues)
    if not any(x["source_role"] == "sensor_candidate" for x in sources):
        issues.append("SENSOR_CANDIDATE_SOURCE_REQUIRED")
    anchor_roles = {"criterion_reference", "questionnaire_anchor", "physical_state_anchor", "model_parameter_anchor", "event_annotation"}
    if not any(x["source_role"] in anchor_roles for x in sources):
        issues.append("INDEPENDENT_ANCHOR_SOURCE_REQUIRED")
    if not any(x["source_role"] == "time_axis" for x in sources):
        issues.append("REGISTERED_TIME_AXIS_REQUIRED")
    pairing = str(raw.get("pairing_strategy") or "")
    if pairing not in PAIRING_STRATEGIES:
        issues.append("PAIRING_STRATEGY_REQUIRED")
    if not str(raw.get("observation_unit") or "").strip():
        issues.append("OBSERVATION_UNIT_REQUIRED")
    if not str(raw.get("independence_unit") or "").strip():
        issues.append("INDEPENDENCE_UNIT_REQUIRED")
    if aim in {"device_verification", "analytical_validation"} and not has_reference:
        issues.append("CRITERION_REFERENCE_REQUIRED_FOR_METHOD_COMPARISON")
    if aim == "sensor_questionnaire_discrepancy":
        if not any(x["source_role"] in {"questionnaire_anchor", "physical_state_anchor", "model_parameter_anchor"} for x in sources):
            issues.append("QUESTIONNAIRE_PHYSICAL_OR_PARAMETER_ANCHOR_REQUIRED")
        if raw.get("discrepancy_metric") not in DISCREPANCY_METRICS:
            issues.append("DISCREPANCY_METRIC_REQUIRED")
        if not str(raw.get("harmonization_rule") or "").strip():
            issues.append("SCALE_HARMONIZATION_RULE_REQUIRED")
    if aim == "prediction":
        if not str(raw.get("split_unit") or "").strip():
            issues.append("PARTICIPANT_GROUPED_SPLIT_REQUIRED")
        if not bool(raw.get("leakage_control")):
            issues.append("DATA_LEAKAGE_CONTROL_REQUIRED")
    if any(not item["compatible"] for item in selected):
        issues.append("SELECTED_METHOD_INCOMPATIBLE")
    if not selected:
        issues.append("ANALYSIS_METHOD_REQUIRED")
    return {
        "schema_version": SENSOR_HYPOTHESIS_SCHEMA_VERSION,
        "validation_aim": aim,
        "outcome_data_kind": data_kind,
        "repeated_measurements": repeated,
        "data_sources": sources,
        "pairing": {
            "strategy": pairing,
            "tolerance_or_window": str(raw.get("pairing_tolerance") or "").strip(),
            "observation_unit": str(raw.get("observation_unit") or "").strip(),
            "independence_unit": str(raw.get("independence_unit") or "").strip(),
            "axis": "UTC",
        },
        "quality_requirements": {
            "minimum_coverage": raw.get("minimum_coverage"),
            "maximum_missingness": raw.get("maximum_missingness"),
            "calibration_reference": str(raw.get("calibration_reference") or "").strip(),
            "signal_quality_rule": str(raw.get("signal_quality_rule") or "").strip(),
        },
        "discordance": {
            "metric": raw.get("discrepancy_metric"),
            "harmonization_rule": str(raw.get("harmonization_rule") or "").strip(),
            "acceptance_threshold": str(raw.get("acceptance_threshold") or "").strip(),
            "threshold_source": str(raw.get("threshold_source") or "").strip(),
        },
        "prediction_validation": {
            "split_unit": str(raw.get("split_unit") or "").strip(),
            "leakage_control": bool(raw.get("leakage_control")),
            "external_validation_dataset_ref": str(raw.get("external_validation_dataset_ref") or "").strip(),
        },
        "compatible_methods": methods,
        "selected_methods": selected,
        "readiness": {"valid": not issues, "issues": list(dict.fromkeys(issues))},
    }
