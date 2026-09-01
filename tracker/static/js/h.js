/* h.js — HTML templating without a framework.
 *
 * `html\`...\`` is a tagged template whose interpolations are escaped by default,
 * so a problem title with `<` or a note with `'` can never break markup. Wrap
 * trusted markup in `raw()` (or nest another `html\`\`` result) to pass it
 * through. `render(el, tpl)` swaps `el.innerHTML` while preserving the focused
 * element, its text selection and the scroll position of the nearest
 * `[data-scroll]` container — so re-rendering a view after a keystroke does not
 * yank the caret or the page around.
 *
 * Pure module: safe to import under node / JavaScriptCore for tests; only
 * `render()` touches the DOM.
 */

const ESC = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;", "`": "&#96;" };

/** Escape text for use in HTML content or a double-quoted attribute. */
export function esc(s) {
  return String(s).replace(/[&<>"'`]/g, (c) => ESC[c]);
}

/** Marker for markup that must NOT be escaped again. */
export class Raw {
  constructor(s) { this.s = s; }
  toString() { return this.s; }
}

export function raw(s) {
  return s instanceof Raw ? s : new Raw(String(s));
}

function val(v) {
  if (v == null || v === false) return "";
  if (v instanceof Raw) return v.s;
  if (Array.isArray(v)) return v.map(val).join("");
  return esc(v);
}

/** html`<b>${title}</b>` → Raw. Arrays join, null/false/undefined vanish. */
export function html(strings, ...values) {
  let out = strings[0];
  for (let i = 0; i < values.length; i++) out += val(values[i]) + strings[i + 1];
  return new Raw(out);
}

/* Attribute-safe URL: only http(s), mailto, same-page anchors and app hashes,
 * or root-relative / relative paths pass; anything else (javascript:, data:)
 * collapses to "#". Returned pre-escaped, so use it inside html`` directly. */
export function attr(url) {
  const s = String(url == null ? "" : url).trim();
  if (/^(https?:|mailto:)/i.test(s) || /^[#/.]/.test(s) || /^[\w-]+(\/|$|\.)/.test(s) && !/^[a-z][a-z0-9+.-]*:/i.test(s)) {
    return new Raw(esc(s));
  }
  return new Raw("#");
}

function focusKey(el) {
  if (!el || el === document.body) return null;
  if (el.id) return { by: "id", v: el.id };
  const k = el.getAttribute && el.getAttribute("data-key");
  return k ? { by: "key", v: k } : null;
}

function findByKey(root, key) {
  if (!key) return null;
  return key.by === "id"
    ? document.getElementById(key.v)
    : root.querySelector(`[data-key="${CSS.escape(key.v)}"]`);
}

/** Replace `el`'s content, keeping focus / selection / scroll where they were. */
export function render(el, tpl) {
  const active = document.activeElement;
  const key = el.contains(active) ? focusKey(active) : null;
  let sel = null;
  if (key && active && typeof active.selectionStart === "number") {
    sel = [active.selectionStart, active.selectionEnd, active.selectionDirection];
  }
  const scroller = el.closest("[data-scroll]");
  const main = document.querySelector("main");
  const tops = [scroller, main].filter(Boolean).map((n) => [n, n.scrollTop]);

  el.innerHTML = String(tpl);

  for (const [n, top] of tops) if (n.scrollTop !== top) n.scrollTop = top;
  const again = findByKey(el, key);
  if (again) {
    again.focus({ preventScroll: true });
    if (sel && typeof again.setSelectionRange === "function") {
      try { again.setSelectionRange(sel[0], sel[1], sel[2] || "none"); } catch (_) { /* not a text input */ }
    }
  }
}
