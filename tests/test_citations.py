from __future__ import annotations

import unittest

from research.citations import build_citation_collection, citation_contract


class CitationTests(unittest.TestCase):
    def test_valid_journal_article_formats_and_preserves_identity(self):
        collection = build_citation_collection(
            title="Submission bibliography", destination="Target Journal", style="apa7",
            references=[{"type": "journal_article", "title": "Measured change", "year": "2025",
                         "authors": [{"family": "Doe", "given": "Jane"}],
                         "container_title": "Journal of Measurement", "doi": "10.1234/example.1",
                         "registered_source_ref": "source-17"}],
        )
        self.assertTrue(collection["validation"]["valid"])
        self.assertEqual("source-17", collection["references"][0]["registered_source_ref"])
        self.assertIn("Doe", collection["formatted_references"][0]["text"])

    def test_multiple_authors_and_requirements_source_are_preserved(self):
        collection = build_citation_collection(
            title="Version", destination="Journal", style="ieee",
            requirements_source="Journal instructions 2026",
            references=[{"type": "software", "title": "Analysis tool", "year": "2026",
                         "authors": [{"family": "One", "given": "A"},
                                     {"family": "Two", "given": "B"}]}],
        )
        self.assertEqual(2, len(collection["references"][0]["authors"]))
        self.assertEqual("Journal instructions 2026", collection["requirements_source"])

    def test_missing_data_is_reported_not_invented(self):
        collection = build_citation_collection(
            title="Draft", destination="", style="vancouver",
            references=[{"type": "journal_article", "title": "Incomplete"}],
        )
        self.assertFalse(collection["validation"]["valid"])
        codes = {x["code"] for x in collection["validation"]["references"][0]["issues"]}
        self.assertIn("REQUIRED_FIELD_MISSING", codes)
        self.assertEqual("blocked_by_validation", collection["formatted_references"][0]["status"])
        self.assertIsNone(collection["formatted_references"][0]["text"])
        self.assertIn("missing_bibliographic_data_is_reported_not_invented", citation_contract()["invariants"])


if __name__ == "__main__":
    unittest.main()
