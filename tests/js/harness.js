/* Tiny test harness that works in two runtimes:
 *
 *   node --test tests/js            (CI; node:test does the reporting)
 *   tests/js/run_jsc.sh             (local, macOS JavaScriptCore — no node
 *                                    needed; tests/test_js.py wraps it)
 *
 * Under jsc the shell script loads this file, then tracker/static/route.js,
 * then one test file, all in one global scope, with the repo root passed as
 * the first script argument. Under node a test file does
 * `require("./harness.js")`, which evaluates route.js into the global scope
 * via vm so `Route` looks the same in both runtimes.
 *
 * Globals defined here: test, assert, assertEq, readJSON, ROOT, Route (node).
 */
(function (g) {
  "use strict";
  const isNode = typeof require !== "undefined" && typeof process !== "undefined";

  if (isNode) {
    const fs = require("fs"), path = require("path"), vm = require("vm");
    g.ROOT = path.resolve(__dirname, "..", "..");
    g.readJSON = (rel) => JSON.parse(fs.readFileSync(path.join(g.ROOT, rel), "utf8"));
    // Evaluate route.js as a classic script so its UMD tail takes the
    // `global.Route` branch (module is undefined inside runInThisContext).
    if (!g.Route) {
      vm.runInThisContext(fs.readFileSync(path.join(g.ROOT, "tracker", "static", "route.js"), "utf8"),
                          { filename: "route.js" });
    }
    g.test = require("node:test").test;
  } else {
    // jsc: `arguments` holds everything after `--`; readFile is a jsc builtin.
    g.ROOT = (g.arguments && g.arguments[0]) || ".";  // the jsc-global `arguments`, not this IIFE's
    g.readJSON = (rel) => JSON.parse(readFile(g.ROOT + "/" + rel));
    const failures = [];
    let count = 0;
    g.test = (name, fn) => {
      count += 1;
      try { fn(); print("  ok    " + name); }
      catch (e) { failures.push(name); print("  FAIL  " + name + "\n        " + (e && e.stack || e)); }
    };
    g.__summary = () => {
      print(count + " tests, " + failures.length + " failed");
      if (failures.length) throw new Error("failed: " + failures.join(", "));
    };
  }

  g.assert = (cond, msg) => { if (!cond) throw new Error(msg || "assertion failed"); };
  g.assertEq = (a, b, msg) => {
    const ja = JSON.stringify(a), jb = JSON.stringify(b);
    if (ja !== jb) throw new Error((msg ? msg + ": " : "") + "expected " + jb + ", got " + ja);
  };
})(typeof globalThis !== "undefined" ? globalThis : this);
