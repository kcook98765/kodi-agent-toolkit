#!/usr/bin/env python3
"""Explicit acquisition of official HTTPS repository metadata, never add-on ZIPs.

Run with the toolkit .venv Python. The default cache is ignored .local/index-cache.
All ten indexes are necessary even for a single target branch. No automatic
fetch occurs during validate/replay. Refresh is explicit; manifest hashes detect
corruption, not malicious replacement of both content and its trusted manifest.
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import io
import json
import os
import re
from pathlib import Path
import tempfile
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

BRANCHES = ("gotham", "helix", "isengard", "jarvis", "krypton", "leia",
            "matrix", "nexus", "omega", "piers")
MAX_GZIP = 32 * 1024 * 1024
MAX_XML = 256 * 1024 * 1024


def safe_directory(path: Path) -> Path:
    if ".." in path.parts:
        raise ValueError("Cache traversal is not allowed")
    path = path.absolute()
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError(f"Cache symlink is not allowed: {part}")
    if path.exists() and not path.is_dir():
        raise ValueError("Cache must be a directory")
    return path


class MetadataRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, newurl):
        parsed = urllib.parse.urlsplit(newurl)
        identity = re.search(r"/addons/([a-z]+)/addons\.xml\.gz$",
                             urllib.parse.urlsplit(request.full_url).path)
        if (parsed.scheme != "https" or parsed.username or parsed.password
                or identity is None
                or not parsed.path.endswith(f"/addons/{identity[1]}/addons.xml.gz")):
            raise ValueError(f"Refusing non-HTTPS/non-metadata redirect: {newurl}")
        return super().redirect_request(request, fp, code, message, headers, newurl)


def fetch(cache: Path, refresh: bool = False) -> dict:
    destination = safe_directory(cache)
    if (destination / "manifest.json").exists() and not refresh:
        raise ValueError("Cache already exists; use --refresh to replace its snapshot")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination = safe_directory(destination)
    opener = urllib.request.build_opener(MetadataRedirect())
    manifest: dict = {"schema_version": 1, "fetched_at": "", "indexes": {}}
    with tempfile.TemporaryDirectory(prefix="index-fetch-", dir=destination.parent) as temporary:
        stage = Path(temporary)
        for branch in BRANCHES:
            url = f"https://mirrors.kodi.tv/addons/{branch}/addons.xml.gz"
            request = urllib.request.Request(url, headers={"User-Agent": "kodi-agent-toolkit-index-fetch/0.1"})
            with opener.open(request, timeout=45) as response:
                final_url = response.geturl()
                final = urllib.parse.urlsplit(final_url)
                if final.scheme != "https" or not final.path.endswith(f"/addons/{branch}/addons.xml.gz"):
                    raise ValueError(f"Unexpected metadata response URL: {final_url}")
                raw = response.read(MAX_GZIP + 1)
            if len(raw) > MAX_GZIP:
                raise ValueError(f"Compressed index exceeds limit: {branch}")
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as zipped:
                xml = zipped.read(MAX_XML + 1)
            if (len(xml) > MAX_XML or b"<!DOCTYPE" in xml.replace(b"\x00", b"").upper()
                    or b"<!ENTITY" in xml.replace(b"\x00", b"").upper() or ET.fromstring(xml).tag != "addons"):
                raise ValueError(f"Unsafe/invalid metadata XML: {branch}")
            filename = f"{branch}.xml.gz"
            (stage / filename).write_bytes(raw)
            entry = {"url": url, "final_url": final_url, "filename": filename,
                     "sha256": hashlib.sha256(raw).hexdigest(), "size": len(raw),
                     "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat()}
            manifest["indexes"][branch] = entry
            print(f"{branch}: {len(raw)} bytes sha256={entry['sha256']}", flush=True)
        manifest["fetched_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
        (stage / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        destination.mkdir(exist_ok=True)
        for branch in BRANCHES:
            target = destination / f"{branch}.xml.gz"
            if target.is_symlink():
                raise ValueError(f"Existing cache file is a symlink: {target}")
            os.replace(stage / target.name, target)
        target = destination / "manifest.json"
        if target.is_symlink():
            raise ValueError("Existing manifest is a symlink")
        # Manifest last: concurrent readers fail closed on any intermediate hash mismatch.
        os.replace(stage / "manifest.json", target)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path,
                        default=Path(__file__).absolute().parents[1] / ".local" / "index-cache")
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    try:
        manifest = fetch(args.cache, args.refresh)
    except Exception as exc:
        parser.exit(1, f"Index acquisition failed; no usable new manifest published: {exc}\n")
    print(json.dumps({"cache": str(args.cache.absolute()), "fetched_at": manifest["fetched_at"],
                      "branches": list(manifest["indexes"])}, indent=2))
