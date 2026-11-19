"""Guard the recipe's runnable examples and opt-in evidence boundaries offline."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
RECIPE = ROOT / "docs/integration-smoke.md"


class IntegrationSmokeRecipeTests(unittest.TestCase):
    def test_shell_examples_only_inspect_configuration_or_help(self):
        text = RECIPE.read_text(encoding="utf-8")
        allowed = {
            "opencode --version", "opencode debug --help", "opencode mcp --help",
            "opencode run --help", "opencode debug config --pure",
            "opencode debug agent kodi-inspect --pure", "opencode debug skill --pure",
            "opencode mcp list --pure",
        }
        commands = [line.strip() for block in re.findall(r"```sh\n(.*?)```", text, re.S)
                    for line in block.splitlines() if line.strip()]
        self.assertTrue(commands)
        self.assertTrue(set(commands) <= allowed)
        self.assertNotIn("--auto", text)

    def test_mutations_and_negative_checks_keep_existing_authority(self):
        text = RECIPE.read_text(encoding="utf-8")
        for term in ("separate affirmative authorization", "before this scenario",
                     "No automatic Reset", "already appropriately restricted authority",
                     "Do not create credentials or change permissions",
                     "original UUID/arguments", "Never stop pre-existing",
                     "20 calls and 15 minutes", "10 MCP calls and 10 minutes"):
            self.assertIn(term, text)

    def test_evidence_distinguishes_recipe_from_actual_native_execution(self):
        text = RECIPE.read_text(encoding="utf-8")
        for term in ("tools/list", "target_status", "system_info", "one additional authorized inspection",
                     "kodi_lab_system_info", "kodi_lab_dev_system_info", "operation",
                     "PARTIAL", "BLOCKED", "EXPECTED DENIAL", "Cleanup", "retained",
                     "It did not run this live smoke", "model's final prose"):
            self.assertIn(term, text)
        for name in ("README.md", "docs/opencode-agents.md"):
            self.assertIn("integration-smoke.md", (ROOT / name).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
