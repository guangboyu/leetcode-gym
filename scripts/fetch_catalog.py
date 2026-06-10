#!/usr/bin/env python3
"""Build source/data/catalog.json: slug -> {id, title, difficulty, paid_only, rating}.

Joins two public sources:
  - https://leetcode.com/api/problems/all/        (all problems: id, title, difficulty, paid flag)
  - https://zerotrac.github.io/leetcode_problem_rating/data.json  (contest difficulty ratings)
"""
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "source" / "data" / "catalog.json"

LC_ALL_URL = "https://leetcode.com/api/problems/all/"
RATINGS_URL = "https://zerotrac.github.io/leetcode_problem_rating/data.json"
DIFFICULTY = {1: "Easy", 2: "Medium", 3: "Hard"}


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def main():
    lc = fetch_json(LC_ALL_URL)
    ratings = {e["TitleSlug"]: round(e["Rating"]) for e in fetch_json(RATINGS_URL)}

    catalog = {}
    for p in lc["stat_status_pairs"]:
        slug = p["stat"]["question__title_slug"]
        catalog[slug] = {
            "id": p["stat"]["frontend_question_id"],
            "title": p["stat"]["question__title"],
            "difficulty": DIFFICULTY[p["difficulty"]["level"]],
            "paid_only": p["paid_only"],
            "rating": ratings.get(slug),
        }

    catalog = dict(sorted(catalog.items()))
    OUT.write_text(json.dumps(catalog, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    rated = sum(1 for v in catalog.values() if v["rating"] is not None)
    print(f"Wrote {OUT}  ({len(catalog)} problems, {rated} with ratings)")


if __name__ == "__main__":
    main()
