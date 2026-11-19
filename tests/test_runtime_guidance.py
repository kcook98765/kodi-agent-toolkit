"""Offline guardrails for current agent workflow instructions."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / ".agents/skills/kodi-mcp-testing/references"


class RuntimeGuidanceTests(unittest.TestCase):
    def test_both_launch_paths_keep_distinct_authority_and_observation(self):
        for name in ("managed-agent-workflow.md", "mcp.md"):
            text = (REF / name).read_text(encoding="utf-8")
            with self.subTest(reference=name):
                for term in ("development_launch", "development.launch", "workspace.inspect",
                             "workspace_launch", "development.execute", "target.control",
                             "Program", "mixed", "dispatch", "fresh", "unchanged"):
                    self.assertIn(term, text)
                self.assertIn("does not require `target.control`", text)

    def test_promotion_reports_prerequisite_without_self_repair_authority(self):
        text = (REF / "managed-agent-workflow.md").read_text(encoding="utf-8")
        section = text.split("## Registered-source promotion diagnostics", 1)[1].split("\n## ", 1)[0]
        for term in ("promotion_source_not_writable", "invalidation_reason", "next_action",
                     "original", "service account", "Do not chmod/chown", "ineligible",
                     "stays invalidated", "Never replace an unresolved operation's UUID"):
            self.assertIn(term, section)

    def test_current_installation_limits_are_closed_not_promised(self):
        text = (REF / "managed-agent-workflow.md").read_text(encoding="utf-8")
        self.assertNotIn("remains unresolved", text)
        for number in (305, 339):
            self.assertIn(f"#{number}, closed Not planned", text)


if __name__ == "__main__":
    unittest.main()
