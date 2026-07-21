from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

from research.model_calculation_schemas import (
    ModelCalculationInputReference,
    ModelCalculationRun,
    ModelCalculationStatus,
    validate_model_calculation_run,
)
from research.model_calculation_store import (
    ModelCalculationPersistentStore,
)
from research.model_registry import (
    RegisteredCalculationModel,
    get_registered_calculation_model,
)


class ModelCalculationService:
    def __init__(
        self,
        store: ModelCalculationPersistentStore,
    ):
        self.store = store

    def create_run(
        self,
        *,
        model_id: str,
        model_version: str,
        calculation_version: str,
        participant_id: str | None = None,
        subject_link_id: str | None = None,
        calculation_scope: str = "participant",
        observation_unit: str = "calculation_run",
        input_references: (
            list[ModelCalculationInputReference]
            | None
        ) = None,
        input_snapshot: dict | None = None,
        input_quality: dict | None = None,
        provenance: dict | None = None,
    ) -> ModelCalculationRun:
        model = self._require_model(
            model_id=model_id,
            model_version=model_version,
            calculation_version=(
                calculation_version
            ),
        )

        run = ModelCalculationRun(
            model_id=model.model_id,
            model_version=model.model_version,
            calculation_version=(
                model.calculation_version
            ),
            input_contract_version=(
                model.input_contract_version
            ),
            participant_id=participant_id,
            subject_link_id=subject_link_id,
            calculation_scope=calculation_scope,
            observation_unit=observation_unit,
            input_references=list(
                input_references or []
            ),
            input_snapshot=deepcopy(
                input_snapshot or {}
            ),
            input_quality=deepcopy(
                input_quality or {}
            ),
            provenance={
                "service": (
                    "research."
                    "model_calculation_service"
                ),
                "model_registry_identity": {
                    "model_id": model.model_id,
                    "model_version": (
                        model.model_version
                    ),
                    "calculation_version": (
                        model.calculation_version
                    ),
                },
                **deepcopy(provenance or {}),
            },
        )

        run.status = (
            ModelCalculationStatus.INPUT_READY
            if run.input_snapshot
            or run.input_references
            else ModelCalculationStatus.CREATED
        )

        return self.store.save(run)

    def run_calculation(
        self,
        calculation_run_id: str,
    ) -> ModelCalculationRun:
        run = self.store.get(
            calculation_run_id
        )

        if run is None:
            raise KeyError(
                "Model calculation run not found: "
                f"{calculation_run_id}"
            )

        if run.invalidated:
            raise ValueError({
                "error": (
                    "MODEL_CALCULATION_RUN_INVALIDATED"
                ),
                "calculation_run_id": (
                    calculation_run_id
                ),
            })

        if run.status not in {
            ModelCalculationStatus.CREATED,
            ModelCalculationStatus.INPUT_READY,
            ModelCalculationStatus.FAILED,
            ModelCalculationStatus.NOT_ENOUGH_DATA,
        }:
            raise ValueError({
                "error": (
                    "MODEL_CALCULATION_RUN_STATUS_INVALID"
                ),
                "calculation_run_id": (
                    calculation_run_id
                ),
                "status": run.status.value,
            })

        model = self._require_model(
            model_id=run.model_id,
            model_version=run.model_version,
            calculation_version=(
                run.calculation_version
            ),
        )

        run.mark_running()
        run.failure = {}
        run.reason_codes = []
        run.warnings = []
        run.parameter_records = []
        run.parameter_record_count = 0

        self.store.save(run)

        try:
            model_input = self._build_model_input(
                model=model,
                run=run,
            )

            run.input_snapshot = deepcopy(
                model_input
            )

            input_validation = (
                self._validate_model_input(
                    model=model,
                    model_input=model_input,
                )
            )

            run.input_validation = deepcopy(
                input_validation
            )

            if (
                input_validation.get("valid")
                is not True
            ):
                reason_codes = self._validation_reason_codes(
                    input_validation
                )

                run.mark_not_enough_data(
                    reason_codes=reason_codes,
                )

                run.warnings = list(
                    input_validation.get(
                        "warnings",
                        [],
                    )
                )

                return self.store.save(run)

            calculation_result = (
                model.calculate(
                    deepcopy(model_input)
                )
            )

            if not isinstance(
                calculation_result,
                dict,
            ):
                raise TypeError(
                    "Registered model calculator "
                    "must return a dict"
                )

            run.calculation_result = deepcopy(
                calculation_result
            )

            observation_time = (
                self._resolve_observation_time(
                    run
                )
            )

            parameter_records = (
                model.build_parameter_records(
                    calculation_run_id=(
                        run.calculation_run_id
                    ),
                    session_id=(
                        self._first_source_session_id(
                            run
                        )
                    ),
                    participant_id=(
                        run.participant_id
                    ),
                    subject_link_id=(
                        run.subject_link_id
                    ),
                    model_id=run.model_id,
                    model_version=(
                        run.model_version
                    ),
                    calculation_version=(
                        run.calculation_version
                    ),
                    analysis_output=(
                        calculation_result
                    ),
                    observation_time=(
                        observation_time
                    ),
                    input_references=deepcopy(
                        run.input_references
                    ),
                    input_snapshot=deepcopy(
                        run.input_snapshot
                    ),
                )
            )

            if not isinstance(
                parameter_records,
                list,
            ):
                raise TypeError(
                    "Registered parameter record "
                    "builder must return a list"
                )

            normalized_records = (
                self._normalize_parameter_records(
                    run=run,
                    records=parameter_records,
                )
            )

            run.parameter_records = (
                normalized_records
            )

            calculation_status = str(
                calculation_result.get(
                    "status",
                    "",
                )
            ).strip().upper()

            if calculation_status in {
                "NOT_ENOUGH_DATA",
                "NOT ENOUGH DATA",
            }:
                reason_codes = list(
                    calculation_result.get(
                        "reason_codes",
                        [],
                    )
                )

                if not reason_codes:
                    reason_codes = [
                        "MODEL_RESULT_NOT_ENOUGH_DATA"
                    ]

                run.mark_not_enough_data(
                    reason_codes=reason_codes,
                )
            else:
                run.mark_completed()

            validation = (
                validate_model_calculation_run(
                    run
                )
            )

            if validation["valid"] is not True:
                raise ValueError({
                    "error": (
                        "MODEL_CALCULATION_RESULT_INVALID"
                    ),
                    "validation": validation,
                })

            return self.store.save(run)

        except Exception as error:
            run.mark_failed(
                error_type=type(error).__name__,
                message=str(error),
            )

            self.store.save(
                run,
                validate=False,
            )

            raise

    def get_run(
        self,
        calculation_run_id: str,
    ) -> ModelCalculationRun | None:
        return self.store.get(
            calculation_run_id
        )

    def list_runs(
        self,
        **filters,
    ) -> list[ModelCalculationRun]:
        return self.store.list_runs(
            **filters
        )

    def list_parameter_records(
        self,
        **filters,
    ) -> list[dict]:
        return self.store.list_parameter_records(
            **filters
        )

    def _require_model(
        self,
        *,
        model_id: str,
        model_version: str,
        calculation_version: str,
    ) -> RegisteredCalculationModel:
        model = (
            get_registered_calculation_model(
                model_id=model_id,
                model_version=model_version,
                calculation_version=(
                    calculation_version
                ),
            )
        )

        if model is None:
            raise KeyError({
                "error": (
                    "CALCULATION_MODEL_NOT_REGISTERED"
                ),
                "model_id": model_id,
                "model_version": (
                    model_version
                ),
                "calculation_version": (
                    calculation_version
                ),
            })

        return model

    @staticmethod
    def _build_model_input(
        *,
        model: RegisteredCalculationModel,
        run: ModelCalculationRun,
    ) -> dict:
        model_input = model.build_input(
            input_snapshot=deepcopy(
                run.input_snapshot
            ),
            input_references=deepcopy(
                run.input_references
            ),
            participant_id=run.participant_id,
            subject_link_id=(
                run.subject_link_id
            ),
            calculation_run_id=(
                run.calculation_run_id
            ),
        )

        if not isinstance(model_input, dict):
            raise TypeError(
                "Registered model input builder "
                "must return a dict"
            )

        return model_input

    @staticmethod
    def _validate_model_input(
        *,
        model: RegisteredCalculationModel,
        model_input: dict,
    ) -> dict:
        if model.validate_input is None:
            return {
                "valid": True,
                "errors": [],
                "warnings": [],
                "reason_codes": [],
            }

        validation = model.validate_input(
            deepcopy(model_input)
        )

        if not isinstance(validation, dict):
            raise TypeError(
                "Registered model input validator "
                "must return a dict"
            )

        return {
            "valid": bool(
                validation.get("valid")
            ),
            "errors": list(
                validation.get(
                    "errors",
                    [],
                )
            ),
            "warnings": list(
                validation.get(
                    "warnings",
                    [],
                )
            ),
            "reason_codes": list(
                validation.get(
                    "reason_codes",
                    [],
                )
            ),
            **{
                key: value
                for key, value
                in validation.items()
                if key not in {
                    "valid",
                    "errors",
                    "warnings",
                    "reason_codes",
                }
            },
        }

    @staticmethod
    def _validation_reason_codes(
        validation: dict,
    ) -> list[str]:
        reason_codes = list(
            validation.get(
                "reason_codes",
                [],
            )
        )

        for error in validation.get(
            "errors",
            [],
        ):
            if not isinstance(error, dict):
                continue

            code = error.get("code")

            if (
                code
                and code not in reason_codes
            ):
                reason_codes.append(code)

        if not reason_codes:
            reason_codes.append(
                "MODEL_INPUT_VALIDATION_FAILED"
            )

        return reason_codes

    @staticmethod
    def _first_source_session_id(
        run: ModelCalculationRun,
    ) -> str | None:
        for reference in (
            run.input_references
        ):
            if reference.source_session_id:
                return (
                    reference.source_session_id
                )

        return None

    @staticmethod
    def _resolve_observation_time(
        run: ModelCalculationRun,
    ) -> str:
        observation_times = [
            reference.observation_time
            for reference
            in run.input_references
            if reference.observation_time
        ]

        if observation_times:
            return max(
                str(value)
                for value in observation_times
            )

        return datetime.now(
            UTC
        ).isoformat()

    @staticmethod
    def _normalize_parameter_records(
        *,
        run: ModelCalculationRun,
        records: list[dict],
    ) -> list[dict]:
        normalized = []

        for index, record in enumerate(
            records
        ):
            if not isinstance(record, dict):
                raise TypeError(
                    "Parameter record at index "
                    f"{index} is not a dict"
                )

            record_model_id = record.get(
                "model_id"
            )

            if (
                record_model_id is not None
                and record_model_id
                != run.model_id
            ):
                raise ValueError({
                    "error": (
                        "PARAMETER_RECORD_MODEL_ID_MISMATCH"
                    ),
                    "record_index": index,
                    "run_model_id": (
                        run.model_id
                    ),
                    "record_model_id": (
                        record_model_id
                    ),
                })

            record_calculation_version = (
                record.get(
                    "calculation_version"
                )
            )

            if (
                record_calculation_version
                is not None
                and str(
                    record_calculation_version
                )
                != str(
                    run.calculation_version
                )
            ):
                raise ValueError({
                    "error": (
                        "PARAMETER_RECORD_CALCULATION_"
                        "VERSION_MISMATCH"
                    ),
                    "record_index": index,
                    "run_calculation_version": (
                        run.calculation_version
                    ),
                    "record_calculation_version": (
                        record_calculation_version
                    ),
                })

            normalized.append({
                **record,
                "calculation_run_id": (
                    run.calculation_run_id
                ),
                "model_id": run.model_id,
                "model_version": (
                    run.model_version
                ),
                "calculation_version": (
                    run.calculation_version
                ),
                "participant_id": (
                    record.get(
                        "participant_id"
                    )
                    or run.participant_id
                ),
                "subject_link_id": (
                    record.get(
                        "subject_link_id"
                    )
                    or run.subject_link_id
                ),
            })

        return normalized
