"""Keep the candidate recipe bounded and connected to actual runtime checks."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class IntegrationSmokeRecipeTests(unittest.TestCase):
    def test_operator_recipe_covers_config_native_results_and_cleanup(self):
        text = (ROOT / "docs/integration-smoke.md").read_text()
        for term in ("disposable packaged site", "debug skill", "debug agent", "mcp list",
                     "tools/list", "fresh execution", "same-version", "snapshot/Reset/Load",
                     "explicit authority", "MCP tool events", "Stop and release"):
            self.assertIn(term, text)
        self.assertNotIn("--auto", text)
        for name in ("README.md", "docs/opencode-agents.md"):
            self.assertIn("integration-smoke.md", (ROOT / name).read_text())
