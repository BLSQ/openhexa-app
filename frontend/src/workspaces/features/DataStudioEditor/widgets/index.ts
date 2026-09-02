export { default as ResultsChart } from "./ResultsChart";
export { default as ResultsTable } from "./ResultsTable";
export { default as WidgetHint } from "./WidgetHint";
export { detectChart } from "./chart";
export { detectMap, toFeatures } from "./map";

// ResultsMap is deliberately absent: it pulls the whole MapLibre stack in at
// module scope, and DataStudioResults loads it through `next/dynamic` to keep
// that weight out of the editor bundle. Re-exporting it here would let any
// static import of this barrel drag MapLibre back in and silently undo the
// split, so that one widget is imported by its own path.
