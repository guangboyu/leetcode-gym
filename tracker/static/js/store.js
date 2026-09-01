/* store.js — one place for application state.
 *
 * Views never keep their own copy of progress or settings; they read from
 * `get()` and re-render when something they depend on changes. `set(patch)`
 * batches writes into one microtask and notifies subscribers whose `deps`
 * intersect the changed keys — so marking a problem bumps `progressVersion`
 * and only the views that declared it re-render, nothing else.
 *
 * Also home to the derived-status rules (`dstatus`) that every table shares,
 * a tiny single-entry memo for expensive selectors, and the wall clock: the
 * old app computed "today" once at load, so a window left open overnight never
 * saw reviews become due. `startClock()` re-checks every minute and on focus.
 */

const state = {
  problems: {},        // slug -> problem
  rows: [],            // [slug, problem][] sorted by id
  byId: new Map(),     // id -> slug
  progress: {},        // slug -> entry
  progressVersion: 0,
  settings: {},        // mirror of the server's settings.json
  settingsVersion: 0,
  activity: null,      // {days: {date: {action: n}}} — loaded lazily by Stats
  tutorials: null,     // data/tutorials.json
  patterns: null,      // data/patterns.json
  today: "",           // YYYY-MM-DD (local)
  dateVersion: 0,
  status: "loading",   // loading | ready | error
  error: null,
  dataDir: "",
  about: null,
  ui: {},              // per-view transient state (cursor rows, drill phase…)
};

const subs = new Set();
let dirty = new Set();
let scheduled = false;

export function get() { return state; }

function flush() {
  scheduled = false;
  const changed = dirty;
  dirty = new Set();
  for (const s of subs) {
    if (!s.deps) { s.fn(state, changed); continue; }
    for (const d of s.deps) {
      if (changed.has(d)) { s.fn(state, changed); break; }
    }
  }
}

function schedule() {
  if (scheduled) return;
  scheduled = true;
  Promise.resolve().then(flush);
}

/** Merge `patch` into state; notify subscribers on the next microtask. */
export function set(patch) {
  for (const k of Object.keys(patch)) {
    state[k] = patch[k];
    dirty.add(k);
  }
  schedule();
}

/** Increment a version counter (e.g. after mutating `progress` in place). */
export function bump(key) {
  set({ [key]: (state[key] || 0) + 1 });
}

/** subscribe(fn, ["progressVersion", "today"]) → unsubscribe. No deps = every change. */
export function subscribe(fn, deps) {
  const s = { fn, deps: deps ? new Set(deps) : null };
  subs.add(s);
  return () => subs.delete(s);
}

/** Deliver pending notifications synchronously (tests). */
export function flushNow() { if (scheduled) flush(); }

/** Single-entry memo: recompute only when keyFn(...args) changes. */
export function memo(keyFn, computeFn) {
  let lastKey, lastVal, primed = false;
  return (...args) => {
    const key = keyFn(...args);
    if (!primed || key !== lastKey) {
      lastKey = key;
      lastVal = computeFn(...args);
      primed = true;
    }
    return lastVal;
  };
}

/* ---------- problems ---------- */

export function loadProblems(problems) {
  const rows = Object.entries(problems).sort((a, b) => a[1].id - b[1].id);
  const byId = new Map(rows.map(([slug, p]) => [p.id, slug]));
  set({ problems, rows, byId });
}

/* ---------- derived status ---------- */

/** new | solved (scheduled) | due | forgotten | mastered — for one slug. */
export function dstatus(slug, s = state) {
  const e = s.progress[slug];
  if (!e) return "new";
  if (e.status === "mastered") return "mastered";
  if (e.status === "forgotten") return "forgotten";
  return e.due && e.due <= s.today ? "due" : "solved";
}

export const isDone = (slug, s = state) => Boolean(s.progress[slug]) && s.progress[slug].status !== "forgotten";
export const isNew = (slug, s = state) => !s.progress[slug];

/** Rating cap from settings: number, or null for "none". */
export function cap(s = state) {
  const v = s.settings.cap;
  return v == null || v === "none" ? null : Number(v);
}

/* ---------- clock ---------- */

/** Local calendar date as YYYY-MM-DD (never UTC — reviews are due "today" here). */
export function todayStr(d = new Date()) {
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}

/** Re-evaluate the date if it rolled over; bumps dateVersion on change. */
export function refreshToday(now = new Date()) {
  const t = todayStr(now);
  if (t !== state.today) {
    set({ today: t });
    bump("dateVersion");
    return true;
  }
  return false;
}

let clock = null;
export function startClock() {
  refreshToday();
  if (clock || typeof setInterval !== "function") return;
  clock = setInterval(refreshToday, 60_000);
  if (typeof document !== "undefined") {
    document.addEventListener("visibilitychange", () => { if (!document.hidden) refreshToday(); });
  }
  if (typeof window !== "undefined") window.addEventListener("focus", () => refreshToday());
}

export function stopClock() {
  if (clock) { clearInterval(clock); clock = null; }
}
