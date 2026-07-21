from measurement_graph.metadata_providers import (
    questionnaire,
    camera,
    manual,
)


PROVIDERS = {
    "questionnaire": questionnaire.resolve,
    "camera": camera.resolve,
    "manual_entry": manual.resolve,
}


def resolve_metadata(
    *,
    connector: dict,
    context: dict | None = None,
) -> dict:
    connector_type = connector.get("connector_type")
    provider = PROVIDERS.get(connector_type)

    if provider is None:
        return {
            "metadata_status": "unsupported_connector_type",
            "metadata_source": "none",
            "instrument": {
                "instrument_type": connector_type,
                "instrument_name": connector.get("title"),
                "instrument_version": None,
                "manufacturer": connector.get("manufacturer"),
                "device_id": (
                    connector.get("device_path")
                    or connector.get("device_index")
                    or connector.get("connector_id")
                ),
                "software_version": None,
            },
            "measurement_description": {
                "data_kind": connector_type,
                "data_format": None,
                "measurement_scales": [],
                "scale_references": [],
                "observation_profiles": [],
                "unresolved_scale_ids": [],
                "units": [],
                "variables": [],
                "question_count": None,
                "item_metadata_available": False,
            },
        }

    return provider(connector, context)
