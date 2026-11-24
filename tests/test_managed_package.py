"""A local HTTP fixture checks exact-byte admission and bounded failures."""
import base64
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import tempfile
import threading
import unittest

from kodi_agent_toolkit.managed_package import admit_package


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        root = tempfile.TemporaryDirectory()
        self.addCleanup(root.cleanup)
        self.package = Path(root.name) / "fixture.zip"
        self.raw = bytes(range(256)) * 5
        self.package.write_bytes(self.raw)
        self.token = Path(root.name) / "token"
        self.token.write_text("fixture_only\n")
        self.requests = []
        self.refuse = False
        self.wrong_digest = False
        self.redirect = False
        case = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                return

            def do_POST(self):
                req = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                case.requests.append((self.path, self.headers["Authorization"], req))
                if case.redirect:
                    self.send_response(302)
                    self.send_header("Location", self.path)
                    self.end_headers()
                    return
                digest = req["params"]["arguments"]["digest"]
                text = ("permission_denied" if case.refuse else json.dumps({"result": {
                    "addon": "script.fixture", "version": "1.0.0",
                    "digest": "0" * 64 if case.wrong_digest else digest,
                }}))
                data = json.dumps({"jsonrpc": "2.0", "id": req["id"], "result": {
                    "content": [{"type": "text", "text": text}], "isError": case.refuse,
                }}).encode()
                self.send_response(200)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        worker = threading.Thread(target=self.server.serve_forever, daemon=True)
        worker.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.endpoint = f"http://127.0.0.1:{self.server.server_port}/mcp"

    def admit(self):
        return admit_package(self.package, self.endpoint, self.token)

    def test_one_tool_call_uses_exact_zip_and_digest(self):
        result = self.admit()
        self.assertEqual(len(self.requests), 1)
        path, auth, rpc = self.requests[0]
        self.assertEqual(path, "/mcp")
        self.assertEqual(auth, "Bearer fixture_only")
        self.assertEqual(rpc["method"], "tools/call")
        self.assertEqual(rpc["params"]["name"], "managed_package_import")
        self.assertEqual(base64.b64decode(rpc["params"]["arguments"]["encoded"]), self.raw)
        digest = hashlib.sha256(self.raw).hexdigest()
        self.assertEqual(result, {"addon": "script.fixture", "version": "1.0.0", "digest": digest})

    def test_oversized_and_insecure_destinations_are_rejected_locally(self):
        self.package.write_bytes(b"x" * (48 * 1024))
        with self.assertRaisesRegex(ValueError, "request limit"):
            self.admit()
        with self.assertRaisesRegex(ValueError, "authorized"):
            admit_package(self.package, "http://example.invalid/mcp", self.token)
        self.assertEqual(self.requests, [])

    def test_rejected_grant_is_reported_without_retry(self):
        self.refuse = True
        with self.assertRaisesRegex(ValueError, "permission_denied"):
            self.admit()
        self.assertEqual(len(self.requests), 1)

    def test_mismatched_response_digest_is_never_admission_success(self):
        self.wrong_digest = True
        with self.assertRaisesRegex(ValueError, "Unexpected"):
            self.admit()
        self.assertEqual(len(self.requests), 1)

    def test_redirect_does_not_replay_the_credential_or_payload(self):
        self.redirect = True
        with self.assertRaisesRegex(ValueError, "HTTP 302"):
            self.admit()
        self.assertEqual(len(self.requests), 1)
