/* md.js — render a tutorial's markdown into the app.
 *
 * Uses the vendored `marked` (global `marked` from vendor/marked.umd.js) with a
 * custom renderer instead of post-processing DOM, so the same code runs in the
 * page and in headless tests:
 *   - heading ids come from data/tutorials.json (`meta.headings[].anchor`, the
 *     Python slug rule) in document order, so #links, the TOC and deep links
 *     all agree;
 *   - `Name.md` links become in-app routes (#/learn/<pattern>), `#anchor` links
 *     stay in-article, external links open in a new tab;
 *   - `assets/…` images are rewritten to /tutorials/assets/…, lazy-loaded, and an
 *     image followed by an italic paragraph becomes <figure>/<figcaption>;
 *   - python fences are highlighted by pyhl.js and get a copy button, mermaid
 *     fences become <div class="mermaid"> (rendered later by ensureMermaid()),
 *     other fences are ASCII diagrams;
 *   - tables whose first header is `LC` are the tutorial's problem lists: each
 *     row is handed to `opts.rowRenderer(id, row)` so the live tracker row can
 *     replace it; other tables render normally.
 */

import { esc } from "./h.js";
import { highlight } from "./pyhl.js";

/** GitHub-ish anchor slug; mirrors scripts/build_tutorials.py (fallback only). */
export function slugify(text, used) {
  let s = String(text).toLowerCase().replace(/[^\p{L}\p{N}_\- ]/gu, "").trim().replace(/ +/g, "-");
  if (used) {
    let base = s, n = 1;
    while (used.has(s)) s = `${base}-${n++}`;
    used.add(s);
  }
  return s;
}

/** "SlidingWindow.md" → "sliding-window" (same rule as the build script). */
export function patternIdFromFile(file) {
  const stem = String(file).replace(/\.md$/i, "");
  return stem.replace(/(?<=[a-z0-9])(?=[A-Z])/g, "-").toLowerCase();
}

function plainText(tokens) {
  return (tokens || []).map((t) => (t.tokens ? plainText(t.tokens) : t.text || "")).join("");
}

/* Mark "image paragraph + italic caption paragraph" pairs as figures. */
function markFigures(tokens) {
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (t.type !== "paragraph" || !t.tokens) continue;
    const inline = t.tokens.filter((x) => !(x.type === "text" && !x.text.trim()));
    if (inline.length === 1 && inline[0].type === "image") {
      t.figure = inline[0];
      let j = i + 1;
      while (tokens[j] && tokens[j].type === "space") j++; // blank lines between the two
      const next = tokens[j];
      if (next && next.type === "paragraph" && next.tokens) {
        const ni = next.tokens.filter((x) => !(x.type === "text" && !x.text.trim()));
        if (ni.length === 1 && ni[0].type === "em") {
          t.caption = ni[0].tokens;
          next.skip = true;
        }
      }
    }
  }
}

/**
 * renderTutorial(markdown, meta, opts) → {html, headings, hasMermaid, lcTables}
 *   meta: entry from data/tutorials.json (headings[], file) — may be null
 *   opts.rowRenderer(id, {cells, headers, raw}) → html string | null (null = default row)
 *   opts.assetBase (default "/tutorials/"), opts.patternIdFor(file), opts.marked
 */
export function renderTutorial(markdown, meta, opts = {}) {
  const marked = opts.marked || globalThis.marked;
  if (!marked) throw new Error("marked is not loaded (vendor/marked.umd.js)");
  const assetBase = opts.assetBase || "/tutorials/";
  const patternIdFor = opts.patternIdFor || patternIdFromFile;
  const anchors = (meta && meta.headings ? meta.headings : []).map((h) => h.anchor);
  const used = new Set();
  const headings = [];
  let hi = 0;
  let hasMermaid = false;
  const lcTables = [];

  const renderer = {
    heading({ tokens, depth }) {
      const text = plainText(tokens);
      const id = hi < anchors.length ? anchors[hi] : slugify(text, used);
      used.add(id);
      hi++;
      headings.push({ level: depth, text, anchor: id });
      return `<h${depth} id="${esc(id)}">${this.parser.parseInline(tokens)}</h${depth}>\n`;
    },
    paragraph(token) {
      if (token.skip) return "";
      if (token.figure) {
        const img = this.parser.parseInline([token.figure]);
        const cap = token.caption ? `<figcaption>${this.parser.parseInline(token.caption)}</figcaption>` : "";
        return `<figure>${img}${cap}</figure>\n`;
      }
      return false;
    },
    image({ href, title, text }) {
      let src = href || "";
      if (/^assets\//.test(src)) src = assetBase + src;
      if (!/^(https?:|\/|data:image\/)/i.test(src)) src = assetBase + src.replace(/^\.\//, "");
      return `<img src="${esc(src)}" alt="${esc(text || "")}"${title ? ` title="${esc(title)}"` : ""} loading="lazy" decoding="async">`;
    },
    link({ href, title, tokens }) {
      const text = this.parser.parseInline(tokens);
      const t = title ? ` title="${esc(title)}"` : "";
      const h = String(href || "");
      if (h.startsWith("#")) {
        return `<a href="${esc(h)}" data-anchor="${esc(h.slice(1))}"${t}>${text}</a>`;
      }
      const md = /^([A-Za-z0-9_-]+\.md)(#(.+))?$/.exec(h);
      if (md) {
        const pid = patternIdFor(md[1]);
        const route = md[3] ? `#/learn/${pid}/read/${md[3]}` : `#/learn/${pid}`;
        return `<a href="${esc(route)}" data-route="${esc(route)}"${t}>${text}</a>`;
      }
      if (/^https?:\/\//i.test(h)) {
        return `<a href="${esc(h)}" target="_blank" rel="noopener"${t}>${text}</a>`;
      }
      return `<a href="${esc(h)}"${t}>${text}</a>`;
    },
    code({ text, lang }) {
      const l = (lang || "").trim().toLowerCase();
      if (l === "python" || l === "py") {
        return `<div class="codeblock"><button type="button" class="btn ghost sm copy" data-copy aria-label="Copy code">Copy</button><pre class="code py"><code>${highlight(text)}</code></pre></div>\n`;
      }
      if (l === "mermaid") {
        hasMermaid = true;
        return `<div class="mermaid" data-src="${esc(text)}">${esc(text)}</div>\n`;
      }
      return `<pre class="code ascii"><code>${esc(text)}</code></pre>\n`;
    },
    table(token) {
      const headers = token.header.map((c) => plainText(c.tokens).trim());
      if (headers[0] !== "LC") return false;
      const rows = token.rows.map((cells) => {
        const id = parseInt(plainText(cells[0].tokens), 10);
        const rendered = cells.map((c) => this.parser.parseInline(c.tokens));
        const byName = {};
        headers.forEach((h, i) => { byName[h] = rendered[i]; });
        return { id, cells: rendered, headers, byName, raw: cells.map((c) => plainText(c.tokens)) };
      });
      lcTables.push({ headers, ids: rows.map((r) => r.id) });
      let head = headers.map((h) => `<th>${esc(h)}</th>`).join("");
      let body = "";
      for (const row of rows) {
        const custom = opts.rowRenderer ? opts.rowRenderer(row.id, row) : null;
        if (custom != null) { body += String(custom); continue; }
        body += `<tr data-lc="${row.id}">${row.cells.map((c) => `<td>${c}</td>`).join("")}</tr>\n`;
      }
      return `<table class="lc-table" data-lc-table>\n<thead><tr>${head}</tr></thead>\n<tbody>${body}</tbody></table>\n`;
    },
  };

  const m = new marked.Marked({ gfm: true, breaks: false });
  m.use({ renderer });
  const tokens = m.lexer(markdown);
  markFigures(tokens);
  const out = m.parser(tokens);
  return { html: out, headings, hasMermaid, lcTables };
}

/* ---------- mermaid (lazy) ---------- */

let mermaidLoading = null;

/** Load vendor/mermaid.min.js once and initialise it; resolves to the mermaid global. */
export function ensureMermaid({ src = "vendor/mermaid.min.js", themeVariables = {} } = {}) {
  if (globalThis.mermaid && mermaidLoading) return mermaidLoading;
  if (!mermaidLoading) {
    mermaidLoading = new Promise((resolve, reject) => {
      if (globalThis.mermaid) return resolve(globalThis.mermaid);
      const s = document.createElement("script");
      s.src = src;
      s.onload = () => resolve(globalThis.mermaid);
      s.onerror = () => reject(new Error("mermaid failed to load"));
      document.head.appendChild(s);
    }).then((mm) => {
      mm.initialize({
        startOnLoad: false,
        securityLevel: "loose",   // the tutorials use <br/> and <b> inside labels
        theme: "base",
        themeVariables: Object.assign({ fontFamily: "-apple-system, system-ui, sans-serif" }, themeVariables),
      });
      return mm;
    });
  }
  return mermaidLoading;
}

/** Render every .mermaid block under `root`; on failure show the source instead. */
export async function runMermaid(root, opts) {
  const nodes = [...root.querySelectorAll(".mermaid:not([data-processed])")];
  if (!nodes.length) return;
  try {
    const mm = await ensureMermaid(opts);
    await mm.run({ nodes });
  } catch (err) {
    for (const n of nodes) {
      if (n.querySelector("svg")) continue;
      const pre = document.createElement("pre");
      pre.className = "code ascii";
      pre.textContent = n.getAttribute("data-src") || n.textContent;
      n.replaceWith(pre);
    }
  }
}
