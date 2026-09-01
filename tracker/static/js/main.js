/* main.js — boots the app and owns the shell.
 *
 * Responsibilities: load data → store; wire the hash router to the six views
 * (one <section> each, only the visible one renders); the toolbar; global
 * keyboard shortcuts + the named actions the native menu calls; `mark()` — the
 * single place a review is recorded, patched into every visible row, and
 * confirmed with an undoable toast; the theme; the one-time import of the old
 * localStorage preferences into settings.json.
 *
 * Views implement the contract in js/views/*.js:
 *   { id, title, routes, deps, mount(el, ctx), render(el, ctx, route),
 *     toolbar(ctx, route), unmount(el), actions? }
 */
import { html, render, raw } from "./h.js";
import * as api from "./api.js";
import * as store from "./store.js";
import * as router from "./router.js";
import * as keys from "./keys.js";
import * as toast from "./toast.js";
import * as desktop from "./desktop.js";
import { relDate, plural } from "./format.js";
import { patchRow } from "./components/problem-table.js";
import { icon } from "./components/status.js";

import learn from "./views/learn.js";
import today from "./views/today.js";
import browse from "./views/browse.js";
import drill from "./views/drill.js";
import stats from "./views/stats.js";
import settings from "./views/settings.js";

const VIEWS = { learn, today, browse, drill, stats, settings };
const mounted = new Set();
let activeView = null;
let activeRoute = null;

/* ---------- shell / theme ---------- */

function applyShellFlag() {
  const q = router.parseQuery(location.search);
  if (q.shell) document.documentElement.dataset.shell = q.shell;
}

export function applyTheme(theme) {
  const root = document.documentElement;
  if (theme === "light" || theme === "dark") root.dataset.theme = theme;
  else delete root.dataset.theme;
}

/* ---------- settings ---------- */

const settingsApi = {
  get(key) { return store.get().settings[key]; },
  async set(patch) {
    const merged = await api.putSettings(patch);
    store.set({ settings: merged });
    store.bump("settingsVersion");
    if ("theme" in patch) applyTheme(merged.theme);
    return merged;
  },
};

/* One-time import of the pre-0.2 localStorage preferences. */
async function importLegacyPrefs() {
  let ls;
  try { ls = window.localStorage; if (ls.getItem("gym-imported")) return; } catch (_) { return; }
  const patch = {};
  const j = (k) => { try { return JSON.parse(ls.getItem(k)); } catch (_) { return null; } };
  const cap = ls.getItem("cap");
  if (cap === "none") patch.cap = null; else if (cap && !isNaN(Number(cap))) patch.cap = Number(cap);
  if (ls.getItem("routeShowOptional") === "1") patch.routeShowOptional = true;
  const skipped = j("routeSkipped"); if (Array.isArray(skipped)) patch.routeSkipped = skipped.map(String);
  const pools = j("drillPools"); if (Array.isArray(pools)) patch.drillPools = pools.map(String);
  const topics = j("drillTopics"); if (Array.isArray(topics)) patch.drillTopics = topics.map(String);
  const lo = Number(ls.getItem("drillLo")), hi = Number(ls.getItem("drillHi"));
  if (lo) patch.drillLo = lo; if (hi) patch.drillHi = hi;
  try {
    if (Object.keys(patch).length) await settingsApi.set(patch);
    ls.setItem("gym-imported", "1");
    ["cap", "routeShowOptional", "routeSkipped", "drillPools", "drillTopics", "drillLo", "drillHi", "guideOpen"].forEach((k) => ls.removeItem(k));
  } catch (_) { /* keep the old prefs for a later try */ }
}

/* ---------- learn state (memoized, shared by Today / Learn / Drill) ---------- */

const learnMemo = store.memo(
  (s) => `${s.progressVersion}|${s.settingsVersion}|${s.dateVersion}|${s.patterns ? 1 : 0}`,
  (s) => {
    if (!s.patterns || !window.Route) return [];
    return window.Route.learnState(s.patterns, s.tutorials, s.rows,
      (slug) => store.isDone(slug, s), store.cap(s),
      { showOptional: Boolean(s.settings.routeShowOptional), skipped: new Set(s.settings.routeSkipped || []) });
  });

/* ---------- marking ---------- */

const busy = new Set();

function consequence(action, entry, s) {
  if (action === "solved" || action === "solved_help") {
    if (entry && entry.status === "mastered") return "mastered — no more reviews";
    return entry && entry.due ? `next review ${relDate(entry.due, s.today)}` : "";
  }
  if (action === "forgotten") return "due again today · ladder restarts";
  if (action === "reset") return "progress cleared";
  if (action === "undo") return "undone";
  return "";
}
const VERB = { solved: "Solved", solved_help: "Solved with help", forgotten: "Forgot", reset: "Reset", undo: "Undo" };

function applyEntry(slug, entry) {
  const s = store.get();
  const progress = { ...s.progress };
  if (entry) progress[slug] = entry; else delete progress[slug];
  store.set({ progress });
  store.bump("progressVersion");
  store.flushNow();
}

export async function mark(slug, action, { quiet = false } = {}) {
  const s = store.get();
  const p = s.problems[slug];
  if (!p || busy.has(slug)) return null;
  busy.add(slug);
  store.set({ ui: { ...s.ui, busy } });
  document.querySelectorAll(`.acts[data-slug="${CSS.escape(slug)}"]`).forEach((n) => n.setAttribute("aria-busy", "true"));
  try {
    const res = await api.review(slug, action);
    applyEntry(slug, res.entry);
    patchRows(slug);
    if (!quiet) {
      const detail = `${p.title} · ${consequence(action, res.entry, store.get())}`;
      toast.show({
        text: VERB[action] || action, detail, kind: "success",
        action: action !== "undo" && res.undoable !== false
          ? { label: "Undo", combo: keys.display("mod+z"), run: () => mark(slug, "undo") }
          : null,
      });
    }
    return res.entry;
  } catch (err) {
    toast.show({ text: "Couldn't save that review", detail: err.message, kind: "error",
      action: { label: "Retry", run: () => mark(slug, action) } });
    return null;
  } finally {
    busy.delete(slug);
    document.querySelectorAll(`.acts[data-slug="${CSS.escape(slug)}"]`).forEach((n) => n.removeAttribute("aria-busy"));
  }
}

export function patchRows(slug) {
  patchRow(slug, document);
  updateDuePill();
}

function updateDuePill() {
  const s = store.get();
  let n = 0;
  for (const [slug] of s.rows) { const st = store.dstatus(slug, s); if (st === "due" || st === "forgotten") n++; }
  const pill = document.getElementById("due-pill");
  if (!pill) return;
  pill.textContent = String(n);
  pill.hidden = n === 0;
}

function updateSyncDot() {
  const dot = document.getElementById("sync-dot");
  const dir = store.get().dataDir || "";
  const synced = /dropbox|icloud|onedrive|google ?drive|cloudstorage/i.test(dir);
  if (!dot) return;
  dot.classList.toggle("off", !synced);
  dot.title = synced ? `Synced · ${dir}` : `Local only · ${dir}`;
}

/* ---------- ctx ---------- */

const ctx = {
  store, api, toast, keys, desktop,
  navigate: (r, o) => router.navigate(r, o),
  mark, patchRows,
  settings: settingsApi,
  learn: () => learnMemo(store.get()),
  effRating: (p) => (window.Route ? window.Route.effRating(p) : null),
  get route() { return activeRoute; },
  shortcuts: () => openShortcuts(),
};

/* ---------- routing ---------- */

function sectionFor(id) { return document.getElementById(`view-${id}`); }

function renderToolbar(view, route) {
  const tb = document.getElementById("toolbar");
  const custom = view.toolbar ? view.toolbar(ctx, route) : null;
  render(tb, html`<div class="drag pywebview-drag-region"></div>${custom || html`<h1>${view.title}</h1>`}`);
}

function showRoute(route, prev) {
  const view = VIEWS[route.view] || VIEWS.today;
  activeRoute = route;
  const boot = document.getElementById("view-boot");
  if (boot) boot.hidden = true;
  const changed = view !== activeView;
  if (changed) {
    if (activeView) {
      const old = sectionFor(activeView.id);
      if (old) old.hidden = true;
      keys.setScope("global");
    }
    activeView = view;
    keys.setScope(view.id);
  }
  const el = sectionFor(view.id);
  if (!mounted.has(view.id)) { view.mount(el, ctx); mounted.add(view.id); }
  el.hidden = false;
  renderToolbar(view, route);
  view.render(el, ctx, route);
  if (changed) {
    el.scrollTop = 0;
    document.querySelectorAll("[data-nav]").forEach((a) => {
      if (a.dataset.nav === view.id) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
    });
    // Focus the pane so table shortcuts work immediately; keep the search box if it asked for focus.
    if (!(document.activeElement && el.contains(document.activeElement))) el.focus({ preventScroll: true });
    if (store.get().settings.lastView !== view.id) settingsApi.set({ lastView: view.id }).catch(() => {});
  }
}

/* ---------- global shortcuts + menu actions ---------- */

function openShortcuts() {
  const dlg = document.getElementById("shortcuts");
  const body = document.getElementById("shortcuts-body");
  const groups = new Map();
  for (const b of keys.describe()) {
    if (!groups.has(b.scope)) groups.set(b.scope, []);
    groups.get(b.scope).push(b);
  }
  const order = ["global", "today", "learn", "browse", "drill", "stats", "settings"];
  const NAMES = { global: "Everywhere", today: "Today", learn: "Learn", browse: "Browse", drill: "Drill", stats: "Stats", settings: "Settings" };
  render(body, html`${order.filter((g) => groups.has(g)).map((g) => html`<h4>${NAMES[g] || g}</h4>${groups.get(g).map((b) => html`<div><span>${b.label}</span><span class="keys">${b.display.split("/").map((k) => html`<kbd>${k.trim()}</kbd>`)}</span></div>`)}`)}`);
  if (typeof dlg.showModal === "function" && !dlg.open) dlg.showModal();
}

function installGlobalKeys() {
  const go = (v) => router.navigate({ view: v });
  const names = { learn: "Learn", today: "Today", browse: "Browse", drill: "Drill", stats: "Stats" };
  ["learn", "today", "browse", "drill", "stats"].forEach((v, i) => {
    keys.register("global", `mod+${i + 1}`, () => go(v), { label: `Go to ${names[v]}`, inInputs: true });
  });
  keys.register("global", "mod+,", () => go("settings"), { label: "Settings", inInputs: true });
  keys.register("global", "mod+f", () => search(), { label: "Search problems", inInputs: true });
  keys.register("global", "mod+/", openShortcuts, { label: "Keyboard shortcuts", inInputs: true });
  keys.register("global", "shift+/", openShortcuts, { label: "" });
  keys.register("global", "mod+z", () => { if (!toast.runAction()) return; }, { label: "Undo the last mark", inInputs: true });
  keys.register("global", "mod+[", () => router.back(), { label: "Back", inInputs: true });
  keys.register("global", "mod+]", () => router.forward(), { label: "Forward", inInputs: true });
  keys.register("global", "escape", () => {
    const dlg = document.getElementById("shortcuts");
    if (dlg && dlg.open) { dlg.close(); return; }
    document.querySelectorAll(".popover[data-open]").forEach((p) => p.remove());
    if (keys.isTyping(document.activeElement)) document.activeElement.blur();
  }, { label: "Close / clear", inInputs: true });

  keys.defineAction("go", (v) => go(v));
  keys.defineAction("search", () => search());
  keys.defineAction("history", (dir) => (dir === "back" ? router.back() : router.forward()));
  keys.defineAction("shortcuts", openShortcuts);
  keys.defineAction("drill", (what) => {
    if (activeView !== drill) router.navigate({ view: "drill" });
    setTimeout(() => drill.actions && drill.actions[what] && drill.actions[what](), 0);
  });
  keys.defineAction("theme", (t) => settingsApi.set({ theme: t }));
}

function search() {
  if (activeView !== browse) router.navigate({ view: "browse" });
  setTimeout(() => { const f = document.getElementById("browse-search"); if (f) { f.focus(); f.select(); } }, 0);
}

/* ---------- delegated clicks ---------- */

function installClicks() {
  document.addEventListener("click", (ev) => {
    const t = ev.target.closest("[data-act]");
    if (!t) return;
    const act = t.dataset.act;
    if (act === "mark") { ev.preventDefault(); mark(t.dataset.slug, t.dataset.action); }
    else if (act === "close-sheet") { const d = t.closest("dialog"); if (d) d.close(); }
    else if (act === "nav") { ev.preventDefault(); router.navigate(t.dataset.to); }
    else if (act === "copy") {
      const pre = t.closest("pre");
      const code = pre ? pre.querySelector("code") || pre : null;
      const text = code ? code.innerText.replace(/^\s*Copy\s*$/m, "") : "";
      if (navigator.clipboard) navigator.clipboard.writeText(text.trim()).then(() => {
        t.classList.add("copied"); t.setAttribute("aria-label", "Copied");
        setTimeout(() => { t.classList.remove("copied"); t.setAttribute("aria-label", "Copy"); }, 1200);
      });
    }
  });
  // Links out: keep target=_blank; pywebview opens them in the system browser.
}

/* ---------- boot ---------- */

function bootError(err) {
  const pane = document.getElementById("view-boot");
  pane.hidden = false;
  render(pane, html`<div class="view"><div class="card errorcard">
    ${icon("alert", "icon")}
    <h2>Couldn't load the problem set</h2>
    <p class="sub">${err && err.message ? err.message : String(err)}<br>The local server did not respond, or the data files are missing.</p>
    <button type="button" class="btn primary" id="boot-retry">Retry</button>
  </div></div>`);
  document.getElementById("boot-retry").addEventListener("click", () => boot());
}

async function boot() {
  applyShellFlag();
  desktop.installDragRegions();
  try {
    const [problems, progress, settingsData, dataDir, tutorials, patterns] = await Promise.all([
      api.getProblems(), api.getProgress(), api.getSettings(), api.getDataDir().catch(() => ({ path: "" })),
      api.getTutorials().catch(() => null), api.getPatterns().catch(() => null),
    ]);
    store.loadProblems(problems);
    store.set({ progress, settings: settingsData, dataDir: dataDir.path || "", tutorials, patterns, status: "ready" });
    store.bump("progressVersion"); store.bump("settingsVersion");
    store.startClock();
    store.flushNow();
    applyTheme(settingsData.theme);
    await importLegacyPrefs();
  } catch (err) {
    store.set({ status: "error", error: err });
    bootError(err);
    return;
  }
  updateDuePill();
  updateSyncDot();
  store.subscribe(() => { updateDuePill(); }, ["progressVersion", "dateVersion"]);
  store.subscribe(() => { updateSyncDot(); }, ["dataDir"]);
  store.subscribe((s, changed) => {
    if (!activeView || !activeRoute) return;
    const deps = activeView.deps || [];
    if (deps.some((d) => changed.has(d))) {
      const el = sectionFor(activeView.id);
      renderToolbar(activeView, activeRoute);
      activeView.render(el, ctx, activeRoute);
    }
  });
  router.onChange(showRoute);
  const last = store.get().settings.lastView;
  router.start(router.VIEWS.includes(last) ? last : "today");
}

keys.install();
installGlobalKeys();
installClicks();
window.Gym = Object.assign(window.Gym || {}, { store, router, mark, ctx, version: "0.3.0" });
boot();
