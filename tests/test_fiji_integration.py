from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research.fiji_integration import (
    FijiIntegrationError,
    build_macro,
    configure_installation,
    discover_installations,
    inspect_installation,
    integration_contract,
    validate_pipeline,
)


def fake_fiji(root: Path) -> Path:
    launcher = root / "Fiji.app" / "ImageJ-linux64"
    launcher.parent.mkdir(parents=True)
    launcher.write_bytes(b"verified-fiji-launcher")
    launcher.chmod(0o755)
    jars = launcher.parent / "jars"
    jars.mkdir()
    (jars / "imagej-common-test.jar").write_bytes(b"jar")
    (launcher.parent / "plugins").mkdir()
    (launcher.parent / "scripts").mkdir()
    return launcher


class FijiIntegrationTests(unittest.TestCase):
    def test_installation_is_validated_by_real_files_and_checksum(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            launcher = fake_fiji(Path(tmp))
            result = inspect_installation(launcher.parent)
            self.assertTrue(result["valid"])
            self.assertEqual(64, len(result["launcher_sha256"]))
            self.assertEqual(str(launcher.resolve()), result["launcher_path"])

    def test_configuration_and_discovery_preserve_selected_launcher(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            launcher = fake_fiji(root)
            with patch.dict(os.environ, {"HEALTH_MODEL_DATA_DIR": str(root / "data")}), patch(
                "research.fiji_integration._candidate_launchers", return_value=[launcher]
            ):
                configure_installation(str(launcher))
                result = discover_installations()
                self.assertEqual(str(launcher.resolve()), result["configured_launcher"])
                self.assertEqual(1, len(result["detected"]))

    def test_pipeline_never_overwrites_raw_input_and_builds_declared_steps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.tif"
            source.write_bytes(b"image")
            payload = {
                "input_path": str(source),
                "output_path": str(root / "processed.tif"),
                "apply_to_stack": True,
                "operations": [
                    {"code": "convert_8bit", "parameters": {}},
                    {"code": "median_filter", "parameters": {"radius": 2}},
                    {"code": "auto_threshold", "parameters": {"method": "Otsu", "background": "Dark"}},
                    {"code": "convert_to_mask", "parameters": {"background": "Dark"}},
                ],
                "time_reference": {"axis": "UTC", "frame_interval_seconds": 0.04},
            }
            pipeline = validate_pipeline(payload)
            macro = build_macro(pipeline)
            self.assertIn('run("Median...", "radius=2.0 stack")', macro)
            self.assertIn('setAutoThreshold("Otsu Dark")', macro)
            self.assertEqual("UTC", pipeline["time_reference"]["axis"])
            with self.assertRaisesRegex(FijiIntegrationError, "MUST_NOT_OVERWRITE"):
                validate_pipeline({**payload, "output_path": str(source)})

    def test_contract_exposes_real_modes_provenance_and_global_time(self) -> None:
        contract = integration_contract("en")
        self.assertIn("interactive_with_bridge", contract["execution_modes"])
        self.assertIn("headless_reproducible_pipeline", contract["execution_modes"])
        self.assertEqual("required_when_frames_represent_time", contract["input_contract"]["global_time_binding"])
        self.assertIn("fiji_launcher_sha256", contract["output_contract"]["provenance_required"])


if __name__ == "__main__":
    unittest.main()
