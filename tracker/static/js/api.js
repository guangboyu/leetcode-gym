/* api.js — the only module that talks to the local server.
 *
 * Every function returns parsed JSON and throws `ApiError` (with the HTTP
 * status and the server's `error` text) on failure, so views can show a toast
 * with a real message instead of the old `alert("Failed: …")`. Endpoints are
 * the ones in tracker/server.py; `/data/problems.json` is served with an ETag,
 * so the browser revalidates it for free on later launches.
 */

export class ApiError extends Error {
  constructor(status, message, body) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

async function request(method, path, body) {
  let res;
  try {
    res = await fetch(path, {
      method,
      headers: body === undefined ? {} : { "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch (err) {
    throw new ApiError(0, "The local server did not respond.", err);
  }
  const text = await res.text();
  let data = null;
  if (text) {
    try { data = JSON.parse(text); } catch (_) { data = { raw: text }; }
  }
  if (!res.ok) {
    const msg = (data && data.error) || `${res.status} ${res.statusText}`;
    throw new ApiError(res.status, msg, data);
  }
  return data;
}

export const getProblems = async () => (await request("GET", "/data/problems.json")).problems;
export const getTutorials = () => request("GET", "/data/tutorials.json");
export const getPatterns = () => request("GET", "/data/patterns.json");
export const getProgress = () => request("GET", "/api/progress");
export const getSettings = () => request("GET", "/api/settings");
export const putSettings = (patch) => request("POST", "/api/settings", patch);
export const resetSettings = () => request("POST", "/api/settings", { reset: true });
/** action: solved | solved_help | forgotten | reset | undo */
export const review = (slug, action) => request("POST", "/api/review", { slug, action });
export const getDataDir = () => request("GET", "/api/data-dir");
export const setDataDir = (path) => request("POST", "/api/data-dir", { path });
export const getActivity = () => request("GET", "/api/activity");
export const getAbout = () => request("GET", "/api/about");

/** Raw markdown of one tutorial, e.g. getTutorialMarkdown("SlidingWindow.md"). */
export async function getTutorialMarkdown(file) {
  let res;
  try {
    res = await fetch(`/tutorials/${encodeURIComponent(file)}`);
  } catch (err) {
    throw new ApiError(0, "The local server did not respond.", err);
  }
  if (!res.ok) throw new ApiError(res.status, `Tutorial ${file} not found`);
  return res.text();
}
