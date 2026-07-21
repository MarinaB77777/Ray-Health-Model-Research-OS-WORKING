"""Backward-compatible entry points for measurement metadata resolution.

The active implementation lives in ``metadata_providers.registry``.  Keeping
these functions as delegating adapters prevents the historical resolver from
becoming a second, inconsistent source of scale metadata.
"""

from measurement_graph.metadata_providers.registry import resolve_metadata


def resolve_questionnaire_metadata(
    *,
    assessment_id: str,
    lang: str = "en",
) -> dict:
    return resolve_metadata(
        connector={
            "connector_type": "questionnaire",
            "connector_id": assessment_id,
            "title": assessment_id,
        },
        context={"lang": lang},
    )


def resolve_connector_metadata(
    *,
    connector: dict,
    lang: str = "en",
) -> dict:
    return resolve_metadata(
        connector=connector,
        context={"lang": lang},
    )
