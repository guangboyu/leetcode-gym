import { test, assert } from "./harness.mjs";
import { get, set, bump, subscribe, flushNow, memo, loadProblems, dstatus, isDone, isNew, cap, todayStr, refreshToday } from "../../tracker/static/js/store.js";

test("store: set batches and notifies by deps", async () => {
  const calls = [];
  const off1 = subscribe(() => calls.push("any"));
  const off2 = subscribe((s, changed) => calls.push("progress:" + [...changed].join(",")), ["progressVersion"]);
  const off3 = subscribe(() => calls.push("settings"), ["settingsVersion"]);
  set({ progress: { "two-sum": { status: "solved", due: "2026-09-05" } } });
  bump("progressVersion");
  await Promise.resolve();
  await Promise.resolve();
  assert.deepEqual(calls, ["any", "progress:progress,progressVersion"], "one flush for two sets; settings sub untouched");
  off1(); off2(); off3();
});

test("store: derived status uses today", async () => {
  set({ today: "2026-09-01", progress: {
    a: { status: "solved", due: "2026-09-05" },
    b: { status: "solved", due: "2026-09-01" },
    c: { status: "forgotten", due: "2026-08-30" },
    d: { status: "mastered", due: null },
  } });
  flushNow();
  assert.equal(dstatus("a"), "solved");
  assert.equal(dstatus("b"), "due");
  assert.equal(dstatus("c"), "forgotten");
  assert.equal(dstatus("d"), "mastered");
  assert.equal(dstatus("zzz"), "new");
  assert.equal(isDone("a") && isDone("d") && !isDone("c") && !isDone("zzz"), true);
  assert.equal(isNew("zzz") && !isNew("a"), true);
});

test("store: cap and clock", () => {
  set({ settings: { cap: 1700 } }); flushNow();
  assert.equal(cap(), 1700);
  set({ settings: { cap: "none" } }); flushNow();
  assert.equal(cap(), null);
  set({ settings: {} }); flushNow();
  assert.equal(cap(), null);
  assert.equal(todayStr(new Date(2026, 8, 1, 23, 59)), "2026-09-01", "local date, not UTC");
  set({ today: "2026-08-31" }); flushNow();
  const before = get().dateVersion;
  assert.equal(refreshToday(new Date(2026, 8, 1)), true);
  flushNow();
  assert.equal(get().today, "2026-09-01");
  assert.equal(refreshToday(new Date(2026, 8, 1, 12)), false, "same day: no bump");
  assert.equal(refreshToday(new Date(2026, 8, 2)), true);
  flushNow();
  assert.equal(get().dateVersion, before + 2);
});

test("store: loadProblems sorts rows and indexes ids; memo recomputes on key change", () => {
  loadProblems({ b: { id: 2 }, a: { id: 1 } });
  flushNow();
  assert.deepEqual(get().rows.map((r) => r[0]), ["a", "b"]);
  assert.equal(get().byId.get(2), "b");
  let n = 0;
  const f = memo((x) => x % 2, (x) => { n++; return x * 10; });
  assert.equal(f(1), 10); assert.equal(f(3), 10); assert.equal(f(4), 40); assert.equal(f(6), 40);
  assert.equal(n, 2);
});
