from assessment.measurement.scale_registry import build_scale_reference


def resolve(connector: dict, context: dict | None = None) -> dict:
    return {
        "metadata_status": "resolved_from_connector",
        "metadata_source": "camera_connector",
        "instrument": {
            "instrument_type": "camera",
            "instrument_name": connector.get("title"),
            "instrument_version": None,
            "manufacturer": connector.get("manufacturer"),
            "device_id": connector.get("device_index") or connector.get("device_path"),
            "software_version": None,
        },
        "measurement_description": {
            "data_kind": "video_recording",
            "data_format": connector.get("data_format"),
            "measurement_scales": [],
            "scale_references": [],
            "observation_profiles": [
                build_scale_reference("image"),
                build_scale_reference("time_series"),
            ],
            "unresolved_scale_ids": [],
            "units": [],
            "sampling_rate": connector.get("fps"),
            "sampling_interval": None,
            "sampling_clock": connector.get("clock_source"),
            "temporal_resolution": connector.get("fps"),
            "spatial_resolution": connector.get("resolution"),
            "measurement_uncertainty": connector.get(
                "measurement_uncertainty"
            ),
            "detection_limit": None,
            "variables": [],
            "question_count": None,
            "item_metadata_available": False,
        },
    }
