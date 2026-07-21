from typing import Any
from research.analyses.health_model.model_parameter_registry import (
    get_model_parameter_definition,
)


MODEL_PARAMETER_CATALOG_SCHEMA_VERSION = (
    "health-model-parameter-catalog-1"
)
EXCLUDED_PARAMETER_PREFIXES = (
    "calculator_input.",
)


def _is_available_model_parameter(
    parameter_code: str,
) -> bool:
    return not parameter_code.startswith(
        EXCLUDED_PARAMETER_PREFIXES
    )


def _extract_research_snapshot_parameter_records(
    research_record: dict,
) -> list[dict]:
    snapshot = research_record.get("research_snapshot") or {}

    health_summary = snapshot.get(
        "health_model_research_model_summary"
    ) or {}

    records = health_summary.get(
        "research_calculated_parameter_records"
    )

    if isinstance(records, list):
        return records

    legacy_records = research_record.get(
        "research_calculated_parameter_records"
    )

    if isinstance(legacy_records, list):
        return legacy_records

    return []


def _extract_pilot_parameter_records(
    session: Any,
) -> list[dict]:
    raw_result = session.raw_engine_result or {}

    records = raw_result.get(
        "research_calculated_parameter_records"
    )

    if isinstance(records, list):
        return records

    return []


def _record_identity(
    record: dict,
) -> tuple[str | None, str | None]:
    return (
        record.get("session_id"),
        record.get("parameter_code"),
    )

def _normalize_parameter_record(
    record: dict,
    *,
    record_source: str,
) -> dict | None:
    parameter_code = record.get(
        "parameter_code"
    )

    if not parameter_code:
        return None

    if not _is_available_model_parameter(
        parameter_code
    ):
        return None

    return {
        **record,

        "record_source": record_source,

        "parameter_id": record.get(
            "parameter_id"
        ),

        "parameter_code": parameter_code,
        "parameter_role": record.get(
            "parameter_role"
        ),
        "parameter_kind": record.get(
            "parameter_kind"
        ),

        "parameter_value": record.get(
            "parameter_value"
        ),

        "parameter_value_type": record.get(
            "parameter_value_type"
        ),

        "runtime_value_type": record.get(
            "runtime_value_type"
        ),

        "scale_type": record.get(
            "scale_type"
        ),

        "calculation_status": record.get(
            "calculation_status"
        ),

        "value_schema": record.get(
            "value_schema"
        ),

        "research_available": record.get(
            "research_available",
            True,
        ),
    }


def collect_health_model_parameter_records(
    *,
    research_records: list[dict],
    pilot_sessions: list[Any],
    study_id: str = "health_model",
) -> list[dict]:
    records_by_identity = {}

    # Research snapshots are preferred when the same
    # session + parameter already exists in both layers.
    for research_record in research_records:
        record_study_id = (
            research_record.get("study_id")
            or study_id
        )

        if record_study_id != study_id:
            continue

        for parameter_record in (
            _extract_research_snapshot_parameter_records(
                research_record
            )
        ):
            normalized = _normalize_parameter_record(
                parameter_record,
                record_source="research_snapshot",
            )

            if normalized is None:
                continue

            identity = _record_identity(normalized)

            if None in identity:
                continue

            records_by_identity[identity] = normalized

    # Pilot sessions are a fallback for sessions that
    # have not yet been exported to a research snapshot.
    for session in pilot_sessions:
        session_study_id = (
            session.study_id
            or "health_model"
        )

        if session_study_id != study_id:
            continue

        for parameter_record in (
            _extract_pilot_parameter_records(session)
        ):
            normalized = _normalize_parameter_record(
                parameter_record,
                record_source="pilot_session",
            )

            if normalized is None:
                continue

            identity = _record_identity(normalized)

            if None in identity:
                continue

            records_by_identity.setdefault(
                identity,
                normalized,
            )

    return sorted(
        records_by_identity.values(),
        key=lambda record: (
            str(record.get("parameter_code") or ""),
            str(record.get("session_id") or ""),
        ),
    )


def _single_or_mixed(
    values: set,
) -> str | None:
    clean = {
        value
        for value in values
        if value is not None and value != ""
    }

    if not clean:
        return None

    if len(clean) == 1:
        return next(iter(clean))

    return "mixed"

def build_available_model_parameter_catalog(
    *,
    research_records: list[dict],
    pilot_sessions: list[Any],
    study_id: str = "health_model",
) -> dict:
    parameter_records = (
        collect_health_model_parameter_records(
            research_records=research_records,
            pilot_sessions=pilot_sessions,
            study_id=study_id,
        )
    )

    grouped = {}

    for record in parameter_records:
        parameter_code = record.get(
            "parameter_code"
        )

        if not parameter_code:
            continue

        grouped.setdefault(
            parameter_code,
            {
                "parameter_code": parameter_code,
                "records": [],
                "parameter_ids": set(),
                "definition_versions": set(),
                "value_types": set(),
                "runtime_value_types": set(),
                "parameter_kinds": set(),
                "parameter_roles": set(),
                "scale_types": set(),
                "model_ids": set(),
                "calculation_versions": set(),
                "source_modes": set(),
                "record_sources": set(),
                "session_ids": set(),
                "participant_ids": set(),
                "subject_link_ids": set(),
                "calculation_status_counts": {},
                "research_available_values": set(),
            },
        )

        group = grouped[parameter_code]
        group["records"].append(record)

        if record.get("parameter_id"):
            group["parameter_ids"].add(
                record["parameter_id"]
            )

        if record.get(
            "parameter_definition_version"
        ) is not None:
            group["definition_versions"].add(
                record[
                    "parameter_definition_version"
                ]
            )

        group["value_types"].add(
            record.get("parameter_value_type")
        )

        group["runtime_value_types"].add(
            record.get("runtime_value_type")
        )

        group["parameter_kinds"].add(
            record.get("parameter_kind")
        )

        group["parameter_roles"].add(
            record.get("parameter_role")
        )

        group["scale_types"].add(
            record.get("scale_type")
        )

        group["model_ids"].add(
            record.get("model_id")
        )

        group["calculation_versions"].add(
            record.get("calculation_version")
        )

        group["source_modes"].add(
            record.get("source_mode")
        )

        group["record_sources"].add(
            record.get("record_source")
        )

        if "research_available" in record:
            group[
                "research_available_values"
            ].add(
                record.get("research_available")
            )

        calculation_status = record.get(
            "calculation_status"
        )

        if not calculation_status:
            calculation_status = (
                "legacy_status_not_recorded"
            )

        group["calculation_status_counts"][
            calculation_status
        ] = (
            group["calculation_status_counts"].get(
                calculation_status,
                0,
            )
            + 1
        )

        if record.get("session_id"):
            group["session_ids"].add(
                record["session_id"]
            )

        if record.get("participant_id"):
            group["participant_ids"].add(
                record["participant_id"]
            )

        if record.get("subject_link_id"):
            group["subject_link_ids"].add(
                record["subject_link_id"]
            )

    parameters = []

    for parameter_code in sorted(grouped):
        group = grouped[parameter_code]

        definition = (
            get_model_parameter_definition(
                parameter_code,
                include_inactive=True,
            )
        )

        definition_research = (
            definition.get("research", {})
            if definition
            else {}
        )

        definition_calculation = (
            definition.get("calculation", {})
            if definition
            else {}
        )

        definition_value_schema = (
            definition.get("value_schema", {})
            if definition
            else {}
        )

        if definition is not None:
            parameter_id = definition.get(
                "parameter_id"
            )
            definition_version = (
                definition.get(
                    "definition_version"
                )
            )
            title = definition.get("title")
            parameter_role = definition.get(
                "parameter_role"
            )
            parameter_kind = definition.get(
                "parameter_kind"
            )
            parameter_value_type = (
                definition.get("value_type")
            )
            scale_type = definition.get(
                "scale_type"
            )
            score_direction = definition.get(
                "score_direction"
            )
            research_available = (
                definition_research.get(
                    "available",
                    False,
                )
            )
            allowed_analysis_roles = (
                definition_research.get(
                    "allowed_analysis_roles",
                    [],
                )
            )
            calculation_version = (
                definition_calculation.get(
                    "calculation_version"
                )
            )
            definition_status = definition.get(
                "status"
            )
            definition_source = definition.get(
                "definition_source"
            )
            registry_definition_found = True

        else:
            parameter_id = _single_or_mixed(
                group["parameter_ids"]
            )
            definition_version = (
                _single_or_mixed(
                    group["definition_versions"]
                )
            )
            title = parameter_code
            parameter_role = _single_or_mixed(
                group["parameter_roles"]
            )
            parameter_kind = _single_or_mixed(
                group["parameter_kinds"]
            )
            parameter_value_type = (
                _single_or_mixed(
                    group["value_types"]
                )
            )
            scale_type = _single_or_mixed(
                group["scale_types"]
            )
            score_direction = None

            recorded_research_values = {
                value
                for value in group[
                    "research_available_values"
                ]
                if isinstance(value, bool)
            }

            research_available = (
                True
                if not recorded_research_values
                else (
                    True
                    if recorded_research_values
                    == {True}
                    else False
                )
            )

            allowed_analysis_roles = []
            calculation_version = (
                _single_or_mixed(
                    group[
                        "calculation_versions"
                    ]
                )
            )
            definition_status = None
            definition_source = None
            registry_definition_found = False

        participant_references = (
            group["subject_link_ids"]
            or group["participant_ids"]
        )

        calculated_record_count = (
            group[
                "calculation_status_counts"
            ].get(
                "calculated",
                0,
            )
        )

        legacy_record_count = (
            group[
                "calculation_status_counts"
            ].get(
                "legacy_status_not_recorded",
                0,
            )
        )

        available_value_record_count = sum(
            1
            for record in group["records"]
            if (
                record.get(
                    "parameter_value"
                )
                is not None
            )
        )

        parameters.append({
            "variable_source": (
                "calculated_model_parameter"
            ),
            "variable_code": parameter_code,
            "parameter_code": parameter_code,
            "parameter_id": parameter_id,
            "parameter_definition_version": (
                definition_version
            ),
            "title": title,
            "study_id": study_id,

            "parameter_role": parameter_role,
            "parameter_kind": parameter_kind,
            "parameter_value_type": (
                parameter_value_type
            ),
            "runtime_value_type": (
                _single_or_mixed(
                    group[
                        "runtime_value_types"
                    ]
                )
            ),
            "scale_type": scale_type,
            "score_direction": score_direction,
            "value_schema": (
                definition_value_schema
            ),

            "research_available": (
                research_available
            ),
            "allowed_analysis_roles": (
                allowed_analysis_roles
            ),

            "registry_definition_found": (
                registry_definition_found
            ),
            "definition_status": (
                definition_status
            ),
            "definition_source": (
                definition_source
            ),
            "calculation_version": (
                calculation_version
            ),

            "available_records_count": len(
                group["records"]
            ),
            "available_value_record_count": (
                available_value_record_count
            ),
            "calculated_record_count": (
                calculated_record_count
            ),
            "legacy_record_count": (
                legacy_record_count
            ),
            "available_session_count": len(
                group["session_ids"]
            ),
            "available_participant_count": len(
                participant_references
            ),

            "calculation_status_counts": dict(
                sorted(
                    group[
                        "calculation_status_counts"
                    ].items()
                )
            ),

            "model_ids": sorted(
                value
                for value in group["model_ids"]
                if value
            ),
            "source_modes": sorted(
                value
                for value in group["source_modes"]
                if value
            ),
            "record_sources": sorted(
                value
                for value in group[
                    "record_sources"
                ]
                if value
            ),
        })

    return {
        "schema_version": (
            MODEL_PARAMETER_CATALOG_SCHEMA_VERSION
        ),
        "study_id": study_id,
        "parameter_count": len(parameters),
        "parameter_record_count": len(
            parameter_records
        ),
        "registered_parameter_count": sum(
            1
            for parameter in parameters
            if parameter[
                "registry_definition_found"
            ]
        ),
        "unregistered_parameter_count": sum(
            1
            for parameter in parameters
            if not parameter[
                "registry_definition_found"
            ]
        ),
        "parameters": parameters,
    }
