"""Compare managed application documentation with the explicit client allowlist."""
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / ".agents/skills/kodi-mcp-testing/references"
EXAMPLES = ROOT / "examples/opencode"


class ManagedContractTests(unittest.TestCase):
    def test_all_managed_tools_use_an_explicit_prefix_and_no_external_authority(self):
        contract = (REF / "current-contract.md").read_text()
        documented = set(re.findall(r"^\| `(managed_[a-z_]+)` \|", contract, re.M))
        preset = json.loads((EXAMPLES / "trusted-managed-lab.json").read_text())
        self.assertEqual(set(preset), {"$schema", "agent"})
        agent = preset["agent"]["kodi-managed-lab"]
        self.assertNotIn("model", agent)
        rules = agent["permission"]
        self.assertEqual(rules["*"], "deny")
        self.assertEqual(rules["external_directory"], "deny")
        self.assertEqual(rules["bash"], "ask")
        discovered = {tool.removeprefix("kodi_lab_dev_") for tool, effect in rules.items()
                      if tool.startswith("kodi_lab_dev_") and effect == "allow"}
        self.assertEqual(len(discovered), 27)
        self.assertEqual(discovered, documented)
        self.assertFalse(any(name.startswith(("kodi_lab_external_", "kodi_lab_production_"))
                             for name in rules))

    def test_default_workflow_uses_current_install_and_source_operations(self):
        workflow = (REF / "managed-agent-workflow.md").read_text()
        for name in ("managed_acquire", "managed_release", "managed-package-import",
                     "managed_addon_install", "managed_workspace_deploy",
                     "managed_snapshot_save", "managed_snapshot_load"):
            self.assertIn(name, workflow)
        self.assertIn("exact compatible runtime image", workflow)
        self.assertIn("verified package, dependency results and enablement", workflow)
        self.assertIn("Confirm execution separately", workflow)
        self.assertIn("one", workflow.lower())
        self.assertNotIn("workspace_deploy_preflight", workflow)
