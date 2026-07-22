from copy import deepcopy
from typing import Any

from assessment.mappings.health_model_v61_required_inputs import (
    build_health_model_v61_input_coverage,
)
from research.analyses.health_model.model_parameter_extractor import (
    build_health_model_parameter_records,
)
from research.analyses.health_model.model_parameter_registry import (
    list_model_parameter_definitions,
)
from research.analyses.health_model.v61_calculator import (
    calculate_health_model_v61,
)
from research.model_registry import (
    RegisteredCalculationModel,
    register_calculation_model,
)


HEALTH_MODEL_ID = "health_model_v6_1"
HEALTH_MODEL_VERSION = "6.1"
HEALTH_MODEL_CALCULATION_VERSION = "1"
HEALTH_MODEL_INPUT_CONTRACT_VERSION = (
    "health-model-v61-input-1"
)


def build_health_model_input(
    *,
    input_snapshot: dict,
    input_references: list | None = None,
    participant_id: str | None = None,
    subject_link_id: str | None = None,
    calculation_run_id: str | None = None,
) -> dict:
    """
    Receives an already assembled model-input snapshot.

    This function does not search questionnaires, question banks,
    participant sessions, or answer records. Transformation from any
    source data into this contract belongs to a separate input
    preparation process.
    """
    if not isinstance(input_snapshot, dict):
        raise TypeError(
            "Health Model input_snapshot must be a dict"
        )

    return deepcopy(input_snapshot)


def validate_health_model_input(
    model_input: dict,
) -> dict:
    if not isinstance(model_input, dict):
        return {
            "valid": False,
            "errors": [
                {
                    "field": "model_input",
                    "code": (
                        "HEALTH_MODEL_INPUT_NOT_OBJECT"
                    ),
                }
            ],
            "warnings": [],
            "reason_codes": [
                "HEALTH_MODEL_INPUT_NOT_OBJECT"
            ],
        }

    coverage = (
        build_health_model_v61_input_coverage(
            model_input
        )
    )

    missing_required_data = list(
        coverage.get(
            "missing_required_data",
            [],
        )
    )

    missing_critical_data = list(
        coverage.get(
            "missing_critical_data",
            [],
        )
    )

    errors = []
    warnings = []

    if missing_required_data:
        warnings.append({
            "field": "model_input",
            "code": (
                "HEALTH_MODEL_REQUIRED_INPUTS_MISSING"
            ),
            "missing_codes": (
                missing_required_data
            ),
        })

    if missing_critical_data:
        warnings.append({
            "field": "model_input",
            "code": (
                "HEALTH_MODEL_CRITICAL_INPUTS_MISSING"
            ),
            "missing_codes": (
                missing_critical_data
            ),
        })

    reason_codes = []

    if missing_critical_data:
        reason_codes.append(
            "HEALTH_MODEL_CRITICAL_INPUTS_MISSING"
        )

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "reason_codes": reason_codes,
        "coverage": coverage,
        "missing_required_data": (
            missing_required_data
        ),
        "missing_critical_data": (
            missing_critical_data
        ),
    }


def calculate_registered_health_model(
    model_input: dict,
) -> dict:
    result = calculate_health_model_v61(
        deepcopy(model_input)
    )

    coverage = (
        build_health_model_v61_input_coverage(
            model_input
        )
    )

    result["coverage"] = coverage
    result["missing_required_data"] = list(
        coverage.get(
            "missing_required_data",
            [],
        )
    )
    result["missing_critical_data"] = list(
        coverage.get(
            "missing_critical_data",
            [],
        )
    )

    if result["missing_critical_data"]:
        result["forecast_allowed"] = False
        result["readiness_status"] = (
            "NOT_ENOUGH_DATA"
        )
        result["status"] = "NOT_ENOUGH_DATA"
        result["reason_codes"] = [
            "HEALTH_MODEL_CRITICAL_INPUTS_MISSING"
        ]

    return result


def build_registered_health_model_parameter_records(
    *,
    calculation_run_id: str,
    session_id: str | None,
    participant_id: str | None,
    subject_link_id: str | None,
    model_id: str,
    model_version: str,
    calculation_version: str,
    analysis_output: dict,
    observation_time: str | None,
    input_references: list | None = None,
    input_snapshot: dict | None = None,
) -> list[dict]:
    study_ids = sorted({
        str(reference.study_id)
        for reference in (input_references or [])
        if getattr(reference, "study_id", None)
    })
    records = build_health_model_parameter_records(
        session_id=session_id,
        participant_id=participant_id,
        subject_link_id=subject_link_id,
        study_id=(
            study_ids[0]
            if len(study_ids) == 1
            else None
        ),
        analysis_output=analysis_output,
        observation_time=observation_time,
    )

    return [
        {
            **record,
            "calculation_run_id": (
                calculation_run_id
            ),
            "model_id": model_id,
            "model_version": model_version,
            "calculation_version": (
                calculation_version
            ),
            "source_session_id": session_id,
            "study_ids": study_ids,
            "study_scope_status": (
                "single_study"
                if len(study_ids) == 1
                else (
                    "multiple_studies"
                    if study_ids
                    else "study_unknown"
                )
            ),
            "input_reference_ids": [
                reference.input_reference_id
                for reference in (
                    input_references or []
                )
                if getattr(
                    reference,
                    "input_reference_id",
                    None,
                )
            ],
        }
        for record in records
    ]


def list_health_model_parameter_definitions(
) -> list[dict]:
    return list_model_parameter_definitions(
        include_inactive=True,
    )


def build_registered_health_model(
) -> RegisteredCalculationModel:
    return RegisteredCalculationModel(
        model_id=HEALTH_MODEL_ID,
        model_version=HEALTH_MODEL_VERSION,
        calculation_version=(
            HEALTH_MODEL_CALCULATION_VERSION
        ),
        input_contract_version=(
            HEALTH_MODEL_INPUT_CONTRACT_VERSION
        ),
        title={
            "ru": (
                "Модель психофизического состояния"
            ),
            "en": (
                "Psychophysical State Model"
            ),
        },
        build_input=build_health_model_input,
        validate_input=(
            validate_health_model_input
        ),
        calculate=(
            calculate_registered_health_model
        ),
        build_parameter_records=(
            build_registered_health_model_parameter_records
        ),
        supported_input_source_types=(
            "questionnaire_answer",
            "sensor_measurement",
            "manual_measurement",
            "prepared_domain_output",
            "previous_model_parameter",
            "verified_external_record",
        ),
        parameter_definition_provider=(
            list_health_model_parameter_definitions
        ),
        status="active",
        metadata={
            "domain": "psychophysical_state",
            "input_requirement": (
                "preassembled_model_input_contract"
            ),
            "automatic_questionnaire_execution": (
                False
            ),
            "questionnaire_dependency": None,
        },
    )


def register_health_model(
    *,
    replace: bool = False,
) -> RegisteredCalculationModel:
    return register_calculation_model(
        build_registered_health_model(),
        replace=replace,
    )
