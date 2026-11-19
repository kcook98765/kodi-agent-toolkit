"""Keep newer integration evidence separate from historical beta trial claims."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
ANCHOR = "evaluation.md#2026-11-18-kodi-labopencode-integration-acceptance"


class AcceptanceDocumentationTests(unittest.TestCase):
    def test_entry_points_link_to_separate_integration_evidence(self):
        for name in ("README.md", "docs/public-beta.md", "docs/development-workflow.md"):
            with self.subTest(document=name):
                self.assertIn(ANCHOR, (ROOT / name).read_text(encoding="utf-8"))

    def test_acceptance_keeps_coverage_denominator_and_scope(self):
        text = (ROOT / "docs/evaluation.md").read_text(encoding="utf-8")
        section = text.split("## 2026-11-18 Kodi Lab/OpenCode integration acceptance", 1)[1]
        for term in ("509 actual MCP calls", "38 focused scenarios", "19 sessions",
                     "44 of 46", "32 additional", "PARTIAL", "four fixes",
                     "Matrix 19.4, Nexus 20.5, Omega 21.3 and Piers 22.0 RC2",
                     "do not isolate", "Neither campaign independently qualifies",
                     "issues/384#issuecomment-6999444095"):
            self.assertIn(term, section)

    def test_historical_failed_and_blocked_results_remain(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        beta = (ROOT / "docs/public-beta.md").read_text(encoding="utf-8")
        self.assertIn("2 PASS, 6 PARTIAL, 5 FAIL", readme)
        self.assertIn("not validated end-to-end", readme)
        self.assertIn("runtime deployment qualification is reported separately as BLOCKED", beta)
        self.assertIn("historical beta classification", beta)


if __name__ == "__main__":
    unittest.main()
