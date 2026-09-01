import { test, assert } from "./harness.mjs";
import { tokenize, highlight, KEYWORDS, BUILTINS } from "../../tracker/static/js/pyhl.js";

const LC3 = `def length_of_longest_substring(s: str) -> int:
    count = defaultdict(int)
    for right, ch in enumerate(s):
        count[ch] += 1
        while count[ch] > 1:                # only the NEW char can be a dup
            count[s[left]] -= 1
    return best`;

test("pyhl: tokenize kinds follow draw.py", () => {
  const t = tokenize('    while count[ch] > 1:  # note "x"');
  assert.deepEqual(t.map((x) => x.kind), ["ws", "kw", "ws", "txt", "op", "txt", "op", "ws", "op", "ws", "num", "op", "ws", "com"]);
  assert.equal(t[t.length - 1].text, '# note "x"', "comment swallows the rest of the line, quotes included");
  assert.deepEqual(tokenize("s = 'a b'").map((x) => x.kind), ["txt", "ws", "op", "ws", "str"]);
  assert.deepEqual(tokenize("x = 3.14").slice(-1)[0], { text: "3.14", kind: "num" });
});

test("pyhl: highlight escapes and wraps", () => {
  const h = highlight(LC3);
  assert.match(h, /<span class="py-kw">def<\/span> length_of_longest_substring<span class="py-op">\(<\/span>s<span class="py-op">:<\/span> <span class="py-fn">str<\/span><span class="py-op">\)<\/span> <span class="py-op">-&gt;<\/span> <span class="py-fn">int<\/span><span class="py-op">:<\/span>/);
  assert.match(h, /<span class="py-kw">while<\/span> count<span class="py-op">\[<\/span>ch<span class="py-op">\]<\/span> <span class="py-op">&gt;<\/span> <span class="py-num">1<\/span><span class="py-op">:<\/span>/);
  assert.match(h, /<span class="py-com"># only the NEW char can be a dup<\/span>/);
  assert.equal(h.split("\n").length, 7, "line count preserved");
  assert.notMatch(h, /<script/);
  assert.equal(highlight("a<b"), 'a<span class="py-op">&lt;</span>b');
});

test("pyhl: word sets are the draw.py ones", () => {
  assert.equal(KEYWORDS.size, 26);
  assert.equal(BUILTINS.size, 25);
  assert.ok(KEYWORDS.has("lambda") && BUILTINS.has("popleft"));
});
