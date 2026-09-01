"""Progress storage.

Source of truth: data/reviews.jsonl — an append-only event log, one JSON object
per line: {"date": "YYYY-MM-DD", "slug": ..., "action": ..., "ts": ...}.
Appends cannot corrupt existing data, and two diverged machines can merge by
unioning lines. `ts` (local time, ISO seconds) was added in 0.2 so that a
same-day repeat such as solved / undo / solved survives de-duplication; events
without it (pre-0.2 logs) still merge exactly as before.

Undo: an "undo" event cancels that slug's most recent still-effective event.
It is just another appended line, so it merges losslessly like everything
else, and replay stays a pure function of the ordered log. There is no
inverse for a "solved" in the scheduler (the ladder only climbs), which is
why undo is an event rather than a compensating action.

data/progress.json is a derived snapshot (slug -> entry), rebuilt by replaying
the log through scheduler.apply_action. It exists for human inspection and is
regenerated after every action; deleting it loses nothing.

data/settings.json holds UI preferences (rating cap, skipped subtopics, drill
defaults, theme...). It lives beside the log so preferences travel with the
progress when the folder is synced between machines. Small, last-writer-wins.

Migration: if the log is missing but a snapshot exists (pre-event-log format),
the log is reconstructed from the per-entry histories.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tracker.scheduler import apply_action

ROOT = Path(__file__).resolve().parent.parent
LOG_FILE = ROOT / "data" / "reviews.jsonl"
SNAPSHOT_FILE = ROOT / "data" / "progress.json"
SETTINGS_FILE = ROOT / "data" / "settings.json"

UNDO = "undo"

# UI preferences with their defaults. Unknown keys are dropped on load so a
# newer app never chokes on (or an older one never resurrects) stale keys.
DEFAULT_SETTINGS = {
    "cap": 1700,                 # rating cap for the 0x3F extension lists; None = no cap
    "routeShowOptional": False,  # show 0x3F "(optional)" / niche subtopics
    "routeSkipped": [],          # "<pattern>/<subtopic>" keys the user skipped
    "drillPools": ["hot100", "interview150", "neetcode250", "ox3f"],
    "drillTopics": None,         # None = every type
    "drillLo": None,             # rating range; None = pick a default in the UI
    "drillHi": None,
    "lastView": "today",
    "lastPattern": None,
    "lastSection": None,
    "theme": "system",           # system | light | dark
}


def set_data_dir(data_dir):
    """Point the event log, snapshot and settings at an arbitrary directory
    (e.g. a separate private repo used for backup). Call once at startup."""
    global LOG_FILE, SNAPSHOT_FILE, SETTINGS_FILE
    data_dir = Path(data_dir).expanduser()
    data_dir.mkdir(parents=True, exist_ok=True)
    LOG_FILE = data_dir / "reviews.jsonl"
    SNAPSHOT_FILE = data_dir / "progress.json"
    SETTINGS_FILE = data_dir / "settings.json"


def effective_events(events):
    """Resolve undo events: each "undo" removes that slug's most recent event
    that is still in effect (nothing to remove -> the undo is a no-op). Returns
    the surviving non-undo events in their original order."""
    kept = []                 # (event, alive flag) in log order
    stack = {}                # slug -> indices into `kept` still alive
    for e in events:
        slug = e["slug"]
        if e["action"] == UNDO:
            alive = stack.get(slug)
            if alive:
                kept[alive.pop()][1] = False
            continue
        stack.setdefault(slug, []).append(len(kept))
        kept.append([e, True])
    return [e for e, alive in kept if alive]


def activity(events):
    """Per-day counts of effective review actions, {date: {action: n}}.
    "reset" is bookkeeping rather than studying, so it is not counted."""
    days = {}
    for e in effective_events(events):
        if e["action"] == "reset":
            continue
        day = days.setdefault(e["date"], {})
        day[e["action"]] = day.get(e["action"], 0) + 1
    return days


def replay(events):
    progress = {}
    for e in effective_events(events):
        entry = apply_action(progress.get(e["slug"]), e["action"], e["date"])
        if entry is None:
            progress.pop(e["slug"], None)
        else:
            progress[e["slug"]] = entry
    return progress


def load_events(log_file=None):
    log_file = log_file or LOG_FILE
    if not log_file.exists():
        return []
    return [json.loads(line) for line in
            log_file.read_text(encoding="utf-8").splitlines() if line.strip()]


def migrate_snapshot_to_log(snapshot_file=None, log_file=None):
    """Rebuild the event log from a pre-event-log progress.json (histories)."""
    snapshot_file = snapshot_file or SNAPSHOT_FILE
    log_file = log_file or LOG_FILE
    snap = json.loads(snapshot_file.read_text(encoding="utf-8"))
    events = []
    for slug, entry in snap.items():
        for seq, (day, action) in enumerate(entry.get("history", [])):
            events.append((day, slug, seq, action))
    events.sort()
    events = [{"date": d, "slug": s, "action": a} for d, s, _, a in events]
    log_file.write_text(
        "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in events),
        encoding="utf-8")
    return events


def load_progress(log_file=None, snapshot_file=None):
    log_file = log_file or LOG_FILE
    snapshot_file = snapshot_file or SNAPSHOT_FILE
    if log_file.exists():
        return replay(load_events(log_file))
    if snapshot_file.exists():
        return replay(migrate_snapshot_to_log(snapshot_file, log_file))
    return {}


def now_ts():
    """Local wall-clock time to the second, ISO 8601 (no timezone: it only has
    to order same-day events on the machine that wrote them)."""
    return datetime.now().isoformat(timespec="seconds")


def append_event(slug, action, day, log_file=None, ts=None):
    log_file = log_file or LOG_FILE
    event = {"date": day, "slug": slug, "action": action, "ts": ts or now_ts()}
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    return event


def merge_events(*event_lists):
    """Union events from several logs, de-duplicated, ordered by date. Because
    the log is append-only, unioning unique lines is a lossless merge — this is
    what lets two diverged machines (or a switch to a cloud-synced folder that
    already has history) reconcile without dropping any progress. Events carry
    `ts` (0.2+) in the key so a deliberate same-day repeat is kept; legacy
    events without it de-duplicate on (date, slug, action) as before. The sort
    is stable, so events sharing a date (and ts) keep their original relative
    order."""
    seen, merged = set(), []
    for events in event_lists:
        for e in events:
            key = (e["date"], e["slug"], e["action"], e.get("ts", ""))
            if key not in seen:
                seen.add(key)
                merged.append(e)
    merged.sort(key=lambda e: (e["date"], e.get("ts", "")))
    return merged


def write_events(events, log_file=None):
    """Atomically overwrite the whole log with `events` (used after a merge)."""
    log_file = log_file or LOG_FILE
    log_file.parent.mkdir(parents=True, exist_ok=True)
    tmp = log_file.with_suffix(".jsonl.tmp")
    tmp.write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in events),
                   encoding="utf-8")
    os.replace(tmp, log_file)


def save_snapshot(progress, snapshot_file=None):
    snapshot_file = snapshot_file or SNAPSHOT_FILE
    tmp = snapshot_file.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(dict(sorted(progress.items())),
                              ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    os.replace(tmp, snapshot_file)


def load_settings(settings_file=None):
    """Defaults overlaid with whatever the file holds; unknown keys dropped,
    a missing or corrupt file just means defaults."""
    settings_file = settings_file or SETTINGS_FILE
    out = json.loads(json.dumps(DEFAULT_SETTINGS))  # deep copy of the lists
    try:
        saved = json.loads(settings_file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return out
    if isinstance(saved, dict):
        for k, v in saved.items():
            if k in DEFAULT_SETTINGS:
                out[k] = v
    return out


def save_settings(settings, settings_file=None):
    """Atomically write the settings file (tmp + rename, like the snapshot)."""
    settings_file = settings_file or SETTINGS_FILE
    settings_file.parent.mkdir(parents=True, exist_ok=True)
    tmp = settings_file.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(settings, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    os.replace(tmp, settings_file)
