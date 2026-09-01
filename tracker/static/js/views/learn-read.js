/* views/learn-read.js — the tutorial itself, rendered in-app.
 *
 * Sticky table of contents on the left, the article on the right. The
 * markdown is fetched once per file and rendered through md.js; the problem
 * tables inside it become live tracker rows (same row component as every
 * other table), python code is highlighted, mermaid diagrams render lazily.
 *
 * Route: #/learn/<pattern>/read[/<anchor>]. Anchor changes (TOC clicks, in-
 * article links, ⌘[ / ⌘]) only scroll — the article is not rebuilt. */
import { html, raw, render } from "../h.js";
import { renderTutorial, runMermaid } from "../md.js";
import { rowHtml, patchRow, attachCursor } from "../components/problem-table.js";
import { icon } from "../components/status.js";

const READ_COLUMNS = ["id", "title", "level", "freq", "status", "actions"];
const mdCache = new Map();          // file -> markdown text (promise)
let current = null;                 // {file, patternId, root, observer, cursor, unsub}

/** Toolbar for reading mode: back link + tutorial title. */
export function readToolbar(sel) {
  const p = sel.pattern;
  return html`<a class="btn ghost" href="#/learn/${p.id}/${sel.sub || ""}">← Back to practice</a><h1>${p.name}</h1><span class="sub">tutorial</span>`;
}

/** Headings worth a TOC entry: H2 and H3, minus the H1 title. */
export function tocEntries(headings) {
  return (headings || []).filter((h) => h.level === 2 || h.level === 3);
}

/** id → row meta ({freq, note_md, state, paid}) from a tutorial's shape tables. */
export function metaById(tutorial) {
  const out = new Map();
  for (const s of (tutorial && tutorial.shapes) || []) {
    for (const pr of s.problems || []) out.set(pr.id, { freq: pr.freq, note_md: pr.note_md, state: pr.state, paid: Boolean(pr.paid), shape: s.id });
  }
  return out;
}

function tocHtml(sel, headings, active) {
  const p = sel.pattern;
  return html`<nav class="toc" aria-label="Contents">
    <a class="back" href="#/learn/${p.id}/${sel.sub || ""}">← Back to practice</a>
    ${tocEntries(headings).map((h) => html`<a class="${h.level === 3 ? "h3" : ""}" href="#/learn/${p.id}/read/${h.anchor}" data-toc="${h.anchor}"${h.anchor === active ? raw(' aria-current="true"') : ""}>${h.text}</a>`)}
  </nav>`;
}

function loadMarkdown(ctx, file) {
  if (!mdCache.has(file)) {
    const pr = ctx.api.getTutorialMarkdown(file).catch((err) => { mdCache.delete(file); throw err; });
    mdCache.set(file, pr);
  }
  return mdCache.get(file);
}

/* Turn md.js's LC tables into the app's table component: our header, our rows. */
function upgradeTables(root) {
  root.querySelectorAll("table[data-lc-table]").forEach((t) => {
    t.className = "tbl compact";
    const head = t.querySelector("thead");
    if (head) head.innerHTML = '<tr><th>#</th><th>Problem</th><th>Level</th><th>Freq</th><th>Status</th><th class="right"></th></tr>';
    if (!t.parentElement.classList.contains("table-wrap")) {
      const wrap = document.createElement("div");
      wrap.className = "table-wrap";
      t.replaceWith(wrap);
      wrap.appendChild(t);
    }
  });
}

/* Scroll the article (only the article — never the page) so `anchor` sits at the top. */
function scrollToAnchor(root, anchor) {
  if (!anchor) { root.scrollTop = 0; return; }
  const target = root.querySelector("#" + CSS.escape(anchor));
  if (!target) return;
  const y = target.getBoundingClientRect().top - root.getBoundingClientRect().top + root.scrollTop - 12;
  root.scrollTop = Math.max(0, y);
}

function watchHeadings(root, onActive) {
  if (typeof IntersectionObserver === "undefined") return null;
  const heads = [...root.querySelectorAll("h2[id], h3[id]")];
  const visible = new Map();
  const obs = new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (e.isIntersecting) visible.set(e.target.id, e.boundingClientRect.top);
      else visible.delete(e.target.id);
    }
    if (!visible.size) return;
    const top = [...visible.entries()].sort((a, b) => a[1] - b[1])[0][0];
    onActive(top);
  }, { root: root.closest("[data-scroll]"), rootMargin: "0px 0px -70% 0px", threshold: 0 });
  heads.forEach((h) => obs.observe(h));
  return obs;
}

function setActiveToc(el, anchor) {
  el.querySelectorAll(".toc a[data-toc]").forEach((a) => {
    if (a.dataset.toc === anchor) { a.setAttribute("aria-current", "true"); a.scrollIntoView({ block: "nearest" }); }
    else a.removeAttribute("aria-current");
  });
}

/** Render (or just re-scroll) the reading layout into `el`. */
export function mountRead(el, ctx, sel, opts = {}) {
  const p = sel.pattern;
  const file = p.tutorialFile;
  const s = ctx.store.get();
  const tutorial = s.tutorials && s.tutorials.tutorials ? s.tutorials.tutorials[p.id] : null;
  if (!file || !tutorial) {
    unmountRead(el);
    render(el, html`<div class="split"><div class="col">${opts.patternList ? opts.patternList() : ""}</div>
      <div class="main"><div class="view"><div class="empty"><b>Tutorial in progress</b><span>A written walkthrough for ${p.name} is coming. The practice page has the curated subtopics meanwhile.</span><a class="btn" href="#/learn/${p.id}">Back to practice</a></div></div></div></div>`);
    return;
  }

  // Same tutorial already on screen: only the anchor changed.
  if (current && current.file === file && el.contains(current.root)) {
    scrollToAnchor(current.root, sel.anchor);
    setActiveToc(el, sel.anchor);
    return;
  }
  unmountRead(el);

  const headings = tutorial.headings;
  render(el, html`<div class="split read-split">
    <div class="col">${opts.patternList ? opts.patternList() : ""}</div>
    <div class="read" data-file="${file}">
      ${tocHtml(sel, headings, sel.anchor)}
      <div class="article" data-scroll><div class="skeleton" aria-busy="true"><i style="width:60%"></i><i></i><i style="width:90%"></i><i style="width:40%"></i></div></div>
    </div>
  </div>`);
  const root = el.querySelector(".article");
  current = { file, patternId: p.id, root, observer: null, cursor: null, unsub: null };
  const mine = current;

  const metas = metaById(tutorial);
  const rowRenderer = (id) => {
    const slug = s.byId.get(id);
    if (!slug) return null;
    const meta = metas.get(id) || {};
    const m = { ...meta, note_html: meta.note_md ? inlineNote(meta.note_md) : "" };
    return String(rowHtml([slug, s.problems[slug], m], { columns: READ_COLUMNS, hints: true }));
  };

  loadMarkdown(ctx, file).then((md) => {
    if (current !== mine) return;                 // navigated away meanwhile
    const out = renderTutorial(md, tutorial, { rowRenderer });
    root.innerHTML = out.html;
    upgradeTables(root);
    if (out.hasMermaid) runMermaid(root, { themeVariables: mermaidTheme() }).catch(() => {});
    scrollToAnchor(root, sel.anchor);
    setActiveToc(el, sel.anchor);
    mine.observer = watchHeadings(root, (anchor) => setActiveToc(el, anchor));
    mine.cursor = attachCursor(root, { onMark: (slug, action) => Promise.resolve(ctx.mark(slug, action)).then(() => (ctx.patchRows ? ctx.patchRows(slug) : patchRow(slug))).catch(() => {}) });
    mine.unsub = ctx.store.subscribe(() => {
      root.querySelectorAll("tr[data-slug]").forEach((tr) => patchRow(tr.dataset.slug, root));
    }, ["progressVersion", "dateVersion"]);
    root.addEventListener("click", onArticleClick);
  }).catch((err) => {
    if (current !== mine) return;
    root.innerHTML = "";
    render(root, html`<div class="empty"><b>Couldn't load the tutorial.</b><span>${err && err.message ? err.message : String(err)}</span><a class="btn" href="#/learn/${p.id}/read">Retry</a></div>`);
  });

  function onArticleClick(ev) {
    const a = ev.target.closest("a[data-anchor]");
    if (!a) return;
    ev.preventDefault();
    ctx.navigate({ view: "learn", pattern: p.id, read: true, anchor: a.dataset.anchor });
  }
}

function inlineNote(md) {
  const m = globalThis.marked;
  return m && m.parseInline ? m.parseInline(md) : md;
}

/** Mermaid colors from the current tokens so diagrams follow light/dark. */
function mermaidTheme() {
  if (typeof getComputedStyle === "undefined") return {};
  const cs = getComputedStyle(document.documentElement);
  const v = (n) => cs.getPropertyValue(n).trim();
  return {
    primaryColor: v("--accent-soft") || "#DBEAFE", primaryTextColor: v("--text") || "#171A1F",
    primaryBorderColor: v("--accent") || "#2563EB", lineColor: v("--text-3") || "#9AA1AB",
    secondaryColor: v("--surface-2") || "#F8F9FB", tertiaryColor: v("--surface-3") || "#F4F5F7",
    background: v("--surface") || "#FFFFFF", fontSize: "13px",
  };
}

/** Tear down observers/subscriptions when leaving reading mode. */
export function unmountRead(el) {
  if (!current) return;
  if (current.observer) current.observer.disconnect();
  if (current.cursor) current.cursor.detach();
  if (current.unsub) current.unsub();
  current = null;
}

export { icon as _icon };
