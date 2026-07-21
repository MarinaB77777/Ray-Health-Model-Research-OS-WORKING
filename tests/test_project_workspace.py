from __future__ import annotations

import os
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

from research.lab_store import create_research_object
from research.project_workspace import (
    PROJECT_SCHEMA_VERSION,
    ProjectWorkspaceError,
    block_catalog,
    connect_block,
    connect_entity,
    create_project,
    disconnect_block,
    disconnect_entity,
    get_project,
    list_projects,
    update_block,
    update_project,
)


@contextmanager
def working_directory(path: str):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def authorship() -> dict:
    return {
        "schema_version": "research-object-authorship-1",
        "contributions": [{
            "author_identity_id": "author-permanent-1",
            "display_name": "Research Author",
            "roles": ["creator", "scientific_author"],
        }],
        "preservation_policy": "authorship_survives_account_deletion",
    }


class ProjectWorkspaceTests(unittest.TestCase):
    def create(self):
        return create_project(
            owner="account-1",
            authorship=authorship(),
            title="Stress recovery study",
            research_question="Does recovery alter decision quality?",
            goal="Estimate the association over time.",
            language="en",
            display_timezone="America/Mexico_City",
        )

    def test_project_has_permanent_authorship_version_and_global_time(self):
        with tempfile.TemporaryDirectory() as tmp, working_directory(tmp):
            project = self.create()
            self.assertEqual(project["schema_version"], PROJECT_SCHEMA_VERSION)
            self.assertEqual(project["version"], 1)
            self.assertEqual(project["authorship"]["contributions"][0]["display_name"], "Research Author")
            self.assertEqual(project["global_time_contract"]["axis"], "UTC")
            self.assertEqual(project["global_time_contract"]["scale_type"], "datetime")
            self.assertEqual(project["global_time_contract"]["display_timezone"], "America/Mexico_City")

    def test_only_title_is_required_at_project_creation(self):
        with tempfile.TemporaryDirectory() as tmp, working_directory(tmp):
            project = create_project(
                owner="account-1", authorship=authorship(), title="Editable draft"
            )
            self.assertEqual(project["research_question"], "")
            self.assertEqual(project["validation"]["issues"][0]["code"], "SCIENTIFIC_QUESTION_NOT_YET_DEFINED")
            project = update_project(project["id"], "account-1", {"research_question": ""})
            self.assertEqual(project["research_question"], "")

    def test_catalog_is_multilingual_and_external_ai_is_not_imagined(self):
        catalog = block_catalog("ru", ["humanities_qualitative"])
        self.assertGreaterEqual(len(catalog["blocks"]), 16)
        introduction = next(item for item in catalog["blocks"] if item["code"] == "introduction")
        review = next(item for item in introduction["actions"] if item["kind"] == "ray_external")
        self.assertFalse(review["available"])
        self.assertEqual(review["unavailable_reason"], "EXTERNAL_SCIENTIFIC_AI_NOT_CONNECTED_UNTIL_POST_PILOT")
        sources = next(item for item in catalog["blocks"] if item["code"] == "sources_corpus")
        signals = next(item for item in catalog["blocks"] if item["code"] == "signal_processing")
        self.assertTrue(sources["recommended"])
        self.assertFalse(signals["recommended"])
        self.assertTrue(any(item["code"] == "signal_processing" for item in catalog["blocks"]))
        training = next(item for item in catalog["blocks"] if item["code"] == "model_training")
        self.assertTrue(any(action.get("route") == "/model-training" for action in training["actions"]))
        fiji = next(item for item in catalog["blocks"] if item["code"] == "image_processing_fiji")
        self.assertTrue(any(action.get("route") == "/fiji-integration" for action in fiji["actions"]))
        inputs = next(field for field in fiji["fields"] if field["code"] == "input_datasets")
        self.assertEqual(["measurement_dataset"], inputs["connection_spec"]["accepted_entity_types"])
        self.assertEqual("data_preparation", fiji["navigation"]["stage_code"])
        self.assertEqual("technical", fiji["navigation"]["track_code"])
        self.assertEqual(6, len(catalog["stages"]))
        self.assertEqual({"common", "technical", "humanities"}, {item["code"] for item in catalog["tracks"]})
        self.assertTrue(all("navigation" in item for item in catalog["blocks"]))
        bibliography = next(item for item in catalog["blocks"] if item["code"] == "bibliography_citations")
        self.assertTrue(any(action.get("route") == "/citation-workspace" for action in bibliography["actions"]))
        self.assertLess(introduction["navigation"]["block_order"], bibliography["navigation"]["block_order"])
        hypotheses = next(item for item in catalog["blocks"] if item["code"] == "hypotheses")
        self.assertTrue(any(action.get("route") == "/research-lab" for action in hypotheses["actions"]))

    def test_single_block_is_not_duplicated_and_multiple_block_can_repeat(self):
        with tempfile.TemporaryDirectory() as tmp, working_directory(tmp):
            project = self.create()
            project = connect_block(project["id"], "account-1", "introduction")
            first_id = project["active_block_id"]
            project = connect_block(project["id"], "account-1", "introduction")
            self.assertEqual(len([b for b in project["blocks"] if b["block_type"] == "introduction"]), 1)
            self.assertEqual(project["active_block_id"], first_id)
            project = connect_block(project["id"], "account-1", "hypotheses")
            project = connect_block(project["id"], "account-1", "hypotheses")
            self.assertEqual(len([b for b in project["blocks"] if b["block_type"] == "hypotheses"]), 2)

    def test_block_revision_validation_and_disconnect_preserve_content(self):
        with tempfile.TemporaryDirectory() as tmp, working_directory(tmp):
            project = self.create()
            project = connect_block(project["id"], "account-1", "experimental_setup")
            block_id = project["active_block_id"]
            project = update_block(
                project["id"], "account-1", block_id,
                {"setup_description": "Camera and ECG", "time_synchronization": "NTP-synchronized UTC clock"},
            )
            block = next(item for item in project["blocks"] if item["block_id"] == block_id)
            self.assertTrue(block["validation"]["valid"])
            self.assertEqual(block["revision"], 2)
            project = disconnect_block(project["id"], "account-1", block_id)
            block = next(item for item in project["blocks"] if item["block_id"] == block_id)
            self.assertEqual(block["lifecycle"], "disconnected")
            self.assertEqual(block["content"]["setup_description"], "Camera and ECG")
            self.assertEqual(project["audit_log"][-1]["event_type"], "project_block_disconnected_content_preserved")

    def test_entity_port_binds_exact_registered_version_and_preserves_history(self):
        with tempfile.TemporaryDirectory() as tmp, working_directory(tmp):
            project = self.create()
            project = connect_block(project["id"], "account-1", "variables_mechanisms")
            block_id = project["active_block_id"]
            project = connect_entity(
                project["id"], "account-1", block_id,
                field_code="parameter_links",
                entity={
                    "entity_type": "model_parameter", "registry_id": "pressure",
                    "version": 3, "status": "trial", "display_name": "Pressure",
                    "source_schema_version": "model-parameter-definition-1",
                },
            )
            block = next(item for item in project["blocks"] if item["block_id"] == block_id)
            link = block["entity_links"][0]
            self.assertEqual(link["version"], 3)
            self.assertEqual(block["content"]["parameter_links"], [link["link_id"]])
            project = disconnect_entity(project["id"], "account-1", block_id, link["link_id"])
            block = next(item for item in project["blocks"] if item["block_id"] == block_id)
            self.assertEqual(block["entity_links"][0]["lifecycle"], "disconnected")
            self.assertEqual(block["content"]["parameter_links"], [])

    def test_standardized_hypothesis_result_connects_to_results_port(self):
        with tempfile.TemporaryDirectory() as tmp, working_directory(tmp):
            project = self.create()
            project = connect_block(project["id"], "account-1", "results")
            block_id = project["active_block_id"]
            project = connect_entity(
                project["id"], "account-1", block_id,
                field_code="result_links",
                entity={
                    "entity_type": "hypothesis_result", "registry_id": "result-1",
                    "version": 1, "status": "draft", "display_name": "Qualitative hypothesis result",
                    "source_schema_version": "health-model-qualitative-hypothesis-result-1",
                },
            )
            block = next(item for item in project["blocks"] if item["block_id"] == block_id)
            self.assertEqual("hypothesis_result", block["entity_links"][0]["entity_type"])

    def test_access_is_scoped_to_owner(self):
        with tempfile.TemporaryDirectory() as tmp, working_directory(tmp):
            project = self.create()
            with self.assertRaisesRegex(ProjectWorkspaceError, "PROJECT_ACCESS_DENIED"):
                get_project(project["id"], "another-account")
            self.assertEqual(len(list_projects("another-account")), 0)

    def test_legacy_project_is_preserved_and_requires_explicit_migration(self):
        with tempfile.TemporaryDirectory() as tmp, working_directory(tmp):
            legacy = create_research_object(
                "project", "account-1", "Legacy project",
                research_question="Legacy question", authorship=authorship(),
            )
            project = get_project(legacy["id"], "account-1")
            self.assertTrue(project["workspace_compatibility"]["requires_rework"])
            with self.assertRaisesRegex(ProjectWorkspaceError, "EXPLICIT_MIGRATION"):
                update_project(legacy["id"], "account-1", {"title": "Changed"})


if __name__ == "__main__":
    unittest.main()
