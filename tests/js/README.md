# Frontend module tests

The modules under `tracker/static/js/` are plain ES modules with no build step,
so their tests are plain ES modules too. They run in two engines:

| Where | Command | Notes |
|---|---|---|
| CI (GitHub Actions) | `node tests/js/run.mjs` | any Node ≥ 20 |
| macOS, no node installed | `tests/js/run_modules_jsc.sh` | uses the JavaScriptCore shell that ships with the OS (`jsc -m`) |
| from the Python suite | `python3 -m unittest tests.test_js_modules` | runs the jsc script when available, else skips |

`harness.mjs` is a ~60-line test runner (`test(name, fn)`, `assert.*`,
`readText(path)`) that works in both engines: jsc has no `node:test`, no
`fs`, no `URLSearchParams` and no `queueMicrotask`, which is also why the app
modules avoid them. `run.mjs` imports every `*.test.mjs` and exits non-zero
on failure in both engines. Paths passed to `readText` are relative to the
repository root (both runners `cd` there).

Modules that touch the DOM (`h.render`, `toast.js`, `router.start`,
`keys.install`, `md.ensureMermaid`) keep those calls inside functions, so
importing them headless is safe; their pure parts are what the tests cover.

`md.test.mjs` imports the vendored `marked.umd.js` directly — the UMD wrapper
assigns `globalThis.marked` when neither CommonJS nor AMD is present, which is
exactly how the browser loads it.
