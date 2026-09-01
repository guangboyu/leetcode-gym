import { test, assert } from "./harness.mjs";
import { normalizeCombo, comboId, comboFromEvent, display, register, setScope, handleKeydown, describe, defineAction, dispatch, isMac, MOD, _resetForTests } from "../../tracker/static/js/keys.js";

const ev = (key, o = {}) => Object.assign({ key, metaKey: false, ctrlKey: false, shiftKey: false, altKey: false, target: null, prevented: false, preventDefault() { this.prevented = true; } }, o);

test("keys: mod maps to the platform modifier (no navigator ⇒ mac)", () => {
  assert.equal(isMac, true);
  assert.equal(MOD, "meta");
  assert.equal(comboId(normalizeCombo("mod+1")), "meta+1");
  assert.equal(comboId(normalizeCombo("Shift+ArrowLeft")), "shift+arrowleft");
  assert.equal(comboId(normalizeCombo("mod+,")), "meta+,");
  assert.equal(comboFromEvent(ev("1", { metaKey: true })), "meta+1");
  assert.equal(comboFromEvent(ev(" ")), " ");
  assert.equal(display("mod+shift+z"), "⇧⌘Z");
  assert.equal(display("space"), "Space");
  assert.equal(display("backspace"), "⌫");
});

test("keys: scope lookup, input guard, preventDefault", () => {
  _resetForTests();
  const hits = [];
  register("global", "mod+1", () => hits.push("go1"), { label: "Learn" });
  register("drill", "s", () => hits.push("solved"), { label: "Mark solved" });
  register("global", "mod+f", () => hits.push("search"), { inInputs: true, label: "Search" });
  register("browse", "s", () => hits.push("browse-s"));

  setScope("drill");
  const e1 = ev("1", { metaKey: true });
  assert.equal(handleKeydown(e1), true);
  assert.equal(e1.prevented, true);
  assert.equal(handleKeydown(ev("s")), true);
  assert.equal(handleKeydown(ev("x")), false, "unbound key");

  const typing = ev("s", { target: { tagName: "INPUT" } });
  assert.equal(handleKeydown(typing), false, "letters are ignored while typing");
  assert.equal(handleKeydown(ev("f", { metaKey: true, target: { tagName: "INPUT" } })), true, "inInputs bindings still fire");

  setScope("browse");
  handleKeydown(ev("s"));
  assert.deepEqual(hits, ["go1", "solved", "search", "browse-s"]);

  const rep = ev("1", { metaKey: true, repeat: true });
  assert.equal(handleKeydown(rep), true);
  assert.equal(hits.length, 4, "key repeat is swallowed, not re-run");

  const d = describe();
  assert.ok(d.some((b) => b.combo === "meta+1" && b.display === "⌘1" && b.label === "Learn"));
  assert.ok(!d.some((b) => b.combo === "s" && b.scope === "browse"), "unlabelled bindings stay off the sheet");
});

test("keys: named actions bridge", () => {
  _resetForTests();
  const got = [];
  defineAction("go", (v) => got.push(v));
  assert.equal(dispatch("go", "drill"), true);
  assert.equal(dispatch("missing"), false);
  assert.deepEqual(got, ["drill"]);
});
