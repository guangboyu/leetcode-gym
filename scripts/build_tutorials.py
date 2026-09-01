#!/usr/bin/env python3
"""Parse the hand-written pattern tutorials (tutorials/*.md) into data/tutorials.json.

The tutorial IS the source of truth for its pattern: its "Shape" sections are the
pattern's subtopics and its problem tables are the problem lists the app shows.
This script extracts that structure (stdlib only) and validates it hard, so a
typo in a table or a broken anchor fails the build instead of the app.

Heading grammar (matched on heading TEXT, not level):

    # Title [(draft)]                     first H1; "(draft)" marks a partial tutorial
    ## Shape N: name                      opens subtopic "shape-N" (closes the previous)
    ### Na. name                          opens child "shape-Na" under the open shape
    ### / #### Title (LC 123)             a worked example inside the open (sub)shape
    ### / #### <label> problems           the next LC table belongs to the innermost open (sub)shape
    ## anything else                      closes the open shape

Problem tables: `| LC | Title | Diff | [State] | Freq | Note |` (State/Note optional).
Freq is 1-3 fire emoji. Diff is Easy / Med / Hard (a mismatch with the catalog only warns).

Anchors follow GitHub's rule (see `slugify`); tracker/static mirrors it, so the
client never re-slugs headings.

Usage:
    python3 scripts/build_tutorials.py            # write data/tutorials.json
    python3 scripts/build_tutorials.py --check    # exit 1 if the committed file is stale
    python3 scripts/build_tutorials.py --readme-table   # refresh the status table in tutorials/README.md
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TUTORIALS = ROOT / "tutorials"
CATALOG = ROOT / "source" / "data" / "catalog.json"
PATTERNS = ROOT / "data" / "patterns.json"
OUT = ROOT / "data" / "tutorials.json"

MAX_GIF_BYTES = 1_000_000

H_ANY = re.compile(r"^(?P<h>#{1,4})\s+(?P<text>.+?)\s*$")
H_TITLE = re.compile(r"^# (?P<title>.+?)(?:\s+\((?P<status>draft)\))?$")
H_SHAPE = re.compile(r"^## Shape (?P<n>\d+): (?P<name>.+)$")
H_SUBSHAPE = re.compile(r"^### (?P<n>\d+)(?P<sub>[a-z])\. (?P<name>.+)$")
H_WORKED = re.compile(r"^#{3,4} (?P<title>.+?) \(LC (?P<id>\d+)\)(?P<rest>.*)$")
H_TABLE = re.compile(r"^#{3,4} (?P<label>.+?) problems$", re.I)
H_SECTION = re.compile(r"^## (?P<text>.+)$")
FENCE = re.compile(r"^```(?P<lang>[A-Za-z0-9_-]*)\s*$")

T_HEAD = re.compile(r"^\|\s*LC\s*\|(?P<rest>.+)\|\s*$")
T_DELIM = re.compile(r"^\|(?:\s*:?-{3,}:?\s*\|)+\s*$")
T_ROW = re.compile(r"^\|(?P<cells>.+)\|\s*$")
FREQ = re.compile(r"^(?:🔥){1,3}$")
DIFF = {"Easy": "Easy", "Med": "Medium", "Medium": "Medium", "Hard": "Hard"}
REQUIRED_COLS = {"LC", "Title", "Diff", "Freq"}
OPTIONAL_COLS = {"State", "Note"}

LINK_ANCHOR = re.compile(r"\]\(#(?P<a>[^)]+)\)")
LINK_FILE = re.compile(r"\]\((?P<f>[A-Za-z][A-Za-z0-9]*\.md)\)")
IMAGE = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<src>assets/[^)\s]+)\)")
LC_IN_FILENAME = re.compile(r"lc(\d{4})")

REQUIRED_SECTIONS = ["Contents", "The one idea", "Which shape", "Pitfalls", "Drills",
                     "Reference card"]

README_START = "<!-- tutorials:status -->"
README_END = "<!-- /tutorials:status -->"


class TutorialError(Exception):
    pass


def pattern_id(stem):
    """SlidingWindow -> sliding-window (CamelCase file stem -> kebab pattern id)."""
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "-", stem).lower()


def slugify(text, seen=None):
    """GitHub-style heading anchor: lowercase, drop everything except word chars,
    hyphens and spaces, spaces -> hyphens, duplicates get -1, -2, ...
    tracker/static/js/md.js must implement the exact same rule."""
    s = text.strip().lower()
    s = re.sub(r"[^\w\- ]", "", s)
    s = s.replace(" ", "-")
    if seen is not None:
        base, n = s, 0
        while s in seen:
            n += 1
            s = f"{base}-{n}"
        seen.add(s)
    return s


def _cells(line):
    return [c.strip() for c in line.strip()[1:-1].split("|")]


class Parser:
    def __init__(self, path, catalog_by_id):
        self.path = path
        self.pid = pattern_id(path.stem)
        self.by_id = catalog_by_id
        self.lines = path.read_text(encoding="utf-8").splitlines()
        self.errors, self.warnings = [], []
        self.title, self.status = None, "done"
        self.headings, self.shapes, self.gifs, self.links_to = [], [], [], set()
        self.worked_elsewhere = []
        self.fences = {}
        self.pattern_template = None
        self._anchors = set()

    def err(self, i, msg):
        self.errors.append(f"{self.path.name}:{i + 1}: {msg}")

    def warn(self, i, msg):
        self.warnings.append(f"{self.path.name}:{i + 1}: {msg}")

    # ---- driver ---------------------------------------------------------
    def parse(self):
        in_fence, lang = False, None
        fence_start = None
        cur = None                  # innermost open (sub)shape
        parent = None               # open top-level shape
        expect_table = None         # (sub)shape that owns the next LC table
        in_which_shape = False
        seen_shape = False
        table = None                # {"cols":..., "owner":...} while reading rows
        blurb_pending = None
        template_pending = None     # (sub)shape whose first python fence is its template
        pattern_template_pending = False

        for i, line in enumerate(self.lines):
            fm = FENCE.match(line)
            if fm and not in_fence:
                in_fence, lang, fence_start = True, fm.group("lang") or "", i
                self.fences[lang] = self.fences.get(lang, 0) + 1
                table = None
                continue
            if fm and in_fence:
                in_fence = False
                if lang == "python":
                    body = "\n".join(self.lines[fence_start + 1:i])
                    if template_pending is not None and template_pending.get("template") is None \
                            and not template_pending["_closed_for_template"]:
                        template_pending["template"] = body
                        template_pending = None
                    elif pattern_template_pending and self.pattern_template is None:
                        self.pattern_template = body
                        pattern_template_pending = False
                continue
            if in_fence:
                continue

            hm = H_ANY.match(line)
            if hm:
                table = None
                text = hm.group("text")
                level = len(hm.group("h"))
                anchor = slugify(text, self._anchors)
                self.headings.append({"level": level, "text": text, "anchor": anchor})

                if level == 1 and self.title is None:
                    m = H_TITLE.match(line)
                    self.title = m.group("title") if m else text
                    if m and m.group("status"):
                        self.status = "draft"
                    continue

                m = H_SHAPE.match(line)
                if m:
                    parent = {"id": f"shape-{m.group('n')}", "label": text,
                              "name": m.group("name").strip(), "anchor": anchor,
                              "parent": None, "blurb": None, "template": None,
                              "_closed_for_template": False,
                              "worked": [], "gifs": [], "problems": [], "_line": i}
                    self.shapes.append(parent)
                    cur = parent
                    blurb_pending = parent
                    template_pending = parent
                    pattern_template_pending = False
                    seen_shape = True
                    expect_table = None
                    continue

                m = H_SUBSHAPE.match(line)
                if m and parent is not None:
                    if m.group("n") != parent["id"].split("-")[1]:
                        self.err(i, f"sub-shape {text!r} does not belong to {parent['id']}")
                    child = {"id": f"shape-{m.group('n')}{m.group('sub')}", "label": text,
                             "name": f"{parent['name']}: {m.group('name').strip()}",
                             "anchor": anchor, "parent": parent["id"], "blurb": None,
                             "template": None, "_closed_for_template": False,
                             "worked": [], "gifs": [], "problems": [], "_line": i}
                    self.shapes.append(child)
                    cur = child
                    blurb_pending = child
                    template_pending = child
                    expect_table = None
                    continue

                if H_SECTION.match(line):
                    cur = parent = None
                    expect_table = None
                    template_pending = None
                    blurb_pending = None
                    in_which_shape = (text == "Which shape")
                    pattern_template_pending = in_which_shape and not seen_shape
                    continue

                m = H_WORKED.match(line)
                if m:
                    rec = {"id": int(m.group("id")), "title": m.group("title").strip(),
                           "anchor": anchor}
                    if cur is not None:
                        cur["worked"].append(rec)
                        cur["_closed_for_template"] = True
                    else:
                        self.worked_elsewhere.append(rec)
                    continue

                m = H_TABLE.match(line)
                if m:
                    if cur is None:
                        self.err(i, f"'{text}' heading outside any Shape section")
                    else:
                        expect_table = cur
                        cur["_closed_for_template"] = True
                    continue
                continue

            # ---- tables --------------------------------------------------
            if table is not None:
                if T_DELIM.match(line):
                    continue
                rm = T_ROW.match(line)
                if rm:
                    self._row(i, table, _cells(line))
                    continue
                table = None            # blank line or prose ends the table

            tm = T_HEAD.match(line)
            if tm:
                cols = _cells(line)
                unknown = set(cols) - REQUIRED_COLS - OPTIONAL_COLS
                if unknown:
                    self.err(i, f"unknown column(s) {sorted(unknown)} in LC table")
                missing = REQUIRED_COLS - set(cols)
                if missing:
                    self.err(i, f"LC table missing column(s) {sorted(missing)}")
                if expect_table is None:
                    self.err(i, "LC table outside a '<label> problems' heading")
                    table = {"cols": cols, "owner": None}
                else:
                    table = {"cols": cols, "owner": expect_table}
                    expect_table = None
                continue

            # ---- blurb: first prose paragraph after a (sub)shape heading ----
            # A paragraph is one or more consecutive non-empty lines; join them
            # so a wrapped sentence is not cut at the first line break.
            if blurb_pending is not None:
                if line.strip() and not line.startswith("|") \
                        and not line.startswith("!") and not line.startswith("*"):
                    prev = blurb_pending.get("blurb")
                    blurb_pending["blurb"] = (prev + " " + line.strip()) if prev else line.strip()
                elif blurb_pending.get("blurb"):
                    blurb_pending = None      # blank line ends the paragraph

            # ---- images ---------------------------------------------------
            for im in IMAGE.finditer(line):
                src = im.group("src")
                lc = LC_IN_FILENAME.search(src)
                rec = {"src": src, "alt": im.group("alt"),
                       "shape": cur["id"] if cur else None,
                       "lc": int(lc.group(1)) if lc else None}
                self.gifs.append(rec)
                if cur is not None:
                    cur["gifs"].append(src)
                p = TUTORIALS / src
                if not p.is_file():
                    self.err(i, f"image not found: {src}")
                else:
                    size = p.stat().st_size
                    if size > MAX_GIF_BYTES:
                        self.warn(i, f"{src} is {size // 1000} KB (> {MAX_GIF_BYTES // 1000} KB)")
                    if src.split("/")[1] != self.pid:
                        self.warn(i, f"{src} lives outside assets/{self.pid}/")

        self._validate_links()
        self._finish()
        return self

    def _row(self, i, table, cells):
        cols = table["cols"]
        if len(cells) != len(cols):
            self.err(i, f"table row has {len(cells)} cells, header has {len(cols)}")
            return
        row = dict(zip(cols, cells))
        try:
            pid = int(row["LC"])
        except ValueError:
            self.err(i, f"LC cell is not a number: {row['LC']!r}")
            return
        c = self.by_id.get(pid)
        if c is None:
            self.err(i, f"LC {pid} is not in the leetcode.com catalog")
            return
        diff = DIFF.get(row["Diff"])
        if diff is None:
            self.err(i, f"LC {pid}: bad Diff {row['Diff']!r} (Easy / Med / Hard)")
        elif diff != c["difficulty"]:
            # The author's call vs. LeetCode's label; the app shows the catalog's.
            self.warn(i, f"LC {pid}: Diff says {diff}, catalog says {c['difficulty']}")
        if not FREQ.match(row["Freq"]):
            self.err(i, f"LC {pid}: Freq must be 1-3 🔥, got {row['Freq']!r}")
            freq = 0
        else:
            freq = row["Freq"].count("🔥")
        owner = table["owner"]
        if owner is None:
            return
        for s in self.shapes:
            if any(p["id"] == pid for p in s["problems"]):
                self.err(i, f"LC {pid} already listed under {s['id']} in this tutorial")
        owner["problems"].append({
            "id": pid, "slug": c["slug"], "title_md": row["Title"], "diff": diff or c["difficulty"],
            "paid": bool(c["paid_only"]), "state": row.get("State") or None,
            "freq": freq, "note_md": row.get("Note") or "",
        })

    def _validate_links(self):
        anchors = {h["anchor"] for h in self.headings}
        in_fence = False
        for i, line in enumerate(self.lines):
            if FENCE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for m in LINK_ANCHOR.finditer(line):
                if m.group("a") not in anchors:
                    self.err(i, f"unresolved anchor #{m.group('a')}")
            for m in LINK_FILE.finditer(line):
                f = m.group("f")
                if not (TUTORIALS / f).is_file() or f == "README.md":
                    self.err(i, f"link to missing tutorial {f}")
                else:
                    self.links_to.add(pattern_id(Path(f).stem))

    def _finish(self):
        if self.title is None:
            self.err(0, "missing H1 title")
        h2 = {h["text"] for h in self.headings if h["level"] == 2}
        for req in REQUIRED_SECTIONS:
            if req not in h2:
                self.err(0, f"missing required section '## {req}'")
        if not self.shapes:
            self.err(0, "no '## Shape N:' sections")
        children = {s["parent"] for s in self.shapes if s["parent"]}
        for s in self.shapes:
            if s["id"] in children and s["problems"]:
                self.err(s["_line"], f"{s['id']} has sub-shapes and its own problem table")
            if s["id"] not in children and not s["problems"]:
                self.warn(s["_line"], f"{s['id']} has no problem table")

    def result(self):
        shapes = []
        for s in self.shapes:
            shapes.append({k: v for k, v in s.items() if not k.startswith("_")})
        ids = sorted({p["id"] for s in shapes for p in s["problems"]})
        return {
            "title": self.title, "file": self.path.name, "status": self.status,
            "has_mermaid": self.fences.get("mermaid", 0) > 0,
            "code_langs": sorted(self.fences),
            "template": self.pattern_template,
            "headings": self.headings,
            "shapes": shapes,
            "gifs": self.gifs,
            "worked_elsewhere": self.worked_elsewhere,
            "links_to": sorted(self.links_to),
            "ids": ids,
        }


def load_catalog():
    cat = json.loads(CATALOG.read_text(encoding="utf-8"))
    return {v["id"]: {"slug": k, **v} for k, v in cat.items()}


def tutorial_files():
    return sorted(p for p in TUTORIALS.glob("*.md") if p.name != "README.md")


def build(strict=True, log=print):
    """Parse every tutorial. Returns the tutorials.json dict; raises TutorialError
    (after printing every problem) when strict and any error was found."""
    by_id = load_catalog()
    out = {"generated_from": [], "slug_rule": "github", "tutorials": {}, "by_id": {}, "dups": []}
    errors, warnings = [], []
    for path in tutorial_files():
        p = Parser(path, by_id).parse()
        errors += p.errors
        warnings += p.warnings
        out["generated_from"].append(f"tutorials/{path.name}")
        out["tutorials"][p.pid] = p.result()
    seen = {}
    for pid, t in out["tutorials"].items():
        for s in t["shapes"]:
            for pr in s["problems"]:
                seen.setdefault(pr["id"], []).append({"tutorial": pid, "shape": s["id"]})
    out["by_id"] = {str(k): v for k, v in sorted(seen.items())}
    out["dups"] = [{"id": k, "in": [f"{m['tutorial']}/{m['shape']}" for m in v]}
                   for k, v in sorted(seen.items()) if len(v) > 1]
    for w in warnings:
        log(f"warning: {w}")
    for e in errors:
        log(f"error: {e}")
    if errors and strict:
        raise TutorialError(f"{len(errors)} error(s) in tutorials")
    return out


def dumps(data):
    return json.dumps(data, ensure_ascii=False, indent=1) + "\n"


def leftover_curriculum_ids(data, patterns):
    """Core ids the legacy curriculum assigned to a pattern that its tutorial
    does not list — printed so the author can decide whether to add them."""
    out = {}
    for pid, t in data["tutorials"].items():
        legacy = patterns.get("patterns", {}).get(pid, {}).get("legacy_core_ids", [])
        missing = sorted(set(legacy) - set(t["ids"]))
        if missing:
            out[pid] = missing
    return out


def readme_table(data, patterns):
    rows = ["| Pattern | Status | Tutorial |", "| --- | --- | --- |"]
    order = patterns.get("order", []) or list(data["tutorials"])
    names = {k: v["name"] for k, v in patterns.get("patterns", {}).items()}
    for pid in order:
        t = data["tutorials"].get(pid)
        name = names.get(pid, t["title"] if t else pid)
        if t is None:
            rows.append(f"| {name} | in progress | — |")
        elif t["status"] == "draft":
            rows.append(f"| {name} | draft | [{t['file']}]({t['file']}) |")
        else:
            rows.append(f"| {name} | ✓ written | [{t['file']}]({t['file']}) |")
    written = sum(1 for p in order if p in data["tutorials"])
    head = (f"{written} of {len(order)} patterns have a written tutorial. The rest are in "
            f"progress and will be added one pattern at a time.")
    return "\n".join([README_START, head, "", *rows, README_END])


def update_readme(table_md):
    path = TUTORIALS / "README.md"
    text = path.read_text(encoding="utf-8")
    if README_START in text and README_END in text:
        pre = text[:text.index(README_START)]
        post = text[text.index(README_END) + len(README_END):]
        new = pre + table_md + post
    else:
        marker = "\n## "
        idx = text.index(marker)   # before the first H2
        new = text[:idx] + "\n## Status\n\n" + table_md + "\n" + text[idx:]
    if new != text:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def main(argv):
    patterns = json.loads(PATTERNS.read_text(encoding="utf-8")) if PATTERNS.exists() else {}
    try:
        data = build()
    except TutorialError as e:
        print(e, file=sys.stderr)
        return 1
    text = dumps(data)
    if "--check" in argv:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != text:
            print(f"{OUT.relative_to(ROOT)} is stale — run scripts/build_tutorials.py", file=sys.stderr)
            return 1
        print("tutorials.json is fresh")
        return 0
    if "--readme-table" in argv:
        table = readme_table(data, patterns)
        changed = update_readme(table)
        print(table)
        print("updated tutorials/README.md" if changed else "tutorials/README.md unchanged")
        return 0
    OUT.write_text(text, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")
    for pid, t in data["tutorials"].items():
        n = sum(len(s["problems"]) for s in t["shapes"])
        print(f"  {pid:16} {t['status']:6} shapes={len(t['shapes']):2} problems={n:3} gifs={len(t['gifs'])}")
    for pid, missing in leftover_curriculum_ids(data, patterns).items():
        print(f"  note: {pid} tutorial does not list legacy core ids {missing}")
    if data["dups"]:
        print(f"  shared across tutorials: {[d['id'] for d in data['dups']]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
