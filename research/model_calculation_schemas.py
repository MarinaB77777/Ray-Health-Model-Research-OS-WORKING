from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4


MODEL_CALCULATION_RUN_SCHEMA_VERSION = (
    "model-calculation-run-1"
)

MODEL_CALCULATION_INPUT_REFERENCE_SCHEMA_VERSION = (
    "model-calculation-input-reference-1"
)


class ModelCalculationStatus(str, Enum):
    CREATED = "CREATED"
    INPUT_READY = "INPUT_READY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    NOT_ENOUGH_DATA = "NOT_ENOUGH_DATA"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    INVALIDATED = "INVALIDATED"


@dataclass
class ModelCalculationInputReference:
    input_reference_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    schema_version: str = (
        MODEL_CALCULATION_INPUT_REFERENCE_SCHEMA_VERSION
    )

    source_type: str = ""
    source_record_type: str = ""

    source_record_id: str | None = None
    source_session_id: str | None = None
    source_submission_id: str | None = None

    participant_id: str | None = None
    subject_link_id: str | None = None

    study_id: str | None = None
    domain_id: str | None = None

    observation_time: str | None = None
    global_time_reference: str | None = None

    selected_variable_codes: list[str] = field(
        default_factory=list
    )

    selected_record_ids: list[str] = field(
        default_factory=list
    )

    provenance: dict = field(
        default_factory=dict
    )


@dataclass
class ModelCalculationRun:
    calculation_run_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    schema_version: str = (
        MODEL_CALCULATION_RUN_SCHEMA_VERSION
    )

    status: ModelCalculationStatus = (
        ModelCalculationStatus.CREATED
    )

    model_id: str = ""
    model_version: str = ""
    calculation_version: str = ""
    input_contract_version: str = ""

    created_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )

    updated_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )

    started_at: datetime | None = None
    completed_at: datetime | None = None
    invalidated_at: datetime | None = None

    participant_id: str | None = None
    subject_link_id: str | None = None

    calculation_scope: str = "participant"
    observation_unit: str = "calculation_run"

    input_references: list[
        ModelCalculationInputReference
    ] = field(default_factory=list)

    input_snapshot: dict = field(
        default_factory=dict
    )

    input_quality: dict = field(
        default_factory=dict
    )

    input_validation: dict = field(
        default_factory=dict
    )

    calculation_result: dict = field(
        default_factory=dict
    )

    parameter_records: list[dict] = field(
        default_factory=list
    )

    parameter_record_count: int = 0

    uncertainty: dict = field(
        default_factory=dict
    )

    warnings: list[dict] = field(
        default_factory=list
    )

    reason_codes: list[str] = field(
        default_factory=list
    )

    provenance: dict = field(
        default_factory=dict
    )

    invalidated: bool = False
    invalidation_reason: str | None = None

    failure: dict = field(
        default_factory=dict
    )

    def refresh_parameter_record_count(
        self,
    ) -> None:
        self.parameter_record_count = len(
            self.parameter_records
        )

    def mark_updated(self) -> None:
        self.updated_at = datetime.now(UTC)

    def mark_running(self) -> None:
        now = datetime.now(UTC)

        self.status = (
            ModelCalculationStatus.RUNNING
        )

        self.started_at = now
        self.updated_at = now

    def mark_completed(self) -> None:
        now = datetime.now(UTC)

        self.refresh_parameter_record_count()

        self.status = (
            ModelCalculationStatus.COMPLETED
        )

        self.completed_at = now
        self.updated_at = now

    def mark_not_enough_data(
        self,
        *,
        reason_codes: list[str] | None = None,
    ) -> None:
        now = datetime.now(UTC)

        self.refresh_parameter_record_count()

        self.status = (
            ModelCalculationStatus.NOT_ENOUGH_DATA
        )

        self.completed_at = now
        self.updated_at = now

        if reason_codes is not None:
            self.reason_codes = list(
                reason_codes
            )

    def mark_failed(
        self,
        *,
        error_type: str,
        message: str,
    ) -> None:
        now = datetime.now(UTC)

        self.status = (
            ModelCalculationStatus.FAILED
        )

        self.completed_at = now
        self.updated_at = now

        self.failure = {
            "error_type": error_type,
            "message": message,
        }

    def invalidate(
        self,
        *,
        reason: str,
    ) -> None:
        now = datetime.now(UTC)

        self.invalidated = True
        self.invalidation_reason = reason
        self.invalidated_at = now
        self.updated_at = now

        self.status = (
            ModelCalculationStatus.INVALIDATED
        )


def validate_model_calculation_run(
    run: ModelCalculationRun,
) -> dict:
    errors = []
    warnings = []

    if not run.model_id:
        errors.append({
            "field": "model_id",
            "code": "MODEL_ID_REQUIRED",
        })

    if not run.model_version:
        errors.append({
            "field": "model_version",
            "code": "MODEL_VERSION_REQUIRED",
        })

    if not run.calculation_version:
        errors.append({
            "field": "calculation_version",
            "code": (
                "CALCULATION_VERSION_REQUIRED"
            ),
        })

    if not run.input_contract_version:
        errors.append({
            "field": "input_contract_version",
            "code": (
                "INPUT_CONTRACT_VERSION_REQUIRED"
            ),
        })

    if (
        run.parameter_record_count
        != len(run.parameter_records)
    ):
        errors.append({
            "field": "parameter_record_count",
            "code": (
                "PARAMETER_RECORD_COUNT_MISMATCH"
            ),
            "declared_count": (
                run.parameter_record_count
            ),
            "actual_count": len(
                run.parameter_records
            ),
        })

    for index, reference in enumerate(
        run.input_references
    ):
        if not reference.source_type:
            errors.append({
                "field": (
                    f"input_references[{index}]"
                    ".source_type"
                ),
                "code": (
                    "INPUT_SOURCE_TYPE_REQUIRED"
                ),
            })

        if not reference.source_record_type:
            errors.append({
                "field": (
                    f"input_references[{index}]"
                    ".source_record_type"
                ),
                "code": (
                    "INPUT_SOURCE_RECORD_TYPE_REQUIRED"
                ),
            })

        if not any([
            reference.source_record_id,
            reference.source_session_id,
            reference.source_submission_id,
            reference.selected_record_ids,
        ]):
            warnings.append({
                "field": (
                    f"input_references[{index}]"
                ),
                "code": (
                    "INPUT_REFERENCE_HAS_NO_RECORD_ID"
                ),
            })

    model_ids_in_records = {
        record.get("model_id")
        for record in run.parameter_records
        if record.get("model_id")
    }

    if (
        model_ids_in_records
        and model_ids_in_records != {
            run.model_id
        }
    ):
        errors.append({
            "field": "parameter_records",
            "code": (
                "PARAMETER_RECORD_MODEL_ID_MISMATCH"
            ),
            "run_model_id": run.model_id,
            "record_model_ids": sorted(
                model_ids_in_records
            ),
        })

    calculation_versions = {
        str(
            record.get(
                "calculation_version"
            )
        )
        for record in run.parameter_records
        if record.get(
            "calculation_version"
        ) is not None
    }

    if (
        calculation_versions
        and calculation_versions != {
            str(run.calculation_version)
        }
    ):
        errors.append({
            "field": "parameter_records",
            "code": (
                "PARAMETER_RECORD_CALCULATION_VERSION_MISMATCH"
            ),
            "run_calculation_version": (
                run.calculation_version
            ),
            "record_calculation_versions": sorted(
                calculation_versions
            ),
        })

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
    }
