/* problem-table.js — the one table every view uses.
 *
 * `tableHtml(rows, opts)` renders a `<table class="tbl">`; `patchRow(slug)`
 * updates just the status + action cells of every row for that slug that is
 * currently in the DOM (after a mark, nothing else moves); `cursor` gives a
 * table keyboard navigation (j/k, ↑/↓, Enter, s/h/f/r) with aria-selected.
 *
 * Columns are chosen by `opts.columns` (array of ids, in order):
 *   id · title · level · freq · status · actions
 * rows: [slug, problem, meta?][]  where meta = {freq, note_md, state, paid}
 * (tutorial rows) or undefined. */
import { html, raw } from "../h.js";
import { get } from "../store.js";
import { chipHtml, levelHtml, freqHtml, actionsHtml, titleHtml, icon } from "./status.js";

export const DEFAULT_COLUMNS = ["id", "title", "level", "status", "actions"];

const HEAD = {
  id: "#", title: "Problem", level: "Level", freq: "Freq", status: "Status", actions: "",
};

function cell(col, slug, p, meta, opts, s) {
  switch (col) {
    case "id": return html`<td class="id num">${p.id}</td>`;
    case "title": return html`<td class="title">${titleHtml(slug, p, { hint: meta && meta.note_html, hintsOn: opts.hints !== false, badges: opts.badges !== false })}</td>`;
    case "level": return html`<td class="lvl">${levelHtml(p)}</td>`;
    case "freq": return html`<td class="freq-cell">${freqHtml(meta && meta.freq)}</td>`;
    case "status": return html`<td class="status">${chipHtml(slug, s)}</td>`;
    case "actions": return html`<td class="right actions">${actionsHtml(slug, s)}</td>`;
    default: return html`<td></td>`;
  }
}

/** One `<tr data-slug>`; `opts.cursor` marks the keyboard-selected row. */
export function rowHtml(row, opts = {}, s = get()) {
  const [slug, p, meta] = row;
  const cols = opts.columns || DEFAULT_COLUMNS;
  const selected = opts.cursor === slug;
  return html`<tr data-slug="${slug}" data-key="row:${slug}"${selected ? raw(' aria-selected="true"') : ""}>${cols.map((c) => cell(c, slug, p, meta, opts, s))}</tr>`;
}

/** Full table. opts: {columns, hints, badges, sticky, sort:{col, dir}, sortable:[cols], compact, cursor, empty} */
export function tableHtml(rows, opts = {}, s = get()) {
  const cols = opts.columns || DEFAULT_COLUMNS;
  if (!rows.length) {
    return html`<div class="empty">${opts.empty || "No problems here."}</div>`;
  }
  const sortable = new Set(opts.sortable || []);
  const sort = opts.sort || {};
  return html`<div class="table-wrap"><table class="tbl${opts.sticky ? " sticky" : ""}${opts.compact ? " compact" : ""}" role="grid" tabindex="0" data-table>
    ${opts.noHead ? "" : html`<thead><tr>${cols.map((c) => {
      const isSort = sortable.has(c);
      const active = sort.col === c;
      return html`<th class="${c === "actions" ? "right" : ""}${isSort ? " sortable" : ""}"${isSort ? raw(` data-act="sort" data-col="${c}"`) : ""}${active ? raw(` aria-sort="${sort.dir === "desc" ? "descending" : "ascending"}"`) : ""}>${HEAD[c]}${active ? icon("sort") : ""}</th>`;
    })}</tr></thead>`}
    <tbody>${rows.map((r) => rowHtml(r, opts, s))}</tbody>
  </table></div>`;
}

/** After a mark: refresh the status + action cells of every visible row for `slug`. */
export function patchRow(slug, root = document) {
  const s = get();
  root.querySelectorAll(`tr[data-slug="${CSS.escape(slug)}"]`).forEach((tr) => {
    const st = tr.querySelector("td.status");
    const ac = tr.querySelector("td.actions");
    if (st) st.innerHTML = String(chipHtml(slug, s));
    if (ac) ac.innerHTML = String(actionsHtml(slug, s));
  });
}

/** Collapse-and-remove a row (Today's due list after marking). Resolves when gone. */
export function leaveRow(tr) {
  return new Promise((resolve) => {
    if (!tr) return resolve();
    const reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) { tr.remove(); return resolve(); }
    tr.classList.add("leaving");
    setTimeout(() => { tr.remove(); resolve(); }, 260);
  });
}

/* ---------- keyboard cursor ----------
 * One cursor per table root. `attach(root, {onOpen, onMark})` wires j/k/↑/↓,
 * Enter/o (open on LeetCode), s/h/f/r (mark). Returns {move, current, detach}. */
export function attachCursor(root, { onMark } = {}) {
  let current = null;
  const rows = () => Array.from(root.querySelectorAll("tr[data-slug]"));
  function select(tr) {
    rows().forEach((r) => r.removeAttribute("aria-selected"));
    current = tr ? tr.dataset.slug : null;
    if (tr) {
      tr.setAttribute("aria-selected", "true");
      tr.scrollIntoView({ block: "nearest" });
    }
  }
  function move(delta) {
    const rs = rows();
    if (!rs.length) return;
    let i = rs.findIndex((r) => r.dataset.slug === current);
    i = i < 0 ? (delta > 0 ? 0 : rs.length - 1) : Math.min(rs.length - 1, Math.max(0, i + delta));
    select(rs[i]);
  }
  function onKey(ev) {
    if (ev.metaKey || ev.ctrlKey || ev.altKey) return;
    const t = ev.target;
    if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.tagName === "SELECT" || t.isContentEditable)) return;
    const k = ev.key;
    if (k === "j" || k === "ArrowDown") { move(1); ev.preventDefault(); }
    else if (k === "k" || k === "ArrowUp") { move(-1); ev.preventDefault(); }
    else if ((k === "Enter" || k === "o") && current) {
      const a = root.querySelector(`tr[data-slug="${CSS.escape(current)}"] a[data-act="open"]`);
      if (a) { window.open(a.href, "_blank", "noopener"); ev.preventDefault(); }
    } else if ("shfr".includes(k) && k.length === 1 && current && onMark) {
      const action = { s: "solved", h: "solved_help", f: "forgotten", r: "reset" }[k];
      onMark(current, action); ev.preventDefault();
    } else if (k === "Escape" && current) { select(null); }
  }
  root.addEventListener("keydown", onKey);
  root.addEventListener("click", (ev) => {
    const tr = ev.target.closest && ev.target.closest("tr[data-slug]");
    if (tr && root.contains(tr) && !ev.target.closest("button, a")) select(tr);
  });
  return {
    move, current: () => current, select,
    restore() { const tr = current && root.querySelector(`tr[data-slug="${CSS.escape(current)}"]`); if (tr) select(tr); },
    detach() { root.removeEventListener("keydown", onKey); },
  };
}
