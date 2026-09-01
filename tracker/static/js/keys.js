/* keys.js — keyboard shortcuts and the named-action bridge.
 *
 * Shortcuts are registered per scope ("global" plus one active view scope) as
 * combos like "mod+1", "shift+arrowleft", "s". `mod` is ⌘ on macOS and Ctrl
 * elsewhere. Plain letter shortcuts are ignored while the user is typing in an
 * input unless registered with `{inInputs: true}` (⌘F wants to work anywhere).
 *
 * Named actions (`defineAction("go", fn)`) are what the native macOS menu calls
 * through `window.Gym.dispatch(name, arg)` — the same functions the in-page
 * shortcuts run, so browser and desktop behave identically. `describe()` feeds
 * the "Keyboard shortcuts" sheet.
 */

export const isMac = (() => {
  if (typeof navigator === "undefined") return true;
  const s = (navigator.platform || "") + " " + (navigator.userAgent || "");
  return /Mac|iPhone|iPad|iPod/.test(s);
})();

export const MOD = isMac ? "meta" : "ctrl";

const KEY_ALIASES = {
  esc: "escape", del: "delete", return: "enter", space: " ", up: "arrowup",
  down: "arrowdown", left: "arrowleft", right: "arrowright", backspace: "backspace",
  cmd: "meta", command: "meta", control: "ctrl", option: "alt", opt: "alt",
};

/** "mod+shift+K" → {key:"k", meta, ctrl, shift, alt} (mod resolved per platform). */
export function normalizeCombo(combo) {
  const parts = String(combo).toLowerCase().split("+").map((p) => p.trim()).filter(Boolean);
  const out = { key: "", meta: false, ctrl: false, shift: false, alt: false };
  for (let p of parts) {
    p = KEY_ALIASES[p] || p;
    if (p === "mod") p = MOD;
    if (p === "meta" || p === "ctrl" || p === "shift" || p === "alt") out[p] = true;
    else out.key = p;
  }
  return out;
}

export function comboId(c) {
  return [c.meta && "meta", c.ctrl && "ctrl", c.alt && "alt", c.shift && "shift", c.key].filter(Boolean).join("+");
}

/** Combo from a keydown-like event {key, metaKey, ctrlKey, shiftKey, altKey}. */
export function comboFromEvent(ev) {
  let key = String(ev.key || "").toLowerCase();
  if (key === " ") key = " ";
  return comboId({ key, meta: !!ev.metaKey, ctrl: !!ev.ctrlKey, shift: !!ev.shiftKey, alt: !!ev.altKey });
}

const SYMBOLS = { meta: "⌘", ctrl: "⌃", alt: "⌥", shift: "⇧" };
const KEY_DISPLAY = {
  " ": "Space", arrowup: "↑", arrowdown: "↓", arrowleft: "←", arrowright: "→",
  escape: "Esc", enter: "↩", backspace: "⌫", delete: "⌦", "/": "/", ",": ",", "[": "[", "]": "]",
};

/** Human-readable form: "⌘1" on mac, "Ctrl+1" elsewhere. */
export function display(combo) {
  const c = typeof combo === "string" ? normalizeCombo(combo) : combo;
  const key = KEY_DISPLAY[c.key] || (c.key.length === 1 ? c.key.toUpperCase() : c.key);
  if (isMac) {
    return (c.ctrl ? SYMBOLS.ctrl : "") + (c.alt ? SYMBOLS.alt : "") + (c.shift ? SYMBOLS.shift : "") + (c.meta ? SYMBOLS.meta : "") + key;
  }
  const mods = [c.ctrl && "Ctrl", c.alt && "Alt", c.shift && "Shift", c.meta && "Win"].filter(Boolean);
  return [...mods, key].join("+");
}

/* ---------- registry ---------- */

const scopes = new Map(); // scope -> Map(comboId -> binding)
let activeScope = "global";

export function register(scope, combo, handler, { inInputs = false, label = "", repeat = false } = {}) {
  const c = normalizeCombo(combo);
  const id = comboId(c);
  if (!scopes.has(scope)) scopes.set(scope, new Map());
  scopes.get(scope).set(id, { combo: c, id, handler, inInputs, label, repeat, scope });
  return () => scopes.get(scope).delete(id);
}

export function setScope(name) { activeScope = name || "global"; }
export function getScope() { return activeScope; }

export function isTyping(target) {
  if (!target) return false;
  const tag = (target.tagName || "").toUpperCase();
  if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return true;
  return Boolean(target.isContentEditable);
}

function lookup(id) {
  const view = scopes.get(activeScope);
  if (view && view.has(id)) return view.get(id);
  const g = scopes.get("global");
  return g ? g.get(id) : undefined;
}

/** Handle a keydown; returns true when a binding ran (event is preventDefault'ed). */
export function handleKeydown(ev) {
  if (ev.defaultPrevented) return false;
  const id = comboFromEvent(ev);
  const b = lookup(id);
  if (!b) return false;
  if (isTyping(ev.target) && !b.inInputs) return false;
  if (ev.repeat && !b.repeat) { if (ev.preventDefault) ev.preventDefault(); return true; }
  if (ev.preventDefault) ev.preventDefault();
  b.handler(ev);
  return true;
}

/** Bindings for the shortcuts sheet: [{scope, combo, display, label}]. */
export function describe() {
  const out = [];
  for (const [scope, map] of scopes) {
    for (const b of map.values()) {
      if (!b.label) continue;
      out.push({ scope, combo: b.id, display: display(b.combo), label: b.label });
    }
  }
  return out;
}

/* ---------- named actions (menu bar ↔ page) ---------- */

const actions = new Map();

export function defineAction(name, fn) { actions.set(name, fn); }

/** Run a named action; unknown names are ignored (returns false). */
export function dispatch(name, arg) {
  const fn = actions.get(name);
  if (!fn) return false;
  fn(arg);
  return true;
}

/** Install the document listener and expose window.Gym.dispatch for the menu. */
export function install() {
  if (typeof document !== "undefined") document.addEventListener("keydown", handleKeydown);
  if (typeof window !== "undefined") {
    window.Gym = Object.assign(window.Gym || {}, { dispatch });
  }
}

export function _resetForTests() { scopes.clear(); actions.clear(); activeScope = "global"; }
