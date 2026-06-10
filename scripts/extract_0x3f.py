#!/usr/bin/env python3
"""Extract the markdown body of a leetcode.cn discuss post from saved HTML.

The post content lives in the page's embedded __NEXT_DATA__ JSON. Usage:

    curl -sL "https://leetcode.cn/discuss/post/SqopEo/" -o post.html
    python3 scripts/extract_0x3f.py post.html source/ox3F/raw-zh/02-binary-search.md
"""
import json.decoder
import sys
from pathlib import Path

TAG = '<script id="__NEXT_DATA__" type="application/json">'


def extract(html_path: Path, out_path: Path):
    html = html_path.read_text(encoding="utf-8")
    start = html.find(TAG)
    if start < 0:
        sys.exit(f"error: no __NEXT_DATA__ in {html_path}")
    blob = html[start + len(TAG):html.index("</script>", start)]

    key = '"content":"'
    ci = blob.find(key)
    if ci < 0:
        sys.exit("error: no content field in __NEXT_DATA__")
    # Decode the JSON string literal in place (the blob is too irregular to parse whole).
    content, _ = json.decoder.scanstring(blob, ci + len(key))
    content = content.replace("\r", "")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    links = content.count("/problems/")
    print(f"OK {out_path}  chars={len(content)}  /problems/ links={links}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    extract(Path(sys.argv[1]), Path(sys.argv[2]))
