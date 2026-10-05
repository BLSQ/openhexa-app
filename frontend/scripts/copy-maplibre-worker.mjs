/**
 * MapLibre 6 ships its tiling worker as a separate ES module instead of
 * inlining it, and resolves its URL from `import.meta.url` at runtime. Next
 * rewrites that to something that is not an http(s) URL, so the lookup returns
 * an empty string and the worker never loads: a working basemap with the data
 * silently absent. The documented fix is to serve the worker ourselves and hand
 * MapLibre the URL (see `setWorkerUrl` in ResultsMap).
 *
 * The shared chunk travels with it: the worker imports it by relative path, so
 * both files have to land in the same directory.
 *
 * Copied from node_modules at build time rather than committed, so the worker
 * can never drift from the installed version.
 */
import { copyFileSync, mkdirSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";

const WORKER_FILES = ["maplibre-gl-worker.mjs", "maplibre-gl-shared.mjs"];

const dist = path.join(
  path.dirname(
    createRequire(import.meta.url).resolve("maplibre-gl/package.json"),
  ),
  "dist",
);
const destination = path.join(process.cwd(), "public", "maplibre");

mkdirSync(destination, { recursive: true });
for (const file of WORKER_FILES) {
  copyFileSync(path.join(dist, file), path.join(destination, file));
}

console.log(
  `Copied ${WORKER_FILES.length} MapLibre worker files to ${destination}`,
);
