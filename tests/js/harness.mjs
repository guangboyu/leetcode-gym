/* Minimal test harness that runs under both node and JavaScriptCore (jsc).
 *
 *   node tests/js/run.mjs
 *   jsc -m tests/js/run.mjs          (macOS: /System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc)
 *
 * Test files import { test, assert } from "./harness.mjs" and register cases;
 * run.mjs imports every test file and calls run(). Failures make the process
 * exit non-zero in both runtimes.
 */

const isNode = typeof process !== "undefined" && process.versions && process.versions.node;
const out = (s) => (isNode ? console.log(s) : print(s));

const tests = [];
export function test(name, fn) { tests.push({ name, fn }); }

function fmt(v) {
  try { return JSON.stringify(v); } catch (_) { return String(v); }
}

export const assert = {
  ok(v, msg = "expected truthy") { if (!v) throw new Error(`${msg}: got ${fmt(v)}`); },
  equal(a, b, msg = "") {
    if (a !== b) throw new Error(`${msg ? msg + ": " : ""}expected ${fmt(b)}, got ${fmt(a)}`);
  },
  deepEqual(a, b, msg = "") {
    const x = JSON.stringify(a), y = JSON.stringify(b);
    if (x !== y) throw new Error(`${msg ? msg + ": " : ""}expected ${y}, got ${x}`);
  },
  match(s, re, msg = "") {
    if (!re.test(String(s))) throw new Error(`${msg ? msg + ": " : ""}${fmt(String(s).slice(0, 200))} does not match ${re}`);
  },
  notMatch(s, re, msg = "") {
    if (re.test(String(s))) throw new Error(`${msg ? msg + ": " : ""}${fmt(String(s).slice(0, 200))} unexpectedly matches ${re}`);
  },
  throws(fn, msg = "expected an exception") {
    let threw = false;
    try { fn(); } catch (_) { threw = true; }
    if (!threw) throw new Error(msg);
  },
};

/** Read a UTF-8 text file relative to the repo root (cwd). */
export async function readText(path) {
  if (isNode) {
    const fs = await import("node:fs");
    return fs.readFileSync(path, "utf8");
  }
  return readFile(path); // jsc global
}

export async function run() {
  let failed = 0;
  for (const t of tests) {
    try {
      await t.fn();
      out(`ok   ${t.name}`);
    } catch (err) {
      failed++;
      const where = err && err.stack ? err.stack.split("\n").filter((l) => /test\.mjs/.test(l)).slice(0, 1).join("") : "";
      out(`FAIL ${t.name}\n     ${err && err.message ? err.message : err}\n     ${where}`);
    }
  }
  out(`\n${tests.length - failed}/${tests.length} passed`);
  if (failed) {
    if (isNode) process.exitCode = 1;
    else throw new Error(`${failed} test(s) failed`);
  }
}
