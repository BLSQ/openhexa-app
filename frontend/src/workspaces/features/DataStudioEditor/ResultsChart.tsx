import { useTranslation } from "next-i18next";
import { ChartKind, formatNumber, niceTicks, Point, toPoints } from "./chart";

type Row = Record<string, unknown>;

type ResultsChartProps = {
  kind: ChartKind;
  rows: Row[];
};

// Data colours, validated against a white chart surface: the categorical slots
// clear the lightness band, the chroma floor, colour-blind separation (worst
// adjacent pair ΔE 9.1) and the normal-vision floor (ΔE 19.6). Three of them sit
// below 3:1 contrast on white, which is why the pie always prints a visible
// label and value beside each slice instead of relying on colour alone.
// Chart chrome (gridlines, axis rules, ticks) uses the app's Tailwind grays so
// the charts sit consistently inside the rest of the editor.
const SERIES_COLOR = "#2a78d6";
const SLICE_COLORS = [
  "#2a78d6", // blue
  "#eb6834", // orange
  "#1baf7a", // aqua
  "#eda100", // yellow
  "#e87ba4", // magenta
  "#008300", // green
];
const OTHER_COLOR = "#898781";

// Past ~30 bars the labels stop being readable in a results panel, and
// part-to-whole stops being readable at a glance past six slices. The rest of
// the rows stay one tab away in the table.
const MAX_BARS = 30;
const MAX_SLICES = 6;
const MAX_POINTS = 1000;
// Past this many points the line's markers merge together and only add ink.
const MAX_MARKERS = 40;

// A fixed coordinate system scaled by the viewBox: the chart has no access to
// its rendered width, and the panel is always wide enough that the ratio holds.
// The bottom band is inside the box so the x labels are never cut off.
const VIEW_WIDTH = 800;
const VIEW_HEIGHT = 260;
const PADDING = { top: 12, right: 16, bottom: 28, left: 56 };
const PLOT_WIDTH = VIEW_WIDTH - PADDING.left - PADDING.right;
const PLOT_HEIGHT = VIEW_HEIGHT - PADDING.top - PADDING.bottom;

// Degrees of surface colour between pie slices. White separating the marks is
// what makes neighbours read as distinct, rather than a stroke around each one.
const SLICE_GAP_DEG = 1;

const Bars = ({ points }: { points: Point[] }) => {
  // Bars grow from zero, not from the smallest value — anchoring anywhere else
  // would overstate the differences between them. Negative values extend to the
  // left of the zero line.
  const values = points.map((point) => point.value);
  const domainMin = Math.min(0, ...values);
  const domainMax = Math.max(0, ...values);
  const span = domainMax - domainMin || 1;
  const zeroOffset = ((0 - domainMin) / span) * 100;

  return (
    <div className="min-w-0">
      {points.map((point, index) => {
        const offset = ((point.value - domainMin) / span) * 100;
        return (
          <div
            key={`${point.label}-${index}`}
            className="flex items-center gap-3 py-[3px]"
          >
            <div
              className="w-[26%] shrink-0 truncate text-right text-xs text-gray-600"
              title={point.label}
            >
              {point.label}
            </div>
            <div className="relative h-4 min-w-0 flex-1">
              <div
                className={
                  point.value < 0
                    ? "absolute h-full rounded-l-[4px]"
                    : "absolute h-full rounded-r-[4px]"
                }
                style={{
                  backgroundColor: SERIES_COLOR,
                  left: `${Math.min(zeroOffset, offset)}%`,
                  width: `${Math.abs(offset - zeroOffset)}%`,
                }}
              />
            </div>
            <div className="w-[14%] shrink-0 text-right font-mono text-xs tabular-nums text-gray-700">
              {formatNumber(point.value)}
            </div>
          </div>
        );
      })}
    </div>
  );
};

/**
 * A single series over an ordered x column. x is treated as ordinal — points
 * are evenly spaced in the order the query returned them — so any label type
 * (dates, months, week numbers) plots without the chart having to parse it.
 * The query's ORDER BY is therefore what defines the reading order.
 */
const Line = ({ points }: { points: Point[] }) => {
  const { t } = useTranslation();
  const values = points.map((point) => point.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  // A flat series would divide by zero; give it a band to sit in the middle of.
  const [domainMin, domainMax] = min === max ? [min - 1, max + 1] : [min, max];

  const xOf = (index: number) =>
    points.length === 1
      ? PADDING.left + PLOT_WIDTH / 2
      : PADDING.left + (index / (points.length - 1)) * PLOT_WIDTH;
  const yOf = (value: number) =>
    PADDING.top +
    PLOT_HEIGHT -
    ((value - domainMin) / (domainMax - domainMin)) * PLOT_HEIGHT;

  const labelIndexes =
    points.length <= 2
      ? points.map((_, index) => index)
      : [0, Math.floor((points.length - 1) / 2), points.length - 1];

  return (
    <svg
      viewBox={`0 0 ${VIEW_WIDTH} ${VIEW_HEIGHT}`}
      className="h-auto w-full"
      role="img"
      aria-label={t("Line chart")}
    >
      {niceTicks(domainMin, domainMax).map((tick) => (
        <g key={tick}>
          <line
            x1={PADDING.left}
            x2={VIEW_WIDTH - PADDING.right}
            y1={yOf(tick)}
            y2={yOf(tick)}
            className="stroke-gray-200"
            strokeWidth={1}
            vectorEffect="non-scaling-stroke"
          />
          <text
            x={PADDING.left - 8}
            y={yOf(tick)}
            dominantBaseline="middle"
            textAnchor="end"
            className="fill-gray-400 text-[11px] tabular-nums"
          >
            {formatNumber(tick)}
          </text>
        </g>
      ))}

      <polyline
        points={points
          .map((point, index) => `${xOf(index)},${yOf(point.value)}`)
          .join(" ")}
        fill="none"
        stroke={SERIES_COLOR}
        strokeWidth={2}
        strokeLinecap="round"
        strokeLinejoin="round"
        vectorEffect="non-scaling-stroke"
      />

      {points.length <= MAX_MARKERS &&
        points.map((point, index) => (
          <circle
            key={`${point.label}-${index}`}
            cx={xOf(index)}
            cy={yOf(point.value)}
            r={4}
            fill={SERIES_COLOR}
            // The ring keeps a marker legible where it overlaps the line.
            stroke="#ffffff"
            strokeWidth={2}
            vectorEffect="non-scaling-stroke"
          >
            <title>{`${point.label}: ${formatNumber(point.value)}`}</title>
          </circle>
        ))}

      {labelIndexes.map((index, position) => (
        <text
          key={index}
          x={xOf(index)}
          y={VIEW_HEIGHT - 8}
          textAnchor={
            position === 0
              ? "start"
              : position === labelIndexes.length - 1
                ? "end"
                : "middle"
          }
          className="fill-gray-400 text-[11px]"
        >
          {points[index].label}
        </text>
      ))}
    </svg>
  );
};

const Pie = ({ points }: { points: Point[] }) => {
  const { t } = useTranslation();

  const hasOther = points.length > MAX_SLICES;
  const slices: Point[] = hasOther
    ? [
        ...points.slice(0, MAX_SLICES - 1),
        {
          label: t("Other"),
          value: points
            .slice(MAX_SLICES - 1)
            .reduce((sum, point) => sum + point.value, 0),
        },
      ]
    : points;

  const total = slices.reduce((sum, slice) => sum + slice.value, 0);
  const colorOf = (index: number) =>
    hasOther && index === slices.length - 1 ? OTHER_COLOR : SLICE_COLORS[index];

  const stops: string[] = [];
  let cursor = 0;
  slices.forEach((slice, index) => {
    const end = cursor + (slice.value / total) * 360;
    // Skip the gap on slivers, where it would eat the whole slice.
    const gap =
      slices.length > 1 && end - cursor > SLICE_GAP_DEG * 2 ? SLICE_GAP_DEG : 0;
    stops.push(`${colorOf(index)} ${cursor}deg ${end - gap}deg`);
    if (gap > 0) {
      stops.push(`#ffffff ${end - gap}deg ${end}deg`);
    }
    cursor = end;
  });

  return (
    <div className="flex flex-wrap items-center gap-6">
      <div
        className="h-[180px] w-[180px] shrink-0 rounded-full"
        style={{ background: `conic-gradient(${stops.join(", ")})` }}
        role="img"
        aria-label={t("Pie chart")}
      />
      <ul className="min-w-0 flex-1 space-y-1.5">
        {slices.map((slice, index) => (
          <li
            key={`${slice.label}-${index}`}
            className="flex items-center gap-2 text-xs"
          >
            <span
              className="h-2.5 w-2.5 shrink-0 rounded-sm"
              style={{ backgroundColor: colorOf(index) }}
            />
            <span
              className="min-w-0 flex-1 truncate text-gray-600"
              title={slice.label}
            >
              {slice.label}
            </span>
            <span className="shrink-0 font-mono tabular-nums text-gray-700">
              {formatNumber(slice.value)}
            </span>
            <span className="w-12 shrink-0 text-right font-mono tabular-nums text-gray-400">
              {((slice.value / total) * 100).toFixed(1)}%
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
};

// A pie takes every row and folds the tail into "Other" itself, so it is not
// capped here.
const LIMITS: Record<ChartKind, number> = {
  bar: MAX_BARS,
  line: MAX_POINTS,
  pie: Number.MAX_SAFE_INTEGER,
};

/**
 * The chart counterpart of ResultsTable: one component for every successful
 * result whose columns follow a chart convention. Callers only pass the kind
 * that `detectChart` resolved; the marks and their limits live here.
 */
const ResultsChart = ({ kind, rows }: ResultsChartProps) => {
  const { t } = useTranslation();

  const raw = toPoints(kind, rows, LIMITS[kind]);
  // A slice can only represent a positive share of a whole, so a pie excludes
  // non-positive rows rather than drawing them as if they were positive.
  const points =
    kind === "pie" ? raw.points.filter((point) => point.value > 0) : raw.points;
  const hidden =
    kind === "pie" ? raw.points.length - points.length : raw.hidden;

  if (points.length === 0) {
    return (
      <div className="flex h-full items-center justify-center p-4 text-sm text-gray-400">
        {kind === "pie"
          ? t("No positive values to chart.")
          : t("No numeric values to chart.")}
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col overflow-auto p-4">
      {kind === "bar" && <Bars points={points} />}
      {kind === "line" && <Line points={points} />}
      {kind === "pie" && <Pie points={points} />}
      {hidden > 0 && (
        <p className="mt-3 shrink-0 text-xs text-gray-400">
          {t("{{count}} more rows not shown — see the Table tab.", {
            count: hidden,
          })}
        </p>
      )}
    </div>
  );
};

export default ResultsChart;
