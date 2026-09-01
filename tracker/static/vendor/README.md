# Vendored third-party assets

Pinned, MIT/OFL-licensed files served as-is by the tracker (no build step, no CDN at
runtime — the desktop app must work offline). Never edit them in place; bump the
version, re-download, and update the checksum here.

| File | Project | Version | Source | SHA-256 |
|---|---|---|---|---|
| `marked.umd.js` | [marked](https://github.com/markedjs/marked) (MIT, `LICENSE-marked.txt`) | 15.0.12 | `https://cdn.jsdelivr.net/npm/marked@15.0.12/lib/marked.umd.js` | `d7931d1cd7bf727dd756c871637edcc9e0f8538003b927368400ec1ee47a9dd9` |
| `mermaid.min.js` | [mermaid](https://github.com/mermaid-js/mermaid) (MIT, `LICENSE-mermaid.txt`) | 11.6.0 | `https://cdn.jsdelivr.net/npm/mermaid@11.6.0/dist/mermaid.min.js` | `3a93016a73dc82ba890d919f9bbb176f3da9d98341650c0b517f2595cc68fef8` |
| `fonts/JetBrainsMono-*.ttf` | [JetBrains Mono](https://www.jetbrains.com/lp/mono/) (SIL OFL 1.1, `fonts/JetBrainsMono-OFL.txt`) | 2.304 | copied from `tutorials/anim/dsaviz/fonts/` so in-app code matches the GIF panels | — |

`mermaid.min.js` (~2.6 MB) is loaded lazily, only when a tutorial page contains a
`mermaid` fence; everything else loads at startup.

Verify: `shasum -a 256 tracker/static/vendor/*.js`
