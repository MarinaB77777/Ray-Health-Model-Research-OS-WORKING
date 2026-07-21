from __future__ import annotations

import unittest
from unittest.mock import patch

from research.entity_registry import list_entities, list_hypothesis_entities


class EntityRegistryTests(unittest.TestCase):
    @patch("research.entity_registry.load_objects", return_value=[])
    def test_unified_utc_axis_is_registered(self, _load):
        axis = list_entities(entity_type="time_variable", language="ru")
        self.assertEqual(1, len(axis))
        self.assertEqual("UTC", axis[0]["time_contract"]["axis"])
        self.assertEqual("datetime", axis[0]["measurement_scale_ref"])

    @patch("research.entity_registry.load_objects")
    def test_measurement_and_questionnaire_results_keep_version_and_contract(self, load):
        load.return_value = [
            {"id": "sensor-data-1", "object_type": "measurement_dataset", "title": "Camera motion", "version": 3, "status": "trial", "scientific_definition": {"measurement_scale_ref": "ratio", "unit": "pixel_per_second", "time_contract": {"axis": "UTC"}}},
            {"id": "survey-result-1", "object_type": "questionnaire_result", "title": "Physical state", "version": 2, "status": "active", "scientific_definition": {"measurement_scale_ref": "ordinal", "unit": "score", "time_contract": {"axis": "UTC"}}},
        ]
        entities = list_entities(language="en")
        sensor = next(x for x in entities if x["registry_id"] == "sensor-data-1")
        survey = next(x for x in entities if x["registry_id"] == "survey-result-1")
        self.assertEqual((3, "ratio", "pixel_per_second"), (sensor["version"], sensor["measurement_scale_ref"], sensor["unit"]))
        self.assertEqual((2, "ordinal", "score"), (survey["version"], survey["measurement_scale_ref"], survey["unit"]))
        self.assertEqual("UTC", sensor["time_contract"]["axis"])

    @patch("research.entity_registry.load_objects")
    def test_qualitative_catalog_excludes_question_definitions_and_time_axis(self, load):
        load.return_value = [
            {"id": "project-1", "object_type": "project", "owner": "owner-1", "blocks": []},
            {"id": "corpus-1", "object_type": "interview_corpus", "owner": "owner-1", "title": "Interviews", "version": 1},
            {"id": "other-1", "object_type": "interview_corpus", "owner": "owner-2", "title": "Private other corpus", "version": 1},
        ]
        entities = list_hypothesis_entities(owner="owner-1", project_id="project-1", language="ru")
        self.assertEqual(["corpus-1"], [x["registry_id"] for x in entities])
        self.assertNotIn("question", {x["entity_type"] for x in entities})
        self.assertNotIn("time_variable", {x["entity_type"] for x in entities})


if __name__ == "__main__":
    unittest.main()
