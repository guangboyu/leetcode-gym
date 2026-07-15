"""Progress storage.

Source of truth: data/reviews.jsonl — an append-only event log, one JSON object
per line: {"date": "YYYY-MM-DD", "slug": ..., "action": ...}. Appends cannot
corrupt existing data, and two diverged machines can merge by unioning lines.

data/progress.json is a derived snapshot (slug -> entry), rebuilt by replaying
the log through scheduler.apply_action. It exists for human inspection and is
regenerated after every action; deleting it loses nothing.

Migration: if the log is missing but a snapshot exists (pre-event-log format),
the log is reconstructed from the per-entry histories.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tracker.scheduler import apply_action

ROOT = Path(__file__).resolve().parent.parent
LOG_FILE = ROOT / "data" / "reviews.jsonl"
SNAPSHOT_FILE = ROOT / "data" / "progress.json"


def set_data_dir(data_dir):
    """Point the event log and snapshot at an arbitrary directory (e.g. a
    separate private repo used for backup). Call once at startup."""
    global LOG_FILE, SNAPSHOT_FILE
    data_dir = Path(data_dir).expanduser()
    data_dir.mkdir(parents=True, exist_ok=True)
    LOG_FILE = data_dir / "reviews.jsonl"
    SNAPSHOT_FILE = data_dir / "progress.json"


def replay(events):
    progress = {}
    for e in events:
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


def append_event(slug, action, day, log_file=None):
    log_file = log_file or LOG_FILE
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"date": day, "slug": slug, "action": action},
                           ensure_ascii=False) + "\n")


def merge_events(*event_lists):
    """Union events from several logs, de-duplicated, ordered by date. Because
    the log is append-only, unioning unique lines is a lossless merge — this is
    what lets two diverged machines (or a switch to a cloud-synced folder that
    already has history) reconcile without dropping any progress. The sort is
    stable, so events sharing a date keep their original relative order."""
    seen, merged = set(), []
    for events in event_lists:
        for e in events:
            key = (e["date"], e["slug"], e["action"])
            if key not in seen:
                seen.add(key)
                merged.append(e)
    merged.sort(key=lambda e: e["date"])
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
