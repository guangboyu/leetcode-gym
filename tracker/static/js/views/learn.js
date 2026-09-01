/* views/learn.js — the Learn tab: one ordered list of patterns, and for each
 * pattern a practice page (quick card → shape chips → the shape's card and its
 * problems → "Extend with 0x3F") or the tutorial itself in reading mode.
 *
 * Everything about *which* problems belong where comes from Route.learnState
 * (tracker/static/route.js); this file only decides what to show for the
 * current route and draws it. The pure helpers (selection, chip model, ring
 * math, toolbar wording, note rendering) are exported for tests; the DOM work
 * stays inside the view object.
 *
 * Routes: #/learn · #/learn/<pattern> · #/learn/<pattern>/<sub>
 *         #/learn/<pattern>/read[/<anchor>]   (learn-read.js)
 */
import { html, raw, render, esc } from "../h.js";
import { highlight } from "../pyhl.js";
import { titleCase } from "../format.js";
import { tableHtml, patchRow, attachCursor } from "../components/problem-table.js";
import { icon } from "../components/status.js";
import { mountRead, unmountRead, readToolbar } from "./learn-read.js";

export const RING_R = 7.5;
export const RING_C = +(2 * Math.PI * RING_R).toFixed(2);      // 47.12
export const EXT_PREVIEW = 10;
const HINTS_KEY = "gym.learn.hints";     // per-viewer convenience; not synced

/* ---------- pure helpers ------------------------------------------------ */

/** stroke-dashoffset for a progress ring: full circle = nothing done. */
export function ringOffset(done, total, c = RING_C) {
  if (!total) return c;
  const f = Math.min(1, Math.max(0, done / total));
  return +(c * (1 - f)).toFixed(2);
}

/** Subtopics a viewer can pick from chips (everything but hidden ones). */
export function chipModel(pattern) {
  return pattern.subtopics.map((s) => ({
    id: s.id, key: s.key, kind: s.kind, name: s.name,
    done: s.done, total: s.total, skipped: s.skipped,
    complete: s.total > 0 && s.done >= s.total,
    dashed: s.kind === "also-core" || s.kind === "ox3f",
  }));
}

/** Default subtopic for a pattern: first non-skipped with work left, else first. */
export function defaultSub(pattern) {
  const subs = pattern.subtopics;
  if (!subs.length) return null;
  const open = subs.find((s) => !s.skipped && s.kind !== "ox3f" && s.todo.length);
  return (open || subs.find((s) => s.kind !== "ox3f") || subs[0]).id;
}

/** Resolve the route (+ remembered choice) to {pattern, sub, read, anchor}. */
export function resolveSelection(learn, route, settings, nextUp) {
  if (!learn.length) return null;
  const byId = new Map(learn.map((p) => [p.id, p]));
  let pid = route && route.pattern && byId.has(route.pattern) ? route.pattern : null;
  if (!pid && settings && settings.lastPattern && byId.has(settings.lastPattern)) pid = settings.lastPattern;
  if (!pid && nextUp) pid = nextUp.pattern.id;
  if (!pid) pid = learn[0].id;
  const pattern = byId.get(pid);
  const has = (id) => pattern.subtopics.some((s) => s.id === id);
  let sub = route && route.sub && has(route.sub) ? route.sub : null;
  if (!sub && settings && settings.lastPattern === pid && settings.lastSection && has(settings.lastSection)) sub = settings.lastSection;
  if (!sub) sub = defaultSub(pattern);
  return { pattern, sub, read: Boolean(route && route.read), anchor: route && route.anchor || null };
}

/** Toolbar wording for a pattern: "14 of 41 · 3 shapes to go". */
export function toolbarText(pattern) {
  const open = pattern.subtopics.filter((s) => !s.skipped && s.kind !== "ox3f" && s.todo.length).length;
  const unit = pattern.hasTutorial ? "shape" : "subtopic";
  const rest = open ? `${open} ${unit}${open === 1 ? "" : "s"} to go` : (pattern.total ? "all done" : "");
  return `${pattern.done} of ${pattern.total}${rest ? " · " + rest : ""}`;
}

/** Which rows of an extension list to show. */
export function extSlice(rows, showAll, preview = EXT_PREVIEW) {
  if (showAll || rows.length <= preview) return { rows, hidden: 0 };
  return { rows: rows.slice(0, preview), hidden: rows.length - preview };
}

/** A tutorial Note cell → inline HTML (marked inline when available). */
export function noteHtml(md) {
  if (!md) return "";
  const m = globalThis.marked;
  if (m && typeof m.parseInline === "function") return m.parseInline(md);
  return esc(md);
}

/** Attach note_html to tutorial rows so the shared row component can show hints. */
export function withNotes(rows) {
  return rows.map(([slug, p, meta]) => [slug, p, meta && meta.note_md ? { ...meta, note_html: noteHtml(meta.note_md) } : meta || {}]);
}

/** Neighbouring pattern / subtopic ids for ←/→ navigation. */
export function neighbour(list, id, delta) {
  const i = list.findIndex((x) => x.id === id);
  if (i < 0) return null;
  const j = i + delta;
  return j >= 0 && j < list.length ? list[j].id : null;
}

const ADVANCED = new Set(["insight", "strings", "number-theory", "fenwick-segment"]);

/* ---------- html pieces --------------------------------------------------- */

function ring(done, total, size) {
  const cls = "ring" + (total && done >= total ? " done" : "") + (size ? " " + size : "");
  return html`<svg class="${cls}" viewBox="0 0 20 20" aria-hidden="true"><circle class="bg" cx="10" cy="10" r="${RING_R}"></circle><circle class="fg" cx="10" cy="10" r="${RING_R}" stroke-dasharray="${RING_C} ${RING_C}" stroke-dashoffset="${ringOffset(done, total)}"></circle></svg>`;
}

function patternList(learn, currentId) {
  let advShown = false;
  const items = learn.map((p) => {
    const adv = ADVANCED.has(p.id);
    const divider = adv && !advShown ? (advShown = true, html`<div class="lbl adv">Advanced</div>`) : "";
    return html`${divider}<a class="pitem" href="#/learn/${p.id}" data-key="pitem:${p.id}"${p.id === currentId ? raw(' aria-current="true"') : ""} title="${p.done} of ${p.total}">
      ${ring(p.done, p.total)}<span class="n">${p.name}</span>
      ${p.hasTutorial ? icon("book", "book") : ""}${p.status === "draft" ? html`<span class="draft">draft</span>` : ""}
    </a>`;
  });
  return html`<nav class="plist" aria-label="Patterns"><div class="lbl">Patterns</div>${items}
    <div class="foot">${icon("book")}has a tutorial · the rest are in progress</div></nav>`;
}

function codeBlock(code) {
  if (!code) return "";
  return html`<pre class="code"><button type="button" class="btn ghost sm copy" data-copy aria-label="Copy code">${icon("copy")}</button><code>${raw(highlight(code))}</code></pre>`;
}

function quickCard(p) {
  return html`<section class="card quick" aria-label="Pattern overview">
    <div class="l">
      <h3>Reach for ${p.name.toLowerCase()} when…</h3>
      <ul>${p.signals.map((s) => html`<li>${s}</li>`)}</ul>
      ${p.oneLiner ? html`<p>${p.oneLiner}</p>` : ""}
      ${p.hasTutorial ? html`<a class="btn ghost sm" href="#/learn/${p.id}/read">Recognize · solve · pitfalls →</a>` : ""}
    </div>
    <div class="r">${p.template ? codeBlock(p.template) : html`<div class="empty">No template yet.</div>`}</div>
  </section>`;
}

function chips(pattern, selectedId) {
  const model = chipModel(pattern);
  const main = model.filter((c) => !c.dashed);
  const extra = model.filter((c) => c.dashed);
  const chip = (c) => html`<button type="button" class="schip${c.complete ? " done" : ""}${c.dashed ? " dash" : ""}" data-act="learn-sub" data-sub="${c.id}" data-key="chip:${c.key}" aria-pressed="${c.id === selectedId}" title="${c.skipped ? "Skipped — click ↩ to restore" : ""}">
      ${c.complete ? icon("check") : ""}<span class="${c.skipped ? "muted" : ""}">${c.name}</span><span class="c">${c.done}/${c.total}</span>
      ${c.kind === "ox3f" ? "" : html`<span class="skip" role="button" tabindex="0" data-act="learn-skip" data-keyid="${c.key}" aria-label="${c.skipped ? "Restore" : "Skip this subtopic"}" title="${c.skipped ? "Restore" : "Skip"}">${c.skipped ? "↩" : "×"}</span>`}
    </button>`;
  return html`<div class="chips" role="tablist">${main.map(chip)}${extra.length ? html`<span class="sep"></span>${extra.map(chip)}` : ""}</div>`;
}

function subtopicCard(pattern, sub) {
  if (sub.kind === "also-core") {
    return html`<section class="card subcard nofig"><div class="txt"><h3>${sub.name}</h3><p>Core problems from Hot 100 / Interview 150 / NeetCode 250 that the tutorial doesn't list yet. Practice them here; they count toward the pattern.</p></div></section>`;
  }
  if (sub.kind === "ox3f") {
    return html`<section class="card subcard nofig"><div class="txt"><h3>${sub.name}</h3><p>Problems from 0x3F's list that map to this pattern as a whole. Optional material — it never counts toward the ring.${sub.post ? html` Original list: <a href="${sub.post}" target="_blank" rel="noopener">${sub.topic}${sub.zh ? `（${sub.zh}）` : ""} ↗</a>` : ""}</p></div></section>`;
  }
  const gif = sub.gifs && sub.gifs[0];
  const worked = (sub.worked || []).length
    ? html`<div class="links"><span class="sub">Worked in the tutorial:</span>${sub.worked.map((w) => html`<a href="#/learn/${pattern.id}/read/${w.anchor}" title="${w.title}">LC ${w.id}${/^\d/.test(w.title) || w.title.length > 40 ? "" : ` · ${w.title}`}</a>`)}</div>`
    : "";
  const body = sub.kind === "shape"
    ? html`${sub.blurb ? html`<p>${sub.blurb}</p>` : ""}${codeBlock(sub.template)}${worked}`
    : html`<div class="recognize"><div><h4>Recognize</h4><p>${sub.recognize || "—"}</p></div><div><h4>Solve</h4><p>${sub.solve || "—"}</p></div></div>${codeBlock(sub.template)}`;
  return html`<section class="card subcard${gif ? "" : " nofig"}">
    <div class="txt"><h3>${sub.label ? sub.label.replace(/^Shape (\d+): (.*)$/, (m, n, t) => `Shape ${n} · ${titleCase(t)}`) : sub.name}</h3>${body}</div>
    ${gif ? html`<div class="fig"><a href="#/learn/${pattern.id}/read/${sub.anchor || ""}" title="Open in the tutorial"><img src="/tutorials/${gif}" alt="Animation for ${sub.name}" loading="lazy" decoding="async"></a></div>` : ""}
  </section>`;
}

function problemsCard(pattern, sub, ui, hints, cap) {
  const isShape = sub.kind === "shape";
  const columns = isShape ? ["id", "title", "level", "freq", "status", "actions"] : ["id", "title", "level", "status", "actions"];
  const rows = withNotes(sub.core);
  const showAll = Boolean(ui.extOpen && ui.extOpen[sub.key] === "all");
  const open = Boolean(ui.extOpen && ui.extOpen[sub.key]);
  const ext = extSlice(sub.ext.inCap, showAll);
  const extTotal = sub.ext.inCap.length;
  const capText = cap == null ? "no cap" : `cap ${cap}`;
  const title = sub.kind === "ox3f" ? sub.name : `${sub.name} problems`;
  const meta = isShape ? "in the tutorial's order" : sub.kind === "curriculum" ? "easiest first" : "";
  return html`<section class="card" aria-label="${title}">
    <div class="hd"><span>${title}</span>${meta ? html`<span class="meta">${meta}</span>` : ""}<span class="grow"></span>
      ${isShape ? html`<button type="button" class="toggle" data-act="learn-hints" aria-pressed="${hints}"><span class="knob"></span>Hints</button>` : ""}</div>
    ${rows.length ? tableHtml(rows, { columns, hints, empty: "" }) : html`<div class="empty">Nothing here yet.</div>`}
    ${(extTotal || sub.ext.above) && sub.kind !== "ox3f" ? html`
      <button type="button" class="extend" data-act="learn-ext" data-keyid="${sub.key}" aria-expanded="${open}">
        ${icon("chevr")}<b>Extend with 0x3F</b><span>${extTotal} within ${capText}${sub.ext.above ? ` · ${sub.ext.above} above` : ""}${sub.ext.done ? ` · ${sub.ext.done} done` : ""}</span>
      </button>
      ${open ? html`<div class="ext-body">
        ${tableHtml(ext.rows, { columns: ["id", "title", "level", "status", "actions"], hints: false, empty: "Nothing within your cap — raise it in Settings." })}
        <div class="ft">
          <span>${ext.hidden ? html`<button type="button" class="btn sm" data-act="learn-ext-all" data-keyid="${sub.key}">Show all ${extTotal}</button>` : ""}
            ${sub.ext.above ? html`<span class="sub">${sub.ext.above} more above your cap — raise it in Settings.</span>` : ""}</span>
          ${extAttribution(sub)}
        </div>
      </div>` : ""}` : ""}
  </section>`;
}

function extAttribution(sub) {
  const topics = new Map();
  for (const [, , m] of sub.ext.inCap) if (m && m.topic && !topics.has(m.topic)) topics.set(m.topic, true);
  const names = [...topics.keys()];
  if (!names.length) return "";
  return html`<span class="sub">From 0x3F's ${names.join(" / ")} list${names.length > 1 ? "s" : ""} ↗</span>`;
}

/* ---------- the view ------------------------------------------------------- */

let ctxRef = null;
let selection = null;      // {pattern, sub, read, anchor}
let cursor = null;
let clickBound = false;
const unregister = [];

function hintsOn() {
  try { return localStorage.getItem(HINTS_KEY) !== "0"; } catch (_) { return true; }
}
function setHints(v) {
  try { localStorage.setItem(HINTS_KEY, v ? "1" : "0"); } catch (_) { /* private mode */ }
}

function uiState() {
  const s = ctxRef.store.get();
  if (!s.ui.learn) s.ui.learn = { extOpen: {} };
  return s.ui.learn;
}

function rememberSelection(sel) {
  const st = ctxRef.settings;
  if (!st) return;
  const patch = {};
  if (st.get("lastPattern") !== sel.pattern.id) patch.lastPattern = sel.pattern.id;
  if (st.get("lastSection") !== sel.sub) patch.lastSection = sel.sub;
  if (Object.keys(patch).length) st.set(patch).catch(() => {});
}

function go(sel, extra = {}) {
  const r = { view: "learn", pattern: sel.pattern.id };
  if (extra.read) { r.read = true; if (extra.anchor) r.anchor = extra.anchor; }
  else r.sub = extra.sub || sel.sub;
  ctxRef.navigate(r);
}

function onClick(ev) {
  const t = ev.target.closest("[data-act]");
  if (!t) return;
  const act = t.dataset.act;
  if (act === "learn-sub") {
    go(selection, { sub: t.dataset.sub });
  } else if (act === "learn-skip") {
    ev.stopPropagation(); ev.preventDefault();
    toggleSkip(t.dataset.keyid);
  } else if (act === "learn-hints") {
    setHints(!hintsOn());
    rerender();
  } else if (act === "learn-ext" || act === "learn-ext-all") {
    const ui = uiState();
    const k = t.dataset.keyid;
    ui.extOpen[k] = act === "learn-ext-all" ? "all" : (ui.extOpen[k] ? null : "open");
    rerender();
  } else if (act === "mark") {
    ev.stopPropagation();
    const slug = t.dataset.slug, action = t.dataset.action;
    Promise.resolve(ctxRef.mark(slug, action)).then(() => ctxRef.patchRows ? ctxRef.patchRows(slug) : patchRow(slug)).catch(() => {});
  } else if (act === "copy") {
    ev.stopPropagation();
  } else {
    return;
  }
  if (t.closest("pre") == null && act !== "mark") ev.preventDefault();
}

function onKeydownSkip(ev) {
  if ((ev.key === "Enter" || ev.key === " ") && ev.target.dataset && ev.target.dataset.act === "learn-skip") {
    ev.preventDefault(); ev.stopPropagation();
    toggleSkip(ev.target.dataset.keyid);
  }
}

function toggleSkip(key) {
  const st = ctxRef.settings;
  const cur = new Set(st.get("routeSkipped") || []);
  if (cur.has(key)) cur.delete(key); else cur.add(key);
  st.set({ routeSkipped: [...cur] }).then(() => rerender()).catch(() => {});
}

function copyHandler(ev) {
  const b = ev.target.closest("[data-copy]");
  if (!b) return;
  const pre = b.closest("pre") || (b.parentElement && b.parentElement.querySelector("pre"));
  const code = pre ? (pre.querySelector("code") || pre).textContent : "";
  const done = () => { b.classList.add("copied"); b.setAttribute("aria-label", "Copied"); setTimeout(() => { b.classList.remove("copied"); b.setAttribute("aria-label", "Copy code"); }, 1200); };
  if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(code).then(done, done);
  else done();
}

let elRef = null, routeRef = null;
function rerender() { if (elRef) view.render(elRef, ctxRef, routeRef); }

const view = {
  id: "learn",
  title: "Learn",
  routes: ["learn"],
  deps: ["progressVersion", "settingsVersion", "dateVersion"],

  mount(el, ctx) {
    ctxRef = ctx;
    elRef = el;
    if (!clickBound) {
      el.addEventListener("click", onClick);
      el.addEventListener("click", copyHandler);
      el.addEventListener("keydown", onKeydownSkip);
      clickBound = true;
    }
    const keys = ctx.keys;
    if (keys && keys.register) {
      const reg = (combo, fn, label) => unregister.push(keys.register("learn", combo, fn, { label }));
      reg("mod+r", () => selection && go(selection, { read: !selection.read }), "Read the tutorial / back to practice");
      reg("r", () => selection && go(selection, { read: !selection.read }), "Read the tutorial / back to practice");
      reg("arrowright", () => stepPattern(1), "Next pattern");
      reg("arrowleft", () => stepPattern(-1), "Previous pattern");
      reg("shift+arrowright", () => stepSub(1), "Next subtopic");
      reg("shift+arrowleft", () => stepSub(-1), "Previous subtopic");
      reg("h", () => { setHints(!hintsOn()); rerender(); }, "Toggle hints");
      if (keys.setScope) keys.setScope("learn");
    }
  },

  toolbar(ctx, route) {
    const learn = ctx.learn();
    const nu = window.Route && window.Route.nextUp ? window.Route.nextUp(learn) : null;
    const sel = resolveSelection(learn, route, settingsView(ctx), nu);
    if (!sel) return html`<h1>Learn</h1>`;
    if (sel.read) return readToolbar(sel);
    const p = sel.pattern;
    return html`<h1>${p.name}</h1><span class="sub tabnum">${toolbarText(p)}</span><span class="grow"></span>
      ${p.hasTutorial
        ? html`<a class="btn" href="#/learn/${p.id}/read">${icon("book")}Read the tutorial<kbd>${ctx.keys && ctx.keys.display ? ctx.keys.display("mod+r") : "⌘R"}</kbd></a>`
        : html`<span class="chip slate" title="A written walkthrough for this pattern is coming; the subtopics below come from the curated curriculum.">Tutorial in progress</span>`}`;
  },

  render(el, ctx, route) {
    ctxRef = ctx; elRef = el; routeRef = route;
    const learn = ctx.learn();
    const nu = window.Route && window.Route.nextUp ? window.Route.nextUp(learn) : null;
    const sel = resolveSelection(learn, route, settingsView(ctx), nu);
    selection = sel;
    if (!sel) { render(el, html`<div class="empty">No patterns loaded.</div>`); return; }
    rememberSelection(sel);
    if (ctx.keys && ctx.keys.setScope) ctx.keys.setScope("learn");

    if (sel.read) {
      // Reading mode owns its DOM (it keeps the article across anchor changes).
      if (cursor) { cursor.detach(); cursor = null; }
      mountRead(el, ctx, sel, { patternList: () => patternList(learn, sel.pattern.id) });
      return;
    }
    unmountRead(el);

    const p = sel.pattern;
    const sub = p.subtopics.find((s) => s.id === sel.sub) || p.subtopics[0];
    const s = ctx.store.get();
    const cap = typeof ctx.cap === "function" ? ctx.cap() : (s.settings.cap == null || s.settings.cap === "none" ? null : Number(s.settings.cap));
    const hints = hintsOn();
    render(el, html`<div class="split">
      <div class="col">${patternList(learn, p.id)}</div>
      <div class="main learn-main"><div class="view learn-page" data-pattern="${p.id}" data-sub="${sub ? sub.id : ""}">
        ${quickCard(p)}
        ${sub ? chips(p, sub.id) : ""}
        ${sub ? subtopicCard(p, sub) : html`<div class="empty">This pattern has no subtopics yet.</div>`}
        ${sub ? problemsCard(p, sub, uiState(), hints, cap) : ""}
      </div></div>
    </div>`);
    const table = el.querySelector(".learn-page");
    if (cursor) cursor.detach();
    cursor = attachCursor(table, { onMark: (slug, action) => Promise.resolve(ctx.mark(slug, action)).then(() => (ctx.patchRows ? ctx.patchRows(slug) : patchRow(slug))).catch(() => {}) });
  },

  unmount(el) {
    unmountRead(el);
    if (cursor) { cursor.detach(); cursor = null; }
    while (unregister.length) unregister.pop()();
    if (ctxRef && ctxRef.keys && ctxRef.keys.setScope) ctxRef.keys.setScope("global");
  },
};

function settingsView(ctx) {
  if (ctx.settings && ctx.settings.get) {
    return { lastPattern: ctx.settings.get("lastPattern"), lastSection: ctx.settings.get("lastSection") };
  }
  return ctx.store.get().settings || {};
}

function stepPattern(delta) {
  if (!selection) return;
  const learn = ctxRef.learn();
  const id = neighbour(learn, selection.pattern.id, delta);
  if (id) ctxRef.navigate({ view: "learn", pattern: id });
}

function stepSub(delta) {
  if (!selection) return;
  const subs = selection.pattern.subtopics.filter((s) => s.kind !== "ox3f");
  const id = neighbour(subs, selection.sub, delta);
  if (id) go(selection, { sub: id });
}

export default view;
