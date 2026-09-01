/* heatmap.js — a year of review activity as a GitHub-style grid, plus streaks.
 *
 * `buildGrid(days, endDate)` is pure: columns are weeks (Monday-first), rows are
 * weekdays, and each cell carries its date, count and a 0–4 level (0 · 1 ·
 * 2–3 · 4–6 · 7+). `streaks(days, today)` follows the "yesterday-anchored"
 * rule: a streak is not broken by a day that is still in progress, so at 9 am
 * with nothing solved yet you still see "12 days — keep it going today".
 *
 * `days` is `/api/activity`'s `days` map: {date: {solved: n, solved_help: n,
 * forgotten: n}} — or {date: number}. All arithmetic is UTC on date strings.
 */

import { html, raw } from "./h.js";

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

export function toUTC(dateStr) {
  const [y, m, d] = String(dateStr).split("-").map(Number);
  return Date.UTC(y, m - 1, d);
}

export function fromUTC(ms) {
  const d = new Date(ms);
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getUTCFullYear()}-${p(d.getUTCMonth() + 1)}-${p(d.getUTCDate())}`;
}

export function addDays(dateStr, n) { return fromUTC(toUTC(dateStr) + n * 86400000); }

/** Monday = 0 … Sunday = 6. */
export function weekday(dateStr) { return (new Date(toUTC(dateStr)).getUTCDay() + 6) % 7; }

export function countOf(v) {
  if (v == null) return 0;
  if (typeof v === "number") return v;
  return Object.values(v).reduce((n, x) => n + (Number(x) || 0), 0);
}

export function level(count) {
  if (count <= 0) return 0;
  if (count === 1) return 1;
  if (count <= 3) return 2;
  if (count <= 6) return 3;
  return 4;
}

/** buildGrid(days, "2026-09-01", 52) → {columns:[{cells:[{date,count,level,future}]}], months:[{col,label}], start, end, weekdays}. */
export function buildGrid(days, endDate, weeks = 52) {
  days = days || {};
  const endDow = weekday(endDate);
  const start = addDays(endDate, -endDow - (weeks - 1) * 7);
  const endMs = toUTC(endDate);
  const columns = [];
  const months = [];
  let lastMonth = -1;
  for (let w = 0; w < weeks; w++) {
    const cells = [];
    const monday = addDays(start, w * 7);
    const month = new Date(toUTC(monday)).getUTCMonth();
    // Label a column when it is the first column whose Monday falls in a new month.
    if (month !== lastMonth) {
      if (w === 0 || lastMonth !== -1) months.push({ col: w, label: MONTHS[month] });
      lastMonth = month;
    }
    for (let r = 0; r < 7; r++) {
      const date = addDays(monday, r);
      const future = toUTC(date) > endMs;
      const count = future ? 0 : countOf(days[date]);
      cells.push({ date, count, level: future ? 0 : level(count), future, detail: future ? null : days[date] || null });
    }
    columns.push({ cells, monday });
  }
  // Drop a leading label that would collide with the next one (< 3 columns apart).
  if (months.length > 1 && months[1].col - months[0].col < 3) months.shift();
  return { columns, months, start, end: endDate, weekdays: WEEKDAYS };
}

/** Streak stats: {current, longest, activeDays, thisMonth, anchoredYesterday}. */
export function streaks(days, today) {
  days = days || {};
  const active = new Set(Object.keys(days).filter((d) => countOf(days[d]) > 0));
  const sorted = [...active].sort();
  let longest = 0, run = 0, prev = null;
  for (const d of sorted) {
    run = prev && addDays(prev, 1) === d ? run + 1 : 1;
    if (run > longest) longest = run;
    prev = d;
  }
  let anchor = today;
  let anchoredYesterday = false;
  if (!active.has(today)) {
    anchor = addDays(today, -1);
    anchoredYesterday = active.has(anchor);
  }
  let current = 0;
  while (active.has(anchor)) { current++; anchor = addDays(anchor, -1); }
  const month = today.slice(0, 7);
  let thisMonth = 0;
  for (const d of Object.keys(days)) if (d.startsWith(month)) thisMonth += countOf(days[d]);
  return { current, longest, activeDays: active.size, thisMonth, anchoredYesterday: current > 0 && anchoredYesterday };
}

function tooltip(cell) {
  const d = new Date(toUTC(cell.date));
  const when = `${WEEKDAYS[weekday(cell.date)]} ${d.getUTCDate()} ${MONTHS[d.getUTCMonth()]}`;
  if (!cell.count) return `${when} · no reviews`;
  const parts = [];
  if (cell.detail && typeof cell.detail === "object") {
    const names = { solved: "solved", solved_help: "with help", forgotten: "forgot" };
    for (const k of Object.keys(names)) if (cell.detail[k]) parts.push(`${cell.detail[k]} ${names[k]}`);
  }
  return `${when} · ${cell.count} review${cell.count === 1 ? "" : "s"}${parts.length ? " · " + parts.join(", ") : ""}`;
}

/** HTML for a grid: month labels row + the cell grid (CSS lays out columns). */
export function renderHeatmap(grid) {
  const cols = grid.columns.length;
  const labels = grid.months.map((m) => html`<span class="hm__month" style="grid-column:${m.col + 1}">${m.label}</span>`);
  const cells = [];
  for (const col of grid.columns) {
    for (const c of col.cells) {
      if (c.future) { cells.push(html`<i class="hm__cell hm__cell--future" aria-hidden="true"></i>`); continue; }
      cells.push(html`<i class="hm__cell h${c.level}" data-date="${c.date}" data-count="${c.count}" title="${tooltip(c)}" tabindex="0" role="img" aria-label="${tooltip(c)}"></i>`);
    }
  }
  return html`
    <div class="hm" style="--hm-cols:${cols}">
      <div class="hm__months" style="grid-template-columns:repeat(${cols},1fr)">${labels}</div>
      <div class="hm__days" aria-hidden="true"><span>Mon</span><span>Wed</span><span>Fri</span></div>
      <div class="hm__grid" style="grid-template-columns:repeat(${cols},auto)">${cells}</div>
    </div>`;
}

export { raw as _raw };
