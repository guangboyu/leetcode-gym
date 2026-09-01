/* Learn-tab and drill-pool logic. Pure functions, no DOM — loadable as a
 * classic script in the browser, under node (module.exports) and under
 * JavaScriptCore (tests/js/run_jsc.sh).
 *
 * One taxonomy: `data/patterns.json` orders the patterns and, for patterns
 * without a hand-written tutorial, lists their subtopics + core problem ids.
 * For patterns WITH a tutorial (`data/tutorials.json`), the tutorial's shapes
 * and problem tables ARE the subtopics — the markdown is the source of truth.
 * 0x3F is an attribute, not a second route: every interview-tier 0x3F
 * membership resolves (section → chapter → topic default) to one of our
 * pattern/subtopic ids and shows up as that subtopic's "Extend with 0x3F"
 * list, rating-capped.
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

  /* ---- Legacy pattern assignment (Hot 100 ∪ Interview 150 ∪ NeetCode 250) ----
   * Still the definition of the "core" union: the coverage test in
   * tests/test_patterns.py requires every problem with a patternOf() to be in
   * some pattern's core list or tutorial table, and the "Also core, not in
   * the tutorial" group is derived from it. scripts/_patternof.py mirrors
   * these dicts; keep them textually identical. */

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

  /* ---- 0x3F sections ------------------------------------------------- */

  // "§2.13 Binary Tree BFS" -> [2, 13]; "1. Grid DFS" -> [1]; "Part A" -> []
  function secNum(section) {
    const m = section.match(/(\d+(?:\.\d+)*)/);
    return m ? m[1].split(".").map(Number) : [];
  }

  // The numeric key patterns.json uses: "§2.1.1 Basics" -> "2.1.1",
  // "4. Other" -> "4", un-numbered sections keep their name ("Part A").
  // Mirrors scripts/draft_patterns.py sec_key().
  function secKey(section) {
    const m = section.match(/(\d+(?:\.\d+)*)/);
    return m ? m[1] : section;
  }

  /* 0x3F's own "(optional)" sections plus the sections patterns.json marks
   * `hidden` (contest-flavored in practice) stay out of the Learn tab unless
   * the "show optional" toggle is on. hidden: Set of "topic||secKey". */
  function isOptional(membership, hidden) {
    if (/\(optional\)/i.test(membership.section)) return true;
    return Boolean(hidden && hidden.has(membership.topic + "||" + secKey(membership.section)));
  }

  /* Where does one 0x3F membership {topic, section, tier} land in our
   * taxonomy? Three tiers, most specific first:
   *   ox3f.sections["topic||2.1.1"]  ->  ox3f.chapters[topic]["2"]  ->
   *   ox3f.topics[topic].default
   * Returns "pattern" or "pattern/subtopic"; null for competition-tier
   * memberships and unknown topics. */
  function resolveOx3f(m, patterns) {
    if (m.tier !== "interview") return null;
    const ox = patterns.ox3f;
    const key = secKey(m.section);
    const bySection = ox.sections[m.topic + "||" + key];
    if (bySection) return bySection;
    const chapter = key.split(".")[0];
    const byChapter = ox.chapters[m.topic] && ox.chapters[m.topic][chapter];
    if (byChapter) return byChapter;
    const topic = ox.topics[m.topic];
    return topic ? topic.default : null;
  }

  /* ---- Learn tab state ------------------------------------------------ */

  function titleCase(s) {
    return s ? s.charAt(0).toUpperCase() + s.slice(1) : s;
  }

  function newSubtopic(pid, id, kind, name, extra) {
    return Object.assign({
      id, key: pid + "/" + id, kind, name,
      core: [], ext: { inCap: [], above: 0 },
      done: 0, total: 0, todo: [], skipped: false, optional: false,
    }, extra || {});
  }

  /* patterns:  data/patterns.json      tutorials: data/tutorials.json
   * rows:      [slug, problem][]       isDone: (slug) => bool
   * cap:       number|null (0x3F "Extend" lists hide rated problems above it)
   * opts:      {showOptional: bool, skipped: Set<"pattern/subtopic">}
   *
   * -> [{id, name, hasTutorial, status, done, total, todo, subtopics}] in
   *    patterns.order, where each subtopic is
   *    {id, key, kind: "shape"|"curriculum"|"also-core"|"ox3f", name, parent?,
   *     blurb?, recognize?, solve?, template?, anchor?, worked?, gifs?,
   *     core: [[slug, p, meta]], ext: {inCap: [[slug, p, meta]], above: n,
   *     done: n}, done, total, todo: [[slug, p, meta]], skipped, optional,
   *     topic?, post?}.
   *    meta = {freq, note_md, state, paid} for tutorial rows, {section,
   *    topic} for ext rows, {} otherwise.
   *
   * Progress (done/total) counts distinct core slugs of non-skipped
   * subtopics; the 0x3F extension is optional material and reports its own
   * ext.done without feeding the pattern's ring. */
  function learnState(patterns, tutorials, rows, isDone, cap, opts) {
    const showOptional = Boolean(opts && opts.showOptional);
    const skipped = (opts && opts.skipped) || new Set();
    const hidden = new Set((patterns.ox3f && patterns.ox3f.hidden) || []);
    const byId = new Map();
    for (const row of rows) byId.set(row[1].id, row);
    const tuts = (tutorials && tutorials.tutorials) || {};

    // Every id that some pattern already claims as core — tutorial tables
    // and curriculum lists alike — so "Also core" only shows true leftovers.
    const claimed = new Set();
    for (const t of Object.values(tuts)) for (const id of t.ids) claimed.add(id);
    for (const pat of Object.values(patterns.patterns)) {
      for (const s of pat.subtopics || []) for (const id of s.core_ids) claimed.add(id);
    }

    // 0x3F memberships grouped by resolved target, computed once for all
    // patterns (rows × memberships, not patterns × rows × memberships).
    const extByTarget = new Map();   // "pattern/subtopic" | "pattern" -> [[slug, p, meta]]
    for (const [slug, p] of rows) {
      if (p.paid_only) continue;
      const seen = new Set();
      for (const m of p.lists.ox3f || []) {
        const target = resolveOx3f(m, patterns);
        if (!target || seen.has(target)) continue;
        if (!showOptional && isOptional(m, hidden)) continue;
        seen.add(target);
        if (!extByTarget.has(target)) extByTarget.set(target, []);
        extByTarget.get(target).push([slug, p, { topic: m.topic, section: m.section }]);
      }
    }
    const aboveCap = (p) => cap != null && p.rating && p.rating > cap;

    return patterns.order.map((pid) => {
      const pat = patterns.patterns[pid];
      const tut = pat.tutorial ? tuts[pid] : null;
      const subs = [];

      if (tut) {
        const parents = new Set(tut.shapes.filter((s) => s.parent).map((s) => s.parent));
        for (const s of tut.shapes) {
          if (parents.has(s.id)) continue;   // a group heading, not a leaf
          const sub = newSubtopic(pid, s.id, "shape", titleCase(s.name), {
            label: s.label, parent: s.parent, anchor: s.anchor, blurb: s.blurb,
            template: s.template, worked: s.worked, gifs: s.gifs,
          });
          for (const pr of s.problems) {
            const row = byId.get(pr.id);
            if (!row) continue;
            sub.core.push([row[0], row[1], { freq: pr.freq, note_md: pr.note_md,
                                             state: pr.state, paid: Boolean(pr.paid) }]);
          }
          subs.push(sub);
        }
      } else {
        for (const s of pat.subtopics || []) {
          const sub = newSubtopic(pid, s.id, "curriculum", s.name, {
            recognize: s.recognize, solve: s.solve,
            template: s.template ? s.template.join("\n") : null,
          });
          for (const id of s.core_ids) {
            const row = byId.get(id);
            if (row) sub.core.push([row[0], row[1], {}]);
          }
          subs.push(sub);
        }
      }

      const leftovers = (pat.legacy_core_ids || []).filter((id) => !claimed.has(id) && byId.has(id));
      if (leftovers.length) {
        const sub = newSubtopic(pid, "also-core", "also-core", "Also core, not in the tutorial");
        for (const id of leftovers) { const row = byId.get(id); sub.core.push([row[0], row[1], {}]); }
        subs.push(sub);
      }

      // Extension lists: per subtopic, plus pattern-level fallback groups for
      // 0x3F chapters/sections that map to the pattern as a whole.
      const coreSlugs = new Set();
      for (const sub of subs) for (const [slug] of sub.core) coreSlugs.add(slug);
      const attachExt = (sub, list) => {
        for (const row of list) {
          if (coreSlugs.has(row[0])) continue;
          if (aboveCap(row[1])) sub.ext.above += 1;
          else sub.ext.inCap.push(row);
        }
        sub.ext.inCap.sort((a, b) => effRating(a[1]) - effRating(b[1]));
        sub.ext.done = sub.ext.inCap.filter(([slug]) => isDone(slug)).length;
      };
      for (const sub of subs) attachExt(sub, extByTarget.get(pid + "/" + sub.id) || []);
      const fallback = extByTarget.get(pid) || [];
      if (fallback.length) {
        // Group by 0x3F topic + chapter so "More from 0x3F" stays navigable.
        const groups = new Map();
        for (const row of fallback) {
          const { topic, section } = row[2];
          const chapter = secNum(section)[0];
          const gid = "ox3f-" + slugify(topic) + "-" + (chapter != null ? chapter : slugify(section));
          if (!groups.has(gid)) {
            const label = chapter != null ? "chapter " + chapter : section;
            const info = patterns.ox3f.topics[topic] || {};
            groups.set(gid, newSubtopic(pid, gid, "ox3f",
              "More from 0x3F: " + topic + " · " + label,
              { topic, chapter: chapter != null ? chapter : null, post: info.post, zh: info.zh }));
          }
          groups.get(gid).core.push(row);
        }
        for (const g of groups.values()) {
          const list = g.core; g.core = [];
          attachExt(g, list);
          g.optional = true;      // extension material: never in the ring
          subs.push(g);
        }
      }

      // Progress: distinct core slugs of non-skipped subtopics.
      const distinct = new Set(), distinctDone = new Set();
      const todo = [];
      for (const sub of subs) {
        sub.skipped = skipped.has(sub.key);
        sub.todo = sub.core.filter(([slug]) => !isDone(slug));
        const ids = new Set(sub.core.map(([slug]) => slug));
        sub.total = ids.size;
        sub.done = sub.core.filter(([slug]) => isDone(slug)).length;
        if (sub.skipped) continue;
        for (const row of sub.core) {
          distinct.add(row[0]);
          if (isDone(row[0])) distinctDone.add(row[0]);
        }
        todo.push(...sub.todo);
      }

      return {
        id: pid, name: pat.name,
        hasTutorial: Boolean(tut), tutorialFile: tut ? tut.file : null,
        status: tut ? (tut.status === "draft" ? "draft" : "done") : "in-progress",
        signals: pat.signals || [], oneLiner: pat.one_liner || "",
        template: (tut && tut.template) || (pat.template ? pat.template.join("\n") : null),
        done: distinctDone.size, total: distinct.size, todo, subtopics: subs,
      };
    });
  }

  function slugify(s) {
    return String(s).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  }

  /* The recommended place to practice next: the first pattern, in order,
   * with a non-skipped core subtopic that still has unsolved problems. */
  function nextUp(learn) {
    for (const pat of learn) {
      for (const sub of pat.subtopics) {
        if (sub.skipped || sub.kind === "ox3f") continue;
        if (sub.todo.length) return { pattern: pat, subtopic: sub, todo: sub.todo };
      }
    }
    return null;
  }

  /* ---- Drill ------------------------------------------------------------ */

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

  /* Compatibility shim for the retired two-route Today tab (app.js) until the
   * Learn tab replaces it: an empty route renders as "nothing to practice". */
  function routeState() { return []; }

  const api = { secNum, secKey, isOptional, resolveOx3f, learnState, nextUp,
                drillPool, inPool, effRating, patternOf, routeState };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else global.Route = api;
})(this);
