/* status.js — the small, shared bits of a problem row: status chip, list
 * badges, difficulty + rating ("Level") cell, action buttons, icons.
 *
 * Every table in the app (Today, Browse, Learn, the live tables inside a
 * rendered tutorial) is built from these so a problem looks the same
 * everywhere. Colors: status uses the verdict axis (blue/amber/red/purple),
 * difficulty uses the pointer family (teal/indigo/pink) — see css/tokens.css. */
import { html, raw } from "../h.js";
import { get, dstatus } from "../store.js";
import { relDate, listBadgeLabel, fmtRating, plural } from "../format.js";

const CHIP_CLASS = { new: "new", solved: "sched", due: "due", forgotten: "forgot", mastered: "master" };
const CHIP_TEXT = { new: "New", solved: "Scheduled", due: "Due", forgotten: "Forgot", mastered: "Mastered" };

/** Inline SVG icon by id from assets/icons.svg (the sprite is inlined in index.html). */
export function icon(name, cls = "icon") {
  return html`<svg class="${cls}" aria-hidden="true"><use href="#i-${name}"></use></svg>`;
}

/** Status chip with the consequence baked in: "Due · 3d overdue", "Scheduled · 5 Sep", "Forgot · ladder restarts". */
export function chipHtml(slug, s = get()) {
  const st = dstatus(slug, s);
  const e = s.progress[slug];
  let extra = "";
  if (e && st === "solved" && e.due) extra = relDate(e.due, s.today);
  else if (e && st === "due" && e.due) extra = relDate(e.due, s.today);
  else if (st === "forgotten") extra = "due now";
  else if (st === "mastered" && e && e.successes) extra = plural(e.successes, "review");
  const ladder = e && st !== "new" && st !== "mastered" && st !== "forgotten" && e.successes
    ? ` · ${ordinal(e.successes + 1)} review` : "";
  return html`<span class="chip ${CHIP_CLASS[st]}" data-status="${st}">${CHIP_TEXT[st]}${extra ? ` · ${extra}` : ""}${ladder}</span>`;
}

function ordinal(n) {
  const s = ["th", "st", "nd", "rd"], v = n % 100;
  return n + (s[(v - 20) % 10] || s[v] || s[0]);
}

/** H100 · I150 · NC250 · 0x3F · TUT badges for the lists a problem belongs to. */
export function badgesHtml(p, { max = 4 } = {}) {
  const L = p.lists || {};
  const keys = [];
  if (L.hot100) keys.push("hot100");
  if (L.interview150) keys.push("interview150");
  if (L.neetcode250) keys.push("neetcode250");
  if ((L.ox3f || []).some((m) => m.tier === "interview")) keys.push("ox3f");
  if (L.tutorial && L.tutorial.length) keys.push("tutorial");
  return keys.slice(0, max).map((k) => html`<span class="badge" title="${LIST_TITLES[k]}">${listBadgeLabel(k)}</span>`);
}
const LIST_TITLES = {
  hot100: "LeetCode Hot 100", interview150: "LeetCode Top Interview 150",
  neetcode250: "NeetCode 250", ox3f: "0x3F topic lists", tutorial: "In a tutorial",
};

/** "Medium ≈1650" — difficulty in the pointer-family color, rating (estimate marked) beside it. */
export function levelHtml(p) {
  const r = fmtRating(p, window.Route && window.Route.effRating);
  return html`<span class="diff ${p.difficulty}">${p.difficulty}</span><span class="num${r.est ? " est" : ""}" title="${r.est ? "Estimated from difficulty (no contest rating)" : "Contest rating"}">${r.text}</span>`;
}

/** 🔥×n frequency mark from a tutorial table (1–3). */
export function freqHtml(n) {
  if (!n) return "";
  return html`<span class="freq" title="${["", "Occasionally asked", "Often asked", "Very frequently asked"][n] || ""}">${"🔥".repeat(n)}</span>`;
}

/** Solved · Help · Forgot (+ ⋯ menu with Reset/Undo when the problem has history). */
export function actionsHtml(slug, s = get()) {
  const st = dstatus(slug, s);
  const busy = s.ui.busy && s.ui.busy.has && s.ui.busy.has(slug);
  return html`<span class="acts" data-slug="${slug}"${busy ? raw(' aria-busy="true"') : ""}>
    <button type="button" class="btn" data-act="mark" data-action="solved" data-slug="${slug}" title="Solved on your own (s)">Solved</button>
    <button type="button" class="btn help" data-act="mark" data-action="solved_help" data-slug="${slug}" title="Solved with help — comes back in 2 days (h)">Help</button>
    <button type="button" class="btn forgot" data-act="mark" data-action="forgotten" data-slug="${slug}" title="Couldn't solve it — due now, ladder restarts (f)">Forgot</button>
    ${st !== "new" ? html`<button type="button" class="btn ghost more" data-act="mark" data-action="reset" data-slug="${slug}" title="Reset progress for this problem (r)" aria-label="Reset">⋯</button>` : ""}
  </span>`;
}

/** LeetCode URL for a slug (slugs are validated server-side; still escaped by html``). */
export function lcUrl(slug) { return `https://leetcode.com/problems/${slug}/`; }

/** The linked title with lock + badges. `hint` (from a tutorial's Note column) renders on a second line. */
export function titleHtml(slug, p, { hint = null, badges = true, hintsOn = true } = {}) {
  return html`<a href="${lcUrl(slug)}" target="_blank" rel="noopener" data-act="open" data-slug="${slug}">${p.title}</a>${p.paid_only ? icon("lock", "icon lock") : ""}${badges ? badgesHtml(p) : ""}${hint && hintsOn ? html`<span class="hint">${raw(hint)}</span>` : ""}`;
}
