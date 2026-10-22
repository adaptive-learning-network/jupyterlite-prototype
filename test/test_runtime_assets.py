"""Validate the real bundled metadata and the SDK's browser Response contract."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from localize_xeus_mapping import ROOT, UPSTREAM_URL, localize_xeus_mapping, localized_xeus_load


class RuntimeAssets(unittest.TestCase):
    def test_aliases_resolve_without_a_network_request_and_patch_is_idempotent(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            bundle = output / "extensions/@jupyterlite/xeus-extension/static/bundle.js"
            bundle.parent.mkdir(parents=True)
            # Make any unpatched fetch fail; Node supplies the same Fetch Response API.
            bundle.write_text('globalThis.fetch=()=>{throw Error("network request")};\n'
                              'fetch(' + json.dumps(UPSTREAM_URL) + ').then(r=>r.json()).then(m=>'
                              'console.log(JSON.stringify(m)));', encoding="utf-8")
            bundle.with_suffix(".js.map").write_text("stale upstream map", encoding="utf-8")
            self.assertEqual(localize_xeus_mapping(output), 1)
            versioned = output / "extensions/@jupyterlite/xeus-extension" / localized_xeus_load("static/bundle.js")
            self.assertNotIn(UPSTREAM_URL, versioned.read_text(encoding="utf-8"))
            self.assertEqual(localize_xeus_mapping(output), 0)
            self.assertFalse(bundle.parent.exists(), "Do not duplicate unused runtime files in the deployment artifact")
            self.assertFalse(versioned.with_suffix(".js.map").exists())
            self.assertEqual(localized_xeus_load(localized_xeus_load("static/bundle.js")), localized_xeus_load("static/bundle.js"))
            self.assertTrue((output / "assets/runtime/parselmouth-LICENSE").is_file())
            node = shutil.which("node")
            self.assertIsNotNone(node, "Node is required by the course build")
            result = subprocess.run([node, str(versioned)], check=True, capture_output=True, text=True)
            expected = json.loads((ROOT / "app-assets/runtime/conda-pypi-mapping.json").read_text(encoding="utf-8"))
            self.assertEqual(json.loads(result.stdout), expected)

    def test_changed_metadata_is_rejected_before_bundling(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "changed.json"
            source.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                localize_xeus_mapping(Path(folder), source)
