"""Matrix lock invariants, also exercised by the default Nexus regression job."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class MatrixLockTests(unittest.TestCase):
    def test_preserves_nexus_dependencies_except_stubs(self):
        def pins(filename):
            return dict(re.findall(r"^([\w.-]+)==([^\s\\]+)",
                                   (ROOT / filename).read_text(), re.M))
        nexus = pins("requirements-dev.lock")
        matrix = pins("requirements-matrix.lock")
        self.assertEqual(matrix.pop("Kodistubs"), "19.0.3")
        self.assertEqual(nexus.pop("Kodistubs"), "20.0.1")
        self.assertEqual(matrix, nexus)
        self.assertEqual(pins("requirements-matrix.in")["Kodistubs"], "19.0.3")
        self.assertIn("aef7fb14ea2349d2ecf673a240e72e87aff0a34966e0ac9ec15ce90d2b7b84e3",
                      (ROOT / "requirements-matrix.lock").read_text())
