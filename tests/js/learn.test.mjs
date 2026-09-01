/* Tests for views/learn.js pure helpers against the real data files
 * (route.js learnState is loaded as a classic script into the global scope). */
import { test, assert, readText } from "./harness.mjs";
import "./marked-global.mjs";
import {
  ringOffset, RING_C, chipModel, defaultSub, resolveSelection, toolbarText,
  extSlice, noteHtml, withNotes, neighbour,
} from "../../tracker/static/js/views/learn.js";
import { tocEntries, metaById } from "../../tracker/static/js/views/learn-read.js";

// route.js is a classic global script; evaluate it once into globalThis.
const routeSrc = await readText("tracker/static/route.js");
(0, eval)(routeSrc);
const Route = globalThis.Route;

const PATTERNS = JSON.parse(await readText("data/patterns.json"));
const TUTORIALS = JSON.parse(await readText("data/tutorials.json"));
const PROBLEMS = JSON.parse(await readText("data/problems.json")).problems;
const ROWS = Object.entries(PROBLEMS).sort((a, b) => a[1].id - b[1].id);
const slugOf = (id) => ROWS.find((r) => r[1].id === id)[0];

function learn(doneIds = [], skipped = []) {
  const done = new Set(doneIds.map(slugOf));
  return Route.learnState(PATTERNS, TUTORIALS, ROWS, (s) => done.has(s), 1700, { skipped: new Set(skipped) });
}
const pat = (state, id) => state.find((p) => p.id === id);

test("ringOffset: empty ring for 0/0, full for done, proportional between", () => {
  assert.equal(ringOffset(0, 0), RING_C);
  assert.equal(ringOffset(5, 5), 0);
  assert.equal(ringOffset(1, 4), +(RING_C * 0.75).toFixed(2));
  assert.equal(ringOffset(9, 4), 0, "clamps above 100%");
});

test("chipModel: sliding window has 4 leaf shapes first, dashed groups after", () => {
  const sw = pat(learn(), "sliding-window");
  const m = chipModel(sw);
  assert.deepEqual(m.slice(0, 4).map((c) => c.id), ["shape-1", "shape-2", "shape-3", "shape-4"]);
  assert.ok(m.slice(0, 4).every((c) => !c.dashed && c.kind === "shape"));
  const alsoCore = m.find((c) => c.kind === "also-core");
  assert.ok(alsoCore && alsoCore.dashed, "also-core chip is dashed");
  assert.equal(alsoCore.total, 3, "SW leftovers 121/219/658");
});

test("chipModel: complete flag and skipped flag", () => {
  const sw = pat(learn([643, 1456, 438, 567, 239, 2461, 1052, 1423, 30], ["sliding-window/shape-3"]), "sliding-window");
  const m = chipModel(sw);
  assert.equal(m.find((c) => c.id === "shape-1").complete, true);
  assert.equal(m.find((c) => c.id === "shape-2").complete, false);
  assert.equal(m.find((c) => c.id === "shape-3").skipped, true);
});

test("defaultSub: first non-skipped shape with work left; falls back to first", () => {
  const all = learn([643, 1456, 438, 567, 239, 2461, 1052, 1423, 30], ["sliding-window/shape-2"]);
  assert.equal(defaultSub(pat(all, "sliding-window")), "shape-3");
  const none = learn();
  assert.equal(defaultSub(pat(none, "two-pointers")), "shape-1");
});

test("resolveSelection: route wins over settings, settings over nextUp, nextUp over first", () => {
  const state = learn();
  const nu = Route.nextUp(state);
  let sel = resolveSelection(state, { view: "learn", pattern: "sliding-window", sub: "shape-4" }, { lastPattern: "tries" }, nu);
  assert.equal(sel.pattern.id, "sliding-window"); assert.equal(sel.sub, "shape-4"); assert.equal(sel.read, false);
  sel = resolveSelection(state, { view: "learn" }, { lastPattern: "tries", lastSection: "build-query" }, nu);
  assert.equal(sel.pattern.id, "tries"); assert.equal(sel.sub, "build-query");
  sel = resolveSelection(state, { view: "learn" }, {}, nu);
  assert.equal(sel.pattern.id, nu.pattern.id); assert.equal(sel.sub, nu.subtopic.id);
  sel = resolveSelection(state, { view: "learn" }, {}, null);
  assert.equal(sel.pattern.id, "arrays-hashing");
});

test("resolveSelection: unknown pattern/sub in the route fall back; read + anchor pass through", () => {
  const state = learn();
  const sel = resolveSelection(state, { view: "learn", pattern: "nope", sub: "x", read: true, anchor: "pitfalls" }, {}, null);
  assert.equal(sel.pattern.id, "arrays-hashing");
  assert.equal(sel.sub, "hash-basics");
  assert.equal(sel.read, true); assert.equal(sel.anchor, "pitfalls");
  const sel2 = resolveSelection(state, { view: "learn", pattern: "sliding-window", sub: "bogus" }, { lastPattern: "sliding-window", lastSection: "shape-3" }, null);
  assert.equal(sel2.sub, "shape-3", "remembered section for the same pattern");
});

test("toolbarText: counts and shapes-to-go wording", () => {
  const state = learn();
  const sw = pat(state, "sliding-window");
  assert.match(toolbarText(sw), /^0 of \d+ · \d+ shapes to go$/);
  const ah = pat(state, "arrays-hashing");
  assert.match(toolbarText(ah), /subtopics to go$/);
  const one = { done: 3, total: 4, hasTutorial: true, subtopics: [{ skipped: false, kind: "shape", todo: [1] }] };
  assert.equal(toolbarText(one), "3 of 4 · 1 shape to go");
  const done = { done: 4, total: 4, hasTutorial: false, subtopics: [{ skipped: false, kind: "curriculum", todo: [] }] };
  assert.equal(toolbarText(done), "4 of 4 · all done");
});

test("extSlice: preview of 10 unless showAll", () => {
  const rows = Array.from({ length: 14 }, (_, i) => [String(i), {}, {}]);
  assert.deepEqual(extSlice(rows, false), { rows: rows.slice(0, 10), hidden: 4 });
  assert.equal(extSlice(rows, true).hidden, 0);
  assert.equal(extSlice(rows.slice(0, 3), false).hidden, 0);
});

test("noteHtml / withNotes: inline markdown via marked, escaped otherwise", () => {
  assert.match(noteHtml("jump variant needs the `>= left` guard"), /<code>&gt;= left<\/code>/);
  assert.equal(noteHtml(""), "");
  const rows = withNotes([["a", { id: 1 }, { freq: 2, note_md: "see *transforms*" }], ["b", { id: 2 }, {}]]);
  assert.match(rows[0][2].note_html, /<em>transforms<\/em>/);
  assert.equal(rows[0][2].freq, 2);
  assert.deepEqual(rows[1][2], {});
});

test("neighbour: previous / next with bounds", () => {
  const list = [{ id: "a" }, { id: "b" }, { id: "c" }];
  assert.equal(neighbour(list, "b", 1), "c");
  assert.equal(neighbour(list, "b", -1), "a");
  assert.equal(neighbour(list, "c", 1), null);
  assert.equal(neighbour(list, "zz", 1), null);
});

test("tocEntries: H2/H3 only, in document order", () => {
  const t = TUTORIALS.tutorials["sliding-window"];
  const toc = tocEntries(t.headings);
  assert.ok(toc.every((h) => h.level === 2 || h.level === 3));
  assert.equal(toc[0].anchor, "contents");
  assert.ok(toc.some((h) => h.anchor === "shape-2-longest-valid"));
});

test("metaById: freq/note/state per tutorial table row", () => {
  const m = metaById(TUTORIALS.tutorials["sliding-window"]);
  const lc3 = m.get(3);
  assert.equal(lc3.freq, 3);
  assert.equal(lc3.shape, "shape-2");
  assert.match(lc3.note_md, /guard/);
  assert.equal(m.get(340).paid, true);
});
