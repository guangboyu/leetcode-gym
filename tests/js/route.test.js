/* Tests for tracker/static/route.js (Learn-tab logic) against the real data
 * files, so a data refresh that breaks the taxonomy fails here too.
 * Runs under node --test and under jsc (see harness.js). */
if (typeof require !== "undefined") require("./harness.js");

const PATTERNS = readJSON("data/patterns.json");
const TUTORIALS = readJSON("data/tutorials.json");
const PROBLEMS = readJSON("data/problems.json").problems;
const ROWS = Object.entries(PROBLEMS).sort((a, b) => a[1].id - b[1].id);
const BY_ID = new Map(ROWS.map((r) => [r[1].id, r]));
const none = () => false;

function learn(isDone, cap, opts) {
  return Route.learnState(PATTERNS, TUTORIALS, ROWS, isDone || none, cap === undefined ? 1700 : cap, opts || {});
}
function pattern(id, state) { return (state || learn()).find((p) => p.id === id); }
function sub(pat, id) { return pat.subtopics.find((s) => s.id === id); }
function ids(rows) { return rows.map((r) => r[1].id); }

/* ---- resolveOx3f: three tiers ------------------------------------------ */

test("resolveOx3f: section tier beats chapter tier", () => {
  const m = { topic: "Sliding Window & Two Pointers", section: "§2.2 Shortest Subarray", tier: "interview" };
  assertEq(Route.resolveOx3f(m, PATTERNS), "sliding-window/shape-3");
});

test("resolveOx3f: chapter tier when no section override", () => {
  const m = { topic: "Sliding Window & Two Pointers", section: "§1.1 Basics", tier: "interview" };
  assertEq(Route.resolveOx3f(m, PATTERNS), "sliding-window/shape-1");
  const bs = { topic: "Binary Search", section: "4. Other", tier: "interview" };
  assertEq(Route.resolveOx3f(bs, PATTERNS), "binary-search/rotated-mountain");
});

test("resolveOx3f: topic default for un-mapped sections; null for competition tier", () => {
  const m = { topic: "Data Structures", section: "Part C", tier: "interview" };
  assertEq(Route.resolveOx3f(m, PATTERNS), "arrays-hashing");
  assertEq(Route.resolveOx3f({ ...m, tier: "competition" }, PATTERNS), null);
  assertEq(Route.resolveOx3f({ topic: "Nope", section: "§1.1", tier: "interview" }, PATTERNS), null);
});

test("every interview-tier membership in problems.json resolves to a known pattern", () => {
  const known = new Set(PATTERNS.order);
  for (const [, p] of ROWS) {
    for (const m of p.lists.ox3f || []) {
      if (m.tier !== "interview") continue;
      const t = Route.resolveOx3f(m, PATTERNS);
      assert(t && known.has(t.split("/")[0]), `${m.topic} || ${m.section} -> ${t}`);
    }
  }
});

test("isOptional: (optional) sections and patterns.json hidden keys", () => {
  const hidden = new Set(PATTERNS.ox3f.hidden);
  assert(Route.isOptional({ topic: "Any", section: "§1.2 Foo (optional)" }, hidden));
  assert(Route.isOptional({ topic: "Data Structures", section: "§1.3 Sum of Distances" }, hidden));
  assert(!Route.isOptional({ topic: "Data Structures", section: "§1.1 Basics" }, hidden));
});

/* ---- learnState ---------------------------------------------------------- */

test("learnState follows patterns.order and flags tutorials", () => {
  const state = learn();
  assertEq(state.map((p) => p.id), PATTERNS.order);
  const sw = pattern("sliding-window", state), ah = pattern("arrays-hashing", state);
  assert(sw.hasTutorial && sw.status === "done" && sw.tutorialFile === "SlidingWindow.md");
  assert(!ah.hasTutorial && ah.status === "in-progress");
  assert(sw.template && sw.template.indexOf("SHRINK_CONDITION") >= 0, "tutorial template wins");
  assert(ah.template && ah.template.indexOf("seen") >= 0, "patterns.json template fallback");
});

test("sliding-window: four leaf shapes in document order, tutorial rows carry meta", () => {
  const sw = pattern("sliding-window");
  const shapes = sw.subtopics.filter((s) => s.kind === "shape");
  assertEq(shapes.map((s) => s.id), ["shape-1", "shape-2", "shape-3", "shape-4"]);
  assertEq(shapes.map((s) => s.name), ["Fixed size k", "Longest valid", "Shortest valid", "Count subarrays"]);
  const s2 = sub(sw, "shape-2");
  assertEq(s2.key, "sliding-window/shape-2");
  assertEq(ids(s2.core).slice(0, 3), [3, 1004, 424]);           // the table's own order
  const meta = s2.core[0][2];
  assertEq(meta.freq, 3);
  assert(meta.note_md.indexOf(">= left") >= 0);
  assert(s2.template && s2.template.indexOf("harvest AFTER") >= 0);
  assert(s2.anchor === "shape-2-longest-valid");
  const paid = s2.core.find((r) => r[1].id === 340);
  assert(paid && paid[2].paid && paid[1].paid_only, "paid rows stay in tutorial tables, flagged");
  assertEq(s2.total, s2.core.length);
});

test("two-pointers: 2a/2b are leaves under shape-2, which is not itself a subtopic", () => {
  const tp = pattern("two-pointers");
  const shapes = tp.subtopics.filter((s) => s.kind === "shape");
  assertEq(shapes.map((s) => s.id), ["shape-1", "shape-2a", "shape-2b", "shape-3"]);
  assertEq(shapes.map((s) => s.parent), [null, "shape-2", "shape-2", null]);
  assertEq(sub(tp, "shape-2a").name, "Chasing: Read and write");
  assert(sub(tp, "shape-2") === undefined);
});

test("also-core group = legacy core ids no tutorial or curriculum claims", () => {
  const sw = pattern("sliding-window"), tp = pattern("two-pointers");
  assertEq(ids(sub(sw, "also-core").core).sort((a, b) => a - b), [121, 219, 658]);
  assertEq(ids(sub(tp, "also-core").core).sort((a, b) => a - b), [31, 189, 881]);
  assertEq(sub(sw, "also-core").kind, "also-core");
  assert(sub(pattern("arrays-hashing"), "also-core") === undefined, "curriculum patterns have none");
});

test("curriculum patterns use subtopics[].core_ids", () => {
  const ah = pattern("arrays-hashing");
  const hb = sub(ah, "hash-basics");
  assertEq(hb.kind, "curriculum");
  assertEq(ids(hb.core), PATTERNS.patterns["arrays-hashing"].subtopics[0].core_ids);
  assert(hb.recognize && hb.solve && hb.template.indexOf("seen") >= 0);
});

test("ext: 0x3F rows land on the resolved subtopic, minus core, split by cap", () => {
  const s3 = sub(pattern("sliding-window"), "shape-3");
  const coreSlugs = new Set(pattern("sliding-window").subtopics.flatMap((s) => s.core.map((r) => r[0])));
  assert(s3.ext.inCap.length > 0, "shortest-window chapter has 0x3F problems");
  for (const [slug, p, meta] of s3.ext.inCap) {
    assert(!coreSlugs.has(slug), "core problems are not repeated in ext");
    assert(!p.paid_only, "paid problems excluded from ext");
    assert(!(p.rating > 1700), "above-cap problems counted, not listed");
    assertEq(Route.resolveOx3f({ ...meta, tier: "interview" }, PATTERNS), "sliding-window/shape-3");
  }
  const ratings = s3.ext.inCap.map((r) => Route.effRating(r[1]));
  assertEq(ratings, ratings.slice().sort((a, b) => a - b), "sorted by effRating");
  const uncapped = sub(pattern("sliding-window", learn(none, null)), "shape-3");
  assertEq(uncapped.ext.above, 0);
  assertEq(uncapped.ext.inCap.length, s3.ext.inCap.length + s3.ext.above);
});

test("ext: hidden/(optional) sections need showOptional", () => {
  const key = "Data Structures||1.3";                       // hidden in patterns.json
  assert(PATTERNS.ox3f.hidden.indexOf(key) >= 0);
  const target = Route.resolveOx3f({ topic: "Data Structures", section: "§1.3 Sum of Distances", tier: "interview" }, PATTERNS);
  const [pid, sid] = target.split("/");
  const inTarget = (state) => {
    const s = sub(pattern(pid, state), sid);
    return s.ext.inCap.filter((r) => r[2].section.indexOf("§1.3") === 0).length;
  };
  assertEq(inTarget(learn(none, null, { showOptional: false })), 0);
  assert(inTarget(learn(none, null, { showOptional: true })) > 0);
});

test("fallback groups: chapter-level targets become 'More from 0x3F' subtopics", () => {
  const dp = pattern("dp-1d", learn(none, null));
  const groups = dp.subtopics.filter((s) => s.kind === "ox3f");
  assert(groups.length > 0);
  for (const g of groups) {
    assert(g.name.indexOf("More from 0x3F") === 0 && g.optional && g.post, g.name);
    assertEq(g.core, []);
    assertEq(g.total, 0, "fallback groups never count toward progress");
  }
});

test("progress counts distinct core slugs and skips skipped subtopics", () => {
  const sw0 = pattern("sliding-window");
  const first = sub(sw0, "shape-1").core[0][0];
  const done = (slug) => slug === first;
  const sw = pattern("sliding-window", learn(done));
  assertEq(sw.done, 1);
  assertEq(sub(sw, "shape-1").done, 1);
  assertEq(sub(sw, "shape-1").todo.length, sub(sw, "shape-1").total - 1);
  const withoutShape1 = pattern("sliding-window", learn(done, 1700, { skipped: new Set(["sliding-window/shape-1"]) }));
  assert(sub(withoutShape1, "shape-1").skipped);
  assertEq(withoutShape1.done, 0);
  assertEq(withoutShape1.total, sw.total - sub(sw, "shape-1").total);
  assert(sw.total <= sw.subtopics.reduce((n, s) => n + s.total, 0), "distinct never exceeds the sum");
});

test("nextUp: first pattern/subtopic with work left; skips skipped and ox3f groups", () => {
  const state = learn();
  const n = Route.nextUp(state);
  assertEq(n.pattern.id, "arrays-hashing");
  assertEq(n.subtopic.id, "hash-basics");
  const allDone = learn(() => true);
  assertEq(Route.nextUp(allDone), null);
  const skipAH = new Set(pattern("arrays-hashing").subtopics.map((s) => s.key));
  const n2 = Route.nextUp(learn(none, 1700, { skipped: skipAH }));
  assertEq(n2.pattern.id, "two-pointers");
  assertEq(n2.subtopic.id, "shape-1");
});

test("drillPool + effRating still behave", () => {
  assertEq(Route.effRating({ rating: null, difficulty: "Medium" }), 1650);
  const pool = Route.drillPool(ROWS, () => true, 1600, 1700, null, new Set(["hot100"]));
  assert(pool.length > 0 && pool.every(([, p]) => p.lists.hot100 && !p.paid_only));
});
