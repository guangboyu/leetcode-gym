/* router.js — hash routes, so every screen has an address.
 *
 *   #/today                         #/browse?list=ox3f&diff=Medium&page=2
 *   #/learn                         #/drill
 *   #/learn/sliding-window          #/stats
 *   #/learn/sliding-window/shape-2  #/settings
 *   #/learn/sliding-window/read
 *   #/learn/sliding-window/read/shape-2-longest-valid
 *
 * Browse keeps its filters in the query string so reload and back/forward
 * restore them. Learn keeps a small in-app history so ⌘[ / ⌘] move between the
 * pattern page and the tutorial without leaving the tab. The module never
 * touches `location` at import time, so it is testable outside a browser.
 */

export const VIEWS = ["today", "learn", "browse", "drill", "stats", "settings"];
const SEG = /^[A-Za-z0-9._%-]+$/;

/* ---------- query strings (no URLSearchParams: JavaScriptCore lacks it) ---------- */

export function parseQuery(qs) {
  const out = {};
  if (!qs) return out;
  for (const part of qs.replace(/^\?/, "").split("&")) {
    if (!part) continue;
    const i = part.indexOf("=");
    const k = decodeURIComponent(i < 0 ? part : part.slice(0, i));
    const v = i < 0 ? "" : decodeURIComponent(part.slice(i + 1).replace(/\+/g, " "));
    out[k] = v;
  }
  return out;
}

export function encodeQuery(obj) {
  const parts = [];
  for (const k of Object.keys(obj)) {
    const v = obj[k];
    if (v == null || v === "" || v === false) continue;
    parts.push(`${encodeURIComponent(k)}=${encodeURIComponent(Array.isArray(v) ? v.join(",") : String(v))}`);
  }
  return parts.length ? "?" + parts.join("&") : "";
}

/* ---------- parse / build ---------- */

/** "#/learn/x/read/anchor?..." → {view, pattern?, sub?, read?, anchor?, query}. */
export function parse(hash) {
  let h = String(hash || "");
  if (h.startsWith("#")) h = h.slice(1);
  if (!h.startsWith("/")) h = "/" + h;
  const qi = h.indexOf("?");
  const query = parseQuery(qi < 0 ? "" : h.slice(qi + 1));
  const path = (qi < 0 ? h : h.slice(0, qi)).split("/").filter(Boolean).map((s) => {
    try { return decodeURIComponent(s); } catch (_) { return s; }
  });
  const view = VIEWS.includes(path[0]) ? path[0] : "today";
  const r = { view, query };
  if (view === "learn") {
    if (path[1]) r.pattern = path[1];
    if (path[2] === "read") {
      r.read = true;
      if (path[3]) r.anchor = path[3];
    } else if (path[2]) {
      r.sub = path[2];
    }
  }
  return r;
}

/** Inverse of parse(). Unknown views fall back to today. */
export function build(route) {
  const r = typeof route === "string" ? { view: route } : route || {};
  const view = VIEWS.includes(r.view) ? r.view : "today";
  let out = "#/" + view;
  if (view === "learn" && r.pattern) {
    out += "/" + encodeURIComponent(r.pattern);
    if (r.read) {
      out += "/read";
      if (r.anchor) out += "/" + encodeURIComponent(r.anchor);
    } else if (r.sub) {
      out += "/" + encodeURIComponent(r.sub);
    }
  }
  if (r.query) out += encodeQuery(r.query);
  return out;
}

export function isValidSegment(s) { return SEG.test(String(s)); }

/* ---------- live routing ---------- */

const listeners = new Set();
let current = null;
const past = [];     // hashes we navigated away from (for ⌘[)
const future = [];   // hashes undone by back (for ⌘])
let travelling = false;
const MAX_HISTORY = 50;

export function currentRoute() {
  if (current) return current;
  return parse(typeof location !== "undefined" ? location.hash : "");
}

/** Go to a route (object or "#/..." string). Records history unless travelling. */
export function navigate(route, { replace = false } = {}) {
  const hash = typeof route === "string" && route.startsWith("#") ? route : build(route);
  if (typeof location === "undefined") { handle(hash); return; }
  if (location.hash === hash) { handle(hash); return; }
  if (!travelling && !replace && location.hash) {
    past.push(location.hash);
    if (past.length > MAX_HISTORY) past.shift();
    future.length = 0;
  }
  if (replace && typeof history !== "undefined") {
    history.replaceState(null, "", hash);
    handle(hash);
  } else {
    location.hash = hash; // hashchange → handle()
  }
}

export function back() {
  const h = past.pop();
  if (!h) return false;
  if (typeof location !== "undefined") future.push(location.hash);
  travelling = true;
  navigate(h);
  travelling = false;
  return true;
}

export function forward() {
  const h = future.pop();
  if (!h) return false;
  if (typeof location !== "undefined") past.push(location.hash);
  travelling = true;
  navigate(h);
  travelling = false;
  return true;
}

export function canGoBack() { return past.length > 0; }
export function canGoForward() { return future.length > 0; }

function handle(hash) {
  const next = parse(hash);
  const prev = current;
  current = next;
  for (const fn of listeners) fn(next, prev);
}

/** onChange((route, prev) => …) → unsubscribe. */
export function onChange(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

/** Start listening to hashchange and fire once for the current hash. */
export function start(defaultView = "today") {
  if (typeof window === "undefined") return;
  window.addEventListener("hashchange", () => handle(location.hash));
  if (!location.hash) history.replaceState(null, "", build({ view: defaultView }));
  handle(location.hash);
}

/** Tests: feed a hash without a window. */
export function _handleForTests(hash) { handle(hash); }
export function _resetForTests() { past.length = 0; future.length = 0; current = null; listeners.clear(); }
