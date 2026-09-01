/* settings.js — a full view (⌘,), not a dialog.
 *
 * Storage comes first because it is the one thing that can lose data: the
 * progress folder can be moved to a synced folder and two histories merge
 * losslessly (append-only event log). Everything else is a preference stored
 * in settings.json next to the progress, so it syncs too. */
import { html, render, raw } from "../h.js";
import { icon } from "../components/status.js";
import { fmtInt } from "../format.js";

const CAPS = [1400, 1500, 1600, 1700, 1800, 2000, 2200, 2400];
let about = null;

function syncedName(dir) {
  const m = /(dropbox|icloud|onedrive|google ?drive)/i.exec(dir || "");
  if (!m) return null;
  const k = m[1].toLowerCase().replace(/\s/g, "");
  return { dropbox: "Dropbox", icloud: "iCloud Drive", onedrive: "OneDrive", googledrive: "Google Drive" }[k] || m[1];
}

async function applyDir(ctx, el, path) {
  const msg = el.querySelector("#sync-msg");
  if (!path) return;
  try {
    const res = await ctx.api.setDataDir(path);
    ctx.store.set({ dataDir: res.path, progress: res.progress || ctx.store.get().progress });
    ctx.store.bump("progressVersion");
    const settings = await ctx.api.getSettings();
    ctx.store.set({ settings }); ctx.store.bump("settingsVersion");
    ctx.toast.show({ text: "Progress folder changed", detail: res.path, kind: "success" });
  } catch (err) {
    if (msg) msg.textContent = `Couldn't use that folder: ${err.message}`;
    ctx.toast.show({ text: "Couldn't switch folder", detail: err.message, kind: "error" });
  }
}

export default {
  id: "settings",
  title: "Settings",
  routes: ["settings"],
  deps: ["settingsVersion", "dataDir"],

  mount(el, ctx) {
    el.addEventListener("click", async (ev) => {
      const t = ev.target.closest("[data-set]");
      if (!t) return;
      const what = t.dataset.set;
      if (what === "choose") {
        const p = await ctx.desktop.chooseFolder();
        if (p) applyDir(ctx, el, p);
        else if (!ctx.desktop.isDesktop()) { const i = el.querySelector("#manual-path"); if (i) { i.focus(); el.querySelector("#sync-msg").textContent = "The native picker needs the desktop app — paste a folder path instead."; } }
      } else if (what === "apply-path") applyDir(ctx, el, el.querySelector("#manual-path").value.trim());
      else if (what === "open-dir") ctx.desktop.openPath(ctx.store.get().dataDir);
      else if (what === "theme") ctx.settings.set({ theme: t.dataset.v });
      else if (what === "optional") ctx.settings.set({ routeShowOptional: t.getAttribute("aria-pressed") !== "true" });
      else if (what === "shortcuts") ctx.shortcuts();
      else if (what === "reset") {
        ctx.toast.show({ text: "Reset all preferences?", detail: "Cap, skipped subtopics, drill defaults and theme go back to defaults. Progress is never touched.", kind: "info", timeout: 10000,
          action: { label: "Reset", run: async () => { const s = await ctx.api.resetSettings(); ctx.store.set({ settings: s }); ctx.store.bump("settingsVersion"); ctx.toast.show({ text: "Preferences reset", kind: "success" }); } } });
      } else if (what === "unskip") ctx.settings.set({ routeSkipped: [] });
    });
    el.addEventListener("change", (ev) => {
      const t = ev.target;
      if (t.id === "set-cap") ctx.settings.set({ cap: t.value === "none" ? null : Number(t.value) });
      if (t.id === "set-lo" || t.id === "set-hi") {
        const lo = Number(el.querySelector("#set-lo").value) || null, hi = Number(el.querySelector("#set-hi").value) || null;
        ctx.settings.set({ drillLo: lo, drillHi: hi });
      }
    });
    el.addEventListener("keydown", (ev) => { if (ev.key === "Enter" && ev.target.id === "manual-path") applyDir(ctx, el, ev.target.value.trim()); });
    ctx.api.getAbout().then((a) => { about = a; ctx.store.bump("settingsVersion"); }).catch(() => {});
  },

  render(el, ctx) {
    const s = ctx.store.get();
    const st = s.settings;
    const cap = ctx.store.cap(s);
    const dir = s.dataDir || "";
    const synced = syncedName(dir);
    const desktop = ctx.desktop.isDesktop();
    const skipped = (st.routeSkipped || []).length;
    render(el, html`<div class="view wide"><div class="setgrid">
      <div>
        <div class="card">
          <div class="hd">Storage</div>
          <div class="set"><div class="k">Progress folder<span class="sub">Point it at Dropbox or iCloud Drive to sync between machines. Histories merge; nothing is lost.</span></div>
            <div class="v"><span class="mono" title="${dir}">${dir || "…"}</span>
              <button type="button" class="btn" data-set="choose">${icon("folder")}Choose folder…</button>
              ${desktop ? html`<button type="button" class="btn ghost" data-set="open-dir">Open</button>` : ""}
              ${desktop ? "" : html`<label class="field grow"><input id="manual-path" type="text" placeholder="…or paste a folder path"></label><button type="button" class="btn" data-set="apply-path">Use</button>`}
              <span id="sync-msg" class="sub"></span></div></div>
          <div class="set"><div class="k">Sync</div><div class="v">${synced ? html`<span class="chip help">Synced via ${synced}</span>` : html`<span class="chip new">Local only</span><span class="sub">Choose a folder inside a cloud drive to sync.</span>`}</div></div>
        </div>
        <div class="card">
          <div class="hd">Study</div>
          <div class="set"><div class="k">Rating cap<span class="sub">Hides 0x3F extension problems rated above this until you raise it.</span></div>
            <div class="v"><select id="set-cap" class="select" aria-label="Rating cap">${CAPS.map((c) => html`<option value="${c}"${cap === c ? raw(" selected") : ""}>${c}</option>`)}<option value="none"${cap == null ? raw(" selected") : ""}>none</option></select></div></div>
          <div class="set"><div class="k">Optional subtopics</div><div class="v"><button type="button" class="toggle" data-set="optional" aria-pressed="${Boolean(st.routeShowOptional)}"><span class="knob"></span>Show rarely-asked 0x3F sections</button></div></div>
          <div class="set"><div class="k">Skipped subtopics</div><div class="v"><span class="sub">${skipped ? `${skipped} skipped` : "None skipped"}</span>${skipped ? html`<button type="button" class="btn sm" data-set="unskip">Restore all</button>` : ""}</div></div>
          <div class="set"><div class="k">Drill defaults<span class="sub">Rating range for random drills.</span></div>
            <div class="v"><input id="set-lo" class="numin" type="number" min="1000" max="3000" step="50" value="${st.drillLo || 1300}" aria-label="Minimum rating"><span class="sub">to</span><input id="set-hi" class="numin" type="number" min="1000" max="3000" step="50" value="${st.drillHi || 1800}" aria-label="Maximum rating"></div></div>
        </div>
      </div>
      <div>
        <div class="card">
          <div class="hd">Appearance</div>
          <div class="set"><div class="k">Theme</div><div class="v"><div class="segc" role="group" aria-label="Theme">${["system", "light", "dark"].map((t) => html`<button type="button" data-set="theme" data-v="${t}" aria-pressed="${(st.theme || "system") === t}">${t[0].toUpperCase() + t.slice(1)}</button>`)}</div></div></div>
          <div class="set"><div class="k">Keyboard</div><div class="v"><button type="button" class="btn" data-set="shortcuts">Show shortcuts <kbd>${ctx.keys.display("mod+/")}</kbd></button></div></div>
        </div>
        <div class="card">
          <div class="hd">About</div>
          <div class="set"><div class="k">LeetCode Gym</div><div class="v sub">${about ? html`${about.version} · problems snapshot ${about.problemsSnapshot || "—"} · ${fmtInt(about.problems)} problems` : "…"}</div></div>
          ${about ? html`<div class="set"><div class="k">Config file</div><div class="v"><span class="mono" title="${about.configFile}">${about.configFile}</span></div></div>` : ""}
          <div class="set"><div class="k">Lists by</div><div class="v sub"><a href="https://leetcode.com" target="_blank" rel="noopener">LeetCode</a> · <a href="https://neetcode.io" target="_blank" rel="noopener">NeetCode</a> · <a href="https://github.com/EndlessCheng" target="_blank" rel="noopener">灵茶山艾府 (0x3F)</a> · ratings by <a href="https://zerotrac.github.io/leetcode_problem_rating/" target="_blank" rel="noopener">zerotrac</a></div></div>
          <div class="set"><div class="k">Source</div><div class="v sub"><a href="https://github.com/guangboyu/leetcode-study-tracker" target="_blank" rel="noopener">github.com/guangboyu/leetcode-study-tracker</a> · MIT</div></div>
          <div class="set"><div class="k">Reset</div><div class="v"><button type="button" class="btn danger" data-set="reset">Reset preferences…</button><span class="sub">Progress is never touched.</span></div></div>
        </div>
      </div>
    </div></div>`);
  },

  unmount() {},
};
