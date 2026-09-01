/* format.js — small, pure text formatters shared by every view.
 *
 * Dates are the local calendar date strings the server uses (YYYY-MM-DD); the
 * arithmetic is done in UTC on those strings so DST never shifts a due date.
 */

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

/** "2026-09-05" → [2026, 9, 5] or null. */
export function parseDate(s) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(s || ""));
  return m ? [Number(m[1]), Number(m[2]), Number(m[3])] : null;
}

/** Whole days from `today` to `dateStr` (negative = past). */
export function daysBetween(dateStr, today) {
  const a = parseDate(dateStr), b = parseDate(today);
  if (!a || !b) return null;
  return Math.round((Date.UTC(a[0], a[1] - 1, a[2]) - Date.UTC(b[0], b[1] - 1, b[2])) / 86400000);
}

/** "5 Sep" (adds the year when it differs from today's). */
export function shortDate(dateStr, today) {
  const a = parseDate(dateStr);
  if (!a) return "";
  const b = parseDate(today);
  const yr = b && b[0] !== a[0] ? ` ${a[0]}` : "";
  return `${a[2]} ${MONTHS[a[1] - 1]}${yr}`;
}

/** Relative wording for a due date: today · tomorrow · in 4d · 3d overdue · 5 Sep. */
export function relDate(dateStr, today) {
  const d = daysBetween(dateStr, today);
  if (d == null) return "";
  if (d === 0) return "today";
  if (d < 0) return `${-d}d overdue`;
  if (d === 1) return "tomorrow";
  if (d <= 14) return `in ${d}d`;
  return shortDate(dateStr, today);
}

export function plural(n, one, many = one + "s") {
  return `${n} ${n === 1 ? one : many}`;
}

const BADGES = { hot100: "H100", interview150: "I150", neetcode250: "NC250", ox3f: "0x3F", tutorial: "TUT" };
export function listBadgeLabel(key) { return BADGES[key] || key; }

/** Rating display: real → "1656"; estimated → "≈1650" with est=true; none → "—". */
export function fmtRating(p, effRating) {
  if (p && p.rating) return { text: String(Math.round(p.rating)), est: false };
  const r = typeof effRating === "function" ? effRating(p) : null;
  return r ? { text: `≈${r}`, est: true } : { text: "—", est: false };
}

/** Capitalise the first character only ("chasing: Read and write" → "Chasing: …"). */
export function titleCase(s) {
  s = String(s || "");
  return s.charAt(0).toUpperCase() + s.slice(1);
}

/** 2678 → "2,678" (tabular tables use their own font feature; this is for prose). */
export function fmtInt(n) {
  return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}
