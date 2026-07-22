import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research.evidence_review import (
    EvidenceReviewError,
    build_plan,
    contract,
    list_reviews,
    save_review,
)
from research.project_workspace import block_catalog
from ray_colleague.contracts import RayRole
from ray_colleague.service import RayColleagueService


CATALOG_ID = "registered_data:dataset-1:v1"


def complete_plan():
    return {
        "title": "Health-model evidence review",
        "review_question": "Which evidence supports the prespecified model claim?",
        "review_type": "systematic_review",
        "reporting_framework_ids": ["prisma_2020", "prisma_search"],
        "inclusion_criteria": "Prespecified population, measurements and outcomes.",
        "exclusion_criteria": "Records outside the declared scope.",
        "search_sources": [{
            "name": "Bibliographic database",
            "source_type": "bibliographic_database",
            "coverage_or_platform": "Declared platform",
            "planned_query": "(health model) AND (validation)",
            "limits_and_justification": "No undeclared language limit",
            "searched_at_utc": "",
        }],
        "screening_process": "Title/abstract followed by full-text screening.",
        "exclusion_reason_policy": "Record one prespecified reason at full text.",
        "extraction_data_items": ["design", "sample", "measurement", "result"],
        "appraisal_approach_ids": ["risk_of_bias_design_specific"],
        "synthesis_approach_ids": ["synthesis_without_meta_analysis"],
        "synthesis_compatibility_rule": "Combine only compatible designs, constructs and estimands.",
        "contradictory_evidence_rule": "Retain null and contradictory findings.",
        "claim_decision_rule": "Claims follow direction, precision, bias and certainty.",
        "selected_catalog_items": [{
            "catalog_id": CATALOG_ID,
            "category": "registered_data",
            "registry_id": "dataset-1",
            "version": 1,
            "title": "Dataset 1",
            "status": "active",
            "planned_role": "candidate evidence",
        }],
        "researcher_approved": True,
    }


class EvidenceReviewTests(unittest.TestCase):
    def test_contract_preserves_scientific_boundaries(self):
        invariants = set(contract()["invariants"])
        self.assertIn("ray_suggestion_is_not_evidence", invariants)
        self.assertIn("absence_of_evidence_is_not_evidence_of_absence", invariants)
        self.assertIn("review_protocol_changes_are_versioned_not_silently_overwritten", invariants)

    def test_draft_reports_missing_elements_but_trial_blocks(self):
        draft = build_plan({}, status="draft", valid_catalog_ids={CATALOG_ID})
        self.assertTrue(draft["readiness"]["valid_for_status"])
        self.assertIn("EVIDENCE_REVIEW_QUESTION_REQUIRED", draft["readiness"]["issues"])
        trial = build_plan({}, status="trial", valid_catalog_ids={CATALOG_ID})
        self.assertFalse(trial["readiness"]["valid_for_status"])
        self.assertIn("EVIDENCE_REVIEW_SEARCH_SOURCE_REQUIRED", trial["readiness"]["blocking_issues"])

    def test_only_registered_catalog_items_can_enter_plan(self):
        value = complete_plan()
        value["selected_catalog_items"][0]["catalog_id"] = "invented:item:v1"
        with self.assertRaises(EvidenceReviewError) as caught:
            build_plan(value, status="trial", valid_catalog_ids={CATALOG_ID})
        self.assertEqual(caught.exception.code, "EVIDENCE_REVIEW_CATALOG_ITEM_NOT_REGISTERED")

    def test_registered_catalog_metadata_is_canonical_not_browser_supplied(self):
        value = complete_plan()
        value["selected_catalog_items"][0].update({
            "title": "Spoofed title",
            "category": "spoofed_category",
            "status": "active",
        })
        registered = {
            CATALOG_ID: {
                "catalog_id": CATALOG_ID,
                "category": "registered_data",
                "registry_id": "dataset-1",
                "version": 1,
                "title": "Canonical dataset title",
                "status": "trial",
                "source_route": "/data-preparation",
            }
        }
        result = build_plan(
            value,
            status="trial",
            valid_catalog_ids=set(registered),
            catalog_items_by_id=registered,
        )
        selected = result["evidence_acquisition_plan"]["selected_catalog_items"][0]
        self.assertEqual(selected["title"], "Canonical dataset title")
        self.assertEqual(selected["category"], "registered_data")
        self.assertEqual(selected["status"], "trial")
        self.assertEqual(selected["planned_role"], "candidate evidence")

    def test_saved_protocol_keeps_stable_id_and_adds_versions(self):
        plan = build_plan(complete_plan(), status="active", valid_catalog_ids={CATALOG_ID})
        with tempfile.TemporaryDirectory() as directory:
            store = Path(directory) / "research_objects.json"
            with patch("research.repository.DATA_FILE", store):
                first = save_review(
                    owner="researcher-1", authorship={"contributions": []},
                    status="active", language="en", plan=plan,
                )
                second = save_review(
                    owner="researcher-1", authorship={"contributions": []},
                    status="active", language="en", plan=plan,
                    review_id=first["review_id"],
                )
                self.assertEqual(first["review_id"], second["review_id"])
                self.assertEqual((first["version"], second["version"]), (1, 2))
                self.assertEqual(len(list_reviews("researcher-1", review_id=first["review_id"])), 2)

    def test_project_actions_open_real_review_constructor(self):
        catalog = {item["code"]: item for item in block_catalog("ru")["blocks"]}
        for block_type in ("introduction", "scientific_context", "discussion"):
            routes = [item.get("route") for item in catalog[block_type]["actions"]]
            self.assertIn("/evidence-review", routes)


class EvidenceReviewSurfaceTests(unittest.TestCase):
    def test_workspace_and_page_use_real_review_route_and_ray_endpoint(self):
        root = Path(__file__).resolve().parents[1]
        workspace = (root / "static" / "research_workspace.html").read_text(encoding="utf-8")
        page = (root / "static" / "scientific_evidence_review.html").read_text(encoding="utf-8")
        main = (root / "main.py").read_text(encoding="utf-8")
        self.assertIn('path: "/evidence-review"', workspace)
        self.assertNotIn('demoCabinet: "Демо-кабинет"', workspace)
        self.assertIn('/ray-colleague/researcher/respond', page)
        self.assertIn('/research/evidence-review/contract', page)
        self.assertIn('@app.get("/evidence-review"', main)
        self.assertNotIn("An isolated demonstration", workspace)
        self.assertNotIn("Demostración aislada", workspace)

    def test_ray_has_a_real_evidence_review_context(self):
        with tempfile.TemporaryDirectory() as directory:
            service = RayColleagueService(directory)
            result = service.respond(
                role=RayRole.RESEARCH_COLLEAGUE,
                owner_id="researcher-1",
                page_id="evidence_review",
                language="ru",
                message="Проверь пробелы протокола",
                project_id="project-1",
                selection={"review_plan": {}, "validation": {"issues": []}},
            )
        self.assertIn("evidence_review_question_scope", result["unresolved"])
        self.assertIn("evidence_review_search", result["unresolved"])
        self.assertTrue(result["clarification_questions"])


if __name__ == "__main__":
    unittest.main()
