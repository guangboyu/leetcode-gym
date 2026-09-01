/* Load the vendored marked UMD build and expose it as globalThis.marked in
 * both runtimes: under jsc the UMD's global branch already sets it; under node
 * the file is CommonJS, so its exports arrive as the default import. */
import * as m from "../../tracker/static/vendor/marked.umd.js";
if (!globalThis.marked) globalThis.marked = m.default && m.default.parse ? m.default : m;
