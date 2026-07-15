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

const $ = (sel) => document.querySelector(sel);
const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

// ---------- settings ----------
function cap() {
  const v = localStorage.getItem("cap") ?? "1700";
  return v === "none" ? null : Number(v);
}
const isDone = (slug) => Boolean(PROGRESS[slug]) && PROGRESS[slug].status !== "forgotten";
const isNew = (slug) => !PROGRESS[slug];

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
    <td class="num">${p.rating ?? ""}</td>
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

  const states = Route.routeState(ROWS, isDone, cap());
  const current = states.find((st) => st.todo.length > 0);
  const overview = states.map((st) => {
    const doneMark = st.todo.length === 0 ? "✓ " : st === current ? "▶ " : "";
    return `<li class="${st.todo.length === 0 ? "stage-done" : st === current ? "stage-current" : ""}">
      ${doneMark}${esc(st.stage.name)} <span class="sub">${st.done}/${st.total}</span></li>`;
  }).join("");

  const routeHtml = current
    ? `<h2>Study route — ${esc(current.stage.name)} <span class="sub">${current.done}/${current.total} done${current.stage.minCap && cap() != null ? ` · cap ${Math.max(cap(), current.stage.minCap)}` : ""}</span></h2>
       ${tableHtml(current.todo.slice(0, SUGGEST))}
       <details class="route"><summary>Route overview (0x3F Method A, rating cap ${cap() ?? "none"})</summary><ol>${overview}</ol></details>`
    : `<h2>Study route</h2><p class="empty">Beginner route complete at cap ${cap() ?? "none"} 🏆 —
       raise the cap, practice the full lists in <b>Browse</b>, or test yourself in <b>Drill</b>.</p>
       <details class="route"><summary>Route overview</summary><ol>${overview}</ol></details>`;

  $("#view-today").innerHTML = dueHtml + routeHtml;
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
function drawDrill() {
  const lo = Number($("#drill-lo")?.value ?? localStorage.getItem("drillLo") ?? (cap() ? cap() - 300 : 1400));
  const hi = Number($("#drill-hi")?.value ?? localStorage.getItem("drillHi") ?? (cap() ?? 1700));
  localStorage.setItem("drillLo", lo);
  localStorage.setItem("drillHi", hi);
  const pool = Route.drillPool(ROWS, isNew, lo, hi);
  drill = pool.length
    ? { slug: pool[Math.floor(Math.random() * pool.length)][0], revealed: false }
    : { slug: null, revealed: false, empty: true };
  renderDrill();
}

function renderDrill() {
  const lo = localStorage.getItem("drillLo") ?? (cap() ? cap() - 300 : 1400);
  const hi = localStorage.getItem("drillHi") ?? (cap() ?? 1700);
  let card = "";
  if (drill.empty) card = `<p class="empty">No untouched rated problems in that range — widen it.</p>`;
  else if (drill.slug) {
    const p = PROBLEMS[drill.slug];
    const url = `https://leetcode.com/problems/${drill.slug}/`;
    card = `<div class="drillcard">
      <p class="drill-title"><a href="${url}" target="_blank" rel="noopener">${p.id}. ${esc(p.title)}</a></p>
      ${drill.revealed
        ? `<p><span class="diff-${p.difficulty}">${p.difficulty}</span> · rating ${p.rating} ${badges(p)}</p>
           <ul class="sub">${(p.lists.ox3f || []).map((m) => `<li>${esc(m.topic)} — ${esc(m.section)}</li>`).join("") || "<li>not in the 0x3F lists</li>"}</ul>
           <p>${chipHtml(drill.slug)}</p>
           <button id="drill-next">Draw next →</button>`
        : `<p class="sub">Type hidden — figure out the approach yourself, then mark it:</p>
           <p class="actions">${actionsHtml(drill.slug)}
           <button id="drill-skip">Skip</button></p>`}
    </div>`;
  }
  $("#view-drill").innerHTML = `
    <h2>Random drill</h2>
    <p class="sub">0x3F's Method B: after the beginner route, occasionally practice without knowing the
    problem type — contests and interviews won't tell you it's DP. Topic and difficulty stay hidden
    until you mark the problem.</p>
    <div id="filters">
      <label>Rating <input id="drill-lo" type="number" step="50" value="${lo}"> –
      <input id="drill-hi" type="number" step="50" value="${hi}"></label>
      <button id="drill-draw">Draw a problem</button>
    </div>
    ${card}`;
  $("#drill-draw").onclick = drawDrill;
  const skip = $("#drill-skip");
  if (skip) skip.onclick = drawDrill;
  const next = $("#drill-next");
  if (next) next.onclick = drawDrill;
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
  if (b) mark(b.dataset.slug, b.dataset.action);
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
  $("#f-topic").innerHTML = `<option value="">All topics</option>` +
    topics.map((t) => `<option>${esc(t)}</option>`).join("");
  renderAll();
}
init();
