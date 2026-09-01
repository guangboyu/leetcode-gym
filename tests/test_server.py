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

    # --- 0.2: caching, settings, undo, activity, about -------------------

    def _raw(self, path, method="GET", headers=None, data=None):
        req = urllib.request.Request(self.base + path, method=method, data=data,
                                     headers=headers or {})
        try:  # headers: an HTTPMessage, so lookups are case-insensitive
            with urllib.request.urlopen(req) as r:
                return r.status, r.headers, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.headers, e.read()

    def test_problems_json_has_etag_and_304(self):
        status, headers, body = self._raw("/data/problems.json")
        self.assertEqual(status, 200)
        etag = headers["ETag"]
        self.assertTrue(etag.startswith('"'))
        self.assertEqual(headers["Cache-Control"], "no-cache")
        self.assertNotIn("Content-Encoding", headers)
        self.assertEqual(json.loads(body)["problems"].keys(), server.SLUGS)
        status, headers, body = self._raw("/data/problems.json",
                                          headers={"If-None-Match": etag})
        self.assertEqual(status, 304)
        self.assertEqual(body, b"")
        status, headers, body = self._raw("/data/problems.json", method="HEAD")
        self.assertEqual((status, body), (200, b""))
        self.assertEqual(headers["ETag"], etag)

    def test_problems_json_gzip(self):
        import gzip
        status, headers, body = self._raw("/data/problems.json",
                                          headers={"Accept-Encoding": "gzip, deflate"})
        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Encoding"], "gzip")
        self.assertEqual(headers["Vary"], "Accept-Encoding")
        self.assertLess(len(body), len(server._PROBLEMS_RAW) // 3)
        self.assertEqual(gzip.decompress(body), server._PROBLEMS_RAW)

    def test_static_js_mime_and_cache_control(self):
        status, headers, _ = self._raw("/app.js")
        self.assertEqual(status, 200)
        self.assertTrue(headers["Content-Type"].startswith("text/javascript"))
        self.assertEqual(headers["Cache-Control"], "no-cache")

    def test_unknown_api_and_data_paths_404_json(self):
        for path in ("/api/nope", "/data/secret.json"):
            status, headers, body = self._raw(path)
            self.assertEqual(status, 404)
            self.assertEqual(json.loads(body), {"error": "not found"})

    def test_settings_defaults_patch_validation_reset(self):
        from tracker import store
        status, body = _get(self.base, "/api/settings")
        self.assertEqual(status, 200)
        self.assertEqual(body, store.DEFAULT_SETTINGS)

        status, body = _post(self.base, "/api/settings", {"cap": 2000, "theme": "dark",
                                                          "routeSkipped": ["a/b"]})
        self.assertEqual(status, 200)
        self.assertEqual((body["cap"], body["theme"], body["routeSkipped"]),
                         (2000, "dark", ["a/b"]))
        self.assertEqual(body["drillPools"], store.DEFAULT_SETTINGS["drillPools"])  # untouched
        # persisted beside the log, and survives a fresh load
        saved = json.loads((Path(self._dir.name) / "settings.json").read_text())
        self.assertEqual(saved["cap"], 2000)
        status, body = _get(self.base, "/api/settings")
        self.assertEqual(body["cap"], 2000)
        # null is allowed where documented
        status, body = _post(self.base, "/api/settings", {"cap": None, "drillTopics": None})
        self.assertEqual((body["cap"], body["drillTopics"]), (None, None))

        for bad in ({"cap": "1700"}, {"cap": True}, {"theme": "blue"},
                    {"routeSkipped": "a"}, {"routeSkipped": [1]}, {"nope": 1},
                    {"routeShowOptional": 1}):
            with self.assertRaises(urllib.error.HTTPError, msg=bad) as cm:
                _post(self.base, "/api/settings", bad)
            self.assertEqual(cm.exception.code, 400)
        status, body = _get(self.base, "/api/settings")
        self.assertEqual(body["cap"], None)  # nothing bad got in

        status, body = _post(self.base, "/api/settings", {"reset": True})
        self.assertEqual(body, store.DEFAULT_SETTINGS)
        self.assertEqual(json.loads((Path(self._dir.name) / "settings.json").read_text()),
                         store.DEFAULT_SETTINGS)

    def test_settings_follow_data_dir_switch(self):
        _post(self.base, "/api/settings", {"cap": 1500})
        with tempfile.TemporaryDirectory() as empty:
            _post(self.base, "/api/data-dir", {"path": empty})
            # seeded into the fresh folder
            self.assertEqual(json.loads((Path(empty) / "settings.json").read_text())["cap"], 1500)
            self.assertEqual(_get(self.base, "/api/settings")[1]["cap"], 1500)
            with tempfile.TemporaryDirectory() as synced:
                (Path(synced) / "settings.json").write_text(json.dumps({"cap": 2400}))
                _post(self.base, "/api/data-dir", {"path": synced})
                # adopted from the synced folder (last writer wins, no merge)
                self.assertEqual(_get(self.base, "/api/settings")[1]["cap"], 2400)

    def test_undo_roundtrip(self):
        slug = next(iter(server.SLUGS))
        with self.assertRaises(urllib.error.HTTPError) as cm:
            _post(self.base, "/api/review", {"slug": slug, "action": "undo"})
        self.assertEqual(cm.exception.code, 400)
        self.assertEqual(json.loads(cm.exception.read())["error"], "nothing to undo")

        status, body = _post(self.base, "/api/review", {"slug": slug, "action": "solved"})
        self.assertTrue(body["undoable"])
        _post(self.base, "/api/review", {"slug": slug, "action": "solved"})
        self.assertEqual(_get(self.base, "/api/progress")[1][slug]["successes"], 2)

        status, body = _post(self.base, "/api/review", {"slug": slug, "action": "undo"})
        self.assertEqual(status, 200)
        self.assertEqual(body["entry"]["successes"], 1)
        self.assertTrue(body["undoable"])
        status, body = _post(self.base, "/api/review", {"slug": slug, "action": "undo"})
        self.assertIsNone(body["entry"])
        self.assertFalse(body["undoable"])
        self.assertNotIn(slug, _get(self.base, "/api/progress")[1])
        # the log is append-only: 2 solves + 2 undos, all with a ts
        lines = [json.loads(l) for l in
                 (Path(self._dir.name) / "reviews.jsonl").read_text().splitlines()]
        self.assertEqual([e["action"] for e in lines], ["solved", "solved", "undo", "undo"])
        self.assertTrue(all(e["ts"] for e in lines))
        # snapshot matches the replayed state
        self.assertEqual(json.loads((Path(self._dir.name) / "progress.json").read_text()), {})

        # undo of a reset restores the entry
        _post(self.base, "/api/review", {"slug": slug, "action": "solved"})
        _post(self.base, "/api/review", {"slug": slug, "action": "reset"})
        self.assertNotIn(slug, _get(self.base, "/api/progress")[1])
        status, body = _post(self.base, "/api/review", {"slug": slug, "action": "undo"})
        self.assertEqual(body["entry"]["status"], "solved")

    def test_activity_reflects_reviews_and_undo(self):
        from datetime import date
        a, b = list(server.SLUGS)[:2]
        status, body = _get(self.base, "/api/activity")
        self.assertEqual(body, {"days": {}, "first": None})
        _post(self.base, "/api/review", {"slug": a, "action": "solved"})
        _post(self.base, "/api/review", {"slug": b, "action": "solved_help"})
        today = date.today().isoformat()
        status, body = _get(self.base, "/api/activity")
        self.assertEqual(body["first"], today)
        self.assertEqual(body["days"][today], {"solved": 1, "solved_help": 1})
        _post(self.base, "/api/review", {"slug": b, "action": "undo"})
        self.assertEqual(_get(self.base, "/api/activity")[1]["days"][today], {"solved": 1})

    def test_about(self):
        from tracker import __version__, config
        status, body = _get(self.base, "/api/about")
        self.assertEqual(status, 200)
        self.assertEqual(body["name"], "LeetCode Gym")
        self.assertEqual(body["version"], __version__)
        self.assertEqual(Path(body["dataDir"]), Path(self._dir.name))
        self.assertEqual(Path(body["configFile"]), config.config_file())
        self.assertEqual(body["problems"], len(server.SLUGS))
        self.assertFalse(body["desktop"])
        self.assertIn("problemsSnapshot", body)
        self.assertRegex(body["python"], r"^\d+\.\d+")

    def test_unknown_slug_rejected(self):
        with self.assertRaises(urllib.error.HTTPError) as cm:
            _post(self.base, "/api/review",
                  {"slug": "definitely-not-a-real-slug", "action": "solved"})
        self.assertEqual(cm.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
