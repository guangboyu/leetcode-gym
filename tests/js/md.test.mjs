import { test, assert, readText } from "./harness.mjs";
import "../../tracker/static/vendor/marked.umd.js"; // UMD → globalThis.marked
import { renderTutorial, slugify, patternIdFromFile } from "../../tracker/static/js/md.js";

const FIXTURE = `# Sliding Window

Intro with a [link](SlidingWindow.md#shape-2-longest-valid) and [outside](https://leetcode.com/problems/two-sum/).

## Contents

- [The one idea](#the-one-idea)

## The one idea

\`\`\`mermaid
flowchart LR
    A{"Is it<br/>contiguous?"} -->|yes| B
\`\`\`

\`\`\`
grow -> shrink
\`\`\`

## Shape 2: longest valid

![LC 3, the window growing](assets/sliding-window/lc0003-longest-substring.gif)

*The window turns red the moment the rule breaks.*

\`\`\`python
def f(s):
    return len(s)  # trivial
\`\`\`

### Longest problems

| LC | Title | Diff | State | Freq | Note |
|---|---|---|---|---|---|
| 3 | Longest Substring Without Repeating Characters | Med | freq | 🔥🔥🔥 | jump variant needs the \`>= left\` guard |
| 1004 | Max Consecutive Ones III | Med | zero count | 🔥🔥🔥 | zeros, not ones |
| 424 | Longest Repeating Character Replacement | Med | freq + max_freq | 🔥🔥🔥 | high-water mark |

| Property | Meaning |
|---|---|
| Shrink-safe | valid stays valid |

See [TwoPointers.md](TwoPointers.md) and [when it breaks](#when-sliding-window-breaks).
`;

const META = {
  file: "SlidingWindow.md",
  headings: [
    { level: 1, text: "Sliding Window", anchor: "sliding-window" },
    { level: 2, text: "Contents", anchor: "contents" },
    { level: 2, text: "The one idea", anchor: "the-one-idea" },
    { level: 2, text: "Shape 2: longest valid", anchor: "shape-2-longest-valid" },
    { level: 3, text: "Longest problems", anchor: "longest-problems" },
  ],
};

test("md: helpers", () => {
  assert.equal(slugify("Shift, don't shrink (LC 424)"), "shift-dont-shrink-lc-424");
  assert.equal(slugify("2a. Read and write"), "2a-read-and-write");
  assert.equal(slugify("Why it is O(n), not O(n²)"), "why-it-is-on-not-on²");
  const used = new Set(["x"]);
  assert.equal(slugify("x", used), "x-1");
  assert.equal(patternIdFromFile("SlidingWindow.md"), "sliding-window");
  assert.equal(patternIdFromFile("TwoPointers.md"), "two-pointers");
});

test("md: renderTutorial rewrites headings, links, images, code, tables", () => {
  const seen = [];
  const r = renderTutorial(FIXTURE, META, {
    rowRenderer(id, row) {
      seen.push([id, row.byName.Title, row.byName.Freq, row.raw[2]]);
      return id === 1004 ? null : `<tr data-slug="lc${id}"><td>live ${id}</td></tr>`;
    },
  });
  const h = r.html;
  assert.match(h, /<h1 id="sliding-window">Sliding Window<\/h1>/);
  assert.match(h, /<h2 id="shape-2-longest-valid">Shape 2: longest valid<\/h2>/);
  assert.match(h, /<h3 id="longest-problems">/);
  assert.deepEqual(r.headings.map((x) => x.anchor), META.headings.map((x) => x.anchor));

  assert.match(h, /<a href="#the-one-idea" data-anchor="the-one-idea">The one idea<\/a>/);
  assert.match(h, /<a href="#\/learn\/two-pointers" data-route="#\/learn\/two-pointers">TwoPointers.md<\/a>/);
  assert.match(h, /<a href="#\/learn\/sliding-window\/read\/shape-2-longest-valid"/);
  assert.match(h, /<a href="https:\/\/leetcode.com\/problems\/two-sum\/" target="_blank" rel="noopener">outside<\/a>/);

  assert.match(h, /<figure><img src="\/tutorials\/assets\/sliding-window\/lc0003-longest-substring.gif" alt="LC 3, the window growing" loading="lazy" decoding="async"><figcaption>The window turns red the moment the rule breaks.<\/figcaption><\/figure>/);
  assert.notMatch(h, /<p><em>The window turns red/, "caption paragraph is consumed by the figure");

  assert.match(h, /<div class="codeblock"><button type="button" class="btn ghost sm copy" data-copy aria-label="Copy code">Copy<\/button><pre class="code py"><code><span class="py-kw">def<\/span> f<span class="py-op">\(<\/span>s<span class="py-op">\):<\/span>/);
  assert.match(h, /<span class="py-com"># trivial<\/span>/);
  assert.match(h, /<pre class="code ascii"><code>grow -&gt; shrink<\/code><\/pre>/);
  assert.match(h, /<div class="mermaid" data-src="flowchart LR\n    A\{&quot;Is it&lt;br\/&gt;contiguous\?&quot;\} --&gt;\|yes\| B">/);
  assert.equal(r.hasMermaid, true);

  assert.deepEqual(seen.map((s) => s[0]), [3, 1004, 424]);
  assert.equal(seen[0][1], "Longest Substring Without Repeating Characters");
  assert.equal(seen[0][2], "🔥🔥🔥");
  assert.equal(seen[0][3], "Med");
  assert.match(h, /<table class="lc-table" data-lc-table>\n<thead><tr><th>LC<\/th><th>Title<\/th><th>Diff<\/th><th>State<\/th><th>Freq<\/th><th>Note<\/th><\/tr><\/thead>/);
  assert.match(h, /<tr data-slug="lc3"><td>live 3<\/td><\/tr>/);
  assert.match(h, /<tr data-lc="1004"><td>1004<\/td><td>Max Consecutive Ones III<\/td>/, "null from rowRenderer keeps the default row");
  assert.match(h, /<table>\n<thead>\n<tr>\n<th>Property<\/th>/, "non-LC tables use marked's default");
  assert.deepEqual(r.lcTables, [{ headers: ["LC", "Title", "Diff", "State", "Freq", "Note"], ids: [3, 1004, 424] }]);
});

test("md: the real SlidingWindow.md renders with every heading anchored from tutorials.json", async () => {
  const md = await readText("tutorials/SlidingWindow.md");
  const meta = JSON.parse(await readText("data/tutorials.json")).tutorials["sliding-window"];
  const ids = [];
  const r = renderTutorial(md, meta, { rowRenderer(id) { ids.push(id); return null; } });
  assert.equal(r.headings.length, meta.headings.length, "heading count matches the build script");
  assert.deepEqual(r.headings.map((h) => h.anchor), meta.headings.map((h) => h.anchor));
  assert.equal(r.hasMermaid, true);
  assert.ok(ids.includes(3) && ids.includes(1004) && ids.includes(424) && ids.includes(992), "LC tables were handed to the row renderer");
  assert.equal(ids.length, meta.ids.length, "every table row reached the callback exactly once");
  assert.equal((r.html.match(/<figure>/g) || []).length, meta.gifs.length, "every GIF became a figure");
  assert.notMatch(r.html, /src="assets\//, "no relative asset paths survive");
});
