import unittest

from assessment.measurement.scale_registry import (
    SCALE_DEFINITIONS,
    build_scale_reference,
    get_scale_definition,
    get_scale_registry_contract,
    scale_matches_requirement,
    validate_scale_reference,
    validate_scale_registry,
)


class ScaleRegistryTests(unittest.TestCase):
    def test_registry_is_valid_and_ids_are_unique(self):
        validation = validate_scale_registry()

        self.assertTrue(validation["valid"], validation["errors"])
        self.assertGreaterEqual(validation["definition_count"], 40)
        self.assertEqual(
            len({item["scale_id"] for item in SCALE_DEFINITIONS.values()}),
            len(SCALE_DEFINITIONS),
        )

    def test_every_definition_has_three_languages(self):
        for definition in SCALE_DEFINITIONS.values():
            self.assertEqual(set(definition["title"]), {"en", "es", "ru"})
            self.assertEqual(
                set(definition["description"]),
                {"en", "es", "ru"},
            )
            self.assertTrue(all(definition["title"].values()))
            self.assertTrue(all(definition["description"].values()))

    def test_continuity_does_not_claim_parametric_measurement_level(self):
        continuous = get_scale_definition("continuous")

        self.assertEqual(continuous["measurement_level"], "context_dependent")
        self.assertTrue(continuous["requires_context_validation"])
        self.assertFalse(
            scale_matches_requirement("continuous", "parametric_numeric")
        )
        self.assertTrue(
            scale_matches_requirement("interval", "parametric_numeric")
        )

    def test_reference_is_versioned_and_validated(self):
        reference = build_scale_reference("duration")

        self.assertTrue(validate_scale_reference(reference)["valid"])
        self.assertIn("scale_id", reference)
        self.assertIn("scale_definition_version", reference)

    def test_contract_exposes_scientific_sources(self):
        contract = get_scale_registry_contract()

        self.assertIn("VIM3", contract["scientific_sources"])
        self.assertIn("JCGM_GUM_1", contract["scientific_sources"])


if __name__ == "__main__":
    unittest.main()
