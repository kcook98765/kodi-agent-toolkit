"""Offline contract checks for the explicit trusted managed profile and skill inventory."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / ".agents/skills/kodi-mcp-testing/references/current-contract.md"
WORKFLOW = ROOT / ".agents/skills/kodi-mcp-testing/references/managed-agent-workflow.md"
OPTIONAL = ROOT / "examples/opencode/trusted-managed-lab.json"
DEFAULT = ROOT / "examples/opencode/agents.json"

CURRENT_TOOL_NAMES = {
    "target_list", "target_status", "addon_list", "inspect_ui_state", "log_read",
    "screenshot_capture", "screenshot_retrieve", "remote_action",
    "managed_status", "managed_start", "managed_stop", "managed_reset",
    "managed_ensure_ready", "managed_release", "managed_selection_preview",
    "managed_select", "workspace_deploy_preflight", "workspace_deploy",
    "workspace_execute", "workspace_launch", "development_launch",
    "workspace_execution_recover", "addon_settings_set", "addon_settings_result",
    "promotion_request", "package_install", "package_install_status",
    "project_create", "project_transfer", "project_import", "project_status",
    "package_import", "package_status", "development_source_list",
    "workspace_create", "workspace_import_preview", "workspace_import",
    "workspace_source_scan", "workspace_capture", "workspace_status",
    "workspace_tree", "workspace_read", "workspace_edit", "workspace_validate",
}
MUTATION_TOOLS = {
    "managed_start", "managed_stop", "managed_reset", "managed_ensure_ready",
    "managed_release", "managed_select", "remote_action", "workspace_deploy",
    "workspace_execute", "workspace_launch", "development_launch",
    "workspace_execution_recover", "addon_settings_set", "project_create",
    "project_transfer", "project_import", "package_import", "package_install",
    "workspace_create", "workspace_import", "workspace_capture", "workspace_edit",
    "promotion_request",
}


class CurrentManagedContractTests(unittest.TestCase):
    def test_index_covers_exactly_44_unique_tools(self):
        text = MATRIX.read_text(encoding="utf-8")
        section = text.split("### Current source inventory (44)", 1)[1].split("---", 1)[0]
        found = re.findall(r"`([a-z][a-z0-9_]+)`", section)
        self.assertEqual(len(found), 44)
        self.assertEqual(len(set(found)), 44)
        self.assertEqual(set(found), CURRENT_TOOL_NAMES)

    def test_optional_profile_has_explicit_deny_by_default(self):
        config = json.loads(OPTIONAL.read_text(encoding="utf-8"))
        self.assertEqual(set(config), {"$schema", "agent"})
        self.assertEqual(set(config["agent"]), {"kodi-managed-lab"})
        agent = config["agent"]["kodi-managed-lab"]
        self.assertEqual(agent["mode"], "primary")
        self.assertNotIn("model", agent)
        rules = agent["permission"]
        self.assertEqual(rules["*"], "deny")
        self.assertEqual(rules["bash"], "ask")
        self.assertEqual(rules["external_directory"], "deny")
        for tool in ("managed_status", "managed_start", "managed_stop", "managed_reset",
                     "project_create", "project_import", "project_transfer",
                     "workspace_deploy", "workspace_launch", "addon_settings_set"):
            self.assertEqual(rules["kodi_lab_dev_" + tool], "allow")
        for tool in ("package_install", "package_import", "promotion_request"):
            self.assertNotIn("kodi_lab_dev_" + tool, rules)
        for prefixed in rules:
            if prefixed.startswith("kodi_lab_dev_"):
                self.assertIn(prefixed.removeprefix("kodi_lab_dev_"), CURRENT_TOOL_NAMES)
            self.assertFalse(prefixed.startswith("kodi_lab_production_"))
        self.assertNotIn("mcp", config)
        self.assertNotIn("provider", config)

    def test_daily_roles_stay_narrow(self):
        config = json.loads(DEFAULT.read_text(encoding="utf-8"))
        self.assertNotIn("kodi-managed-lab", config["agent"])
        for agent in config["agent"].values():
            for name in ("managed_reset", "managed_start", "managed_stop", "project_create"):
                self.assertNotEqual(agent["permission"].get("kodi_lab_dev_" + name), "allow")

    def test_workflow_preserves_security_and_receipts(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        for term in ("expected_profile", "bridge_preparation", "project_import",
                     "project_transfer", "workspace_deploy_preflight", "direct",
                     "human", "UUID", "package_install", "repository"):
            self.assertIn(term.lower(), text.lower())


if __name__ == "__main__":
    unittest.main()
