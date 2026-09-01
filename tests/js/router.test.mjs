import { test, assert } from "./harness.mjs";
import { parse, build, parseQuery, encodeQuery, onChange, _handleForTests, _resetForTests } from "../../tracker/static/js/router.js";

test("router: parse", () => {
  assert.deepEqual(parse("#/today"), { view: "today", query: {} });
  assert.deepEqual(parse(""), { view: "today", query: {} });
  assert.deepEqual(parse("#/nope"), { view: "today", query: {} });
  assert.deepEqual(parse("#/learn"), { view: "learn", query: {} });
  assert.deepEqual(parse("#/learn/sliding-window"), { view: "learn", query: {}, pattern: "sliding-window" });
  assert.deepEqual(parse("#/learn/sliding-window/shape-2"), { view: "learn", query: {}, pattern: "sliding-window", sub: "shape-2" });
  assert.deepEqual(parse("#/learn/sliding-window/read"), { view: "learn", query: {}, pattern: "sliding-window", read: true });
  assert.deepEqual(parse("#/learn/sliding-window/read/shape-2-longest-valid"),
    { view: "learn", query: {}, pattern: "sliding-window", read: true, anchor: "shape-2-longest-valid" });
  assert.deepEqual(parse("#/browse?list=ox3f&topics=a,b&q=two%20sum&page=2"),
    { view: "browse", query: { list: "ox3f", topics: "a,b", q: "two sum", page: "2" } });
});

test("router: build round-trips", () => {
  for (const h of ["#/today", "#/learn", "#/learn/two-pointers", "#/learn/two-pointers/shape-2a",
    "#/learn/two-pointers/read", "#/learn/two-pointers/read/2a-read-and-write",
    "#/browse?list=hot100&diff=Medium&page=3", "#/drill", "#/stats", "#/settings"]) {
    assert.equal(build(parse(h)), h, h);
  }
  assert.equal(build("stats"), "#/stats");
  assert.equal(build({ view: "bogus" }), "#/today");
  assert.equal(build({ view: "browse", query: { q: "", page: null, cap: false, topics: ["a", "b"] } }), "#/browse?topics=a%2Cb");
});

test("router: query helpers", () => {
  assert.deepEqual(parseQuery("?a=1&b=x+y&c"), { a: "1", b: "x y", c: "" });
  assert.equal(encodeQuery({}), "");
  assert.equal(encodeQuery({ q: "a&b" }), "?q=a%26b");
});

test("router: onChange fires with route and previous", () => {
  _resetForTests();
  const seen = [];
  onChange((r, prev) => seen.push([r.view, prev && prev.view]));
  _handleForTests("#/drill");
  _handleForTests("#/stats");
  assert.deepEqual(seen, [["drill", null], ["stats", "drill"]]);
  _resetForTests();
});
