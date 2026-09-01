/* browse.js — every problem, filterable and sortable.
 *
 * Filters live in the hash (#/browse?list=ox3f&topics=a,b&diff=Medium&status=due
 * &q=window&sort=rating&dir=desc&page=2&cap=1&comp=1) so reload and ⌘[ restore
 * them. The predicate reads a parsed filter object — never the DOM — and the
 * per-problem topic set is precomputed once, so typing in the search box
 * costs one pass over 2,676 rows and nothing else. */
import { html, render, raw } from "../h.js";
import { tableHtml, attachCursor } from "../components/problem-table.js";
import { icon } from "../components/status.js";
import { fmtInt } from "../format.js";

const PAGE = 100;
const LISTS = [["", "All"], ["hot100", "Hot 100"], ["interview150", "Interview 150"], ["neetcode250", "NeetCode 250"], ["ox3f", "0x3F"]];
const STATUSES = [["", "Any status"], ["new", "New"], ["solved", "Scheduled"], ["due", "Due"], ["forgotten", "Forgot"], ["mastered", "Mastered"]];
const DIFFS = [["", "Any difficulty"], ["Easy", "Easy"], ["Medium", "Medium"], ["Hard", "Hard"]];

let topicsOf = null;   // Map slug -> Set(topic) (interview tier)
let allTopics = [];
let cursor = null;
let searchTimer = null;

/** Parsed filters from a route query. Exported for tests. */
export function filtersFrom(query) {
  const q = query || {};
  return {
    list: q.list || "",
    topics: q.topics ? q.topics.split(",").filter(Boolean) : [],
    diff: q.diff || "",
    status: q.status || "",
    q: q.q || "",
    sort: q.sort || "id",
    dir: q.dir === "desc" ? "desc" : "asc",
    page: Math.max(0, Number(q.page || 0) || 0),
    cap: q.cap === "1",
    comp: q.comp === "1",
  };
}

export function toQuery(f) {
  return {
    list: f.list, topics: f.topics.length ? f.topics.join(",") : "", diff: f.diff, status: f.status, q: f.q,
    sort: f.sort === "id" ? "" : f.sort, dir: f.dir === "desc" ? "desc" : "", page: f.page || "",
    cap: f.cap ? "1" : "", comp: f.comp ? "1" : "",
  };
}

function ensureIndex(s) {
  if (topicsOf && topicsOf.size === s.rows.length) return;
  topicsOf = new Map();
  const set = new Set();
  for (const [slug, p] of s.rows) {
    const t = new Set();
    for (const m of p.lists.ox3f || []) if (m.tier === "interview") { t.add(m.topic); set.add(m.topic); }
    topicsOf.set(slug, t);
  }
  allTopics = [...set].sort();
}

/** The row predicate, pure given (filters, store, cap). Exported for tests. */
export function matches(f, slug, p, st, cap, topics) {
  if (f.list) {
    if (f.list === "ox3f") {
      const ms = (p.lists.ox3f || []).filter((m) => f.comp || m.tier === "interview");
      if (!ms.length) return false;
    } else if (!p.lists[f.list]) return false;
  }
  if (f.topics.length) {
    const t = topics || new Set();
    if (!f.topics.some((x) => t.has(x))) return false;
  }
  if (f.diff && p.difficulty !== f.diff) return false;
  if (f.status && st !== f.status) return false;
  if (f.cap && cap != null && p.rating && p.rating > cap) return false;
  if (f.q) {
    const q = f.q.trim().toLowerCase();
    if (q.startsWith("#")) { if (String(p.id) !== q.slice(1)) return false; }
    else if (/^\d+$/.test(q)) { if (String(p.id) !== q && !p.title.toLowerCase().includes(q)) return false; }
    else if (!p.title.toLowerCase().includes(q) && slug.indexOf(q) < 0) return false;
  }
  return true;
}

const STATUS_ORDER = { forgotten: 0, due: 1, solved: 2, new: 3, mastered: 4 };

export function comparator(f, s, store, effRating) {
  const dir = f.dir === "desc" ? -1 : 1;
  const by = {
    id: (a, b) => a[1].id - b[1].id,
    title: (a, b) => a[1].title.localeCompare(b[1].title),
    level: (a, b) => (effRating(a[1]) || 0) - (effRating(b[1]) || 0) || a[1].id - b[1].id,
    status: (a, b) => {
      const sa = store.dstatus(a[0], s), sb = store.dstatus(b[0], s);
      if (STATUS_ORDER[sa] !== STATUS_ORDER[sb]) return STATUS_ORDER[sa] - STATUS_ORDER[sb];
      const da = (s.progress[a[0]] || {}).due || "", db = (s.progress[b[0]] || {}).due || "";
      return da < db ? -1 : da > db ? 1 : a[1].id - b[1].id;
    },
  }[f.sort] || ((a, b) => a[1].id - b[1].id);
  return (a, b) => dir * by(a, b);
}

function update(ctx, patch) {
  const f = { ...filtersFrom(ctx.route.query), ...patch };
  if (!("page" in patch)) f.page = 0;
  ctx.navigate({ view: "browse", query: toQuery(f) }, { replace: true });
}

export default {
  id: "browse",
  title: "Browse",
  routes: ["browse"],
  deps: ["progressVersion", "settingsVersion", "dateVersion"],

  mount(el, ctx) {
    cursor = attachCursor(el, { onMark: (slug, action) => ctx.mark(slug, action) });
    el.addEventListener("click", (ev) => {
      const t = ev.target.closest("[data-f]");
      if (t) {
        const k = t.dataset.f, v = t.dataset.v;
        if (k === "topics-toggle") { toggleTopics(el, ctx); return; }
        if (k === "topics-all") { update(ctx, { topics: [] }); return; }
        if (k === "topics-none") { update(ctx, { topics: ["—"] }); return; }
        if (k === "cap" || k === "comp") { update(ctx, { [k]: t.getAttribute("aria-pressed") !== "true" }); return; }
        if (k === "page") { update(ctx, { page: Number(v) }); return; }
        update(ctx, { [k]: v });
        return;
      }
      const th = ev.target.closest("th[data-act='sort']");
      if (th) {
        const f = filtersFrom(ctx.route.query);
        const col = th.dataset.col;
        update(ctx, { sort: col, dir: f.sort === col && f.dir === "asc" ? "desc" : "asc", page: f.page });
      }
    });
    el.addEventListener("change", (ev) => {
      const t = ev.target;
      if (t.matches("select[data-f]")) update(ctx, { [t.dataset.f]: t.value });
      if (t.matches("input[data-topic]")) {
        const f = filtersFrom(ctx.route.query);
        const set = new Set(f.topics.filter((x) => x !== "—"));
        if (t.checked) set.add(t.dataset.topic); else set.delete(t.dataset.topic);
        update(ctx, { topics: [...set] });
      }
    });
    ctx.keys.register("browse", "/", () => { const f = document.getElementById("browse-search"); if (f) { f.focus(); f.select(); } }, { label: "Focus search" });
    ctx.keys.register("browse", "[", () => page(ctx, -1), { label: "Previous page" });
    ctx.keys.register("browse", "]", () => page(ctx, 1), { label: "Next page" });
    ctx.keys.register("browse", "j", () => {}, { label: "Move down (also ↓)" });
    ctx.keys.register("browse", "k", () => {}, { label: "Move up (also ↑)" });
    ctx.keys.register("browse", "enter", () => {}, { label: "Open on LeetCode" });
    ctx.keys.register("browse", "s", () => {}, { label: "Mark selected solved" });
    ctx.keys.register("browse", "h", () => {}, { label: "Mark selected solved with help" });
    ctx.keys.register("browse", "f", () => {}, { label: "Mark selected forgot" });
  },

  toolbar(ctx) {
    const f = filtersFrom(ctx.route.query);
    return html`<h1>Browse</h1><span class="grow"></span>
      <label class="field" style="width:280px">${icon("search")}<input id="browse-search" type="search" placeholder="Search title or #id" value="${f.q}" aria-label="Search problems" autocomplete="off"><kbd>${ctx.keys.display("mod+f")}</kbd></label>`;
  },

  render(el, ctx, route) {
    const s = ctx.store.get();
    ensureIndex(s);
    const f = filtersFrom(route.query);
    const cap = ctx.store.cap(s);
    const st = (slug) => ctx.store.dstatus(slug, s);
    const rows = s.rows.filter(([slug, p]) => matches(f, slug, p, st(slug), cap, topicsOf.get(slug)));
    rows.sort(comparator(f, s, ctx.store, ctx.effRating));
    const pages = Math.max(1, Math.ceil(rows.length / PAGE));
    const page = Math.min(f.page, pages - 1);
    const slice = rows.slice(page * PAGE, page * PAGE + PAGE);
    const topicsSel = f.topics.filter((x) => x !== "—");
    const topicLabel = f.topics.includes("—") ? "No topics" : topicsSel.length ? `Topics · ${topicsSel.length}` : "All topics";

    render(el, html`<div class="view wide">
      <div class="filters">
        <div class="segc" role="group" aria-label="List">${LISTS.map(([v, l]) => html`<button type="button" data-f="list" data-v="${v}" aria-pressed="${f.list === v}">${l}</button>`)}</div>
        <button type="button" class="select" data-f="topics-toggle" aria-haspopup="true">${topicLabel}</button>
        <select class="select" data-f="diff" aria-label="Difficulty">${DIFFS.map(([v, l]) => html`<option value="${v}"${f.diff === v ? raw(" selected") : ""}>${l}</option>`)}</select>
        <select class="select" data-f="status" aria-label="Status">${STATUSES.map(([v, l]) => html`<option value="${v}"${f.status === v ? raw(" selected") : ""}>${l}</option>`)}</select>
        <button type="button" class="toggle" data-f="cap" aria-pressed="${f.cap}" title="Hide problems rated above the cap"><span class="knob"></span>≤ cap${cap != null ? ` ${cap}` : ""}</button>
        ${f.list === "ox3f" ? html`<button type="button" class="toggle" data-f="comp" aria-pressed="${f.comp}" title="Include 0x3F's competition-tier sections"><span class="knob"></span>competition tier</button>` : ""}
        <span class="grow"></span>
        <span class="sub num">${fmtInt(rows.length)} ${rows.length === 1 ? "problem" : "problems"}</span>
      </div>
      <div class="card">${tableHtml(slice, {
        columns: ["id", "title", "level", "status", "actions"], sticky: true,
        sortable: ["id", "title", "level", "status"], sort: { col: f.sort, dir: f.dir },
        cursor: cursor && cursor.current(), empty: "No problems match these filters.",
      }, s)}</div>
      ${pages > 1 || rows.length > PAGE ? html`<div class="pager">
        <span class="num">${page * PAGE + 1}–${Math.min(rows.length, (page + 1) * PAGE)} of ${fmtInt(rows.length)}</span>
        <button type="button" class="btn sm" data-f="page" data-v="${page - 1}" ${page === 0 ? raw("disabled") : ""} aria-label="Previous page">${icon("chevl")}<kbd>[</kbd></button>
        <button type="button" class="btn sm" data-f="page" data-v="${page + 1}" ${page >= pages - 1 ? raw("disabled") : ""} aria-label="Next page">${icon("chevr")}<kbd>]</kbd></button>
      </div>` : ""}
    </div>`);
    if (cursor) cursor.restore();
    wireSearch(ctx);
  },

  unmount() {},
};

function page(ctx, delta) {
  const f = filtersFrom(ctx.route.query);
  update(ctx, { page: Math.max(0, f.page + delta) });
}

function wireSearch(ctx) {
  const input = document.getElementById("browse-search");
  if (!input || input.dataset.wired) return;
  input.dataset.wired = "1";
  input.addEventListener("input", () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => update(ctx, { q: input.value }), 120);
  });
  input.addEventListener("keydown", (ev) => { if (ev.key === "Escape") { input.value = ""; update(ctx, { q: "" }); input.blur(); } });
}

function toggleTopics(el, ctx) {
  const existing = el.querySelector(".popover[data-open]");
  if (existing) { existing.remove(); return; }
  const f = filtersFrom(ctx.route.query);
  const sel = new Set(f.topics);
  const anchor = el.querySelector("[data-f='topics-toggle']");
  const pop = document.createElement("div");
  pop.className = "popover";
  pop.dataset.open = "1";
  pop.setAttribute("role", "dialog");
  pop.style.top = `${anchor.offsetTop + anchor.offsetHeight + 6}px`;
  pop.style.left = `${anchor.offsetLeft}px`;
  render(pop, html`<div class="row"><button type="button" class="btn sm" data-f="topics-all">All</button><button type="button" class="btn sm" data-f="topics-none">None</button></div>
    ${allTopics.map((t) => html`<label><input type="checkbox" data-topic="${t}"${sel.has(t) ? raw(" checked") : ""}> ${t}</label>`)}`);
  anchor.parentElement.appendChild(pop);
  const close = (ev) => { if (!pop.contains(ev.target) && ev.target !== anchor) { pop.remove(); document.removeEventListener("mousedown", close); } };
  setTimeout(() => document.addEventListener("mousedown", close), 0);
}
