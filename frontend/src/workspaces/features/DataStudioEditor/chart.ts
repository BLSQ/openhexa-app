import { isNumericValue, stringifyCellValue } from "./format";

type Row = Record<string, unknown>;

export type ChartKind = "bar" | "line" | "pie";

export type Point = {
  label: string;
  value: number;
};

/**
 * A chart is selected by the names of the columns a query returns — the
 * convention django-sql-dashboard uses, kept identical so the names are already
 * familiar. Only the pair a chart plots has to be present: a query is free to
 * return extra columns (an id, a filter it also selects, anything kept while
 * debugging) and is still charted, with the extras a tab away in the table.
 * The declaration order below is the precedence when a query happens to return
 * more than one convention, so the choice stays predictable.
 */
export const CHART_CONVENTIONS: {
  kind: ChartKind;
  label: string;
  value: string;
}[] = [
  { kind: "bar", label: "bar_label", value: "bar_quantity" },
  { kind: "line", label: "line_x", value: "line_y" },
  { kind: "pie", label: "pie_label", value: "pie_quantity" },
];

const findChart = (columns: string[]) =>
  CHART_CONVENTIONS.find(
    (chart) => columns.includes(chart.label) && columns.includes(chart.value),
  );

/** Postgres serialises NUMERIC/bigint as strings, so parse through the same
 * numeric-shape check the results table uses rather than trusting typeof. */
const toNumber = (value: unknown): number | null =>
  isNumericValue(value) ? Number(value) : null;

const toLabel = (value: unknown): string =>
  stringifyCellValue(value).trim() || "—";

export const formatNumber = (value: number): string =>
  Number.isInteger(value)
    ? value.toLocaleString()
    : value.toLocaleString(undefined, { maximumFractionDigits: 2 });

/**
 * The chart a result should be drawn as, or null to fall back to the table.
 * Column names alone are not enough: a text column named `bar_quantity` cannot
 * be placed on a scale, so the values are checked before committing to a chart.
 */
export const detectChart = (
  columns: string[],
  rows: Row[],
): ChartKind | null => {
  const chart = findChart(columns);
  if (!chart || rows.length === 0) {
    return null;
  }
  const present = rows.filter((row) => row[chart.value] !== null);
  const plottable =
    present.length > 0 &&
    present.every((row) => isNumericValue(row[chart.value]));
  return plottable ? chart.kind : null;
};

/**
 * Turn raw result rows into chartable points, preserving the order the query
 * returned them in — the SQL author's ORDER BY is the intended reading order,
 * so charts never re-sort. Rows whose value is not numeric are dropped: they
 * cannot be placed on a scale, and the table tab still shows them.
 */
export const toPoints = (
  kind: ChartKind,
  rows: Row[],
  limit: number,
): { points: Point[]; hidden: number } => {
  const chart = CHART_CONVENTIONS.find((entry) => entry.kind === kind)!;
  const points: Point[] = [];
  for (const row of rows) {
    const value = toNumber(row[chart.value]);
    if (value !== null) {
      points.push({ label: toLabel(row[chart.label]), value });
    }
  }
  return {
    points: points.slice(0, limit),
    hidden: Math.max(0, points.length - limit),
  };
};

/**
 * Axis ticks on 1/2/5 × 10ⁿ boundaries, so labels read as round numbers instead
 * of the raw data extremes.
 */
export const niceTicks = (min: number, max: number, count = 4): number[] => {
  if (!Number.isFinite(min) || !Number.isFinite(max) || min === max) {
    return [min];
  }
  const rawStep = (max - min) / count;
  const magnitude = 10 ** Math.floor(Math.log10(rawStep));
  const normalized = rawStep / magnitude;
  // Round the step to the nearest 1/2/5 × 10ⁿ rather than the next one up, so a
  // domain like 0–100 gets six ticks of 20 instead of three of 50.
  const step =
    (normalized < 1.5 ? 1 : normalized < 3 ? 2 : normalized < 7 ? 5 : 10) *
    magnitude;

  const first = Math.ceil(min / step) * step;
  const ticks: number[] = [];
  // Stepping by index and rounding before the bound check: accumulating `+=
  // step` drifts, and a drifted last tick (1.0000000000000002 for a domain
  // ending at 1) tests as out of range and silently disappears from the axis.
  for (let index = 0; ; index++) {
    const tick = Number((first + index * step).toPrecision(12));
    if (tick > max) {
      return ticks;
    }
    ticks.push(tick);
  }
};
