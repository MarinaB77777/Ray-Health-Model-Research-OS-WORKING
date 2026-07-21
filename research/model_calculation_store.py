import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable

from research.model_calculation_schemas import (
    ModelCalculationInputReference,
    ModelCalculationRun,
    ModelCalculationStatus,
    validate_model_calculation_run,
)


MODEL_CALCULATION_STORE_SCHEMA_VERSION = (
    "model-calculation-store-1"
)


class ModelCalculationPersistentStore:
    def __init__(
        self,
        storage_path: str | Path,
    ):
        self.storage_path = Path(storage_path)

        self.storage_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._runs: dict[
            str,
            ModelCalculationRun,
        ] = {}

        self._load()

    def save(
        self,
        run: ModelCalculationRun,
        *,
        validate: bool = True,
    ) -> ModelCalculationRun:
        run.refresh_parameter_record_count()
        run.mark_updated()

        if validate:
            validation = (
                validate_model_calculation_run(
                    run
                )
            )

            if validation["valid"] is not True:
                raise ValueError({
                    "error": (
                        "MODEL_CALCULATION_RUN_INVALID"
                    ),
                    "calculation_run_id": (
                        run.calculation_run_id
                    ),
                    "validation": validation,
                })

        self._runs[
            run.calculation_run_id
        ] = run

        self._persist()

        return run

    def get(
        self,
        calculation_run_id: str,
    ) -> ModelCalculationRun | None:
        return self._runs.get(
            calculation_run_id
        )

    def exists(
        self,
        calculation_run_id: str,
    ) -> bool:
        return (
            calculation_run_id
            in self._runs
        )

    def list_all(
        self,
    ) -> list[ModelCalculationRun]:
        return sorted(
            self._runs.values(),
            key=lambda run: (
                run.created_at,
                run.calculation_run_id,
            ),
        )

    def list_runs(
        self,
        *,
        model_id: str | None = None,
        model_version: str | None = None,
        calculation_version: str | None = None,
        status: (
            ModelCalculationStatus
            | str
            | None
        ) = None,
        participant_id: str | None = None,
        subject_link_id: str | None = None,
        source_session_id: str | None = None,
        include_invalidated: bool = False,
    ) -> list[ModelCalculationRun]:
        runs = self.list_all()

        if not include_invalidated:
            runs = [
                run
                for run in runs
                if not run.invalidated
                and run.status
                != ModelCalculationStatus.INVALIDATED
            ]

        if model_id is not None:
            runs = [
                run
                for run in runs
                if run.model_id == model_id
            ]

        if model_version is not None:
            runs = [
                run
                for run in runs
                if (
                    run.model_version
                    == model_version
                )
            ]

        if calculation_version is not None:
            runs = [
                run
                for run in runs
                if (
                    run.calculation_version
                    == calculation_version
                )
            ]

        if status is not None:
            normalized_status = (
                status
                if isinstance(
                    status,
                    ModelCalculationStatus,
                )
                else ModelCalculationStatus(
                    status
                )
            )

            runs = [
                run
                for run in runs
                if run.status
                == normalized_status
            ]

        if participant_id is not None:
            runs = [
                run
                for run in runs
                if run.participant_id
                == participant_id
            ]

        if subject_link_id is not None:
            runs = [
                run
                for run in runs
                if run.subject_link_id
                == subject_link_id
            ]

        if source_session_id is not None:
            runs = [
                run
                for run in runs
                if any(
                    reference.source_session_id
                    == source_session_id
                    for reference
                    in run.input_references
                )
            ]

        return runs

    def list_parameter_records(
        self,
        *,
        model_id: str | None = None,
        parameter_id: str | None = None,
        parameter_code: str | None = None,
        calculation_run_id: str | None = None,
        participant_id: str | None = None,
        subject_link_id: str | None = None,
        calculation_status: str | None = None,
        include_invalidated_runs: bool = False,
    ) -> list[dict]:
        if calculation_run_id is not None:
            run = self.get(
                calculation_run_id
            )

            runs = [run] if run else []
        else:
            runs = self.list_runs(
                model_id=model_id,
                participant_id=participant_id,
                subject_link_id=(
                    subject_link_id
                ),
                include_invalidated=(
                    include_invalidated_runs
                ),
            )

        records = []

        for run in runs:
            if run is None:
                continue

            if (
                not include_invalidated_runs
                and (
                    run.invalidated
                    or run.status
                    == ModelCalculationStatus.INVALIDATED
                )
            ):
                continue

            for record in (
                run.parameter_records
                or []
            ):
                if (
                    model_id is not None
                    and record.get("model_id")
                    != model_id
                ):
                    continue

                if (
                    parameter_id is not None
                    and record.get(
                        "parameter_id"
                    )
                    != parameter_id
                ):
                    continue

                if (
                    parameter_code is not None
                    and record.get(
                        "parameter_code"
                    )
                    != parameter_code
                ):
                    continue

                if (
                    calculation_status
                    is not None
                    and record.get(
                        "calculation_status"
                    )
                    != calculation_status
                ):
                    continue

                records.append({
                    **record,
                    "calculation_run_id": (
                        run.calculation_run_id
                    ),
                    "run_status": (
                        run.status.value
                    ),
                    "run_created_at": (
                        run.created_at.isoformat()
                    ),
                    "run_completed_at": (
                        run.completed_at.isoformat()
                        if run.completed_at
                        else None
                    ),
                })

        return sorted(
            records,
            key=lambda record: (
                str(
                    record.get(
                        "observation_time"
                    )
                    or ""
                ),
                str(
                    record.get(
                        "calculation_run_id"
                    )
                    or ""
                ),
                str(
                    record.get(
                        "parameter_record_id"
                    )
                    or ""
                ),
            ),
        )

    def invalidate(
        self,
        calculation_run_id: str,
        *,
        reason: str,
    ) -> ModelCalculationRun:
        run = self.get(
            calculation_run_id
        )

        if run is None:
            raise KeyError(
                "Model calculation run not found: "
                f"{calculation_run_id}"
            )

        run.invalidate(reason=reason)

        return self.save(
            run,
            validate=True,
        )

    def _persist(
        self,
    ) -> None:
        payload = {
            "schema_version": (
                MODEL_CALCULATION_STORE_SCHEMA_VERSION
            ),
            "run_count": len(
                self._runs
            ),
            "runs": [
                self._serialize_run(run)
                for run in self.list_all()
            ],
        }

        temporary_path = (
            self.storage_path.with_suffix(
                self.storage_path.suffix
                + ".tmp"
            )
        )

        temporary_path.write_text(
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        temporary_path.replace(
            self.storage_path
        )

    def _load(
        self,
    ) -> None:
        if not self.storage_path.exists():
            return

        raw = self.storage_path.read_text(
            encoding="utf-8"
        ).strip()

        if not raw:
            return

        payload = json.loads(raw)

        # Compatibility with a possible early
        # list-only storage representation.
        if isinstance(payload, list):
            raw_runs = payload

        elif isinstance(payload, dict):
            raw_runs = payload.get(
                "runs",
                [],
            )

        else:
            raise ValueError(
                "Model calculation storage must "
                "contain a JSON object or list"
            )

        if not isinstance(raw_runs, list):
            raise ValueError(
                "Model calculation storage runs "
                "must be a JSON list"
            )

        loaded_runs = {}

        for item in raw_runs:
            if not isinstance(item, dict):
                continue

            run = self._deserialize_run(
                item
            )

            loaded_runs[
                run.calculation_run_id
            ] = run

        self._runs = loaded_runs

    def _serialize_run(
        self,
        run: ModelCalculationRun,
    ) -> dict:
        data = asdict(run)

        data["status"] = (
            run.status.value
        )

        for field_name in (
            "created_at",
            "updated_at",
            "started_at",
            "completed_at",
            "invalidated_at",
        ):
            value = getattr(
                run,
                field_name,
            )

            data[field_name] = (
                value.isoformat()
                if value is not None
                else None
            )

        return data

    def _deserialize_run(
        self,
        data: dict,
    ) -> ModelCalculationRun:
        raw_references = data.get(
            "input_references",
            [],
        )

        input_references = []

        for item in raw_references:
            if not isinstance(item, dict):
                continue

            input_references.append(
                ModelCalculationInputReference(
                    input_reference_id=(
                        item.get(
                            "input_reference_id"
                        )
                    ),
                    schema_version=(
                        item.get(
                            "schema_version"
                        )
                        or (
                            "model-calculation-"
                            "input-reference-1"
                        )
                    ),
                    source_type=(
                        item.get(
                            "source_type",
                            "",
                        )
                    ),
                    source_record_type=(
                        item.get(
                            "source_record_type",
                            "",
                        )
                    ),
                    source_record_id=(
                        item.get(
                            "source_record_id"
                        )
                    ),
                    source_session_id=(
                        item.get(
                            "source_session_id"
                        )
                    ),
                    source_submission_id=(
                        item.get(
                            "source_submission_id"
                        )
                    ),
                    participant_id=(
                        item.get(
                            "participant_id"
                        )
                    ),
                    subject_link_id=(
                        item.get(
                            "subject_link_id"
                        )
                    ),
                    study_id=(
                        item.get("study_id")
                    ),
                    domain_id=(
                        item.get("domain_id")
                    ),
                    observation_time=(
                        item.get(
                            "observation_time"
                        )
                    ),
                    global_time_reference=(
                        item.get(
                            "global_time_reference"
                        )
                    ),
                    selected_variable_codes=(
                        list(
                            item.get(
                                "selected_variable_codes",
                                [],
                            )
                        )
                    ),
                    selected_record_ids=(
                        list(
                            item.get(
                                "selected_record_ids",
                                [],
                            )
                        )
                    ),
                    provenance=dict(
                        item.get(
                            "provenance",
                            {},
                        )
                    ),
                )
            )

        run = ModelCalculationRun(
            calculation_run_id=data[
                "calculation_run_id"
            ],
            schema_version=data.get(
                "schema_version",
                "model-calculation-run-1",
            ),
            status=ModelCalculationStatus(
                data.get(
                    "status",
                    ModelCalculationStatus.CREATED.value,
                )
            ),
            model_id=data.get(
                "model_id",
                "",
            ),
            model_version=data.get(
                "model_version",
                "",
            ),
            calculation_version=data.get(
                "calculation_version",
                "",
            ),
            input_contract_version=data.get(
                "input_contract_version",
                "",
            ),
            created_at=self._parse_datetime(
                data.get("created_at")
            ),
            updated_at=self._parse_datetime(
                data.get("updated_at")
            ),
            started_at=self._parse_datetime(
                data.get("started_at"),
                required=False,
            ),
            completed_at=self._parse_datetime(
                data.get("completed_at"),
                required=False,
            ),
            invalidated_at=self._parse_datetime(
                data.get("invalidated_at"),
                required=False,
            ),
            participant_id=data.get(
                "participant_id"
            ),
            subject_link_id=data.get(
                "subject_link_id"
            ),
            calculation_scope=data.get(
                "calculation_scope",
                "participant",
            ),
            observation_unit=data.get(
                "observation_unit",
                "calculation_run",
            ),
            input_references=(
                input_references
            ),
            input_snapshot=dict(
                data.get(
                    "input_snapshot",
                    {},
                )
            ),
            input_quality=dict(
                data.get(
                    "input_quality",
                    {},
                )
            ),
            input_validation=dict(
                data.get(
                    "input_validation",
                    {},
                )
            ),
            calculation_result=dict(
                data.get(
                    "calculation_result",
                    {},
                )
            ),
            parameter_records=list(
                data.get(
                    "parameter_records",
                    [],
                )
            ),
            parameter_record_count=int(
                data.get(
                    "parameter_record_count",
                    0,
                )
            ),
            uncertainty=dict(
                data.get(
                    "uncertainty",
                    {},
                )
            ),
            warnings=list(
                data.get(
                    "warnings",
                    [],
                )
            ),
            reason_codes=list(
                data.get(
                    "reason_codes",
                    [],
                )
            ),
            provenance=dict(
                data.get(
                    "provenance",
                    {},
                )
            ),
            invalidated=bool(
                data.get(
                    "invalidated",
                    False,
                )
            ),
            invalidation_reason=(
                data.get(
                    "invalidation_reason"
                )
            ),
            failure=dict(
                data.get(
                    "failure",
                    {},
                )
            ),
        )

        run.refresh_parameter_record_count()

        return run

    @staticmethod
    def _parse_datetime(
        value: str | datetime | None,
        *,
        required: bool = True,
    ) -> datetime | None:
        if isinstance(value, datetime):
            return value

        if value:
            return datetime.fromisoformat(
                value
            )

        if required:
            raise ValueError(
                "Required model calculation "
                "datetime is missing"
            )

        return None
