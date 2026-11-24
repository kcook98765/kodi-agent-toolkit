"""Keep outdated operations out of the current skill entry points."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class RuntimeGuidanceTests(unittest.TestCase):
    def test_ordinary_guidance_has_no_retired_managed_calls(self):
        current = [*ROOT.glob(".agents/skills/**/*.md"),
                   ROOT / "docs/development-workflow.md", ROOT / "docs/opencode-agents.md"]
        retired = ("managed_selection_preview", "managed_ensure_ready", "package_install_status",
                   "promotion_request", "workspace_launch", "bridge_preparation")
        for path in current:
            text = path.read_text()
            with self.subTest(file=path):
                for name in retired:
                    self.assertNotIn(name, text)

    def test_mixed_python_notes_preserve_install_and_service_boundaries(self):
        notes = (ROOT / ".agents/skills/kodi-mcp-testing/references/mixed-python-addons.md").read_text()
        self.assertIn("Kodi owns the service lifecycle", notes)
        self.assertIn("allow_services", notes)
        self.assertIn('start="login"', notes)
