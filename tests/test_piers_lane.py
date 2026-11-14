"""Piers lock invariant; real packages run separately in tests/lanes/piers.py."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PiersLockTests(unittest.TestCase):
    def test_preserves_all_other_nexus_pins_and_hashes(self):
        def without_stub(filename):
            text = (ROOT / filename).read_text()
            return re.sub(r"^Kodistubs==[^\n]+\n(?:    --hash=sha256:[a-f0-9]+(?: \\)?\n?)+",
                          "", "\n".join(text.splitlines()[2:]), flags=re.M)
        self.assertEqual(without_stub("requirements-piers.lock"), without_stub("requirements-dev.lock"))
        lock = (ROOT / "requirements-piers.lock").read_text()
        self.assertIn("Kodistubs==22.0.1rc1", lock)
        self.assertIn("a211fcb3215f2c8891f4f1efb4f1aaf562d85172efbe439ef68f95af0152ea6d", lock)
