/* toast.js — one unobtrusive confirmation at a time.
 *
 * Marking a problem shows "Solved · Two Sum · next review in 4 days [Undo]".
 * There is a single action toast on screen: a new one replaces the previous
 * (the previous action stays undoable server-side, just not from the toast).
 * `current()` returns the visible toast so ⌘Z can run its action. Errors use
 * kind "error", are announced assertively and stay until dismissed.
 *
 * Markup: <div id="toast-root"><div class="toast" role="status">…</div></div>
 */

import { html, render } from "./h.js";

let root = null;
let live = null;
let timer = null;

function ensureRoot() {
  if (root && root.isConnected) return root;
  root = document.getElementById("toast-root");
  if (!root) {
    root = document.createElement("div");
    root.id = "toast-root";
    document.body.appendChild(root);
  }
  return root;
}

function clearTimer() {
  if (timer) { clearTimeout(timer); timer = null; }
}

/** show({text, detail, kind: "info"|"success"|"error", action: {label, combo, run}, timeout}) */
export function show({ text, detail = "", kind = "info", action = null, timeout } = {}) {
  const el = ensureRoot();
  clearTimer();
  const id = Symbol("toast");
  live = { id, text, action, kind };
  const ms = timeout ?? (kind === "error" ? 0 : 6000);
  render(el, html`
    <div class="toast toast--${kind}" role="${kind === "error" ? "alert" : "status"}" aria-live="${kind === "error" ? "assertive" : "polite"}">
      <span class="toast__icon" aria-hidden="true"></span>
      <span class="toast__body"><b>${text}</b>${detail ? html` <span class="toast__detail">${detail}</span>` : ""}</span>
      ${action ? html`<button type="button" class="btn sm toast__action" data-toast-action>${action.label}${action.combo ? html`<kbd>${action.combo}</kbd>` : ""}</button>` : ""}
      <button type="button" class="btn ghost sm toast__close" data-toast-close aria-label="Dismiss">×</button>
    </div>`);
  const btn = el.querySelector("[data-toast-action]");
  if (btn) btn.addEventListener("click", () => runAction());
  el.querySelector("[data-toast-close]").addEventListener("click", dismiss);
  if (ms > 0) timer = setTimeout(dismiss, ms);
  return id;
}

export function error(text, detail) {
  return show({ text, detail, kind: "error" });
}

/** Run the visible toast's action (Undo) and dismiss it. Returns true if it ran. */
export function runAction() {
  if (!live || !live.action) return false;
  const run = live.action.run;
  dismiss();
  run();
  return true;
}

export function current() { return live; }

export function dismiss() {
  clearTimer();
  live = null;
  if (root) root.innerHTML = "";
}
