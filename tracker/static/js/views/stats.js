/* stats.js — where you stand: four tiles, a year of activity, per-list
 * coverage, and the complexity cheat-sheet.
 *
 * Activity comes from /api/activity (derived from the event log with undo
 * applied) and is fetched lazily the first time this view opens, then
 * refreshed after every mark. */
import { html, render, raw } from "../h.js";
import { buildGrid, streaks, renderHeatmap } from "../heatmap.js";
import { fmtInt, plural } from "../format.js";

const CHEAT = [
  ["n ≤ 10", "O(n!) / O(Cⁿ)", "backtracking, brute force"],
  ["n ≤ 20", "O(2ⁿ)", "bitmask DP"],
  ["n ≤ 40", raw("O(2<sup>n/2</sup>)"), "meet in the middle"],
  ["n ≤ 100", "O(n³)", "triple-loop DP, Floyd–Warshall"],
  ["n ≤ 1 000", "O(n²)", "double-loop DP, knapsack"],
  ["n ≤ 100 000", "O(n log n)", "most problems: sorting, heaps, binary search"],
  ["n ≤ 1 000 000", "O(n)", "linear DP, sliding window"],
  ["n ≤ 10⁹", "O(√n)", "primality testing"],
  ["n ≤ 10¹⁸", "O(log n) / O(1)", "binary search on the answer, fast power, math"],
];

let activityVersion = -1;
let loading = false;

async function loadActivity(ctx) {
  const s = ctx.store.get();
  if (loading || activityVersion === s.progressVersion) return;
  loading = true;
  try {
    const a = await ctx.api.getActivity();
    activityVersion = s.progressVersion;
    ctx.store.set({ activity: a });
    ctx.store.bump("activityVersion");
  } catch (_) { /* the heatmap just shows empty */ } finally { loading = false; }
}

export function coverage(s, store, cap) {
  const lists = [
    ["Hot 100", (p) => p.lists.hot100],
    ["Top Interview 150", (p) => p.lists.interview150],
    ["NeetCode 250", (p) => p.lists.neetcode250],
    ["Tutorials", (p) => p.lists.tutorial && p.lists.tutorial.length],
  ];
  const topics = [...new Set(s.rows.flatMap(([, p]) => (p.lists.ox3f || []).filter((m) => m.tier === "interview").map((m) => m.topic)))];
  for (const t of topics) lists.push([`0x3F · ${t}`, (p) => (p.lists.ox3f || []).some((m) => m.topic === t && m.tier === "interview")]);
  return lists.map(([name, pred]) => {
    const subset = s.rows.filter(([, p]) => pred(p));
    const started = subset.filter(([slug]) => s.progress[slug]).length;
    const mastered = subset.filter(([slug]) => store.dstatus(slug, s) === "mastered").length;
    const inCap = cap != null ? subset.filter(([, p]) => !p.rating || p.rating <= cap) : subset;
    const startedCap = inCap.filter(([slug]) => s.progress[slug]).length;
    const pct = inCap.length ? Math.round((100 * startedCap) / inCap.length) : 0;
    return { name, total: subset.length, started, mastered, inCap: inCap.length, startedCap, pct };
  });
}

export default {
  id: "stats",
  title: "Stats",
  routes: ["stats"],
  deps: ["progressVersion", "settingsVersion", "dateVersion", "activityVersion"],

  mount(el) {
    // Custom tooltip for heatmap cells (title= is slow to appear and unstyled).
    let tip = null;
    el.addEventListener("mouseover", (ev) => {
      const c = ev.target.closest(".hm__cell[data-date]");
      if (!c) { if (tip) { tip.remove(); tip = null; } return; }
      if (!tip) { tip = document.createElement("div"); tip.className = "tipbox"; el.querySelector(".hm-wrap").appendChild(tip); }
      tip.textContent = c.getAttribute("aria-label") || "";
      const wrap = el.querySelector(".hm-wrap").getBoundingClientRect();
      const r = c.getBoundingClientRect();
      tip.style.left = `${r.left - wrap.left + 8}px`;
      tip.style.top = `${r.top - wrap.top - 34}px`;
    });
    el.addEventListener("mouseleave", () => { if (tip) { tip.remove(); tip = null; } }, true);
  },

  render(el, ctx) {
    const s = ctx.store.get();
    loadActivity(ctx);
    const counts = { new: 0, solved: 0, due: 0, forgotten: 0, mastered: 0 };
    for (const [slug] of s.rows) counts[ctx.store.dstatus(slug, s)]++;
    const cap = ctx.store.cap(s);
    const cov = coverage(s, ctx.store, cap);
    const days = (s.activity && s.activity.days) || {};
    const grid = buildGrid(days, s.today, 52);
    const st = streaks(days, s.today);

    render(el, html`<div class="view">
      <div class="tiles">
        <div class="card tile"><div class="k"><i style="background:var(--st-due)"></i>Due now</div><div class="v">${fmtInt(counts.due + counts.forgotten)}</div></div>
        <div class="card tile"><div class="k"><i style="background:var(--st-sched)"></i>Scheduled</div><div class="v">${fmtInt(counts.solved)}</div></div>
        <div class="card tile"><div class="k"><i style="background:var(--st-master)"></i>Mastered</div><div class="v">${fmtInt(counts.mastered)}</div></div>
        <div class="card tile"><div class="k"><i style="background:var(--st-new)"></i>Untouched</div><div class="v">${fmtInt(counts.new)}</div></div>
      </div>
      <div class="card">
        <div class="hd">Activity <span class="meta">last 52 weeks</span></div>
        <div class="bd heat">
          <div class="hm-wrap">
            ${renderHeatmap(grid)}
            <div class="legend">Less <i></i><i class="h1"></i><i class="h2"></i><i class="h3"></i><i class="h4"></i> More</div>
          </div>
          <div class="streak">
            <div><div class="k">Current streak</div><div class="v">${st.current}<small>${st.current === 1 ? "day" : "days"}${st.anchoredYesterday ? " · keep it going today" : ""}</small></div></div>
            <div><div class="k">Longest</div><div class="v">${st.longest}<small>${st.longest === 1 ? "day" : "days"}</small></div></div>
            <div><div class="k">This month</div><div class="v">${st.thisMonth}<small>${st.thisMonth === 1 ? "review" : "reviews"}</small></div></div>
            <div><div class="k">Active days</div><div class="v">${st.activeDays}<small>of 365</small></div></div>
          </div>
        </div>
      </div>
      <div class="card"><div class="table-wrap"><table class="tbl compact">
        <thead><tr><th>List</th><th class="right">Problems</th><th class="right">Started</th><th class="right">Mastered</th><th>Coverage${cap != null ? html` <span class="muted">≤ ${cap}</span>` : ""}</th></tr></thead>
        <tbody>${cov.map((r) => html`<tr><td>${r.name}</td><td class="num right">${fmtInt(r.total)}</td><td class="num right">${fmtInt(r.started)}</td><td class="num right">${fmtInt(r.mastered)}</td>
          <td><span class="barcell"><span class="pbar"><i style="width:${r.pct}%"></i></span><span class="sub num">${r.pct}%${cap != null && r.inCap !== r.total ? html` <span class="muted">· ${r.startedCap}/${r.inCap}</span>` : ""}</span></span></td></tr>`)}</tbody>
      </table></div></div>
      <details class="card">
        <summary class="hd" style="cursor:pointer">Data range → expected complexity <span class="meta">from 0x3F's guide · ~10⁸ simple operations per second, ÷10 for Python</span></summary>
        <div class="table-wrap"><table class="tbl compact">
          <thead><tr><th>Data range</th><th>Allowed complexity</th><th>Typical algorithms</th></tr></thead>
          <tbody>${CHEAT.map(([n, t, a]) => html`<tr><td class="num">${n}</td><td>${t}</td><td>${a}</td></tr>`)}</tbody>
        </table></div>
      </details>
    </div>`);
  },

  unmount() {},
};
