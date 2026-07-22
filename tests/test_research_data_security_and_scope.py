import ast
import unittest
from pathlib import Path

from research.analyses.health_model.model_parameter_pair_dataset import (
    build_model_parameter_pair_dataset,
)


ROOT = Path(__file__).resolve().parents[1]


class ResearchDataSecurityTests(unittest.TestCase):
    def test_sensitive_research_routes_require_researcher_session(self):
        tree = ast.parse((ROOT / "main.py").read_text(encoding="utf-8"))
        functions = {
            node.name: node
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        protected = {
            "list_participant_data_records",
            "get_participant_data_record",
            "scientific_results_catalog",
            "list_research_entities_api",
            "get_questionnaire_sample_summaries",
            "get_questionnaire_dataset",
            "questionnaire_multivariable_options",
            "run_questionnaire_multivariable_analysis",
            "list_model_parameter_records_api",
            "list_model_parameter_measurements_api",
            "build_model_parameter_dataset_api",
            "check_model_parameter_analysis",
            "run_model_parameter_statistical_analysis",
        }
        self.assertTrue(protected.issubset(functions))
        for name in protected:
            source = ast.unparse(functions[name])
            self.assertIn("_researcher_session(request)", source, name)

    def test_entity_catalog_filters_registered_objects_by_owner(self):
        source = (ROOT / "research/entity_registry.py").read_text(encoding="utf-8")
        self.assertIn("owner: str | None = None", source)
        self.assertIn('str(item.get("owner") or "") == owner', source)


class DataPreparationScopeTests(unittest.TestCase):
    def test_scope_is_separate_from_data_type_and_supports_groups(self):
        source = (ROOT / "static/data_preparation.html").read_text(encoding="utf-8")
        scope_position = source.index('id="analysisScopeBox"')
        data_type_position = source.index('id="recordsBox"')
        self.assertLess(scope_position, data_type_position)
        self.assertIn('data-analysis-scope="sample"', source)
        self.assertIn('data-analysis-scope="trajectory"', source)
        self.assertIn('data-analysis-scope="groups"', source)
        self.assertIn('return "GROUP_COMPARISON"', source)
        self.assertNotIn('id="modelParameterAnalysisScope"', source)

    def test_project_context_is_not_hard_coded_when_provided(self):
        source = (ROOT / "static/data_preparation.html").read_text(encoding="utf-8")
        self.assertIn('dataExplorerParams.get("project_id")', source)
        self.assertIn('requestedResearchProjectId || "health_model_pilot"', source)

    def test_parameter_pair_selection_builds_dataset_immediately(self):
        source = (ROOT / "static/data_preparation.html").read_text(encoding="utf-8")
        start = source.index("async function updateSelectedModelParameterPair")
        end = source.index("function renderSelectedParameterSummary", start)
        implementation = source[start:end]
        self.assertIn("await refreshModelParameterDatasetPreview()", implementation)

    def test_parameter_dataset_preserves_research_study_provenance(self):
        records = []
        for code, value in (("left", 1.0), ("right", 2.0)):
            records.append({
                "model_id": "health_model_v6_1",
                "study_id": "study-a",
                "study_ids": ["study-a"],
                "parameter_code": code,
                "parameter_value": value,
                "parameter_value_type": "number",
                "scale_type": "ratio",
                "calculation_status": "calculated",
                "calculation_run_id": "run-1",
                "participant_id": "participant-1",
                "observation_time": "2026-07-22T12:00:00+00:00",
            })

        dataset = build_model_parameter_pair_dataset(
            parameter_records=records,
            model_id="health_model_v6_1",
            left_parameter_code="left",
            right_parameter_code="right",
            analysis_scope="CROSS_PARTICIPANT",
        )

        self.assertTrue(dataset["ok"])
        self.assertEqual(dataset["study_id"], "study-a")
        self.assertEqual(
            {record["study_id"] for record in dataset["compatible_answer_records"]},
            {"study-a"},
        )
        self.assertNotEqual(
            dataset["compatible_answer_records"][0]["study_id"],
            dataset["model_id"],
        )


if __name__ == "__main__":
    unittest.main()
