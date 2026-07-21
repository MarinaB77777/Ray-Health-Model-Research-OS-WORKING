import importlib.util
import unittest
from pathlib import Path

from assessment.questionnaire_components import (
    get_compatible_scale_types_for_response,
    list_scale_types,
)
from research.analyses.health_model.model_parameter_registry import (
    build_model_parameter_registry,
)
from assessment.analysis.checks.scale_pattern import scale_matches
from assessment.analysis.data_type_builder import build_data_types
from assessment.analysis.measurement_scale_builder import (
    build_measurement_scales,
)
from assessment.analysis.variable_characteristics_builder import (
    build_variable_characteristics,
)


class ScaleIntegrationTests(unittest.TestCase):
    def test_questionnaire_components_come_from_registry(self):
        components = list_scale_types()

        self.assertIn("likert", {item["id"] for item in components})
        self.assertIn("scale_id", components[0])
        self.assertIn("localized_title", components[0])
        self.assertIn("count", get_compatible_scale_types_for_response("numeric"))

    def test_model_parameters_use_scale_references_and_three_languages(self):
        registry = build_model_parameter_registry()

        self.assertTrue(registry["ok"])
        self.assertEqual(
            registry["supported_development_statuses"],
            ["active", "draft", "trial"],
        )
        for definition in registry["definitions"]:
            self.assertEqual(set(definition["title"]), {"en", "es", "ru"})
            if definition["scale_type"] is not None:
                self.assertEqual(
                    definition["scale_type"],
                    definition["scale_reference"]["scale_code"],
                )

    def test_statistical_patterns_use_registry_capabilities(self):
        pearson = {
            "scale_patterns": [
                {
                    "left": ["parametric_numeric"],
                    "right": ["parametric_numeric"],
                }
            ]
        }

        self.assertTrue(scale_matches(pearson, "interval", "ratio"))
        self.assertFalse(scale_matches(pearson, "continuous", "ratio"))

    def test_analysis_builders_derive_axes_from_registry(self):
        source = {
            "questions": {
                "count": {
                    "type": "number",
                    "scale_type": "count",
                },
                "rating": {
                    "type": "single_select",
                    "scale_type": "likert",
                },
                "comment": {
                    "type": "text",
                    "scale_type": "text",
                },
            }
        }

        self.assertEqual(
            build_measurement_scales(
                source_category="questionnaire",
                source_definition=source,
            ),
            ["count", "likert", "text"],
        )
        data_types = build_data_types(
            source_category="questionnaire",
            source_definition=source,
        )
        characteristics = build_variable_characteristics(
            source_category="questionnaire",
            source_definition=source,
        )
        self.assertIn("numeric", data_types)
        self.assertIn("ordinal", data_types)
        self.assertIn("text", data_types)
        self.assertIn("ordered", characteristics)

    def test_question_ids_are_unique_within_each_language_bank(self):
        root = Path(__file__).parents[1]
        for language in ("RU", "EN", "ES"):
            path = root / "question_banks" / f"QUESTION_BANK_{language}.py"
            spec = importlib.util.spec_from_file_location(
                f"question_bank_{language.lower()}_test",
                path,
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            bank = getattr(module, f"QUESTION_BANK_{language}")
            question_ids = [item["question_id"] for item in bank.values()]

            self.assertEqual(
                len(question_ids),
                len(set(question_ids)),
                language,
            )


if __name__ == "__main__":
    unittest.main()
