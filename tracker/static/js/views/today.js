/* today.js — what to do right now: reviews that are due, then "Next up".
 *
 * Due rows are sorted by due date (most overdue first) then by rating so the
 * easier one comes first on a tie. Marking a due row lets it slide out of the
 * list; nothing else moves. "Next up" is Route.nextUp over the Learn state:
 * the first subtopic, in pattern order, with unsolved core problems. */
import { html, render, raw } from "../h.js";
import { tableHtml, leaveRow, attachCursor } from "../components/problem-table.js";
import { icon } from "../components/status.js";
import { shortDate, plural } from "../format.js";

const CAPS = [1400, 1500, 1600, 1700, 1800, 2000, 2200, 2400];

/** Sort key for due rows: overdue first, then lower rating first. Exported for tests. */
export function dueComparator(progress, effRating) {
  return (a, b) => {
    const da = progress[a[0]].due || "", db = progress[b[0]].due || "";
    if (da !== db) return da < db ? -1 : 1;
    return (effRating(a[1]) || 0) - (effRating(b[1]) || 0);
  };
}

export function dueRows(s, store, effRating) {
  const rows = s.rows.filter(([slug]) => { const st = store.dstatus(slug, s); return st === "due" || st === "forgotten"; });
  return rows.sort(dueComparator(s.progress, effRating));
}

export function nextReview(s) {
  let best = null, n = 0;
  for (const [slug] of s.rows) {
    const e = s.progress[slug];
    if (!e || e.status !== "solved" || !e.due || e.due <= s.today) continue;
    if (!best || e.due < best) { best = e.due; n = 1; } else if (e.due === best) n++;
  }
  return best ? { date: best, n } : null;
}

function ring(done, total, cls = "ring lg") {
  const r = 7.5, c = 2 * Math.PI * r;
  const frac = total ? done / total : 0;
  return html`<svg class="${cls}${total && done >= total ? " done" : ""}" viewBox="0 0 20 20" aria-hidden="true"><circle class="bg" cx="10" cy="10" r="${r}"/><circle class="fg" cx="10" cy="10" r="${r}" stroke-dasharray="${c.toFixed(1)} ${c.toFixed(1)}" stroke-dashoffset="${(c * (1 - frac)).toFixed(1)}"/></svg>`;
}

let cursor = null;

export default {
  id: "today",
  title: "Today",
  routes: ["today"],
  deps: ["progressVersion", "settingsVersion", "dateVersion"],

  mount(el, ctx) {
    cursor = attachCursor(el, { onMark: (slug, action) => ctx.mark(slug, action) });
    el.addEventListener("click", (ev) => {
      const b = ev.target.closest("[data-act='mark'][data-slug]");
      if (!b) return;
      const tr = b.closest("tr[data-slug]");
      if (tr && tr.closest("[data-due]")) {
        // Let mark() finish, then slide the row out if it is no longer due.
        setTimeout(async () => {
          const st = ctx.store.dstatus(tr.dataset.slug);
          if (st !== "due" && st !== "forgotten") {
            await leaveRow(tr);
            this.render(el, ctx, ctx.route);
          }
        }, 60);
      }
    });
    el.addEventListener("change", (ev) => {
      if (ev.target.id === "cap-select") {
        const v = ev.target.value;
        ctx.settings.set({ cap: v === "none" ? null : Number(v) });
      }
    });
    ctx.keys.register("today", "arrowleft", () => {}, { label: "" });
  },

  toolbar(ctx) {
    const s = ctx.store.get();
    const d = new Date();
    const date = d.toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long" });
    const cap = ctx.store.cap(s);
    return html`<h1>Today</h1><span class="sub">${date}</span><span class="grow"></span>
      <label class="sub" for="cap-select" title="Rating cap for the 0x3F extension lists">Cap</label>
      <select id="cap-select" class="select" aria-label="Rating cap">
        ${CAPS.map((c) => html`<option value="${c}"${cap === c ? raw(" selected") : ""}>${c}</option>`)}
        <option value="none"${cap == null ? raw(" selected") : ""}>none</option>
      </select>`;
  },

  render(el, ctx) {
    const s = ctx.store.get();
    const due = dueRows(s, ctx.store, ctx.effRating);
    const forgotten = due.filter(([slug]) => ctx.store.dstatus(slug, s) === "forgotten").length;
    const next = nextReview(s);
    const nu = window.Route ? window.Route.nextUp(ctx.learn()) : null;

    let nextUp = html`<div class="card nextup"><div class="hd">Next up</div>
      <div class="empty">Every core problem is solved. Raise the cap in Learn or try a random Drill.</div></div>`;
    if (nu) {
      const { pattern, subtopic, todo } = nu;
      const subs = pattern.subtopics.filter((x) => !x.skipped && x.kind !== "ox3f");
      const i = subs.indexOf(subtopic);
      const after = subs[i + 1];
      const link = `#/learn/${encodeURIComponent(pattern.id)}/${encodeURIComponent(subtopic.id)}`;
      nextUp = html`<div class="card nextup">
        <div class="hd">Next up</div>
        <div class="who">
          ${ring(subtopic.done, subtopic.total)}
          <div><div class="t">${pattern.name} · ${subtopic.name}</div>
            <div class="s">${subtopic.done} of ${subtopic.total} solved${after ? html` · then ${after.name}` : ""}${pattern.hasTutorial ? "" : " · tutorial in progress"}</div></div>
          <span class="grow"></span>
          <a class="btn primary" href="${link}">Open in Learn ${icon("chevr")}</a>
        </div>
        ${tableHtml(todo.slice(0, 5), { columns: ["id", "title", "level", "freq", "actions"], noHead: true, badges: false }, s)}
      </div>`;
    }

    render(el, html`<div class="view">
      <div class="card" data-due>
        <div class="hd">Reviews due <span class="meta num">${due.length}${forgotten ? ` · ${forgotten} forgotten` : ""}</span></div>
        ${due.length
          ? tableHtml(due, { columns: ["id", "title", "level", "status", "actions"], cursor: cursor && cursor.current() }, s)
          : html`<div class="empty">${icon("check", "icon")}<div>Nothing due${next ? html` — next review ${shortDate(next.date, s.today)} (${plural(next.n, "problem")})` : ""}.</div></div>`}
      </div>
      ${nextUp}
    </div>`);
    if (cursor) cursor.restore();
  },

  unmount() {},
};
