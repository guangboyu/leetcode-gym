"use strict";

let PROBLEMS = {};   // slug -> problem metadata (data/problems.json)
let PROGRESS = {};   // slug -> progress entry   (/api/progress)
let ROWS = [];       // [slug, problem] sorted by id
const TODAY = new Date().toLocaleDateString("en-CA"); // local YYYY-MM-DD
const PAGE_SIZE = 100;
const LIST_BADGES = { hot100: "H100", interview150: "I150", neetcode250: "NC250" };

let tab = "due";
let page = 0;

const $ = (sel) => document.querySelector(sel);
const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

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

function rowHtml(slug, p) {
  const url = `https://leetcode.com/problems/${slug}/`;
  return `<tr>
    <td class="num">${p.id}</td>
    <td><a href="${url}" target="_blank" rel="noopener">${esc(p.title)}</a>${p.paid_only ? " 🔒" : ""}${badges(p)}</td>
    <td class="diff-${p.difficulty}">${p.difficulty}</td>
    <td class="num">${p.rating ?? ""}</td>
    <td>${chipHtml(slug)}</td>
    <td class="actions">
      <button data-slug="${slug}" data-action="solved">Solved</button>
      <button data-slug="${slug}" data-action="forgotten">Forgot</button>
      ${PROGRESS[slug] ? `<button data-slug="${slug}" data-action="reset">Reset</button>` : ""}
    </td>
  </tr>`;
}

function tableHtml(rows) {
  return `<table>
    <thead><tr><th>ID</th><th>Problem</th><th>Diff</th><th>Rating</th><th>Status</th><th></th></tr></thead>
    <tbody>${rows.map(([s, p]) => rowHtml(s, p)).join("")}</tbody>
  </table>`;
}

function renderDue() {
  const due = ROWS.filter(([s]) => ["due", "forgotten"].includes(dstatus(s)))
    .sort((a, b) => (PROGRESS[a[0]].due < PROGRESS[b[0]].due ? -1 : 1) || (a[1].rating ?? 9999) - (b[1].rating ?? 9999));
  $("#due-count").textContent = due.length || "";
  const upcoming = ROWS.filter(([s]) => dstatus(s) === "solved")
    .map(([s]) => PROGRESS[s].due).sort()[0];
  $("#view-due").innerHTML = due.length
    ? tableHtml(due)
    : `<p class="empty">Nothing due today 🎉${upcoming ? ` — next review on ${upcoming}` : ""}<br>
       Pick new problems in <b>Browse</b> and mark them Solved to start their review cycle.</p>`;
}

function matchesFilters(slug, p) {
  const list = $("#f-list").value;
  if (list === "ox3f") {
    const topic = $("#f-topic").value;
    const comp = $("#f-comp").checked;
    const ms = (p.lists.ox3f || []).filter((m) => (!topic || m.topic === topic) && (comp || m.tier === "interview"));
    if (!ms.length) return false;
  } else if (list !== "all" && !p.lists[list]) return false;

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

  const rows = lists.map(([name, pred]) => {
    const subset = ROWS.filter(([, p]) => pred(p));
    const started = subset.filter(([s]) => PROGRESS[s]).length;
    const mastered = subset.filter(([s]) => dstatus(s) === "mastered").length;
    const pct = subset.length ? Math.round((100 * started) / subset.length) : 0;
    return `<tr><td>${esc(name)}</td><td class="num">${subset.length}</td>
      <td class="num">${started} (${pct}%)</td><td class="num">${mastered}</td></tr>`;
  }).join("");

  $("#view-stats").innerHTML = `
    <div class="statgrid">${cards}</div>
    <table><thead><tr><th>List</th><th>Problems</th><th>Started</th><th>Mastered</th></tr></thead>
    <tbody>${rows}</tbody></table>`;
}

function renderAll() {
  renderDue();
  if (tab === "browse") renderBrowse();
  if (tab === "stats") renderStats();
}

// ---------- actions ----------
async function mark(slug, action) {
  const res = await fetch("/api/review", { method: "POST", body: JSON.stringify({ slug, action }) });
  if (!res.ok) { alert(`Failed: ${(await res.json()).error}`); return; }
  const { entry } = await res.json();
  if (entry === null) delete PROGRESS[slug];
  else PROGRESS[slug] = entry;
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
    ["due", "browse", "stats"].forEach((t) => { $(`#view-${t}`).hidden = t !== tab; });
    renderAll();
  };
});

["#f-list", "#f-topic", "#f-diff", "#f-status", "#f-sort", "#f-comp"].forEach((sel) => {
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
