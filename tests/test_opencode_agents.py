"""Check the portable roles and independent connection boundaries offline."""
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples/opencode"
AGENTS = json.loads((EXAMPLES / "agents.json").read_text())["agent"]


def allowlist(agent):
    return {name for name, action in AGENTS[agent]["permission"].items() if action == "allow"}


class OpenCodeAgentBoundaryTests(unittest.TestCase):
    def test_external_permissions_are_current_and_separately_scoped(self):
        text = (ROOT / ".agents/skills/kodi-mcp-testing/references/current-contract.md").read_text()
        external = text.split("## External tools", 1)[1]
        declared = set(re.findall(r"^\| `([a-z_]+)` \|", external, re.M))
        scoped = {name[len("kodi_lab_external_dev_"):] for name in allowlist("kodi-external-develop")
                  if name.startswith("kodi_lab_external_dev_")}
        self.assertEqual(len(declared), 13)
        self.assertEqual(scoped, declared)
        for role in ("kodi-inspect", "kodi-support"):
            allowed = allowlist(role)
            observed = {name[len("kodi_lab_"):] for name in allowed if name.startswith("kodi_lab_")}
            self.assertLessEqual(observed, declared)
            self.assertTrue({"target_status", "system_info", "log_read", "log_scan"} <= observed)
            self.assertFalse({"remote_action", "workspace_deploy", "workspace_execute"} & observed)
            self.assertFalse({"bash", "edit", "task", "external_directory"} & allowed)
        self.assertIn("kodi_lab_screenshot_capture", allowlist("kodi-inspect"))
        self.assertNotIn("kodi_lab_screenshot_capture", allowlist("kodi-support"))

    def test_local_developer_and_common_role_defaults(self):
        self.assertFalse(any(name.startswith("kodi_lab_") for name in allowlist("kodi-develop")))
        for agent in AGENTS.values():
            self.assertNotIn("model", agent)
            self.assertEqual(agent["permission"]["*"], "deny")
            self.assertEqual(agent["permission"]["external_directory"], "deny")
            self.assertEqual(agent["permission"]["skill"]["*"], "deny")
            for name, action in agent["permission"]["skill"].items():
                if action == "allow":
                    self.assertTrue((ROOT / ".agents/skills" / name / "SKILL.md").is_file())
            self.assertFalse(any("managed_" in name for name in agent["permission"]))

    def test_connections_default_disabled_with_private_substitution(self):
        connections = json.loads((EXAMPLES / "connections.example.json").read_text())["mcp"]
        self.assertEqual(set(connections), {"kodi_lab", "kodi_lab_dev", "kodi_lab_external_dev"})
        for connection in connections.values():
            self.assertIs(connection["enabled"], False)
            self.assertRegex(connection["url"], r"^\{env:[A-Z_]+\}$")
            self.assertRegex(connection["headers"]["Authorization"], r"^Bearer \{env:[A-Z_]+\}$")
