"""End-to-end test of the HTTP layer the desktop app relies on.

Exercises the exact runtime path a packaged build uses — configure() with a
throwaway data dir, make_server(port=0), a real request/response round-trip —
without opening a GUI window.
"""
import json
import os
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tracker import config, server


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
        self._cfg = tempfile.TemporaryDirectory()
        os.environ["LEETCODE_TRACKER_CONFIG_DIR"] = self._cfg.name  # keep tests off real config
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
        self._cfg.cleanup()
        os.environ.pop("LEETCODE_TRACKER_CONFIG_DIR", None)

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

    def test_get_data_dir_reports_current(self):
        status, body = _get(self.base, "/api/data-dir")
        self.assertEqual(status, 200)
        self.assertEqual(Path(body["path"]), Path(self._dir.name))

    def test_switch_data_dir_merges_and_persists(self):
        here, there = list(server.SLUGS)[:2]
        _post(self.base, "/api/review", {"slug": here, "action": "solved"})

        # A second folder that already holds different history (e.g. from another machine).
        with tempfile.TemporaryDirectory() as other:
            (Path(other) / "reviews.jsonl").write_text(
                json.dumps({"date": "2026-06-01", "slug": there, "action": "solved"}) + "\n",
                encoding="utf-8")

            status, body = _post(self.base, "/api/data-dir", {"path": other})
            self.assertEqual(status, 200)
            self.assertEqual(Path(body["path"]), Path(other))
            # Both histories survive the switch (lossless union)...
            self.assertIn(here, body["progress"])
            self.assertIn(there, body["progress"])
            merged = (Path(other) / "reviews.jsonl").read_text(encoding="utf-8")
            self.assertIn(here, merged)
            self.assertIn(there, merged)
            # ...and the choice is remembered.
            self.assertEqual(Path(config.get_data_dir()), Path(other))

    def test_switch_to_empty_dir_keeps_progress(self):
        here = next(iter(server.SLUGS))
        _post(self.base, "/api/review", {"slug": here, "action": "solved"})
        with tempfile.TemporaryDirectory() as empty:
            status, body = _post(self.base, "/api/data-dir", {"path": empty})
            self.assertEqual(status, 200)
            self.assertIn(here, body["progress"])  # not lost when moving to a fresh folder
            self.assertTrue((Path(empty) / "reviews.jsonl").exists())

    def test_unknown_slug_rejected(self):
        with self.assertRaises(urllib.error.HTTPError) as cm:
            _post(self.base, "/api/review",
                  {"slug": "definitely-not-a-real-slug", "action": "solved"})
        self.assertEqual(cm.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
