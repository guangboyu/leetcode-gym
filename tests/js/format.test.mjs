import { test, assert } from "./harness.mjs";
import { relDate, daysBetween, shortDate, plural, listBadgeLabel, fmtRating, titleCase, fmtInt } from "../../tracker/static/js/format.js";

const T = "2026-09-01";

test("format: relDate", () => {
  assert.equal(relDate("2026-09-01", T), "today");
  assert.equal(relDate("2026-09-02", T), "tomorrow");
  assert.equal(relDate("2026-09-05", T), "in 4d");
  assert.equal(relDate("2026-09-15", T), "in 14d");
  assert.equal(relDate("2026-09-16", T), "16 Sep");
  assert.equal(relDate("2026-08-29", T), "3d overdue");
  assert.equal(relDate("2027-01-03", T), "3 Jan 2027");
  assert.equal(relDate(null, T), "");
});

test("format: daysBetween crosses months and DST-free", () => {
  assert.equal(daysBetween("2026-10-01", T), 30);
  assert.equal(daysBetween("2026-03-30", "2026-03-28"), 2);
  assert.equal(shortDate("2026-12-25", T), "25 Dec");
});

test("format: plural / badges / rating / titleCase / fmtInt", () => {
  assert.equal(plural(1, "day"), "1 day");
  assert.equal(plural(3, "day"), "3 days");
  assert.equal(listBadgeLabel("hot100"), "H100");
  assert.equal(listBadgeLabel("tutorial"), "TUT");
  assert.deepEqual(fmtRating({ rating: 1655.6 }, () => 1650), { text: "1656", est: false });
  assert.deepEqual(fmtRating({ rating: null, difficulty: "Medium" }, () => 1650), { text: "≈1650", est: true });
  assert.deepEqual(fmtRating({ rating: null }, () => null), { text: "—", est: false });
  assert.equal(titleCase("chasing: Read and write"), "Chasing: Read and write");
  assert.equal(fmtInt(2678), "2,678");
  assert.equal(fmtInt(999), "999");
});
