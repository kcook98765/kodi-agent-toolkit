"""Public harness must not infer providers or read workstation credentials."""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

class PublicHarnessTests(unittest.TestCase):
    def load(self):
        spec = importlib.util.spec_from_file_location("public_harness", ROOT / "evaluation/run.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_default_import_never_searches_private_credentials(self):
        with patch.dict(os.environ, {"KODI_EVAL_SECRET_FILES": ""}), patch.object(Path, "glob", side_effect=AssertionError("Implicit credential discovery")):
            runner = self.load()
        self.assertEqual(runner.TOKENS, [])
        with self.assertRaisesRegex(ValueError, "explicit provider/model ID"):
            runner.run("coder", "xml", False, "never-created")

    def test_explicit_secret_files_redact_nested_text_without_printing_values(self):
        with tempfile.TemporaryDirectory() as temporary:
            file = Path(temporary) / "credential.txt"
            secret = "synthetic-private-credential-value"
            file.write_text(secret, encoding="utf-8")
            with patch.dict(os.environ, {"KODI_EVAL_SECRET_FILES": str(file)}):
                runner = self.load()
            result = runner.clean({"authorization": "hidden", "content": [{"text": "value " + secret}]})
            self.assertEqual(result["authorization"], "[REDACTED]")
            self.assertNotIn(secret, str(result))
            self.assertIn("[CREDENTIAL REDACTED]", str(result))
