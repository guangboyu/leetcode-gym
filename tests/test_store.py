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
            for i, e in enumerate(EVENTS):
                out = store.append_event(e["slug"], e["action"], e["date"],
                                         log_file=log, ts=f"{e['date']}T10:00:0{i}")
                self.assertEqual(out["ts"], f"{e['date']}T10:00:0{i}")
            loaded = store.load_events(log_file=log)
            self.assertEqual([{k: v for k, v in e.items() if k != "ts"} for e in loaded],
                             EVENTS)
            self.assertTrue(all("ts" in e for e in loaded))
            self.assertEqual(store.load_progress(log_file=log,
                                                 snapshot_file=Path(d) / "none.json"),
                             store.replay(EVENTS))
            # default ts is "now" to the second, ISO 8601
            store.append_event("x", "solved", "2026-06-09", log_file=log)
            self.assertRegex(store.load_events(log_file=log)[-1]["ts"],
                             r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d$")

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

    def test_merge_events_unions_dedupes_and_orders(self):
        a = [{"date": "2026-06-01", "slug": "x", "action": "solved"},
             {"date": "2026-06-03", "slug": "y", "action": "solved"}]
        b = [{"date": "2026-06-01", "slug": "x", "action": "solved"},   # duplicate
             {"date": "2026-06-02", "slug": "z", "action": "solved"}]
        merged = store.merge_events(a, b)
        self.assertEqual(len(merged), 3)                                # x deduped
        self.assertEqual([e["slug"] for e in merged], ["x", "z", "y"])  # by date

    def test_merge_keeps_same_day_repeats_with_ts_and_dedupes_legacy(self):
        # A deliberate same-day repeat (solved / undo / solved) has distinct ts
        # values and must survive; legacy ts-less duplicates still collapse.
        a = [{"date": "2026-06-01", "slug": "x", "action": "solved", "ts": "2026-06-01T09:00:00"},
             {"date": "2026-06-01", "slug": "x", "action": "undo", "ts": "2026-06-01T09:00:05"},
             {"date": "2026-06-01", "slug": "x", "action": "solved", "ts": "2026-06-01T09:00:09"},
             {"date": "2026-05-30", "slug": "y", "action": "solved"}]
        b = [{"date": "2026-05-30", "slug": "y", "action": "solved"},               # legacy dup
             {"date": "2026-06-01", "slug": "x", "action": "solved", "ts": "2026-06-01T09:00:09"}]
        merged = store.merge_events(a, b)
        self.assertEqual(len(merged), 4)
        self.assertEqual([e["slug"] for e in merged], ["y", "x", "x", "x"])
        self.assertEqual([e.get("ts") for e in merged][1:],
                         ["2026-06-01T09:00:00", "2026-06-01T09:00:05", "2026-06-01T09:00:09"])

    def test_effective_events_resolves_undo(self):
        ev = [{"date": "2026-06-01", "slug": "a", "action": "solved"},
              {"date": "2026-06-01", "slug": "b", "action": "solved"},
              {"date": "2026-06-02", "slug": "a", "action": "solved"},
              {"date": "2026-06-02", "slug": "a", "action": "undo"},      # cancels a's 2nd solve
              {"date": "2026-06-03", "slug": "c", "action": "undo"},      # nothing to undo: no-op
              {"date": "2026-06-04", "slug": "b", "action": "reset"},
              {"date": "2026-06-04", "slug": "b", "action": "undo"}]      # undo of a reset restores
        eff = store.effective_events(ev)
        self.assertEqual([(e["slug"], e["action"], e["date"]) for e in eff],
                         [("a", "solved", "2026-06-01"), ("b", "solved", "2026-06-01")])
        progress = store.replay(ev)
        self.assertEqual(progress["a"]["successes"], 1)
        self.assertEqual(progress["b"]["status"], "solved")
        # double undo pops two events; then there is nothing left for that slug
        ev2 = ev[:3] + [{"date": "2026-06-05", "slug": "a", "action": "undo"}] * 3
        self.assertNotIn("a", store.replay(ev2))

    def test_replay_equals_manual_after_undo(self):
        ev = [{"date": "2026-06-01", "slug": "a", "action": "solved"},
              {"date": "2026-06-02", "slug": "a", "action": "forgotten"},
              {"date": "2026-06-02", "slug": "a", "action": "undo"}]
        self.assertEqual(store.replay(ev)["a"], apply_action(None, "solved", "2026-06-01"))

    def test_activity_counts_effective_actions_per_day(self):
        ev = [{"date": "2026-06-01", "slug": "a", "action": "solved"},
              {"date": "2026-06-01", "slug": "b", "action": "solved_help"},
              {"date": "2026-06-01", "slug": "c", "action": "solved"},
              {"date": "2026-06-01", "slug": "c", "action": "undo"},       # not counted
              {"date": "2026-06-02", "slug": "a", "action": "forgotten"},
              {"date": "2026-06-02", "slug": "b", "action": "reset"}]      # bookkeeping, not counted
        self.assertEqual(store.activity(ev),
                         {"2026-06-01": {"solved": 1, "solved_help": 1},
                          "2026-06-02": {"forgotten": 1}})

    def test_settings_defaults_overlay_and_drop_unknown(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "settings.json"
            self.assertEqual(store.load_settings(settings_file=f), store.DEFAULT_SETTINGS)
            f.write_text(json.dumps({"cap": 2000, "bogus": 1, "theme": "dark"}))
            s = store.load_settings(settings_file=f)
            self.assertEqual(s["cap"], 2000)
            self.assertEqual(s["theme"], "dark")
            self.assertNotIn("bogus", s)
            self.assertEqual(s["drillPools"], store.DEFAULT_SETTINGS["drillPools"])
            f.write_text("{not json")
            self.assertEqual(store.load_settings(settings_file=f), store.DEFAULT_SETTINGS)
            store.save_settings(s, settings_file=f)
            self.assertEqual(store.load_settings(settings_file=f), s)
            self.assertFalse(f.with_suffix(".json.tmp").exists())

    def test_load_settings_returns_a_fresh_copy(self):
        with tempfile.TemporaryDirectory() as d:
            s = store.load_settings(settings_file=Path(d) / "none.json")
            s["drillPools"].append("x")
            self.assertNotIn("x", store.DEFAULT_SETTINGS["drillPools"])

    def test_write_events_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / "reviews.jsonl"
            store.write_events(EVENTS, log_file=log)
            self.assertEqual(store.load_events(log_file=log), EVENTS)

    def test_snapshot_is_sorted_and_stable(self):
        with tempfile.TemporaryDirectory() as d:
            snap = Path(d) / "progress.json"
            store.save_snapshot({"zzz": {"a": 1}, "aaa": {"b": 2}}, snapshot_file=snap)
            self.assertEqual(list(json.loads(snap.read_text()).keys()), ["aaa", "zzz"])


if __name__ == "__main__":
    unittest.main()
