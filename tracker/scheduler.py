"""Ebbinghaus review scheduling.

A problem's progress entry (one value in data/progress.json):

  {
    "status": "solved" | "forgotten" | "mastered",
    "successes": <consecutive successful reviews>,
    "last": "YYYY-MM-DD",
    "due": "YYYY-MM-DD" | null,        # null once mastered
    "history": [["YYYY-MM-DD", action], ...]
  }

Actions:
  solved    -> climb the interval ladder; past the last rung the problem is mastered
  forgotten -> due immediately, the ladder restarts on the next solve
  reset     -> back to untouched (entry removed)
"""
from datetime import date, timedelta

INTERVALS = [1, 2, 4, 7, 15, 30]  # days until next review, per consecutive success
ACTIONS = ("solved", "forgotten", "reset")


def apply_action(entry, action, today=None):
    """Return the updated entry, or None when the problem becomes untouched."""
    if action not in ACTIONS:
        raise ValueError(f"unknown action: {action}")
    if action == "reset":
        return None

    today = today or date.today().isoformat()
    history = (entry or {}).get("history", []) + [[today, action]]

    if action == "forgotten":
        return {"status": "forgotten", "successes": 0, "last": today,
                "due": today, "history": history}

    successes = 1 if entry is None or entry["status"] == "forgotten" \
        else entry["successes"] + 1
    if successes > len(INTERVALS):
        return {"status": "mastered", "successes": successes, "last": today,
                "due": None, "history": history}
    due = date.fromisoformat(today) + timedelta(days=INTERVALS[successes - 1])
    return {"status": "solved", "successes": successes, "last": today,
            "due": due.isoformat(), "history": history}
