/* drill.js — type-blind random practice.
 *
 * idle → hidden → revealed. A drawn problem shows only its number and title;
 * you decide the approach first, then mark it (which reveals) or press Reveal.
 * The pool is Route.drillPool: untouched, non-paid problems in the rating
 * range, narrowed by source lists and 0x3F types. The last ten draws are
 * remembered so the same problem does not come straight back. */
import { html, render, raw } from "../h.js";
import { icon, levelHtml, badgesHtml, chipHtml, lcUrl } from "../components/status.js";
import { fmtInt } from "../format.js";

const POOLS = [["hot100", "Hot 100"], ["interview150", "Interview 150"], ["neetcode250", "NeetCode 250"], ["ox3f", "0x3F"]];
const RANGE = { min: 1000, max: 3000, step: 50 };
const DEFAULT_LO = 1300, DEFAULT_HI = 1800;
const RECENT = 10;

const drill = { slug: null, phase: "idle", recent: [] };
let allTopics = [];

/** Pick a random row not in `recent` (unless the pool is too small). Exported for tests. */
export function pick(pool, recent, rand = Math.random) {
  if (!pool.length) return null;
  const avoid = new Set(recent);
  let cands = pool.filter(([slug]) => !avoid.has(slug));
  if (!cands.length) cands = pool.filter(([slug]) => slug !== recent[recent.length - 1]);
  if (!cands.length) cands = pool;
  return cands[Math.floor(rand() * cands.length)];
}

function prefs(ctx) {
  const s = ctx.store.get().settings;
  const lo = s.drillLo || DEFAULT_LO, hi = s.drillHi || DEFAULT_HI;
  const pools = new Set(s.drillPools && s.drillPools.length ? s.drillPools : POOLS.map((p) => p[0]));
  const topics = s.drillTopics == null ? null : new Set(s.drillTopics);
  return { lo, hi, pools, topics };
}

function pool(ctx) {
  const s = ctx.store.get();
  const { lo, hi, pools, topics } = prefs(ctx);
  const allPools = pools.size === POOLS.length ? null : pools;
  return window.Route.drillPool(s.rows, (slug) => ctx.store.isNew(slug, s), lo, hi, topics, allPools);
}

function draw(ctx) {
  const row = pick(pool(ctx), drill.recent);
  if (!row) { drill.slug = null; drill.phase = "idle"; drill.empty = true; }
  else {
    drill.slug = row[0]; drill.phase = "hidden"; drill.empty = false;
    drill.recent.push(row[0]); if (drill.recent.length > RECENT) drill.recent.shift();
  }
  rerender(ctx);
}

function reveal(ctx) { if (drill.phase === "hidden") { drill.phase = "revealed"; rerender(ctx); } }

async function markCurrent(ctx, action) {
  if (!drill.slug) return;
  const entry = await ctx.mark(drill.slug, action);
  if (entry !== null) { drill.phase = "revealed"; rerender(ctx); }
}

function rerender(ctx) {
  const el = document.getElementById("view-drill");
  if (el && !el.hidden) { view.render(el, ctx, ctx.route); }
}

const view = {
  id: "drill",
  title: "Drill",
  routes: ["drill"],
  deps: ["progressVersion", "settingsVersion"],

  actions: {},

  mount(el, ctx) {
    this.actions = {
      draw: () => draw(ctx), reveal: () => reveal(ctx), skip: () => draw(ctx),
      solved: () => markCurrent(ctx, "solved"), solved_help: () => markCurrent(ctx, "solved_help"), forgotten: () => markCurrent(ctx, "forgotten"),
    };
    el.addEventListener("click", (ev) => {
      const t = ev.target.closest("[data-drill]");
      if (!t) return;
      const what = t.dataset.drill;
      if (what === "draw" || what === "skip") draw(ctx);
      else if (what === "reveal") reveal(ctx);
      else if (what === "pool") {
        const { pools } = prefs(ctx);
        const k = t.dataset.v;
        if (pools.has(k)) { if (pools.size > 1) pools.delete(k); } else pools.add(k);
        ctx.settings.set({ drillPools: [...pools] });
      } else if (what === "topics-toggle") toggleTopics(el, ctx);
      else if (what === "topics-all") ctx.settings.set({ drillTopics: null });
      else if (what === "topics-none") ctx.settings.set({ drillTopics: [] });
      else if (what === "widen") { const { hi } = prefs(ctx); ctx.settings.set({ drillHi: Math.min(RANGE.max, hi + 200) }); }
    });
    el.addEventListener("input", (ev) => {
      const t = ev.target;
      if (t.matches("[data-range]")) syncRange(el, t);
    });
    el.addEventListener("change", (ev) => {
      const t = ev.target;
      if (t.matches("[data-range]")) {
        const lo = Number(el.querySelector("[data-range='lo']").value), hi = Number(el.querySelector("[data-range='hi']").value);
        ctx.settings.set({ drillLo: Math.min(lo, hi), drillHi: Math.max(lo, hi) });
      }
      if (t.matches("input[data-topic]")) {
        const { topics } = prefs(ctx);
        const set = new Set(topics == null ? allTopics : topics);
        if (t.checked) set.add(t.dataset.topic); else set.delete(t.dataset.topic);
        ctx.settings.set({ drillTopics: set.size === allTopics.length ? null : [...set] });
      }
    });
    ctx.keys.register("drill", " ", () => (drill.phase === "hidden" ? reveal(ctx) : draw(ctx)), { label: "Draw (or reveal)" });
    ctx.keys.register("drill", "d", () => draw(ctx), { label: "Draw a problem" });
    ctx.keys.register("drill", "n", () => draw(ctx), { label: "" });
    ctx.keys.register("drill", "arrowright", () => draw(ctx), { label: "" });
    ctx.keys.register("drill", "r", () => reveal(ctx), { label: "Reveal the type" });
    ctx.keys.register("drill", "s", () => markCurrent(ctx, "solved"), { label: "Mark solved" });
    ctx.keys.register("drill", "h", () => markCurrent(ctx, "solved_help"), { label: "Mark solved with help" });
    ctx.keys.register("drill", "f", () => markCurrent(ctx, "forgotten"), { label: "Mark forgot" });
    ctx.keys.register("drill", "backspace", () => draw(ctx), { label: "Skip" });
  },

  toolbar(ctx) {
    const n = pool(ctx).length;
    return html`<h1>Drill</h1><span class="sub num">${fmtInt(n)} untouched ${n === 1 ? "problem matches" : "problems match"}</span>`;
  },

  render(el, ctx) {
    const s = ctx.store.get();
    if (!allTopics.length) {
      const set = new Set();
      for (const [, p] of s.rows) for (const m of p.lists.ox3f || []) if (m.tier === "interview") set.add(m.topic);
      allTopics = [...set].sort();
    }
    const { lo, hi, pools, topics } = prefs(ctx);
    const pct = (v) => ((v - RANGE.min) / (RANGE.max - RANGE.min) * 100).toFixed(1);
    const typesLabel = topics == null ? `All ${allTopics.length} types` : topics.size === 0 ? "No types" : `${topics.size} of ${allTopics.length} types`;
    const p = drill.slug ? s.problems[drill.slug] : null;
    const kbd = (k) => html`<kbd>${k}</kbd>`;

    let card;
    if (!p) {
      card = html`<div class="card drillcard"><div class="empty">
        ${drill.empty
          ? html`<div>No untouched problems match.</div><div class="sub">Widen the rating range, or select more lists and types.</div><button type="button" class="btn" data-drill="widen">Widen range by 200</button>`
          : html`<div>Draw a problem, decide the approach, then mark it.</div><div class="sub">Its type stays hidden until you do.</div><button type="button" class="btn primary" data-drill="draw">Draw a problem ${kbd("space")}</button>`}
      </div></div>`;
    } else if (drill.phase === "hidden") {
      card = html`<div class="card drillcard">
        <div class="prob"><div class="t"><a href="${lcUrl(drill.slug)}" target="_blank" rel="noopener">${p.id}. ${p.title}</a>${icon("ext")}</div></div>
        <div class="meta"><span class="hidden-tag">${icon("eye-off")}Type hidden</span><span>Decide the approach first, then mark it.</span></div>
        <div class="actions">
          <button type="button" class="btn" data-drill="mark" data-act="mark" data-action="solved" data-slug="${drill.slug}">Solved ${kbd("s")}</button>
          <button type="button" class="btn help" data-act="mark" data-action="solved_help" data-slug="${drill.slug}">With help ${kbd("h")}</button>
          <button type="button" class="btn forgot" data-act="mark" data-action="forgotten" data-slug="${drill.slug}">Forgot ${kbd("f")}</button>
          <button type="button" class="btn ghost" data-drill="reveal">Reveal ${kbd("r")}</button>
          <button type="button" class="btn ghost" data-drill="skip">Skip ${kbd("⌫")}</button>
        </div>
      </div>`;
    } else {
      const secs = (p.lists.ox3f || []).filter((m) => m.tier === "interview");
      card = html`<div class="card drillcard">
        <div class="prob"><div class="t"><a href="${lcUrl(drill.slug)}" target="_blank" rel="noopener">${p.id}. ${p.title}</a>${icon("ext")}</div></div>
        <div class="meta">${levelHtml(p)}${badgesHtml(p)}${chipHtml(drill.slug, s)}</div>
        ${secs.length
          ? html`<ul class="types">${secs.map((m) => html`<li>${m.topic} — ${m.section}</li>`)}</ul>`
          : html`<div class="types">Not in the 0x3F lists.</div>`}
        <div class="actions">
          ${ctx.store.isNew(drill.slug, s) ? html`<button type="button" class="btn" data-act="mark" data-action="solved" data-slug="${drill.slug}">Solved ${kbd("s")}</button>
          <button type="button" class="btn help" data-act="mark" data-action="solved_help" data-slug="${drill.slug}">With help ${kbd("h")}</button>
          <button type="button" class="btn forgot" data-act="mark" data-action="forgotten" data-slug="${drill.slug}">Forgot ${kbd("f")}</button>` : ""}
          <button type="button" class="btn primary" data-drill="draw">Draw next ${kbd("space")}</button>
        </div>
      </div>`;
    }

    render(el, html`<div class="view wide"><div class="drillgrid">
      <div class="card"><div class="bd" style="display:flex;flex-direction:column;gap:18px">
        <div class="ctl"><span class="lbl">Rating range</span>
          <div class="range" data-range-wrap>
            <div class="track"></div><div class="fill" style="left:${pct(lo)}%;right:${(100 - pct(hi)).toFixed(1)}%"></div>
            <input type="range" data-range="lo" min="${RANGE.min}" max="${RANGE.max}" step="${RANGE.step}" value="${lo}" aria-label="Minimum rating">
            <input type="range" data-range="hi" min="${RANGE.min}" max="${RANGE.max}" step="${RANGE.step}" value="${hi}" aria-label="Maximum rating">
          </div>
          <div style="display:flex;gap:8px;align-items:center"><span class="numin" data-range-out="lo">${lo}</span><span class="sub">to</span><span class="numin" data-range-out="hi">${hi}</span></div>
        </div>
        <div class="ctl"><span class="lbl">Draw from</span>
          <div class="chips">${POOLS.map(([k, l]) => html`<button type="button" class="schip sm" data-drill="pool" data-v="${k}" aria-pressed="${pools.has(k)}">${l}</button>`)}</div>
        </div>
        <div class="ctl" style="position:relative"><span class="lbl">Types</span><button type="button" class="select" data-drill="topics-toggle" style="align-self:flex-start">${typesLabel}</button></div>
        <button type="button" class="btn primary" data-drill="draw" style="height:32px">${p ? "Draw another" : "Draw a problem"} ${kbd("space")}</button>
      </div></div>
      ${card}
    </div></div>`);
  },

  unmount() {},
};

function syncRange(el, input) {
  const lo = el.querySelector("[data-range='lo']"), hi = el.querySelector("[data-range='hi']");
  let a = Number(lo.value), b = Number(hi.value);
  if (a > b) { if (input === lo) { hi.value = a; b = a; } else { lo.value = b; a = b; } }
  const pct = (v) => ((v - RANGE.min) / (RANGE.max - RANGE.min) * 100).toFixed(1);
  const fill = el.querySelector(".range .fill");
  if (fill) { fill.style.left = `${pct(a)}%`; fill.style.right = `${(100 - pct(b)).toFixed(1)}%`; }
  el.querySelector("[data-range-out='lo']").textContent = String(a);
  el.querySelector("[data-range-out='hi']").textContent = String(b);
}

function toggleTopics(el, ctx) {
  const existing = el.querySelector(".popover[data-open]");
  if (existing) { existing.remove(); return; }
  const { topics } = prefs(ctx);
  const sel = topics == null ? new Set(allTopics) : topics;
  const anchor = el.querySelector("[data-drill='topics-toggle']");
  const pop = document.createElement("div");
  pop.className = "popover"; pop.dataset.open = "1"; pop.setAttribute("role", "dialog");
  pop.style.top = `${anchor.offsetTop + anchor.offsetHeight + 6}px`; pop.style.left = "0";
  render(pop, html`<div class="row"><button type="button" class="btn sm" data-drill="topics-all">All</button><button type="button" class="btn sm" data-drill="topics-none">None</button></div>
    ${allTopics.map((t) => html`<label><input type="checkbox" data-topic="${t}"${sel.has(t) ? raw(" checked") : ""}> ${t}</label>`)}`);
  anchor.parentElement.appendChild(pop);
  const close = (ev) => { if (!pop.contains(ev.target) && ev.target !== anchor) { pop.remove(); document.removeEventListener("mousedown", close); } };
  setTimeout(() => document.addEventListener("mousedown", close), 0);
}

export default view;
