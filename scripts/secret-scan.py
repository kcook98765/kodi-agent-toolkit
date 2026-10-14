"""Heuristic scan of public Git candidates; findings never contain matched values."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Iterator

ROOT = Path(__file__).resolve().parents[1]
rules = {
    "private-IP": re.compile(rb"\b(?:192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+)\b"),
    "private-host": re.compile(rb"(?<![A-Za-z])(?:[A-Za-z0-9-]+\.)?home\.arpa\b"),
    "private-key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----"),
    "credential-value": re.compile(rb"(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|Bearer [A-Za-z0-9_-]{30,})"),
}


def git(root: Path, *arguments: str) -> bytes:
    result = subprocess.run(["git", "-C", str(root), *arguments],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        # Git stderr can contain private paths/configuration; do not repeat it.
        raise RuntimeError("Git candidate enumeration failed")
    return result.stdout


def blob_candidates(root: Path, mode: str) -> Iterator[tuple[str, bytes]]:
    if mode == "staged":
        entries = git(root, "ls-files", "--stage", "-z").split(b"\0")
        for entry in filter(None, entries):
            metadata, name = entry.split(b"\t", 1)
            oid = metadata.split()[1].decode("ascii")
            yield os.fsdecode(name), git(root, "cat-file", "blob", oid)
        return
    # Enumerate commit trees with NUL delimiters so spaces/newlines in paths work.
    # Identical blobs need scanning once, even if many commits reference them.
    seen = set()
    for commit in git(root, "rev-list", "--all").decode("ascii").splitlines():
        entries = git(root, "ls-tree", "-r", "--full-tree", "-z", commit).split(b"\0")
        for entry in filter(None, entries):
            metadata, name = entry.split(b"\t", 1)
            _, kind, oid = metadata.split()
            if kind != b"blob" or oid in seen:
                continue
            seen.add(oid)
            yield os.fsdecode(name), git(root, "cat-file", "blob", oid.decode("ascii"))


def public_name(filename: str, known: tuple[bytes, ...]) -> str:
    name = os.fsencode(filename)
    for value in known:
        name = name.replace(value, b"[REDACTED]")
    for rule in rules.values():
        name = rule.sub(b"[REDACTED]", name)
    return os.fsdecode(name)


def scan(root: Path, mode: str = "working-tree",
         known: tuple[bytes, ...] = ()) -> dict:
    if mode not in {"working-tree", "staged", "history"}:
        raise ValueError("Unknown scan mode")
    hits = []
    scanned = 0
    if mode == "working-tree":
        names = git(root, "ls-files", "--cached", "--others",
                    "--exclude-standard", "-z").split(b"\0")
        candidates = []
        for name in sorted(set(filter(None, names))):
            filename = os.fsdecode(name)
            file = root / filename
            if file.is_symlink() or any(p.is_symlink() for p in file.parents if p != root):
                hits.append({"file": public_name(filename, known), "rule": "symlink-not-scanned"})
                continue
            if not file.exists():  # Deleted worktree file; index/history modes inspect its blob.
                continue
            try:
                data = file.read_bytes()
            except OSError:
                hits.append({"file": public_name(filename, known), "rule": "unreadable-file"})
                continue
            candidates.append((filename, data))
    else:
        candidates = blob_candidates(root, mode)
    for filename, data in candidates:
        scanned += 1
        # Bytes preserve exact credentials in images, binary and non-UTF-8 files.
        name = os.fsencode(filename)
        label = public_name(filename, known)
        if any(value in data or value in name for value in known):
            hits.append({"file": label, "rule": "known-local-credential"})
        for category, rule in rules.items():
            if rule.search(data) or rule.search(name):
                hits.append({"file": label, "rule": category})
    return {"passed": not hits, "findings": hits, "mode": mode,
            "files_scanned": scanned}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--staged", action="store_true", help="Scan actual index blobs, not worktree copies")
    modes.add_argument("--history", action="store_true", help="Scan all blobs reachable from all Git refs")
    parser.add_argument("--secret-file", type=Path, action="append", default=[],
                        help="Private exact-value denylist file; contents are never printed")
    args = parser.parse_args(argv)
    try:
        known = tuple(file.read_bytes().strip() for file in args.secret_file)
    except OSError:
        parser.error("Unable to read an exact-value denylist file")
    if any(len(value) < 16 for value in known):
        parser.error("Known credential files must contain a nontrivial exact value")
    mode = "staged" if args.staged else "history" if args.history else "working-tree"
    try:
        result = scan(ROOT, mode, known)
    except (OSError, RuntimeError):
        print(json.dumps({"passed": False, "findings": [{"file": ".", "rule": "git-scan-failed"}],
                          "mode": mode}))
        return 2
    print(json.dumps(result))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
