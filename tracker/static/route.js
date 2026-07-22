/* Study-route and drill-pool logic. Pure functions, no DOM — also loadable
 * from node for tests.
 *
 * Part 1 (beginner route): a curated pattern-by-pattern curriculum drawn from
 * Hot 100 + Top Interview 150 + NeetCode 250 — the union most interviews are
 * hired on. Each problem is assigned ONE pattern (NeetCode's category first,
 * then Hot 100 / Interview 150 group), so the stages partition the union.
 * Part 2: the 12 full 0x3F topic lists for going deep on any single type,
 * with his rating-cap rule (finish problems <= the cap first, default 1700;
 * DP widens to 2000 because easy DP problems are sparse).
 */
(function (global) {
  "use strict";

  /* Most classic-list problems predate contest ratings (zerotrac only rates
   * contest problems), so unrated problems get a difficulty-based estimate:
   * the median rating of all rated problems of that difficulty. */
  const FALLBACK_RATING = { Easy: 1250, Medium: 1650, Hard: 2150 };
  function effRating(p) {
    return p.rating || FALLBACK_RATING[p.difficulty] || 0;
  }

  /* ---- Part 1: curated beginner route (pattern -> problems) ---- */

  // list category/group -> canonical pattern stage
  const NC_PATTERN = {
    "Arrays & Hashing": "Arrays & Hashing",
    "Two Pointers": "Two Pointers",
    "Sliding Window": "Sliding Window",
    "Stack": "Stack & Monotonic Stack",
    "Binary Search": "Binary Search",
    "Linked List": "Linked List",
    "Trees": "Trees & BSTs",
    "Heap / Priority Queue": "Heap / Priority Queue",
    "Backtracking": "Backtracking",
    "Tries": "Tries",
    "Graphs": "Graphs",
    "Advanced Graphs": "Advanced Graphs",
    "1-D Dynamic Programming": "1-D Dynamic Programming",
    "2-D Dynamic Programming": "2-D Dynamic Programming",
    "Greedy": "Greedy",
    "Intervals": "Intervals",
    "Math & Geometry": "Math & Bit Manipulation",
    "Bit Manipulation": "Math & Bit Manipulation",
  };
  const H1_PATTERN = {
    "Hashing": "Arrays & Hashing",
    "Misc": "Arrays & Hashing",
    "Two Pointers": "Two Pointers",
    "Sliding Window": "Sliding Window",
    "Stack": "Stack & Monotonic Stack",
    "Binary Search": "Binary Search",
    "Linked Lists": "Linked List",
    "Binary Tree": "Trees & BSTs",
    "Heap": "Heap / Priority Queue",
    "Backtracking": "Backtracking",
    "Trie": "Tries",
    "Graph": "Graphs",
    "Dynamic Programming": "1-D Dynamic Programming",
    "Greedy": "Greedy",
    "Matrix": "Math & Bit Manipulation",
  };
  const I150_PATTERN = {
    "Hashmap": "Arrays & Hashing",
    "Array / String": "Arrays & Hashing",
    "Divide & Conquer": "Arrays & Hashing",
    "Two Pointers": "Two Pointers",
    "Sliding Window": "Sliding Window",
    "Stack": "Stack & Monotonic Stack",
    "Binary Search": "Binary Search",
    "Linked List": "Linked List",
    "Binary Tree General": "Trees & BSTs",
    "Binary Tree BFS": "Trees & BSTs",
    "Binary Search Tree": "Trees & BSTs",
    "Heap": "Heap / Priority Queue",
    "Backtracking": "Backtracking",
    "Trie": "Tries",
    "Graph General": "Graphs",
    "Graph BFS": "Graphs",
    "1D DP": "1-D Dynamic Programming",
    "Kadane's Algorithm": "1-D Dynamic Programming",
    "Multidimensional DP": "2-D Dynamic Programming",
    "Intervals": "Intervals",
    "Math": "Math & Bit Manipulation",
    "Bit Manipulation": "Math & Bit Manipulation",
    "Matrix": "Math & Bit Manipulation",
  };
  // Hot 100 fallthroughs whose group is not their real pattern.
  const PATTERN_OVERRIDES = {
    31: "Two Pointers",     // Next Permutation (H1 "Misc")
    240: "Binary Search",   // Search a 2D Matrix II (H1 "Matrix")
  };
  function patternOf(p) {
    if (PATTERN_OVERRIDES[p.id]) return PATTERN_OVERRIDES[p.id];
    const L = p.lists;
    if (L.neetcode250) return NC_PATTERN[L.neetcode250.category] || null;
    if (L.hot100) return H1_PATTERN[L.hot100.group] || null;
    if (L.interview150) return I150_PATTERN[L.interview150.group] || null;
    return null;
  }

  // Foundations -> pointer patterns -> data structures -> recursion ->
  // graphs -> DP -> the rest. Difficulty tiers inside a stage do the pacing,
  // so the rating cap does not apply to these stages.
  const PATTERN_ORDER = [
    "Arrays & Hashing", "Two Pointers", "Sliding Window",
    "Stack & Monotonic Stack", "Binary Search", "Linked List", "Trees & BSTs",
    "Heap / Priority Queue", "Backtracking", "Tries", "Graphs",
    "Advanced Graphs", "1-D Dynamic Programming", "2-D Dynamic Programming",
    "Greedy", "Intervals", "Math & Bit Manipulation",
  ];
  const TIER = { Easy: "1. Warm-up (Easy)", Medium: "2. Core (Medium)", Hard: "3. Advanced (Hard)" };
  const BEGINNER = PATTERN_ORDER.map((name) => ({ name, pattern: name, part: "beginner" }));

  /* Part 2: the 12 full 0x3F topic lists (every interview-tier chapter),
   * in his list order — for practicing any type freely after (or alongside)
   * the beginner route. chapters: null = all chapters. */
  const TOPIC_NAMES = [
    "Sliding Window & Two Pointers", "Binary Search", "Monotonic Stack",
    "Grid Graph", "Bit Manipulation", "Graph Theory", "Dynamic Programming",
    "Data Structures", "Math", "Greedy & Thinking",
    "Linked List, Tree & Backtracking", "Strings",
  ];
  const ROUTE = BEGINNER.concat(TOPIC_NAMES.map((t) => ({
    name: t, topic: t, chapters: null, part: "topics",
    minCap: t === "Dynamic Programming" ? 2000 : 0,
  })));

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
    if (stage.pattern) {                          // curated beginner stage
      if (patternOf(p) !== stage.pattern) return null;
      return { section: TIER[p.difficulty] || TIER.Medium };
    }
    return (p.lists.ox3f || []).find((m) => {
      if (m.topic !== stage.topic || m.tier !== "interview") return false;
      if (stage.chapters) {                       // null = every chapter
        const [c, s] = secNum(m.section);
        if (!stage.chapters.includes(c)) return false;
        if (stage.subMax && s !== undefined && s > stage.subMax) return false;
      }
      return true;
    });
  }

  function stageHas(stage, p, cap) {
    if (p.paid_only) return false;
    if (!stage.pattern) {  // cap is an 0x3F-route knob; tiers pace the beginner route
      const limit = stageCap(stage, cap);
      if (limit && p.rating && p.rating > limit) return false;
    }
    return Boolean(stageMembership(stage, p));
  }

  /* Interview-tier sections that are contest-flavored in practice (rarely asked
   * in interviews); hidden from the route by default, revealed by the same
   * toggle as 0x3F's own "(optional)" sections. Keys are "topic||section",
   * exact strings from the data. Judgment call — edit freely. */
  const NICHE = new Set([
    "Data Structures||§1.3 Sum of Distances",
    "Data Structures||§1.4 Bitmask Prefix Sums",
    "Data Structures||§3.6 Two Opposing Stacks",
    "Data Structures||§5.5 Regret Heap (Greedy with Undo)",
  ]);

  function sectionKey(stage, section) { return (stage.topic || stage.name) + "||" + section; }
  function isOptional(stage, section) {
    return /\(optional\)/i.test(section) || NICHE.has(sectionKey(stage, section));
  }

  /* rows: [slug, problem][]  isDone: (slug) => bool  cap: number|null
   * opts: {showOptional: bool, skipped: Set<sectionKey>}
   * -> [{stage, sections, total, done, todo}] where sections (in 0x3F order,
   *    problems by section then rating) = {section, key, optional, skipped,
   *    probs, todo, total, done}. Optional/niche sections are dropped unless
   *    showOptional; skipped sections stay listed but are excluded from the
   *    stage's total/done/todo so route progress and the recommended-next
   *    computation move past them. */
  function routeState(rows, isDone, cap, opts) {
    const showOptional = Boolean(opts && opts.showOptional);
    const skipped = (opts && opts.skipped) || new Set();
    return ROUTE.map((stage) => {
      // Un-numbered sections ("Special Topic: …") sort after every chapter.
      const key = (row) => {
        const k = secNum(stageMembership(stage, row[1]).section);
        return k.length ? k : [Infinity];
      };
      const probs = rows
        .filter(([, p]) => stageHas(stage, p, cap))
        .sort((a, b) => {
          const ka = key(a), kb = key(b);
          for (let i = 0; i < Math.max(ka.length, kb.length); i++) {
            const d = (ka[i] ?? 0) - (kb[i] ?? 0);
            if (d) return d;
          }
          return effRating(a[1]) - effRating(b[1]);
        });

      const sections = [];
      const bySec = new Map();
      for (const row of probs) {
        const sec = stageMembership(stage, row[1]).section;
        let s = bySec.get(sec);
        if (!s) {
          const key = sectionKey(stage, sec);
          s = { section: sec, key, optional: isOptional(stage, sec),
                skipped: skipped.has(key), probs: [], todo: [] };
          bySec.set(sec, s);
          sections.push(s);
        }
        s.probs.push(row);
        if (!isDone(row[0])) s.todo.push(row);
      }
      sections.forEach((s) => { s.total = s.probs.length; s.done = s.total - s.todo.length; });

      const visible = sections.filter((s) => showOptional || !s.optional);
      const active = visible.filter((s) => !s.skipped);
      return {
        stage,
        sections: visible,
        total: active.reduce((n, s) => n + s.total, 0),
        done: active.reduce((n, s) => n + s.done, 0),
        todo: active.flatMap((s) => s.todo),
      };
    });
  }

  /* Does p belong to any of the selected problem pools? pools: Set of list keys
   * ("hot100" | "interview150" | "neetcode250" | "ox3f") or null = no filter.
   * ox3f membership counts only at interview tier (as everywhere else). */
  function inPool(p, pools) {
    if (!pools) return true;
    if (pools.has("hot100") && p.lists.hot100) return true;
    if (pools.has("interview150") && p.lists.interview150) return true;
    if (pools.has("neetcode250") && p.lists.neetcode250) return true;
    if (pools.has("ox3f") && (p.lists.ox3f || []).some((m) => m.tier === "interview")) return true;
    return false;
  }

  /* Untouched, non-paid problems whose rating (real, or the difficulty-based
   * estimate for unrated classics) falls in [lo, hi]. `topics` (Set of 0x3F
   * interview topics) narrows by problem TYPE; `pools` (see inPool) narrows by
   * source LIST — e.g. Hot 100 + Interview 150 + NeetCode 250 covers most
   * companies. Pass null for either to leave that axis unfiltered. */
  function drillPool(rows, isNew, lo, hi, topics, pools) {
    return rows.filter(([slug, p]) => {
      const r = effRating(p);
      if (!isNew(slug) || p.paid_only || !r || r < lo || r > hi) return false;
      if (!inPool(p, pools)) return false;
      if (!topics) return true;
      return (p.lists.ox3f || []).some((m) => m.tier === "interview" && topics.has(m.topic));
    });
  }

  const api = { ROUTE, secNum, stageHas, routeState, drillPool, inPool, sectionKey,
                isOptional, effRating, patternOf };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else global.Route = api;
})(this);
