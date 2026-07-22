"use strict";

let PROBLEMS = {};   // slug -> problem metadata (data/problems.json)
let PROGRESS = {};   // slug -> progress entry   (/api/progress)
let ROWS = [];       // [slug, problem] sorted by id
const TODAY = new Date().toLocaleDateString("en-CA"); // local YYYY-MM-DD
const PAGE_SIZE = 100;
const SUGGEST = 5;   // new problems suggested per day on the Today tab
const LIST_BADGES = { hot100: "H100", interview150: "I150", neetcode250: "NC250" };

let tab = "today";
let page = 0;
let drill = { slug: null, revealed: false };
let routeStage = null;   // study-route stage the user picked; null = follow the recommended one
let routeSection = null; // section key picked within the stage; null = recommended section
let ALL_TOPICS = [];     // every 0x3F interview topic (for the Drill type filter)

const $ = (sel) => document.querySelector(sel);
const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

// ---------- settings ----------
function cap() {
  const v = localStorage.getItem("cap") ?? "1700";
  return v === "none" ? null : Number(v);
}
const isDone = (slug) => Boolean(PROGRESS[slug]) && PROGRESS[slug].status !== "forgotten";
const isNew = (slug) => !PROGRESS[slug];

// Study-route personalization: optional/niche subtopic visibility + skipped subtopics.
const showOptionalSections = () => localStorage.getItem("routeShowOptional") === "1";
const guideOpen = () => localStorage.getItem("guideOpen") !== "0";  // guide card open by default
const skippedSections = () => new Set(JSON.parse(localStorage.getItem("routeSkipped") || "[]"));
function toggleSkipped(key) {
  const set = skippedSections();
  if (set.has(key)) set.delete(key); else set.add(key);
  localStorage.setItem("routeSkipped", JSON.stringify([...set]));
}

// ---------- status ----------
function dstatus(slug) {
  const e = PROGRESS[slug];
  if (!e) return "new";
  if (e.status === "mastered") return "mastered";
  if (e.status === "forgotten") return "forgotten";
  return e.due <= TODAY ? "due" : "solved";
}

const CHIP_TEXT = { new: "New", solved: "Scheduled", due: "Due", forgotten: "Forgotten", mastered: "Mastered" };

function chipHtml(slug) {
  const st = dstatus(slug);
  const e = PROGRESS[slug];
  let sub = "";
  if (st === "solved") sub = `<div class="sub">next ${e.due}</div>`;
  else if (st === "due" || st === "forgotten") sub = `<div class="sub">since ${e.due}</div>`;
  else if (st === "mastered") sub = `<div class="sub">${e.successes} reviews</div>`;
  return `<span class="chip ${st}">${CHIP_TEXT[st]}</span>${sub}`;
}

// ---------- rendering ----------
function badges(p) {
  let out = Object.keys(LIST_BADGES).filter((k) => p.lists[k])
    .map((k) => `<span class="badge">${LIST_BADGES[k]}</span>`).join("");
  if (p.lists.ox3f) out += `<span class="badge">0x3F</span>`;
  return out;
}

function actionsHtml(slug) {
  return `<button data-slug="${slug}" data-action="solved">Solved</button>
    <button data-slug="${slug}" data-action="solved_help">w/ help</button>
    <button data-slug="${slug}" data-action="forgotten">Forgot</button>
    ${PROGRESS[slug] ? `<button data-slug="${slug}" data-action="reset">Reset</button>` : ""}`;
}

function rowHtml(slug, p) {
  const url = `https://leetcode.com/problems/${slug}/`;
  return `<tr>
    <td class="num">${p.id}</td>
    <td><a href="${url}" target="_blank" rel="noopener">${esc(p.title)}</a>${p.paid_only ? " 🔒" : ""}${badges(p)}</td>
    <td class="diff-${p.difficulty}">${p.difficulty}</td>
    <td class="num">${p.rating ?? `<span class="est" title="No contest rating — estimated from difficulty">≈${Route.effRating(p)}</span>`}</td>
    <td>${chipHtml(slug)}</td>
    <td class="actions">${actionsHtml(slug)}</td>
  </tr>`;
}

function tableHtml(rows) {
  return `<table>
    <thead><tr><th>ID</th><th>Problem</th><th>Diff</th><th>Rating</th><th>Status</th><th></th></tr></thead>
    <tbody>${rows.map(([s, p]) => rowHtml(s, p)).join("")}</tbody>
  </table>`;
}

// ---------- Today: due reviews + study route ----------
function renderToday() {
  const due = ROWS.filter(([s]) => ["due", "forgotten"].includes(dstatus(s)))
    .sort((a, b) => (PROGRESS[a[0]].due < PROGRESS[b[0]].due ? -1 : 1) || (a[1].rating ?? 9999) - (b[1].rating ?? 9999));
  $("#due-count").textContent = due.length || "";

  const upcoming = ROWS.filter(([s]) => dstatus(s) === "solved")
    .map(([s]) => PROGRESS[s].due).sort()[0];
  const dueHtml = due.length
    ? `<h2>Reviews due (${due.length})</h2>` + tableHtml(due)
    : `<p class="empty">No reviews due 🎉${upcoming ? ` — next on ${upcoming}` : ""}</p>`;

  const states = Route.routeState(ROWS, isDone, cap(),
    { showOptional: showOptionalSections(), skipped: skippedSections() });
  const recIdx = states.findIndex((st) => st.todo.length > 0);  // 0x3F's recommended next stage
  // Show the stage the user picked; fall back to the recommended one (or the last if all done).
  let selIdx = routeStage;
  if (selIdx == null || selIdx < 0 || selIdx >= states.length) selIdx = recIdx;
  const sel = selIdx >= 0 ? states[selIdx] : null;

  const stageLi = (st, i) => {
    const complete = st.todo.length === 0;
    const cls = [complete ? "stage-done" : "", i === selIdx ? "stage-current" : ""].filter(Boolean).join(" ");
    const mark = complete ? "✓ " : i === recIdx ? "▶ " : "";
    const star = i === recIdx ? ` <span class="sub">recommended</span>` : "";
    return `<li class="route-stage ${cls}" data-stage="${i}" title="Practice this type">
      ${mark}${esc(st.stage.name)} <span class="sub">${st.done}/${st.total}</span>${star}</li>`;
  };
  const beginnerLis = states.map((st, i) => st.stage.part === "topics" ? "" : stageLi(st, i)).join("");
  const topicLis = states.map((st, i) => st.stage.part === "topics" ? stageLi(st, i) : "").join("");
  const optToggle = `<label class="opt-toggle"><input type="checkbox" id="route-opt"${showOptionalSections() ? " checked" : ""}>
    show optional &amp; niche subtopics</label>`;
  const overviewBlock = `<div class="route"><p class="sub">Click any type to practice it. ${optToggle}</p>
    <p class="route-part">Beginner route — one pattern at a time, from Hot 100 · Top Interview 150 · NeetCode 250:</p><ol>${beginnerLis}</ol>
    <p class="route-part">Go deeper — the 12 full 0x3F topic lists, interview-tier sections (rating cap ${cap() ?? "none"}):</p><ol>${topicLis}</ol></div>`;

  let routeHtml;
  if (!sel) {
    routeHtml = `<h2>Study route</h2><p class="empty">Route complete 🏆 — every pattern and every
       0x3F list at cap ${cap() ?? "none"}. Raise the cap, or test yourself in <b>Drill</b>.</p>${overviewBlock}`;
  } else {
    // Subtopic (section) chips: click to practice one, × to skip it, ↩ to restore.
    // Grouped under their 0x3F chapter names (定长/不定长/背包/... in English).
    const secs = sel.sections;
    const recSec = secs.find((s) => !s.skipped && s.todo.length > 0);
    const cur = secs.find((s) => s.key === routeSection) || recSec || secs[0];
    const chapOf = (s) => { const k = Route.secNum(s.section); return k.length ? k[0] : null; };
    const chipHtmlFor = (s) => {
      const cls = ["sec-chip",
        s === cur ? "sec-current" : "",
        s.skipped ? "sec-skipped" : "",
        s.optional ? "sec-optional" : "",
        !s.skipped && s.todo.length === 0 ? "sec-done" : ""].filter(Boolean).join(" ");
      const skipBtn = `<button class="sec-skip" data-skip="${esc(s.key)}"
        title="${s.skipped ? "Restore this subtopic" : "Skip this subtopic (exclude from your plan)"}">${s.skipped ? "↩" : "×"}</button>`;
      return `<span class="${cls}" data-sec="${esc(s.key)}" title="Practice this subtopic">
        ${!s.skipped && s.todo.length === 0 ? "✓ " : ""}${esc(s.section)} <span class="sub">${s.done}/${s.total}</span>${skipBtn}</span>`;
    };
    let secList, guideCard;
    if (sel.stage.pattern) {
      // Curated pattern stage: semantic subtopics as chips; two cards — the
      // pattern's mental map, then the selected subtopic's recognize/solve.
      secList = `<div class="chap-group"><div class="chap-chips">${secs.map(chipHtmlFor).join("")}</div></div>`;
      const g = Guide.pattern(sel.stage.name);
      const mapCard = g ? `<details class="guide"${guideOpen() ? " open" : ""}>
          <summary><b>${esc(sel.stage.name)}</b> — the mental map</summary>
          <ul class="signals">${g.signals.map((s) => `<li>${esc(s)}</li>`).join("")}</ul>
          <p>${esc(g.intro)}</p>
          <p class="sub">Curated from NeetCode 250 + LeetCode Hot 100 / Top Interview 150.</p>
        </details>` : "";
      const sub = cur && (Curriculum.SUB[sel.stage.name] || []).find((s) => s.name === cur.section);
      const subCard = sub ? `<details class="guide"${guideOpen() ? " open" : ""}>
          <summary><b>${esc(sub.name)}</b> — recognize &amp; solve</summary>
          <p><b>Recognize:</b> ${esc(sub.recognize)}</p>
          <p><b>Solve:</b> ${esc(sub.solve)}</p>
          ${sub.tmpl ? `<pre class="tmpl">${esc(sub.tmpl)}</pre>` : ""}
        </details>` : "";
      guideCard = mapCard + subCard;
    } else {
      const groups = [];
      for (const s of secs) {
        const c = chapOf(s);
        if (!groups.length || groups[groups.length - 1].chap !== c) groups.push({ chap: c, chips: [] });
        groups[groups.length - 1].chips.push(s);
      }
      secList = groups.map((gr) => {
        const gi = Guide.chapter(sel.stage.topic, gr.chap, gr.chips[0].section);
        const label = gr.chap == null ? "Special topics"
          : gi ? `${gr.chap}. ${gi.name}` : `Chapter ${gr.chap}`;
        return `<div class="chap-group"><div class="chap-label">${esc(label)}</div>
          <div class="chap-chips">${gr.chips.map(chipHtmlFor).join("")}</div></div>`;
      }).join("");

      // Guide card: what this subtopic's technique is + its template.
      const tg = Guide.topic(sel.stage.topic);
      const gcur = cur ? Guide.chapter(sel.stage.topic, chapOf(cur), cur.section) : null;
      guideCard = gcur ? `<details class="guide"${guideOpen() ? " open" : ""}>
          <summary><b>${esc(gcur.name)}</b> · ${esc(gcur.zh)} — what &amp; how</summary>
          <p>${esc(gcur.intro)}</p>
          ${gcur.tmpl ? `<pre class="tmpl">${esc(gcur.tmpl)}</pre>` : ""}
          <p class="sub">From <a href="${tg ? tg.post : "#"}" target="_blank" rel="noopener">0x3F's ${esc(sel.stage.topic)} list（${esc(tg ? tg.zh : "")}）↗</a></p>
        </details>` : "";
    }

    const capNote = sel.stage.minCap && cap() != null ? ` · cap ${Math.max(cap(), sel.stage.minCap)}` : "";
    const capTxt = sel.stage.pattern ? "" : ` at cap ${cap() ?? "none"}`;
    const body = !cur
      ? `<p class="empty">Nothing to practice here${capTxt}.</p>`
      : cur.todo.length
        ? tableHtml(cur.todo.slice(0, SUGGEST))
        : `<p class="empty">Every problem in ${esc(cur.section)} is done${capTxt} ✓ — pick another subtopic.</p>`;
    const practicing = cur
      ? `<p class="sub practicing">Practicing: <b>${esc(cur.section)}</b> ${cur.done}/${cur.total}${cur === recSec ? " · recommended next" : ""}</p>`
      : "";
    routeHtml = `<h2>Study route: ${esc(sel.stage.name)} <span class="sub">${sel.done}/${sel.total} done${capNote}</span></h2>
       <div class="sec-list">${secList}</div>
       ${practicing}${guideCard}${body}${overviewBlock}`;
  }

  $("#view-today").innerHTML = dueHtml + routeHtml;
  const opt = $("#route-opt");
  if (opt) opt.onchange = () => {
    localStorage.setItem("routeShowOptional", opt.checked ? "1" : "0");
    renderToday();
  };
  document.querySelectorAll(".guide").forEach((gd) =>
    gd.addEventListener("toggle", () =>
      localStorage.setItem("guideOpen", gd.open ? "1" : "0")));
}

// ---------- Browse ----------
function matchesFilters(slug, p) {
  const list = $("#f-list").value;
  if (list === "ox3f") {
    const topic = $("#f-topic").value;
    const comp = $("#f-comp").checked;
    const ms = (p.lists.ox3f || []).filter((m) => (!topic || m.topic === topic) && (comp || m.tier === "interview"));
    if (!ms.length) return false;
  } else if (list !== "all" && !p.lists[list]) return false;

  if ($("#f-cap").checked && cap() && p.rating && p.rating > cap()) return false;
  const diff = $("#f-diff").value;
  if (diff && p.difficulty !== diff) return false;
  const st = $("#f-status").value;
  if (st && dstatus(slug) !== st) return false;
  const q = $("#f-search").value.trim().toLowerCase();
  if (q && !p.title.toLowerCase().includes(q) && String(p.id) !== q.replace(/^#/, "")) return false;
  return true;
}

function renderBrowse() {
  const sort = $("#f-sort").value;
  let rows = ROWS.filter(([s, p]) => matchesFilters(s, p));
  if (sort === "rating") rows.sort((a, b) => (a[1].rating ?? 9999) - (b[1].rating ?? 9999));
  else if (sort === "due") rows.sort((a, b) => ((PROGRESS[a[0]]?.due ?? "9999") < (PROGRESS[b[0]]?.due ?? "9999") ? -1 : 1));

  const pages = Math.max(1, Math.ceil(rows.length / PAGE_SIZE));
  page = Math.min(page, pages - 1);
  const slice = rows.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);
  $("#browse-table").innerHTML = rows.length ? tableHtml(slice) : `<p class="empty">No problems match.</p>`;
  $("#pager").innerHTML = pages > 1
    ? `<button id="pg-prev" ${page === 0 ? "disabled" : ""}>&larr;</button>
       <span>${page + 1} / ${pages} &middot; ${rows.length} problems</span>
       <button id="pg-next" ${page === pages - 1 ? "disabled" : ""}>&rarr;</button>`
    : rows.length ? `<span>${rows.length} problems</span>` : "";
  if (pages > 1) {
    $("#pg-prev").onclick = () => { page--; renderBrowse(); };
    $("#pg-next").onclick = () => { page++; renderBrowse(); };
  }
}

// ---------- Drill (0x3F Method B: type-blind practice) ----------
// Which problem pools (source lists) Drill draws from. Default: all four.
// Hot 100 + Interview 150 + NeetCode 250 is plenty for most companies;
// the 0x3F lists are the deep pool.
const POOLS = [
  ["hot100", "Hot 100"],
  ["interview150", "Top Interview 150"],
  ["neetcode250", "NeetCode 250"],
  ["ox3f", "0x3F lists"],
];

function selectedPools() {
  const saved = JSON.parse(localStorage.getItem("drillPools") || "null");
  const keys = POOLS.map(([k]) => k);
  if (!Array.isArray(saved)) return keys;
  return keys.filter((k) => saved.includes(k));
}

function savePools(keys) {
  localStorage.setItem("drillPools", JSON.stringify(keys));
}

// Which 0x3F topics the drill pool is limited to. Default: all of them.
function selectedTopics() {
  const saved = JSON.parse(localStorage.getItem("drillTopics") || "null");
  if (!Array.isArray(saved)) return ALL_TOPICS.slice();
  // Drop any topics that no longer exist, then intersect with the known set.
  return ALL_TOPICS.filter((t) => saved.includes(t));
}

function saveTopics(topics) {
  localStorage.setItem("drillTopics", JSON.stringify(topics));
  const s = $("#drill-topics > summary");
  if (s) s.textContent = topicsLabel(topics);
}

function topicsLabel(topics) {
  return `Types: ${topics.length >= ALL_TOPICS.length ? "all" : `${topics.length} of ${ALL_TOPICS.length}`}`;
}

function drawDrill() {
  const lo = Number($("#drill-lo")?.value ?? localStorage.getItem("drillLo") ?? (cap() ? cap() - 300 : 1400));
  const hi = Number($("#drill-hi")?.value ?? localStorage.getItem("drillHi") ?? (cap() ?? 1700));
  localStorage.setItem("drillLo", lo);
  localStorage.setItem("drillHi", hi);
  const topics = selectedTopics();
  // All types selected -> no filter (also keeps problems that aren't in any 0x3F list).
  const topicSet = topics.length >= ALL_TOPICS.length ? null : new Set(topics);
  const pools = selectedPools();
  const poolSet = pools.length >= POOLS.length ? null : new Set(pools);
  const pool = Route.drillPool(ROWS, isNew, lo, hi, topicSet, poolSet);
  drill = pool.length
    ? { slug: pool[Math.floor(Math.random() * pool.length)][0], revealed: false }
    : { slug: null, revealed: false, empty: true };
  renderDrill();
}

function renderDrill() {
  const lo = localStorage.getItem("drillLo") ?? (cap() ? cap() - 300 : 1400);
  const hi = localStorage.getItem("drillHi") ?? (cap() ?? 1700);
  let card = "";
  if (drill.empty) card = `<p class="empty">No untouched problems match. Widen the rating range, or select more lists / types.</p>`;
  else if (drill.slug) {
    const p = PROBLEMS[drill.slug];
    const url = `https://leetcode.com/problems/${drill.slug}/`;
    card = `<div class="drillcard">
      <p class="drill-title"><a href="${url}" target="_blank" rel="noopener">${p.id}. ${esc(p.title)}</a></p>
      ${drill.revealed
        ? `<p><span class="diff-${p.difficulty}">${p.difficulty}</span> · rating ${p.rating ?? `≈${Route.effRating(p)} (est.)`} ${badges(p)}</p>
           <ul class="sub">${(p.lists.ox3f || []).map((m) => `<li>${esc(m.topic)} — ${esc(m.section)}</li>`).join("") || "<li>not in the 0x3F lists</li>"}</ul>
           <p>${chipHtml(drill.slug)}</p>
           <button id="drill-next">Draw next →</button>`
        : `<p class="sub">Type hidden — figure out the approach yourself, then mark it:</p>
           <p class="actions">${actionsHtml(drill.slug)}
           <button id="drill-skip">Skip</button></p>`}
    </div>`;
  }
  const topics = selectedTopics();
  const chosen = new Set(topics);
  const topicBoxes = ALL_TOPICS.map((t) =>
    `<label class="topic-chip"><input type="checkbox" class="drill-topic" value="${esc(t)}" ${chosen.has(t) ? "checked" : ""}> ${esc(t)}</label>`).join("");
  const pools = new Set(selectedPools());
  const poolBoxes = POOLS.map(([k, label]) =>
    `<label class="topic-chip"><input type="checkbox" class="drill-pool" value="${k}" ${pools.has(k) ? "checked" : ""}> ${label}</label>`).join("");

  $("#view-drill").innerHTML = `
    <h2>Random drill</h2>
    <p class="sub">0x3F's Method B: practice without knowing the problem type, since contests and
    interviews won't tell you it's DP. The specific problem's type and difficulty stay hidden until
    you mark it. Narrow by list and by type below — for most companies Hot 100 + Top Interview 150 +
    NeetCode 250 is plenty. Classics without a contest rating count as ≈1250 (Easy), ≈1650 (Medium),
    or ≈2150 (Hard).</p>
    <div id="filters">
      <label>Rating <input id="drill-lo" type="number" step="50" value="${lo}"> –
      <input id="drill-hi" type="number" step="50" value="${hi}"></label>
      <button id="drill-draw">Draw a problem</button>
    </div>
    <div class="pool-row"><span class="sub">Draw from:</span> ${poolBoxes}</div>
    <details id="drill-topics" class="drill-topics"${topics.length < ALL_TOPICS.length ? " open" : ""}>
      <summary>${topicsLabel(topics)}</summary>
      <div class="topic-actions">
        <button type="button" id="topics-all">Select all</button>
        <button type="button" id="topics-none">Clear</button>
      </div>
      <div id="drill-topic-list" class="topic-list">${topicBoxes}</div>
    </details>
    ${card}`;
  $("#drill-draw").onclick = drawDrill;
  const skip = $("#drill-skip");
  if (skip) skip.onclick = drawDrill;
  const next = $("#drill-next");
  if (next) next.onclick = drawDrill;

  const readTopics = () => [...document.querySelectorAll(".drill-topic:checked")].map((b) => b.value);
  document.querySelectorAll(".drill-topic").forEach((b) => { b.onchange = () => saveTopics(readTopics()); });
  document.querySelectorAll(".drill-pool").forEach((b) => {
    b.onchange = () => savePools([...document.querySelectorAll(".drill-pool:checked")].map((x) => x.value));
  });
  $("#topics-all").onclick = () => {
    document.querySelectorAll(".drill-topic").forEach((b) => { b.checked = true; });
    saveTopics(ALL_TOPICS.slice());
  };
  $("#topics-none").onclick = () => {
    document.querySelectorAll(".drill-topic").forEach((b) => { b.checked = false; });
    saveTopics([]);
  };
}

// ---------- Stats ----------
const CHEAT = [
  ["n ≤ 10", "O(n!) / O(Cⁿ)", "backtracking, brute force"],
  ["n ≤ 20", "O(2ⁿ)", "bitmask DP"],
  ["n ≤ 40", "O(2<sup>n/2</sup>)", "meet in the middle"],
  ["n ≤ 100", "O(n³)", "triple-loop DP, Floyd-Warshall"],
  ["n ≤ 1 000", "O(n²)", "double-loop DP, knapsack"],
  ["n ≤ 100 000", "O(n log n)", "most problems: sorting, heaps, binary search"],
  ["n ≤ 1 000 000", "O(n)", "linear DP, sliding window"],
  ["n ≤ 10⁹", "O(√n)", "primality testing"],
  ["n ≤ 10¹⁸", "O(log n) / O(1)", "binary search on answer, fast power, math"],
];

function renderStats() {
  const counts = { new: 0, solved: 0, due: 0, forgotten: 0, mastered: 0 };
  ROWS.forEach(([s]) => counts[dstatus(s)]++);
  const cards = [
    ["Due now", counts.due + counts.forgotten, "due"],
    ["Scheduled", counts.solved, "solved"],
    ["Mastered", counts.mastered, "mastered"],
    ["Untouched", counts.new, "new"],
  ].map(([lbl, n, cls]) => `<div class="statcard"><div class="big chip ${cls}">${n}</div><div class="lbl">${lbl}</div></div>`).join("");

  const lists = [
    ["Hot 100", (p) => p.lists.hot100],
    ["Interview 150", (p) => p.lists.interview150],
    ["NeetCode 250", (p) => p.lists.neetcode250],
  ];
  const topics = [...new Set(ROWS.flatMap(([, p]) => (p.lists.ox3f || []).map((m) => m.topic)))];
  topics.forEach((t) => lists.push([`0x3F · ${t}`, (p) => (p.lists.ox3f || []).some((m) => m.topic === t && m.tier === "interview")]));

  const c = cap();
  const rows = lists.map(([name, pred]) => {
    const subset = ROWS.filter(([, p]) => pred(p));
    const started = subset.filter(([s]) => PROGRESS[s]).length;
    const mastered = subset.filter(([s]) => dstatus(s) === "mastered").length;
    const inCap = c ? subset.filter(([, p]) => !p.rating || p.rating <= c) : subset;
    const startedCap = inCap.filter(([s]) => PROGRESS[s]).length;
    const pct = inCap.length ? Math.round((100 * startedCap) / inCap.length) : 0;
    return `<tr><td>${esc(name)}</td><td class="num">${subset.length}</td>
      <td class="num">${started}</td><td class="num">${mastered}</td>
      <td class="num">${startedCap}/${inCap.length} (${pct}%)</td></tr>`;
  }).join("");

  const cheat = CHEAT.map(([n, t, a]) => `<tr><td class="num">${n}</td><td>${t}</td><td>${a}</td></tr>`).join("");

  $("#view-stats").innerHTML = `
    <div class="statgrid">${cards}</div>
    <table><thead><tr><th>List</th><th>Problems</th><th>Started</th><th>Mastered</th><th>&le; cap ${c ?? "—"}</th></tr></thead>
    <tbody>${rows}</tbody></table>
    <h2>Data range → expected complexity</h2>
    <p class="sub">From 0x3F's guide: ~10⁸ simple operations/second (divide by ~10 for Python).</p>
    <table><thead><tr><th>Data range</th><th>Allowed complexity</th><th>Typical algorithms</th></tr></thead>
    <tbody>${cheat}</tbody></table>`;
}

function renderAll() {
  renderToday();
  if (tab === "browse") renderBrowse();
  if (tab === "drill") renderDrill();
  if (tab === "stats") renderStats();
}

// ---------- actions ----------
async function mark(slug, action) {
  const res = await fetch("/api/review", { method: "POST", body: JSON.stringify({ slug, action }) });
  if (!res.ok) { alert(`Failed: ${(await res.json()).error}`); return; }
  const { entry } = await res.json();
  if (entry === null) delete PROGRESS[slug];
  else PROGRESS[slug] = entry;
  if (slug === drill.slug) drill.revealed = true;
  renderAll();
}

// ---------- wiring ----------
document.addEventListener("click", (ev) => {
  const b = ev.target.closest("button[data-action]");
  if (b) { mark(b.dataset.slug, b.dataset.action); return; }
  const skipBtn = ev.target.closest("button[data-skip]");
  if (skipBtn) { toggleSkipped(skipBtn.dataset.skip); renderToday(); return; }
  const secChip = ev.target.closest("[data-sec]");
  if (secChip) { routeSection = secChip.dataset.sec; renderToday(); return; }
  const stageLi = ev.target.closest("li[data-stage]");
  if (stageLi) { routeStage = Number(stageLi.dataset.stage); routeSection = null; renderToday(); }
});

document.querySelectorAll("#tabs button").forEach((b) => {
  b.onclick = () => {
    tab = b.dataset.tab;
    document.querySelectorAll("#tabs button").forEach((x) => x.classList.toggle("active", x === b));
    ["today", "browse", "drill", "stats"].forEach((t) => { $(`#view-${t}`).hidden = t !== tab; });
    renderAll();
  };
});

$("#cap-select").value = localStorage.getItem("cap") ?? "1700";
$("#cap-select").addEventListener("change", () => {
  localStorage.setItem("cap", $("#cap-select").value);
  renderAll();
});

["#f-list", "#f-topic", "#f-diff", "#f-status", "#f-sort", "#f-cap", "#f-comp"].forEach((sel) => {
  $(sel).addEventListener("change", () => {
    if (sel === "#f-list") {
      const isOx = $("#f-list").value === "ox3f";
      $("#f-topic").hidden = !isOx;
      $("#comp-label").hidden = !isOx;
    }
    page = 0;
    renderBrowse();
  });
});
$("#f-search").addEventListener("input", () => { page = 0; renderBrowse(); });

// ---------- settings: sync folder ----------
let DATA_DIR = "";

// Native folder picker only exists in the desktop app (pywebview bridge).
const isDesktop = () =>
  Boolean(window.pywebview && window.pywebview.api && window.pywebview.api.choose_folder);

async function loadDataDir() {
  try {
    const r = await fetch("/api/data-dir");
    if (!r.ok) return;
    DATA_DIR = (await r.json()).path;
    $("#cur-data-dir").textContent = DATA_DIR;
  } catch (_) { /* older server without the endpoint — leave the dialog blank */ }
}

async function applyDataDir(path) {
  const msg = $("#sync-msg");
  if (!path) return;
  msg.textContent = "Switching…";
  const res = await fetch("/api/data-dir", { method: "POST", body: JSON.stringify({ path }) });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) { msg.textContent = `Failed: ${body.error || res.status}`; return; }
  DATA_DIR = body.path;
  PROGRESS = body.progress || {};
  $("#cur-data-dir").textContent = DATA_DIR;
  $("#manual-path").value = "";
  msg.textContent = "Now syncing to this folder ✓";
  renderAll();
}

$("#settings-btn").onclick = () => {
  $("#sync-msg").textContent = "";
  $("#picker-hint").textContent = isDesktop() ? "" : "(desktop app only)";
  $("#settings-dlg").showModal();
};
$("#choose-folder").onclick = async () => {
  if (isDesktop()) {
    const path = await window.pywebview.api.choose_folder();
    if (path) applyDataDir(path);
  } else {
    $("#sync-msg").textContent = "The native picker needs the desktop app — paste a folder path below instead.";
    $("#manual-path").focus();
  }
};
$("#set-path").onclick = () => applyDataDir($("#manual-path").value.trim());
loadDataDir();

async function init() {
  const [probs, prog] = await Promise.all([
    fetch("/data/problems.json").then((r) => r.json()),
    fetch("/api/progress").then((r) => r.json()),
  ]);
  PROBLEMS = probs.problems;
  PROGRESS = prog;
  ROWS = Object.entries(PROBLEMS).sort((a, b) => a[1].id - b[1].id);
  const topics = [...new Set(ROWS.flatMap(([, p]) => (p.lists.ox3f || []).map((m) => m.topic)))];
  // Interview-tier topics only, for the Drill type filter (matches the route/stats view).
  ALL_TOPICS = [...new Set(ROWS.flatMap(([, p]) =>
    (p.lists.ox3f || []).filter((m) => m.tier === "interview").map((m) => m.topic)))].sort();
  $("#f-topic").innerHTML = `<option value="">All topics</option>` +
    topics.map((t) => `<option>${esc(t)}</option>`).join("");
  renderAll();
}
init();
