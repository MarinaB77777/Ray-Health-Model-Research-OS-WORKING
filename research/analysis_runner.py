import json
from pathlib import Path

from assessment.prepared_output import build_prepared_domain_output
from research.records_store import list_research_records
from research.analysis_store import save_analysis_result
from assessment.analysis.analyzer_constructor import (
    build_analyzer_input_from_prepared_outputs,
    construct_analyzer_objects,
)

from research.analyses.health_model.readiness_analysis import (
    analyze_research_readiness,
)
from research.analyses.health_model.level_map_analysis import (
    analyze_level_maps,
)
from research.analyses.health_model.function_layer import (
    extract_functions_from_level_maps,
)
from research.analyses.health_model.mechanism_layer import (
    build_mechanism_layer,
)
from research.analyses.health_model.constellation_layer import (
    build_constellation_layer,
)
from research.public_output.health_model.participant_report import (
    build_participant_report,
)
from research.analyses.health_model.model_parameter_extractor import (
    build_health_model_parameter_records,
)


PILOT_SESSIONS_PATH = Path("data/pilot_sessions.json")


def load_health_model_pilot_session_records() -> list[dict]:
    if not PILOT_SESSIONS_PATH.exists():
        return []

    data = json.loads(
        PILOT_SESSIONS_PATH.read_text(encoding="utf-8")
    )

    records = []

    for session in data:
        study_id = session.get("study_id")

        if study_id not in {None, "health_model"}:
            continue

        raw_result = session.get("raw_engine_result") or {}

        if not raw_result:
            continue

        raw_payload = {
            "payload_type": "questionnaire_answers",
            "study_id": "health_model",
            "answers": session.get("answers") or {},
        }

        analysis_output = raw_result

        calculated_parameter_records = build_health_model_parameter_records(
            session_id=session.get("session_id"),
            participant_id=session.get("participant_id"),
            subject_link_id=session.get("subject_link_id"),
            study_id="health_model",
            analysis_output=analysis_output,
        )

        prepared_domain_output = build_prepared_domain_output(
            domain_data_identity=session.get("domain_data_identity") or {},
            raw_payload=raw_payload,
            analysis_output=analysis_output,
        )

        records.append({
            "record_id": session.get("session_id"),
            "record_type": "pilot_session",
            "status": session.get("status"),
            "created_at": session.get("created_at"),
            "updated_at": session.get("updated_at"),
            "session_id": session.get("session_id"),
            "participant_id": session.get("participant_id"),
            "subject_link_id": session.get("subject_link_id"),
            "study_id": "health_model",

            "domain_data_identity": session.get("domain_data_identity") or {},
            "raw_payload": raw_payload,
            "prepared_domain_output": prepared_domain_output,
            "analysis_output": analysis_output,

            "answers": session.get("answers") or {},
            "result": raw_result,
            "raw_engine_result": raw_result,
            "public_output": session.get("public_output") or {},
            "research_calculated_parameter_records": calculated_parameter_records,
        })

    return records


def run_health_model_research_analysis(
    study_id: str | None = None,
) -> dict:
    records = list_research_records(
        study_id=study_id,
    )

    if study_id == "health_model":
        records.extend(
            load_health_model_pilot_session_records()
        )
    prepared_outputs = [
        record.get("prepared_domain_output")
        for record in records
        if isinstance(record.get("prepared_domain_output"), dict)
    ]

    analyzer_input = build_analyzer_input_from_prepared_outputs(
        prepared_outputs
    )

    analyzer_objects = construct_analyzer_objects(
        analyzer_input
    )

    accepted_prepared_outputs = analyzer_input.get(
        "accepted_prepared_outputs",
        []
    )
    
    analysis_records = records

    if accepted_prepared_outputs:
        analysis_records = [
            {
                "record_id": output.get("prepared_output_id"),
                "record_type": "prepared_domain_output",
                "session_id": output.get("session_id"),
                "study_id": output.get("study_id"),
                "prepared_domain_output": output,
                "result": output.get("prepared_payload", {}),
            }
            for output in accepted_prepared_outputs
        ]

    readiness = analyze_research_readiness(analysis_records)
    level_maps = analyze_level_maps(analysis_records)
    
    function_layer = extract_functions_from_level_maps(
        level_maps
    )

    mechanism_layer = build_mechanism_layer(
        function_layer
    )

    constellation_layer = build_constellation_layer(
        mechanism_layer
    )

    draft_analysis = {
        "analysis_type": "health_model_research_analysis",
        "analysis_scope": "research_records",
        "study_id": study_id,
        "analyzer_input": analyzer_input,
        "analyzer_objects": analyzer_objects,
        "record_count": len(records),
        "constellation_layer": constellation_layer,
        "readiness": readiness,
        "level_maps": level_maps,
        "function_layer": function_layer,
        "mechanism_layer": mechanism_layer,
        "analysis_input_source": (
            "accepted_prepared_outputs"
            if accepted_prepared_outputs
            else "legacy_records_fallback"
    ),
    }

    participant_report = build_participant_report(draft_analysis)

    analysis = {
        **draft_analysis,
        "participant_report": participant_report,
    }

    return save_analysis_result(analysis)