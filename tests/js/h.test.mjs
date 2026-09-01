import { test, assert } from "./harness.mjs";
import { html, raw, esc, attr } from "../../tracker/static/js/h.js";

test("h: escapes every dangerous character", () => {
  assert.equal(esc(`&<>"'\``), "&amp;&lt;&gt;&quot;&#39;&#96;");
  assert.equal(String(html`<b title="${`x" onmouseover="alert(1)`}">${"<i>"}</b>`),
    '<b title="x&quot; onmouseover=&quot;alert(1)">&lt;i&gt;</b>');
});

test("h: raw passes through, arrays join, null/false/undefined vanish", () => {
  const items = [1, 2].map((n) => html`<li>${n}</li>`);
  assert.equal(String(html`<ul>${items}</ul>`), "<ul><li>1</li><li>2</li></ul>");
  assert.equal(String(html`a${null}b${false}c${undefined}d${0}`), "abcd0");
  assert.equal(String(html`${raw("<em>ok</em>")}`), "<em>ok</em>");
  assert.equal(String(html`${html`<i>${"<"}</i>`}`), "<i>&lt;</i>", "nested templates are not double-escaped");
});

test("h: attr() only lets safe URLs through", () => {
  assert.equal(String(attr("https://leetcode.com/problems/two-sum/")), "https://leetcode.com/problems/two-sum/");
  assert.equal(String(attr("#/learn/x")), "#/learn/x");
  assert.equal(String(attr("/tutorials/assets/a.gif")), "/tutorials/assets/a.gif");
  assert.equal(String(attr("javascript:alert(1)")), "#");
  assert.equal(String(attr("data:text/html,<script>")), "#");
  assert.equal(String(attr('https://x.y/?q="1"')), "https://x.y/?q=&quot;1&quot;");
});
