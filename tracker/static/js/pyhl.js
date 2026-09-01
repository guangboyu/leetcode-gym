/* pyhl.js — Python syntax highlighting that matches the tutorial GIFs.
 *
 * A direct port of tutorials/anim/dsaviz/draw.py (`tokenize` + KEYWORDS +
 * BUILTINS), so a template on a pattern page is coloured exactly like the code
 * panel in the animations. Same deliberate limits as draw.py: no triple-quoted
 * strings, no f-string internals — it is a per-line tokenizer for short
 * teaching snippets, not a parser. tests/test_pyhl_parity.py keeps the two
 * word sets identical.
 */

import { esc } from "./h.js";

export const KEYWORDS = new Set([
  "def", "return", "for", "while", "if", "elif", "else", "in", "not", "and",
  "or", "None", "True", "False", "break", "continue", "pass", "import",
  "from", "as", "with", "class", "lambda", "is", "yield", "global",
]);

export const BUILTINS = new Set([
  "len", "max", "min", "range", "set", "dict", "list", "sum", "abs", "sorted",
  "enumerate", "deque", "Counter", "float", "int", "str", "append", "pop",
  "popleft", "add", "remove", "get", "items", "keys", "values",
]);

// Same alternation order as draw.py's TOKEN_RE: comment, string, number, word, operator, whitespace.
const TOKEN_RE = /(#.*$)|("[^"]*"|'[^']*')|(\b\d+(?:\.\d+)?\b)|([A-Za-z_][A-Za-z_0-9]*)|([^A-Za-z_0-9\s]+)|(\s+)/g;

/** One line → [{text, kind}] with kind ∈ com str num kw fn txt op ws. */
export function tokenize(line) {
  const out = [];
  TOKEN_RE.lastIndex = 0;
  let m;
  while ((m = TOKEN_RE.exec(line)) !== null) {
    if (m[0] === "") { TOKEN_RE.lastIndex++; continue; }
    const txt = m[0];
    let kind;
    if (m[1] !== undefined) kind = "com";
    else if (m[2] !== undefined) kind = "str";
    else if (m[3] !== undefined) kind = "num";
    else if (m[4] !== undefined) kind = KEYWORDS.has(txt) ? "kw" : BUILTINS.has(txt) ? "fn" : "txt";
    else if (m[5] !== undefined) kind = "op";
    else kind = "ws";
    out.push({ text: txt, kind });
  }
  return out;
}

/** Whole snippet → HTML with <span class="py-kw">…</span> etc. (escaped). */
export function highlight(code) {
  return String(code).replace(/\r\n?/g, "\n").split("\n").map((line) =>
    tokenize(line).map((t) =>
      t.kind === "ws" || t.kind === "txt" ? esc(t.text) : `<span class="py-${t.kind}">${esc(t.text)}</span>`
    ).join("")
  ).join("\n");
}
