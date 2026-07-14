"""End-to-end test of the HTTP layer the desktop app relies on.

Exercises the exact runtime path a packaged build uses — configure() with a
throwaway data dir, make_server(port=0), a real request/response round-trip —
without opening a GUI window.
"""
import json
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tracker import server


def _get(base, path):
    with urllib.request.urlopen(base + path) as r:
        return r.status, json.loads(r.read())


def _post(base, path, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(base + path, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return r.status, json.loads(r.read())


class TestServer(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        server.configure(data_dir=self._dir.name)
        self.httpd = server.make_server(port=0)  # OS-assigned free port
        self.base = f"http://127.0.0.1:{self.httpd.server_address[1]}"
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=5)
        self._dir.cleanup()

    def test_serves_problems_json(self):
        status, body = _get(self.base, "/data/problems.json")
        self.assertEqual(status, 200)
        self.assertIn("problems", body)
        self.assertGreater(len(body["problems"]), 0)

    def test_review_roundtrip_persists(self):
        slug = next(iter(server.SLUGS))  # any real slug from the dataset
        status, body = _post(self.base, "/api/review",
                             {"slug": slug, "action": "solved"})
        self.assertEqual(status, 200)
        self.assertEqual(body["entry"]["status"], "solved")

        # Progress endpoint reflects it, and it was written to the event log.
        status, progress = _get(self.base, "/api/progress")
        self.assertEqual(status, 200)
        self.assertIn(slug, progress)
        log = Path(self._dir.name) / "reviews.jsonl"
        self.assertTrue(log.exists())
        self.assertIn(slug, log.read_text(encoding="utf-8"))

    def test_unknown_slug_rejected(self):
        with self.assertRaises(urllib.error.HTTPError) as cm:
            _post(self.base, "/api/review",
                  {"slug": "definitely-not-a-real-slug", "action": "solved"})
        self.assertEqual(cm.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
