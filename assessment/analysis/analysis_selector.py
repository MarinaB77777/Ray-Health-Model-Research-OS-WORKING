from assessment.analysis.dependency_builder import (
    build_available_dependencies,
)
from assessment.measurement.scale_registry import (
    get_scale_definition,
    scale_supports_capability,
)


def _single_variable_methods(variable: dict) -> list[dict]:
    scale_type = variable.get("scale_type")

    if scale_type is None:
        return []

    definition = get_scale_definition(scale_type)

    if definition is None:
        return []

    methods = []

    if scale_supports_capability(scale_type, "frequency_table"):
        methods.append({
            "method_id": "frequency_table",
            "title": "Frequency table",
            "purpose": "show how often each answer was selected",
            "selection_status": "available",
            "missing_condition_checks": [],
        })

    if scale_supports_capability(scale_type, "ordered_summary"):
        methods.append({
            "method_id": "summary_statistics",
            "title": "Summary statistics",
            "purpose": (
                "show scale-appropriate count, range, distribution, "
                "and ordered or numeric summaries"
            ),
            "selection_status": "available",
            "missing_condition_checks": [],
            "measurement_level": definition["measurement_level"],
            "limitations": definition.get("limitations", []),
        })

    if scale_supports_capability(scale_type, "numeric_plot"):
        methods.append({
            "method_id": "histogram",
            "title": "Histogram",
            "purpose": "show the shape of numeric answers",
            "selection_status": "available",
            "missing_condition_checks": [],
            "measurement_level": definition["measurement_level"],
            "limitations": definition.get("limitations", []),
        })

    return methods


def build_analysis_catalog(
    study_id: str,
    answer_records: list[dict],
) -> dict:
    dependency_catalog = build_available_dependencies(
        study_id=study_id,
        answer_records=answer_records,
    )

    single_variable_analyses = []

    for variable in dependency_catalog["available_variables"]:
        methods = _single_variable_methods(variable)

        single_variable_analyses.append({
            "variable": variable,
            "standard_methods": methods,
            "method_selection_status": (
                "methods_available"
                if methods
                else "metadata_required"
            ),
        })

    pairwise_analyses = []

    for dependency in dependency_catalog["available_dependencies"]:
        pairwise_analyses.append({
            "dependency_id": dependency["dependency_id"],
            "left_variable": dependency["left"],
            "right_variable": dependency["right"],
            "standard_methods": [
                {
                    "method_id": method["method_id"],
                    "title": method["title"],
                    "purpose": method.get("purpose"),
                    "selection_status": method.get("selection_status"),
                    "missing_condition_checks": method.get(
                        "missing_condition_checks",
                        [],
                    ),
                }
                for method in dependency[
                    "available_standard_methods"
                ]
            ],
            "author_methods": dependency[
                "available_author_methods"
            ],
            "method_selection_status": dependency[
                "method_selection_status"
            ],
        })

    return {
        "study_id": study_id,

        "single_variable_analysis_count": len(single_variable_analyses),
        "single_variable_analyses": single_variable_analyses,

        "pairwise_analysis_count": len(pairwise_analyses),
        "pairwise_analyses": pairwise_analyses,

        # backward compatibility for old UI
        "analysis_count": len(pairwise_analyses),
        "analyses": pairwise_analyses,
    }
