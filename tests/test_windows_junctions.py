"""Actual Windows junction boundaries without changing OS security settings."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from kodi_agent_toolkit.review import _root, _safe_path, EvidenceError
from kodi_agent_toolkit.checker_runner import inspect_source, SourceViolation


@unittest.skipUnless(os.name == 'nt', 'Native Windows junction functionality')
class JunctionTests(unittest.TestCase):
    def test_existing_inside_and_outside_junctions_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix='Kodi junction ') as t:
            parent=Path(t);root=parent/'addon';root.mkdir()
            inside=root/'actual';inside.mkdir();outside=parent/'outside';outside.mkdir()
            for target in (inside,outside):
                (target/'code.py').write_text('pass\n')
            for name,target in (('internal',inside),('external',outside)):
                link=root/name
                env={**os.environ,'KODI_TEST_LINK':str(link),'KODI_TEST_TARGET':str(target)}
                p=subprocess.run(['powershell.exe','-NoProfile','-Command',
                    'New-Item -ItemType Junction -Path $env:KODI_TEST_LINK -Target $env:KODI_TEST_TARGET | Out-Null'],
                    env=env,capture_output=True,text=True)
                self.assertEqual(p.returncode,0,p.stderr)
                with self.assertRaises(EvidenceError):_safe_path(root,name+'/code.py')
                with self.assertRaises(EvidenceError):_root(link)
                with self.assertRaises(SourceViolation):inspect_source(root)
                # rmdir removes the junction itself, never recurses into its target.
                os.rmdir(link)
                self.assertTrue((target/'code.py').is_file())
