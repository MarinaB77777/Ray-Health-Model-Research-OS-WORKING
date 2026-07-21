from __future__ import annotations

import json
import unittest

from research.model_training import (
    ModelTrainingError,
    build_colab_notebook,
    drive_folder_id,
    training_contract,
    validate_training_configuration,
)


VALID = {
    "source_folder": "https://drive.google.com/drive/folders/1SourceFolderExample",
    "mask_folder": "https://drive.google.com/drive/folders/1MaskFolderExample00",
    "output_folder": "https://drive.google.com/drive/folders/1OutputFolderExample",
    "language": "ru",
    "task_type": "grayscale_binary_segmentation",
    "group_regex": r"participant_([^/]+)",
}


class ModelTrainingContractTests(unittest.TestCase):
    def test_drive_folder_id_accepts_url_and_raw_id(self) -> None:
        self.assertEqual("1SourceFolderExample", drive_folder_id(VALID["source_folder"]))
        self.assertEqual("1SourceFolderExample", drive_folder_id("1SourceFolderExample"))
        self.assertIsNone(drive_folder_id("/local/folder"))

    def test_source_and_masks_must_be_distinct(self) -> None:
        invalid = dict(VALID, mask_folder=VALID["source_folder"])
        with self.assertRaisesRegex(ModelTrainingError, "SOURCE_AND_MASK_FOLDERS_MUST_DIFFER"):
            validate_training_configuration(invalid)

    def test_contract_exposes_scientific_guards_and_outputs(self) -> None:
        contract = training_contract("en")
        self.assertIn("group_exclusive_split", contract["scientific_guards"])
        self.assertIn("best_model.keras", contract["required_outputs"])

    def test_notebook_has_no_saved_outputs_and_compilable_code(self) -> None:
        notebook = build_colab_notebook(
            VALID,
            author={"author_identity_id": "author-1", "display_name": "Researcher"},
        )
        self.assertEqual(4, notebook["nbformat"])
        self.assertEqual("GPU", notebook["metadata"]["accelerator"])
        self.assertEqual("grayscale_binary_segmentation", notebook["metadata"]["health_model_training"]["task_type"])
        for cell in notebook["cells"]:
            if cell["cell_type"] != "code":
                continue
            self.assertEqual([], cell["outputs"])
            compile("".join(cell["source"]), "generated-training-notebook", "exec")
        config_line = "".join(notebook["cells"][1]["source"]).splitlines()[0]
        encoded = config_line.split("=", 1)[1].strip()
        config = json.loads(json.loads(encoded))
        self.assertEqual("author-1", config["authorship"]["author_identity_id"])
        self.assertEqual("authorship_survives_account_deletion", config["authorship"]["preservation_policy"])


if __name__ == "__main__":
    unittest.main()
