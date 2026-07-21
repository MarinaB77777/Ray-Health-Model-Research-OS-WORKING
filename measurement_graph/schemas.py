MEASUREMENT_GRAPH_SCHEMA_VERSION = "measurement-graph-2"


def build_empty_measurement_graph() -> dict:
    return {
        "schema_version": MEASUREMENT_GRAPH_SCHEMA_VERSION,
        "compatible_schema_versions": ["measurement-graph-1"],

        "measurement_identity": {
            "measurement_id": None,
            "measurement_type": None,
            "study_id": None,
            "participant_id": None,
            "session_id": None,
            "series_id": None,
            "series_position": None,
            "is_repeated_measurement": False,
        },

        "time_reference": {
            "contract_version": "measurement-time-contract-1",
            "started_at": None,
            "finished_at": None,
            "observation_time": None,
            "reference_period_started_at": None,
            "reference_period_finished_at": None,
            "aggregation_window": None,
            "forecast_horizon": None,
            "global_time_reference": None,
            "global_time_scale": None,
            "time_scale": None,
            "observation_time_source": None,
            "timezone": None,
            "synchronization_reference": None,
            "clock_source": None,
            "clock_uncertainty": None,
        },

        "instrument": {
            "instrument_type": None,
            "instrument_name": None,
            "instrument_version": None,
            "manufacturer": None,
            "device_id": None,
            "software_version": None,
        },

        "measurement_description": {
            "data_kind": None,
            "data_format": None,
            "measurement_scales": [],
            "scale_references": [],
            "observation_profiles": [],
            "unresolved_scale_ids": [],
            "scale_metadata_coverage": None,
            "units": [],
            "sampling_rate": None,
            "sampling_interval": None,
            "sampling_clock": None,
            "temporal_resolution": None,
            "spatial_resolution": None,
            "measurement_uncertainty": None,
            "detection_limit": None,
            "variables": [],
            "question_count": None,
            "item_metadata_available": False,
        },

        "data_file": {
            "file_id": None,
            "file_name": None,
            "file_path": None,
            "file_type": None,
            "checksum": None,
            "data_included": True,
        },

        "quality": {
            "quality_status": "unknown",
            "quality_flags": [],
            "missingness": None,
            "artifact_summary": None,
            "measurement_uncertainty": None,
            "uncertainty_method": None,
        },

        "coverage": {
            "expected_item_count": None,
            "available_item_count": None,
            "missing_item_count": None,
            "coverage_score": None,
        },

        "calibration": {
            "calibration_required": False,
            "calibration_available": False,
            "calibration_reference_id": None,
            "calibration_method": None,
            "calibrated_at": None,
            "calibration_valid_until": None,
            "traceability_chain": [],
        },

        "permissions": {
            "collection_allowed": True,
            "analysis_allowed": True,
            "research_allowed": True,
            "export_allowed": False,
        },
    }
