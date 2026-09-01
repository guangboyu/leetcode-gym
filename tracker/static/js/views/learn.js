/* learn.js — placeholder; the Learn tab is implemented separately and
 * replaces this file wholesale. Keeps the shell bootable meanwhile. */
import { html, render } from "../h.js";

export default {
  id: "learn",
  title: "Learn",
  routes: ["learn"],
  deps: ["progressVersion", "settingsVersion"],
  mount() {},
  render(el) {
    render(el, html`<div class="view"><div class="empty">Loading Learn…</div></div>`);
  },
  toolbar() { return null; },
  unmount() {},
};
