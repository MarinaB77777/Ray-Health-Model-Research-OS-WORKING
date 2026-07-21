from assessment.preparation.data_type_builder import (
    build_data_types,
)
from assessment.preparation.measurement_scale_builder import (
    build_measurement_scales,
)
from assessment.preparation.variable_characteristics_builder import (
    build_variable_characteristics,
)


ANALYSIS_CAPABILITY_SCHEMA_VERSION = "analysis-capability"


def build_analysis_capability(
    *,
    source_category: str,
    source_definition: dict,
) -> dict:
    return {
        "schema_version": ANALYSIS_CAPABILITY_SCHEMA_VERSION,
        "source_category": source_category,

        "data_characteristics": {
            "data_types": build_data_types(
                source_category=source_category,
                source_definition=source_definition,
            ),
            "measurement_scales": build_measurement_scales(
                source_category=source_category,
                source_definition=source_definition,
            ),
            "variable_characteristics": build_variable_characteristics(
                source_category=source_category,
                source_definition=source_definition,
            ),
        },

        "dataset_structure": [],
        "observation_units": [],
        "sampling_characteristics": [],
        "measurement_characteristics": [],

        "analysis_capability": {
            "allowed_analysis_families": [],
            "forbidden_analysis_families": [],
            "analysis_constraints": [],
        },

        "builder_notes": [],
    }