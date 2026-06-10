/* 0x3F's beginner route (Method A in his "how to practice scientifically" post)
 * and drill-pool logic. Pure functions, no DOM — also loadable from node for tests.
 *
 * Stages reference 0x3F topic chapters (the leading number in each section name).
 * His rules: within a stage, finish problems rated <= the cap first (default 1700);
 * for DP the cap widens to 2000 because easy DP problems are sparse.
 */
(function (global) {
  "use strict";

  const ROUTE = [
    { name: "Sliding window", topic: "Sliding Window & Two Pointers", chapters: [1, 2] },
    { name: "Binary search basics", topic: "Binary Search", chapters: [1] },
    { name: "Core data structures", topic: "Data Structures", chapters: [0, 1, 3, 4, 5] },
    { name: "Binary tree DFS", topic: "Linked List, Tree & Backtracking", chapters: [2], subMax: 12 },
    { name: "Grid DFS", topic: "Grid Graph", chapters: [1] },
    { name: "Backtracking", topic: "Linked List, Tree & Backtracking", chapters: [4] },
    { name: "DP chapters 1–6", topic: "Dynamic Programming", chapters: [1, 2, 3, 4, 5, 6], minCap: 2000 },
  ];

  // "§2.13 Binary Tree BFS" -> [2, 13]; "1. Grid DFS" -> [1]
  function secNum(section) {
    const m = section.match(/(\d+(?:\.\d+)*)/);
    return m ? m[1].split(".").map(Number) : [];
  }

  function stageCap(stage, cap) {
    if (cap == null) return null;
    return Math.max(cap, stage.minCap || 0);
  }

  function stageMembership(stage, p) {
    return (p.lists.ox3f || []).find((m) => {
      if (m.topic !== stage.topic || m.tier !== "interview") return false;
      const [c, s] = secNum(m.section);
      if (!stage.chapters.includes(c)) return false;
      if (stage.subMax && s !== undefined && s > stage.subMax) return false;
      return true;
    });
  }

  function stageHas(stage, p, cap) {
    if (p.paid_only) return false;
    const limit = stageCap(stage, cap);
    if (limit && p.rating && p.rating > limit) return false;
    return Boolean(stageMembership(stage, p));
  }

  /* rows: [slug, problem][]  isDone: (slug) => bool  cap: number|null
   * -> [{stage, total, done, todo}] with todo in section order, then by rating. */
  function routeState(rows, isDone, cap) {
    return ROUTE.map((stage) => {
      const probs = rows
        .filter(([, p]) => stageHas(stage, p, cap))
        .sort((a, b) => {
          const ka = secNum(stageMembership(stage, a[1]).section);
          const kb = secNum(stageMembership(stage, b[1]).section);
          for (let i = 0; i < Math.max(ka.length, kb.length); i++) {
            const d = (ka[i] ?? 0) - (kb[i] ?? 0);
            if (d) return d;
          }
          return (a[1].rating ?? 0) - (b[1].rating ?? 0);
        });
      const todo = probs.filter(([slug]) => !isDone(slug));
      return { stage, total: probs.length, done: probs.length - todo.length, todo };
    });
  }

  function drillPool(rows, isNew, lo, hi) {
    return rows.filter(([slug, p]) =>
      isNew(slug) && !p.paid_only && p.rating && p.rating >= lo && p.rating <= hi);
  }

  const api = { ROUTE, secNum, stageHas, routeState, drillPool };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else global.Route = api;
})(this);
