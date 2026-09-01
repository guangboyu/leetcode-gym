/* Pure logic of the views: Today's sort, Browse's filter predicate + sort,
 * Drill's no-repeat pick. The DOM-facing parts are exercised in the browser. */
import { test, assert } from "./harness.mjs";
import { dueComparator, nextReview } from "../../tracker/static/js/views/today.js";
import { filtersFrom, toQuery, matches, comparator } from "../../tracker/static/js/views/browse.js";
import { pick } from "../../tracker/static/js/views/drill.js";

const P = (id, title, difficulty, rating, lists = {}) => ({ id, title, difficulty, rating, paid_only: false, lists });
const eff = (p) => p.rating || { Easy: 1250, Medium: 1650, Hard: 2150 }[p.difficulty];

test("today: due rows sort by due date, then rating", () => {
  const progress = { a: { due: "2026-08-30" }, b: { due: "2026-08-28" }, c: { due: "2026-08-30" } };
  const rows = [["a", P(1, "A", "Hard", 2000)], ["b", P(2, "B", "Easy", null)], ["c", P(3, "C", "Easy", 1300)]];
  rows.sort(dueComparator(progress, eff));
  assert.deepEqual(rows.map((r) => r[0]), ["b", "c", "a"]);
});

test("today: next review is the earliest future due date with its count", () => {
  const s = { today: "2026-09-01", rows: [["a", {}], ["b", {}], ["c", {}], ["d", {}]],
    progress: { a: { status: "solved", due: "2026-09-05" }, b: { status: "solved", due: "2026-09-03" }, c: { status: "solved", due: "2026-09-03" }, d: { status: "solved", due: "2026-08-30" } } };
  assert.deepEqual(nextReview(s), { date: "2026-09-03", n: 2 });
  assert.equal(nextReview({ today: "2026-09-01", rows: [], progress: {} }), null);
});

test("browse: filters round-trip through the query string", () => {
  const f = filtersFrom({ list: "ox3f", topics: "Math,Strings", diff: "Hard", status: "due", q: "win", sort: "level", dir: "desc", page: "2", cap: "1", comp: "1" });
  assert.equal(f.list, "ox3f"); assert.deepEqual(f.topics, ["Math", "Strings"]); assert.equal(f.page, 2); assert.ok(f.cap && f.comp);
  const q = toQuery(f);
  assert.deepEqual(filtersFrom(q), f);
  assert.equal(filtersFrom({}).sort, "id");
  assert.equal(toQuery(filtersFrom({})).sort, "");
});

test("browse: predicate honours list, topics, difficulty, status, cap and search", () => {
  const p = P(3, "Longest Substring Without Repeating Characters", "Medium", 1800,
    { hot100: { group: "x" }, ox3f: [{ topic: "Sliding Window", section: "§1", tier: "interview" }, { topic: "Comp", section: "§9", tier: "competition" }] });
  const topics = new Set(["Sliding Window"]);
  const f0 = filtersFrom({});
  assert.ok(matches(f0, "slug", p, "new", 1700, topics));
  assert.ok(matches(filtersFrom({ list: "hot100" }), "slug", p, "new", null, topics));
  assert.ok(!matches(filtersFrom({ list: "neetcode250" }), "slug", p, "new", null, topics));
  assert.ok(matches(filtersFrom({ list: "ox3f" }), "slug", p, "new", null, topics));
  assert.ok(matches(filtersFrom({ topics: "Sliding Window" }), "slug", p, "new", null, topics));
  assert.ok(!matches(filtersFrom({ topics: "Math" }), "slug", p, "new", null, topics));
  assert.ok(!matches(filtersFrom({ diff: "Easy" }), "slug", p, "new", null, topics));
  assert.ok(!matches(filtersFrom({ status: "due" }), "slug", p, "new", null, topics));
  assert.ok(!matches(filtersFrom({ cap: "1" }), "slug", p, "new", 1700, topics), "rated above cap is hidden");
  assert.ok(matches(filtersFrom({ cap: "1" }), "slug", p, "new", null, topics), "no cap → shown");
  assert.ok(matches(filtersFrom({ q: "substring" }), "slug", p, "new", null, topics));
  assert.ok(matches(filtersFrom({ q: "#3" }), "slug", p, "new", null, topics));
  assert.ok(!matches(filtersFrom({ q: "#33" }), "slug", p, "new", null, topics));
  assert.ok(!matches(filtersFrom({ q: "zzz" }), "slug", p, "new", null, topics));
});

test("browse: level sort uses estimated ratings; status sort groups due first", () => {
  const store = { dstatus: (slug, s) => s.st[slug] };
  const s = { st: { a: "new", b: "due", c: "solved" }, progress: { b: { due: "2026-08-30" }, c: { due: "2026-09-09" } } };
  const rows = [["a", P(1, "A", "Hard", null)], ["b", P(2, "B", "Easy", null)], ["c", P(3, "C", "Medium", 1500)]];
  rows.sort(comparator(filtersFrom({ sort: "level" }), s, store, eff));
  assert.deepEqual(rows.map((r) => r[0]), ["b", "c", "a"]);
  rows.sort(comparator(filtersFrom({ sort: "level", dir: "desc" }), s, store, eff));
  assert.deepEqual(rows.map((r) => r[0]), ["a", "c", "b"]);
  rows.sort(comparator(filtersFrom({ sort: "status" }), s, store, eff));
  assert.deepEqual(rows.map((r) => r[0]), ["b", "c", "a"]);
});

test("drill: pick avoids the recent draws until the pool is exhausted", () => {
  const pool = [["a", {}], ["b", {}], ["c", {}]];
  const rand = () => 0;
  assert.equal(pick(pool, ["a"], rand)[0], "b");
  assert.equal(pick(pool, ["a", "b"], rand)[0], "c");
  // everything recent: anything but the very last draw
  assert.equal(pick(pool, ["a", "b", "c"], rand)[0], "a");
  assert.equal(pick([["c", {}]], ["c"], rand)[0], "c", "a single-problem pool repeats");
  assert.equal(pick([], [], rand), null);
});
