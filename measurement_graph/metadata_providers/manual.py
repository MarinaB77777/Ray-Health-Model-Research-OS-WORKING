from assessment.measurement.scale_registry import (
    build_scale_reference,
    get_scale_definition,
    normalize_scale_id,
)


def resolve(connector: dict, context: dict | None = None) -> dict:
    context = context or {}

    scale_codes = [
        normalize_scale_id(scale_id)
        for scale_id in context.get("measurement_scales", [])
    ]
    scale_codes = [code for code in scale_codes if code]

    scale_references = [
        build_scale_reference(code)
        for code in scale_codes
        if get_scale_definition(code) is not None
    ]

    unresolved_scale_ids = sorted({
        code
        for code in scale_codes
        if get_scale_definition(code) is None
    })

    return {
        "metadata_status": "manual",
        "metadata_source": "manual_form",
        "instrument": {
            "instrument_type": context.get("instrument_type"),
            "instrument_name": context.get("instrument_name"),
            "instrument_version": context.get("instrument_version"),
            "manufacturer": context.get("manufacturer"),
            "device_id": context.get("device_id"),
            "software_version": context.get("software_version"),
        },
        "measurement_description": {
            "data_kind": context.get("data_kind"),
            "data_format": context.get("data_format"),
            "measurement_scales": scale_codes,
            "scale_references": scale_references,
            "observation_profiles": context.get(
                "observation_profiles",
                [],
            ),
            "unresolved_scale_ids": unresolved_scale_ids,
            "units": context.get("units", []),
            "sampling_rate": context.get("sampling_rate"),
            "sampling_interval": context.get("sampling_interval"),
            "sampling_clock": context.get("sampling_clock"),
            "temporal_resolution": context.get("temporal_resolution"),
            "spatial_resolution": context.get("spatial_resolution"),
            "measurement_uncertainty": context.get(
                "measurement_uncertainty"
            ),
            "detection_limit": context.get("detection_limit"),
            "variables": context.get("variables", []),
            "question_count": context.get("question_count"),
            "item_metadata_available": False,
        },
    }
