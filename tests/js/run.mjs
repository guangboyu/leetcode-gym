/* Entry point: imports every *.test.mjs and runs them. See harness.mjs. */
import "./h.test.mjs";
import "./format.test.mjs";
import "./heatmap.test.mjs";
import "./router.test.mjs";
import "./keys.test.mjs";
import "./store.test.mjs";
import "./pyhl.test.mjs";
import "./md.test.mjs";
import "./views.test.mjs";
import { run } from "./harness.mjs";

await run();
