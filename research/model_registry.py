from copy import deepcopy
from dataclasses import dataclass
from typing import Callable, Any


MODEL_REGISTRY_SCHEMA_VERSION = (
    "calculation-model-registry-1"
)


ModelInputBuilder = Callable[..., dict]
ModelCalculator = Callable[[dict], dict]
ModelParameterRecordBuilder = Callable[..., list[dict]]
ModelInputValidator = Callable[[dict], dict]


@dataclass(frozen=True)
class RegisteredCalculationModel:
    model_id: str
    model_version: str
    calculation_version: str
    input_contract_version: str

    title: dict

    build_input: ModelInputBuilder
    calculate: ModelCalculator
    build_parameter_records: (
        ModelParameterRecordBuilder
    )

    validate_input: (
        ModelInputValidator | None
    ) = None

    supported_input_source_types: tuple[
        str,
        ...
    ] = ()

    parameter_definition_provider: (
        Callable[..., list[dict]]
        | None
    ) = None

    status: str = "active"

    metadata: dict | None = None


_REGISTERED_MODELS: dict[
    tuple[str, str, str],
    RegisteredCalculationModel,
] = {}


def _model_key(
    *,
    model_id: str,
    model_version: str,
    calculation_version: str,
) -> tuple[str, str, str]:
    return (
        str(model_id).strip(),
        str(model_version).strip(),
        str(calculation_version).strip(),
    )


def validate_registered_model(
    model: RegisteredCalculationModel,
) -> dict:
    errors = []
    warnings = []

    if not model.model_id.strip():
        errors.append({
            "field": "model_id",
            "code": "MODEL_ID_REQUIRED",
        })

    if not model.model_version.strip():
        errors.append({
            "field": "model_version",
            "code": "MODEL_VERSION_REQUIRED",
        })

    if not model.calculation_version.strip():
        errors.append({
            "field": "calculation_version",
            "code": (
                "CALCULATION_VERSION_REQUIRED"
            ),
        })

    if not model.input_contract_version.strip():
        errors.append({
            "field": "input_contract_version",
            "code": (
                "INPUT_CONTRACT_VERSION_REQUIRED"
            ),
        })

    if not isinstance(model.title, dict):
        errors.append({
            "field": "title",
            "code": (
                "MULTILINGUAL_TITLE_REQUIRED"
            ),
        })

    elif not any(
        str(value or "").strip()
        for value in model.title.values()
    ):
        errors.append({
            "field": "title",
            "code": "MODEL_TITLE_REQUIRED",
        })

    if not callable(model.build_input):
        errors.append({
            "field": "build_input",
            "code": (
                "MODEL_INPUT_BUILDER_REQUIRED"
            ),
        })

    if not callable(model.calculate):
        errors.append({
            "field": "calculate",
            "code": (
                "MODEL_CALCULATOR_REQUIRED"
            ),
        })

    if not callable(
        model.build_parameter_records
    ):
        errors.append({
            "field": (
                "build_parameter_records"
            ),
            "code": (
                "PARAMETER_RECORD_BUILDER_REQUIRED"
            ),
        })

    if (
        model.validate_input is not None
        and not callable(model.validate_input)
    ):
        errors.append({
            "field": "validate_input",
            "code": (
                "MODEL_INPUT_VALIDATOR_INVALID"
            ),
        })

    if (
        model.parameter_definition_provider
        is not None
        and not callable(
            model.parameter_definition_provider
        )
    ):
        errors.append({
            "field": (
                "parameter_definition_provider"
            ),
            "code": (
                "PARAMETER_DEFINITION_PROVIDER_INVALID"
            ),
        })

    if model.status not in {
        "active",
        "draft",
        "disabled",
        "deprecated",
    }:
        errors.append({
            "field": "status",
            "code": (
                "UNSUPPORTED_MODEL_STATUS"
            ),
            "value": model.status,
        })

    if not model.supported_input_source_types:
        warnings.append({
            "field": (
                "supported_input_source_types"
            ),
            "code": (
                "MODEL_INPUT_SOURCE_TYPES_EMPTY"
            ),
        })

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
    }


def register_calculation_model(
    model: RegisteredCalculationModel,
    *,
    replace: bool = False,
) -> RegisteredCalculationModel:
    validation = validate_registered_model(
        model
    )

    if validation["valid"] is not True:
        raise ValueError({
            "error": (
                "CALCULATION_MODEL_INVALID"
            ),
            "validation": validation,
        })

    key = _model_key(
        model_id=model.model_id,
        model_version=model.model_version,
        calculation_version=(
            model.calculation_version
        ),
    )

    if key in _REGISTERED_MODELS and not replace:
        raise ValueError({
            "error": (
                "CALCULATION_MODEL_ALREADY_REGISTERED"
            ),
            "model_id": model.model_id,
            "model_version": (
                model.model_version
            ),
            "calculation_version": (
                model.calculation_version
            ),
        })

    _REGISTERED_MODELS[key] = model

    return model


def get_registered_calculation_model(
    *,
    model_id: str,
    model_version: str | None = None,
    calculation_version: str | None = None,
    include_inactive: bool = False,
) -> RegisteredCalculationModel | None:
    candidates = [
        model
        for key, model
        in _REGISTERED_MODELS.items()
        if key[0] == str(model_id).strip()
    ]

    if model_version is not None:
        candidates = [
            model
            for model in candidates
            if model.model_version
            == str(model_version).strip()
        ]

    if calculation_version is not None:
        candidates = [
            model
            for model in candidates
            if model.calculation_version
            == str(
                calculation_version
            ).strip()
        ]

    if not include_inactive:
        candidates = [
            model
            for model in candidates
            if model.status == "active"
        ]

    if not candidates:
        return None

    if (
        model_version is None
        or calculation_version is None
    ):
        if len(candidates) != 1:
            return None

    return candidates[0]


def list_registered_calculation_models(
    *,
    include_inactive: bool = False,
) -> list[dict]:
    models = []

    for model in _REGISTERED_MODELS.values():
        if (
            not include_inactive
            and model.status != "active"
        ):
            continue

        definitions = []

        if (
            model.parameter_definition_provider
            is not None
        ):
            provided = (
                model.parameter_definition_provider()
            )

            if isinstance(provided, list):
                definitions = provided

        models.append({
            "registry_schema_version": (
                MODEL_REGISTRY_SCHEMA_VERSION
            ),
            "model_id": model.model_id,
            "model_version": (
                model.model_version
            ),
            "calculation_version": (
                model.calculation_version
            ),
            "input_contract_version": (
                model.input_contract_version
            ),
            "title": deepcopy(model.title),
            "status": model.status,
            "supported_input_source_types": (
                list(
                    model.supported_input_source_types
                )
            ),
            "parameter_definition_count": (
                len(definitions)
            ),
            "metadata": deepcopy(
                model.metadata or {}
            ),
            "validation": (
                validate_registered_model(model)
            ),
        })

    return sorted(
        models,
        key=lambda item: (
            item["model_id"],
            item["model_version"],
            item["calculation_version"],
        ),
    )


def clear_registered_calculation_models() -> None:
    _REGISTERED_MODELS.clear()
