"""Secret scanner regressions use only isolated, disposable Git repositories."""
from pathlib import Path
import json
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCANNER = ROOT / "scripts/secret-scan.py"
scan = runpy.run_path(str(SCANNER))["scan"]


class SecretScanTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="toolkit-secret-scan-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "repo with spaces"
        self.root.mkdir()
        self.git("init", "-q")
        self.git("config", "user.name", "Scanner tests")
        self.git("config", "user.email", "scanner@localhost")
        self.secret = b"sk-" + b"A" * 24

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def write(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-qm", message)

    def test_default_excludes_ignored_private_files(self):
        self.write(".gitignore", b".private/\n")
        self.write(".private/provider.json", self.secret)
        self.write("public.txt", b"public example")
        self.assertTrue(scan(self.root)["passed"])

    def test_binary_and_non_utf8_candidates_are_scanned(self):
        self.write("picture.png", b"\x89PNG\xff" + self.secret)
        self.write("opaque.dat", b"\xff\xfe" + self.secret)
        result = scan(self.root)
        self.assertFalse(result["passed"])
        self.assertEqual({hit["file"] for hit in result["findings"]},
                         {"picture.png", "opaque.dat"})

    def test_index_blob_is_scanned_even_when_worktree_is_clean(self):
        file = self.write("staged.txt", self.secret)
        self.git("add", "staged.txt")
        file.write_bytes(b"clean worktree")
        self.assertTrue(scan(self.root)["passed"])
        self.assertFalse(scan(self.root, "staged")["passed"])

    def test_index_mode_does_not_substitute_unstaged_content(self):
        file = self.write("staged.txt", b"clean index")
        self.git("add", "staged.txt")
        file.write_bytes(self.secret)
        self.assertTrue(scan(self.root, "staged")["passed"])
        self.assertFalse(scan(self.root)["passed"])

    def test_deleted_historical_credential_is_detected(self):
        file = self.write("removed.txt", self.secret)
        self.commit("temporary synthetic credential")
        file.unlink()
        self.write("clean.txt", b"clean")
        self.commit("remove synthetic credential")
        self.assertTrue(scan(self.root)["passed"])
        self.assertTrue(scan(self.root, "staged")["passed"])
        result = scan(self.root, "history")
        self.assertFalse(result["passed"])
        self.assertEqual(result["findings"][0]["file"], "removed.txt")

    def test_paths_with_spaces_and_newlines_survive_git_enumeration(self):
        if sys.platform == "win32":
            self.skipTest("Windows rejects newlines in file names")
        name = "folder with spaces/file\nname.txt"
        self.write(name, self.secret)
        self.commit("path fixture")
        for mode in ("working-tree", "staged", "history"):
            self.assertEqual(scan(self.root, mode)["findings"][0]["file"], name)

    def test_known_value_is_checked_in_binary_without_printing_it(self):
        known = b"opaque-" + b"credential" * 3
        self.write("binary.png", b"\x89PNG\xff" + known)
        self.commit("binary known-value fixture")
        for mode in ("working-tree", "staged", "history"):
            result = scan(self.root, mode, known=(known,))
            self.assertEqual(result["findings"][0]["rule"], "known-local-credential")
            self.assertNotIn(known.decode(), json.dumps(result))

    def test_sensitive_filename_is_flagged_and_redacted(self):
        self.write(self.secret.decode() + ".txt", b"clean content")
        result = scan(self.root)
        self.assertFalse(result["passed"])
        self.assertNotIn(self.secret.decode(), json.dumps(result))
        self.assertEqual(result["findings"][0]["file"], "[REDACTED].txt")

    def test_history_includes_non_head_branch(self):
        self.write("clean.txt", b"clean")
        self.commit("initial")
        branch = self.git("branch", "--show-current").stdout.decode().strip()
        self.git("checkout", "-qb", "synthetic-credential-branch")
        self.write("branch.txt", self.secret)
        self.commit("branch-only fixture")
        self.git("checkout", "-q", branch)
        self.assertTrue(scan(self.root)["passed"])
        self.assertFalse(scan(self.root, "history")["passed"])

    def test_symlink_is_not_followed_into_private_file(self):
        private = Path(self.temporary.name) / "private.txt"
        private.write_bytes(self.secret)
        link = self.root / "link.txt"
        try:
            link.symlink_to(private)
        except OSError:
            self.skipTest("Symlink creation unavailable on this platform")
        result = scan(self.root)
        self.assertEqual(result["findings"], [
            {"file": "link.txt", "rule": "symlink-not-scanned"}])

    def test_cli_uses_its_repository_root_and_redacts_exact_value(self):
        copied = self.root / "scripts/secret-scan.py"
        copied.parent.mkdir()
        shutil.copy2(SCANNER, copied)
        known = b"opaque-" + b"credential" * 3
        private = Path(self.temporary.name) / "denylist"
        private.write_bytes(known + b"\n")
        self.write("binary.png", b"\xff" + known)
        result = subprocess.run([sys.executable, str(copied), "--secret-file", str(private)],
                                cwd=self.temporary.name, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(known.decode(), result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["findings"][0]["file"], "binary.png")

    def test_cli_git_failure_is_explicit_and_contains_no_traceback(self):
        copied = Path(self.temporary.name) / "scripts/secret-scan.py"
        copied.parent.mkdir()
        shutil.copy2(SCANNER, copied)
        result = subprocess.run([sys.executable, str(copied)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(json.loads(result.stdout)["passed"])
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
