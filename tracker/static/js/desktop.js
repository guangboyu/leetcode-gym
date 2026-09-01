/* desktop.js — the thin bridge to the native window (pywebview).
 *
 * In a browser tab none of this exists and every helper degrades to a no-op
 * or a browser equivalent, so views never branch on "am I in the app" beyond
 * `isDesktop()`. The Python side is tracker/desktop.py (`_Api`). */

function api() {
  const w = typeof window !== "undefined" ? window : {};
  return w.pywebview && w.pywebview.api ? w.pywebview.api : null;
}

export function isDesktop() {
  if (typeof document === "undefined") return false;
  return Boolean(document.documentElement.dataset.shell) || Boolean(api());
}

export function shell() {
  return typeof document === "undefined" ? "" : document.documentElement.dataset.shell || "";
}

/** Native folder picker → path string, or null when cancelled / unavailable. */
export async function chooseFolder() {
  const a = api();
  if (!a || typeof a.choose_folder !== "function") return null;
  try { return (await a.choose_folder()) || null; } catch (_) { return null; }
}

/** macOS "zoom" (title-bar double-click). */
export async function zoom() {
  const a = api();
  if (a && typeof a.zoom === "function") { try { await a.zoom(); } catch (_) { /* ignore */ } }
}

/** Reveal a folder/file in Finder / Explorer. */
export async function openPath(path) {
  const a = api();
  if (a && typeof a.open_path === "function") { try { await a.open_path(path); } catch (_) { /* ignore */ } }
}

export async function revealLog() {
  const a = api();
  if (a && typeof a.reveal_log === "function") { try { await a.reveal_log(); } catch (_) { /* ignore */ } }
}

/** Title-bar behaviour: double-clicking an empty drag strip zooms the window. */
export function installDragRegions() {
  if (typeof document === "undefined") return;
  document.addEventListener("dblclick", (ev) => {
    const t = ev.target;
    if (t && t.classList && t.classList.contains("pywebview-drag-region")) zoom();
  });
}
