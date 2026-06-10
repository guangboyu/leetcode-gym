import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tracker import store
from tracker.scheduler import apply_action

EVENTS = [
    {"date": "2026-06-01", "slug": "two-sum", "action": "solved"},
    {"date": "2026-06-02", "slug": "two-sum", "action": "solved"},
    {"date": "2026-06-01", "slug": "binary-search", "action": "solved"},
    {"date": "2026-06-04", "slug": "two-sum", "action": "forgotten"},
    {"date": "2026-06-05", "slug": "binary-search", "action": "reset"},
]


class TestStore(unittest.TestCase):
    def test_replay_matches_direct_application(self):
        progress = store.replay(EVENTS)
        manual = None
        for e in EVENTS:
            if e["slug"] == "two-sum":
                manual = apply_action(manual, e["action"], e["date"])
        self.assertEqual(progress["two-sum"], manual)
        self.assertNotIn("binary-search", progress)  # reset removed it

    def test_append_then_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / "reviews.jsonl"
            for e in EVENTS:
                store.append_event(e["slug"], e["action"], e["date"], log_file=log)
            self.assertEqual(store.load_events(log_file=log), EVENTS)
            self.assertEqual(store.load_progress(log_file=log,
                                                 snapshot_file=Path(d) / "none.json"),
                             store.replay(EVENTS))

    def test_migration_from_old_snapshot(self):
        # Build an old-format snapshot (no log), then load: the log must be
        # reconstructed and replay to entries identical to the snapshot.
        old = store.replay([e for e in EVENTS if e["action"] != "reset"
                            or e["slug"] != "binary-search"][:4])
        with tempfile.TemporaryDirectory() as d:
            snap, log = Path(d) / "progress.json", Path(d) / "reviews.jsonl"
            snap.write_text(json.dumps(old), encoding="utf-8")
            progress = store.load_progress(log_file=log, snapshot_file=snap)
            self.assertTrue(log.exists())
            self.assertEqual(progress, old)
            # replaying the new log again is stable
            self.assertEqual(store.replay(store.load_events(log_file=log)), old)

    def test_snapshot_is_sorted_and_stable(self):
        with tempfile.TemporaryDirectory() as d:
            snap = Path(d) / "progress.json"
            store.save_snapshot({"zzz": {"a": 1}, "aaa": {"b": 2}}, snapshot_file=snap)
            self.assertEqual(list(json.loads(snap.read_text()).keys()), ["aaa", "zzz"])


if __name__ == "__main__":
    unittest.main()
