import { test, assert } from "./harness.mjs";
import { buildGrid, streaks, level, weekday, addDays, renderHeatmap } from "../../tracker/static/js/heatmap.js";

test("heatmap: date helpers", () => {
  assert.equal(weekday("2026-09-01"), 1, "2026-09-01 is a Tuesday");
  assert.equal(weekday("2026-08-31"), 0, "Monday");
  assert.equal(weekday("2026-09-06"), 6, "Sunday");
  assert.equal(addDays("2026-08-31", 1), "2026-09-01");
  assert.equal(addDays("2026-01-01", -1), "2025-12-31");
});

test("heatmap: levels", () => {
  assert.deepEqual([0, 1, 2, 3, 4, 6, 7, 20].map(level), [0, 1, 2, 2, 3, 3, 4, 4]);
});

test("heatmap: grid ends on today, columns are Monday-first weeks", () => {
  const g = buildGrid({ "2026-09-01": { solved: 2, solved_help: 1 }, "2026-08-31": 1 }, "2026-09-01", 52);
  assert.equal(g.columns.length, 52);
  const last = g.columns[51].cells;
  assert.equal(last[0].date, "2026-08-31", "last column starts on the Monday of this week");
  assert.equal(last[1].date, "2026-09-01");
  assert.equal(last[1].count, 3);
  assert.equal(last[1].level, 2);
  assert.equal(last[0].level, 1);
  assert.ok(last[2].future && last[6].future, "days after today are future");
  assert.equal(g.columns[0].cells[0].date, addDays("2026-08-31", -51 * 7), "52 weeks back");
  assert.ok(g.months.length >= 11 && g.months.length <= 13, `month labels: ${g.months.length}`);
  assert.ok(g.months.every((m, i) => i === 0 || m.col > g.months[i - 1].col));
});

test("heatmap: streaks — today active", () => {
  const days = { "2026-08-30": 1, "2026-08-31": 2, "2026-09-01": 1, "2026-08-20": 1, "2026-08-21": 1, "2026-08-22": 1, "2026-08-23": 1 };
  const s = streaks(days, "2026-09-01");
  assert.equal(s.current, 3);
  assert.equal(s.longest, 4);
  assert.equal(s.activeDays, 7);
  assert.equal(s.thisMonth, 1);
  assert.equal(s.anchoredYesterday, false);
});

test("heatmap: streaks — today empty anchors on yesterday", () => {
  const days = { "2026-08-30": 1, "2026-08-31": 2 };
  const s = streaks(days, "2026-09-01");
  assert.equal(s.current, 2);
  assert.equal(s.anchoredYesterday, true);
  const gap = streaks({ "2026-08-29": 1 }, "2026-09-01");
  assert.equal(gap.current, 0, "a two-day gap breaks the streak");
  assert.equal(gap.anchoredYesterday, false);
  assert.deepEqual(streaks({}, "2026-09-01"), { current: 0, longest: 0, activeDays: 0, thisMonth: 0, anchoredYesterday: false });
});

test("heatmap: renderHeatmap emits one cell per day with data attrs", () => {
  const g = buildGrid({ "2026-09-01": { solved: 4 } }, "2026-09-01", 2);
  const out = String(renderHeatmap(g));
  assert.match(out, /class="hm__cell h3" data-date="2026-09-01" data-count="4" title="Tue 1 Sep · 4 reviews · 4 solved"/);
  assert.equal((out.match(/<i /g) || []).length, 14);
  assert.equal((out.match(/hm__cell--future/g) || []).length, 5);
});
