"""Protect the portable presets' permission boundaries without contacting services."""
import fnmatch
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "opencode"
AGENTS = json.loads((EXAMPLES / "agents.json").read_text(encoding="utf-8"))["agent"]


def effect(rules, tool):
    """Evaluate the ordered flat rules used by these example permission maps."""
    result = None
    for pattern, action in rules.items():
        if fnmatch.fnmatchcase(tool, pattern):
            result = action
    return result


class OpenCodeAgentBoundaryTests(unittest.TestCase):
    def test_inspection_roles_deny_mutations_shell_and_delegation(self):
        forbidden = ["bash", "edit", "task", "external_directory", "new_unknown_tool",
                     "kodi_lab_remote_action", "kodi_lab_workspace_deploy",
                     "kodi_lab_dev_workspace_edit", "kodi_lab_dev_workspace_validate",
                     "kodi_lab_dev_workspace_deploy", "kodi_lab_dev_workspace_launch",
                     "kodi_lab_dev_workspace_execute"]
        for name, agent in AGENTS.items():
            if name in {"kodi-develop", "kodi-test"}:
                continue
            for tool in forbidden:
                with self.subTest(agent=name, tool=tool):
                    self.assertEqual(effect(agent["permission"], tool), "deny")
            self.assertEqual(effect(agent["permission"], "kodi_lab_target_status"), "allow")

    def test_tester_cannot_change_source_or_prepare_infrastructure(self):
        rules = AGENTS["kodi-test"]["permission"]
        for tool in ["bash", "edit", "task", "kodi_lab_dev_workspace_create",
                     "kodi_lab_dev_workspace_edit", "kodi_lab_dev_workspace_import",
                     "kodi_lab_dev_source_prepare", "kodi_lab_remote_action"]:
            with self.subTest(tool=tool):
                self.assertEqual(effect(rules, tool), "deny")
        self.assertEqual(effect(rules, "kodi_lab_dev_workspace_deploy_preflight"), "allow")
        self.assertEqual(effect(rules, "kodi_lab_dev_workspace_launch"), "allow")

    def test_no_preset_grants_unrelated_servers_or_lifecycle_operations(self):
        for name, agent in AGENTS.items():
            for tool in ["kodi_lab_control_remote_action", "kodi_lab_production_target_status",
                         "kodi_lab_dev_target_restart", "kodi_lab_target_start",
                         "unrelated_server_workspace_edit"]:
                with self.subTest(agent=name, tool=tool):
                    self.assertEqual(effect(agent["permission"], tool), "deny")
        self.assertEqual(effect(AGENTS["kodi-develop"]["permission"], "bash"), "ask")

    def test_presets_use_installed_skills_and_inherit_model(self):
        config = json.loads((EXAMPLES / "agents.json").read_text(encoding="utf-8"))
        self.assertEqual(set(config), {"$schema", "agent"})
        for name, agent in AGENTS.items():
            with self.subTest(agent=name):
                self.assertEqual(agent["mode"], "primary")
                self.assertNotIn("model", agent)
                skill_rules = agent["permission"]["skill"]
                self.assertEqual(skill_rules["*"], "deny")
                for skill, action in skill_rules.items():
                    if action == "allow":
                        self.assertTrue((ROOT / ".agents" / "skills" / skill / "SKILL.md").is_file())

    def test_connection_examples_are_disabled_and_have_no_embedded_credentials(self):
        config = json.loads((EXAMPLES / "connections.example.json").read_text(encoding="utf-8"))
        self.assertEqual(set(config), {"$schema", "mcp"})
        self.assertEqual(set(config["mcp"]), {"kodi_lab", "kodi_lab_dev"})
        for connection in config["mcp"].values():
            self.assertIs(connection["enabled"], False)
            self.assertRegex(connection["url"], r"^\{env:[A-Z_]+\}$")
            self.assertRegex(connection["headers"]["Authorization"], r"^Bearer \{env:[A-Z_]+\}$")


if __name__ == "__main__":
    unittest.main()
