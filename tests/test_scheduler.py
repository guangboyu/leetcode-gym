import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tracker.scheduler import INTERVALS, apply_action


class TestScheduler(unittest.TestCase):
    def test_first_solve(self):
        e = apply_action(None, "solved", "2026-06-09")
        self.assertEqual(e["status"], "solved")
        self.assertEqual(e["successes"], 1)
        self.assertEqual(e["due"], "2026-06-10")
        self.assertEqual(e["history"], [["2026-06-09", "solved"]])

    def test_ladder_progression(self):
        e, day = None, "2026-06-09"
        expected_gaps = INTERVALS  # 1, 2, 4, 7, 15, 30
        for i, gap in enumerate(expected_gaps):
            e = apply_action(e, "solved", day)
            self.assertEqual(e["successes"], i + 1)
            self.assertEqual(e["status"], "solved")
            day = e["due"]  # review exactly when due
        # one more success past the last rung -> mastered
        e = apply_action(e, "solved", day)
        self.assertEqual(e["status"], "mastered")
        self.assertIsNone(e["due"])

    def test_forgotten_resets_ladder(self):
        e = apply_action(None, "solved", "2026-06-09")
        e = apply_action(e, "solved", "2026-06-10")
        self.assertEqual(e["successes"], 2)
        e = apply_action(e, "forgotten", "2026-06-12")
        self.assertEqual(e["status"], "forgotten")
        self.assertEqual(e["successes"], 0)
        self.assertEqual(e["due"], "2026-06-12")  # due immediately
        e = apply_action(e, "solved", "2026-06-13")
        self.assertEqual(e["successes"], 1)  # ladder restarted
        self.assertEqual(e["due"], "2026-06-14")

    def test_history_accumulates(self):
        e = apply_action(None, "solved", "2026-06-09")
        e = apply_action(e, "forgotten", "2026-06-10")
        e = apply_action(e, "solved", "2026-06-11")
        self.assertEqual([a for _, a in e["history"]],
                         ["solved", "forgotten", "solved"])

    def test_solved_help_does_not_climb_ladder(self):
        e = apply_action(None, "solved_help", "2026-06-09")
        self.assertEqual((e["status"], e["successes"], e["due"]),
                         ("solved", 0, "2026-06-11"))
        e = apply_action(e, "solved", "2026-06-11")
        self.assertEqual((e["successes"], e["due"]), (1, "2026-06-12"))

    def test_solved_help_pauses_existing_ladder(self):
        e = apply_action(None, "solved", "2026-06-09")
        e = apply_action(e, "solved", "2026-06-10")        # successes 2
        e = apply_action(e, "solved_help", "2026-06-12")
        self.assertEqual((e["successes"], e["due"]), (2, "2026-06-14"))
        e = apply_action(e, "solved", "2026-06-14")        # resumes at 3
        self.assertEqual((e["successes"], e["due"]), (3, "2026-06-18"))

    def test_solved_help_after_forgotten_restarts(self):
        e = apply_action(None, "solved", "2026-06-09")
        e = apply_action(e, "forgotten", "2026-06-10")
        e = apply_action(e, "solved_help", "2026-06-11")
        self.assertEqual((e["status"], e["successes"], e["due"]),
                         ("solved", 0, "2026-06-13"))

    def test_reset_removes_entry(self):
        e = apply_action(None, "solved", "2026-06-09")
        self.assertIsNone(apply_action(e, "reset", "2026-06-10"))

    def test_unknown_action(self):
        with self.assertRaises(ValueError):
            apply_action(None, "skipped", "2026-06-09")


if __name__ == "__main__":
    unittest.main()
