import clsx from "clsx";
import { useTranslation } from "next-i18next";
import { CSSProperties, MouseEvent, useState } from "react";
import { ChartKind, formatNumber, niceTicks, Point, toPoints } from "./chart";

type Row = Record<string, unknown>;

type ResultsChartProps = {
  kind: ChartKind;
  rows: Row[];
};

// Chart chrome (gridlines, axis rules, ticks) uses the app's Tailwind grays so
// the charts sit consistently inside the rest of the editor.
const SERIES_COLOR = "var(--color-brand)";
const SLICE_COLORS = [
  "var(--color-brand)", // pink
  "var(--color-amber-600)",
  "var(--color-sky-600)",
  "var(--color-red-600)",
  "var(--color-violet-600)",
  "var(--color-emerald-600)",
];
const OTHER_COLOR = "var(--color-gray-500)";

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

// The pie has its own square coordinate system, kept 1:1 with its rendered
// pixels so a slice's geometry can also position its tooltip. The radius leaves
// room for the hovered slice to be pushed out without clipping.
const PIE_SIZE = 200;
const PIE_CENTER = PIE_SIZE / 2;
const PIE_RADIUS = 88;
const SLICE_POP = 6;
// Where along a slice's mid-angle its tooltip hangs from, as a share of the
// radius: close enough to the middle that the tooltip stays inside the box.
const TOOLTIP_RADIUS_RATIO = 0.6;

const percent = (share: number): string => `${(share * 100).toFixed(1)}%`;

// SVG angles start at 3 o'clock and grow clockwise, so everything is shifted by
// a quarter turn to make the first slice start at 12 o'clock.
const polar = (radius: number, degrees: number) => {
  const radians = ((degrees - 90) * Math.PI) / 180;
  return {
    x: PIE_CENTER + radius * Math.cos(radians),
    y: PIE_CENTER + radius * Math.sin(radians),
  };
};

const slicePath = (start: number, end: number): string => {
  // A full turn has identical endpoints, which an arc command draws as nothing;
  // two half turns give the single-slice case a real circle.
  if (end - start >= 359.99) {
    const top = polar(PIE_RADIUS, 0);
    const bottom = polar(PIE_RADIUS, 180);
    return [
      `M ${top.x} ${top.y}`,
      `A ${PIE_RADIUS} ${PIE_RADIUS} 0 1 1 ${bottom.x} ${bottom.y}`,
      `A ${PIE_RADIUS} ${PIE_RADIUS} 0 1 1 ${top.x} ${top.y}`,
      "Z",
    ].join(" ");
  }
  const from = polar(PIE_RADIUS, start);
  const to = polar(PIE_RADIUS, end);
  return [
    `M ${PIE_CENTER} ${PIE_CENTER}`,
    `L ${from.x} ${from.y}`,
    `A ${PIE_RADIUS} ${PIE_RADIUS} 0 ${end - start > 180 ? 1 : 0} 1 ${to.x} ${to.y}`,
    "Z",
  ].join(" ");
};

/**
 * The readout for whatever mark the pointer is on, positioned by its caller
 * inside a `relative` box: the marks are drawn in their own coordinate systems,
 * so each chart converts its geometry to a position and this only has to render.
 */
const Tooltip = ({
  label,
  value,
  share,
  style,
}: {
  label: string;
  value: number;
  share?: number;
  style: CSSProperties;
}) => (
  <div
    role="tooltip"
    className="pointer-events-none absolute z-10 -translate-x-1/2 -translate-y-full rounded-md bg-gray-900/90 px-2 py-1 text-xs whitespace-nowrap text-white shadow-sm"
    style={style}
  >
    <span className="font-medium">{label}</span>{" "}
    <span className="font-mono tabular-nums">
      {formatNumber(value)}
      {share !== undefined && ` (${percent(share)})`}
    </span>
  </div>
);

const Bars = ({ points }: { points: Point[] }) => {
  const [activeIndex, setActiveIndex] = useState<number | null>(null);

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
        const isActive = activeIndex === index;
        return (
          // A bar prints its own label and value, so pointing at one highlights
          // the row rather than repeating both in a tooltip: what the reader
          // gains is the row they are on, kept legible across a long list.
          <div
            key={`${point.label}-${index}`}
            className={clsx(
              "-mx-1 flex items-center gap-3 rounded px-1 py-[3px]",
              isActive && "bg-gray-50",
            )}
            onMouseEnter={() => setActiveIndex(index)}
            onMouseLeave={() => setActiveIndex(null)}
          >
            <div
              className={clsx(
                "w-[26%] shrink-0 truncate text-right text-xs",
                isActive ? "font-medium text-gray-900" : "text-gray-600",
              )}
              title={point.label}
            >
              {point.label}
            </div>
            <div className="relative h-4 min-w-0 flex-1">
              <div
                className={clsx(
                  "absolute h-full transition-opacity",
                  point.value < 0 ? "rounded-l-[4px]" : "rounded-r-[4px]",
                )}
                style={{
                  backgroundColor: SERIES_COLOR,
                  left: `${Math.min(zeroOffset, offset)}%`,
                  width: `${Math.abs(offset - zeroOffset)}%`,
                  opacity: activeIndex === null || isActive ? 1 : 0.4,
                }}
              />
            </div>
            <div
              className={clsx(
                "w-[14%] shrink-0 text-right font-mono text-xs tabular-nums",
                isActive ? "text-gray-900" : "text-gray-700",
              )}
            >
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
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
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

  // Points are too small and too dense to hover one by one, so a single band
  // over the plot resolves the nearest one instead. The band spans exactly the
  // plot and the x scale is linear across it, so where the pointer sits inside
  // the band — a ratio, not a pixel — is all the mapping needs, and the chart
  // never has to know its own rendered width.
  const trackPointer = (event: MouseEvent<SVGRectElement>) => {
    const box = event.currentTarget.getBoundingClientRect();
    if (!box.width) {
      return;
    }
    const ratio = (event.clientX - box.left) / box.width;
    const nearest = Math.round(ratio * (points.length - 1));
    setActiveIndex(Math.min(Math.max(nearest, 0), points.length - 1));
  };

  const active = activeIndex === null ? null : points[activeIndex];

  return (
    <div className="relative">
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
          style={{ stroke: SERIES_COLOR }}
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
              style={{ fill: SERIES_COLOR }}
              // The ring keeps a marker legible where it overlaps the line.
              stroke="#ffffff"
              strokeWidth={2}
              vectorEffect="non-scaling-stroke"
            />
          ))}

        {activeIndex !== null && active && (
          <g>
            {/* The rule ties the point back to its x label, which for a dense
                series is the only way to tell which row is being read. */}
            <line
              x1={xOf(activeIndex)}
              x2={xOf(activeIndex)}
              y1={PADDING.top}
              y2={PADDING.top + PLOT_HEIGHT}
              className="stroke-gray-300"
              strokeWidth={1}
              strokeDasharray="3 3"
              vectorEffect="non-scaling-stroke"
            />
            {/* Drawn whatever the series length: past MAX_MARKERS the standing
                markers are gone, and this is then the only one. */}
            <circle
              cx={xOf(activeIndex)}
              cy={yOf(active.value)}
              r={5}
              style={{ fill: SERIES_COLOR }}
              stroke="#ffffff"
              strokeWidth={2}
              vectorEffect="non-scaling-stroke"
            />
          </g>
        )}

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

        <rect
          x={PADDING.left}
          y={PADDING.top}
          width={PLOT_WIDTH}
          height={PLOT_HEIGHT}
          fill="transparent"
          onMouseMove={trackPointer}
          onMouseLeave={() => setActiveIndex(null)}
        />
      </svg>
      {activeIndex !== null && active && (
        <Tooltip
          label={active.label}
          value={active.value}
          style={{
            // Percentages of the box rather than pixels: the viewBox scales with
            // the panel, so a share of it survives any width. Clamped so a
            // tooltip at either end is not cut off by the panel edge.
            left: `${Math.min(Math.max((xOf(activeIndex) / VIEW_WIDTH) * 100, 10), 90)}%`,
            top: `${((yOf(active.value) - 10) / VIEW_HEIGHT) * 100}%`,
          }}
        />
      )}
    </div>
  );
};

const Pie = ({ points }: { points: Point[] }) => {
  const { t } = useTranslation();
  // Held for the whole pie rather than per slice so pointing at either a slice
  // or its legend row highlights the pair.
  const [activeIndex, setActiveIndex] = useState<number | null>(null);

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

  // Each slice is laid out once, from its running start angle: the mid-angle is
  // what both the pushed-out hover state and the tooltip position are derived
  // from, so the geometry is the single source for the interaction too.
  let cursor = 0;
  const arcs = slices.map((slice, index) => {
    const start = cursor;
    cursor += (slice.value / total) * 360;
    const middle = (start + cursor) / 2;
    const pop = polar(SLICE_POP, middle);
    return {
      ...slice,
      index,
      share: slice.value / total,
      color: colorOf(index),
      path: slicePath(start, cursor),
      offset: { x: pop.x - PIE_CENTER, y: pop.y - PIE_CENTER },
      anchor: polar(PIE_RADIUS * TOOLTIP_RADIUS_RATIO, middle),
    };
  });

  const active = activeIndex === null ? null : arcs[activeIndex];

  return (
    <div className="flex flex-wrap items-center gap-6">
      <div
        className="relative shrink-0"
        style={{ width: PIE_SIZE, height: PIE_SIZE }}
      >
        <svg
          viewBox={`0 0 ${PIE_SIZE} ${PIE_SIZE}`}
          className="h-full w-full"
          role="img"
          aria-label={t("Pie chart")}
        >
          {arcs.map((arc) => (
            <path
              key={`${arc.label}-${arc.index}`}
              d={arc.path}
              // A hairline of the surface colour is enough to separate
              // neighbours; a wedge of background between them reads as a hole.
              stroke="#ffffff"
              strokeWidth={1}
              // Fill, offset and dimming go through `style`, not presentation
              // attributes: the palette is CSS custom properties, which
              // attributes do not resolve, and CSS properties are what the
              // transition below can actually animate. Pushing the hovered
              // slice out along its own mid-angle and dimming the others is
              // what makes it stand out without changing the shares being
              // compared.
              style={{
                fill: arc.color,
                opacity: active && active.index !== arc.index ? 0.4 : 1,
                transform:
                  active?.index === arc.index
                    ? `translate(${arc.offset.x}px, ${arc.offset.y}px)`
                    : undefined,
              }}
              className="cursor-default transition-[opacity,transform] duration-150"
              onMouseEnter={() => setActiveIndex(arc.index)}
              onMouseLeave={() => setActiveIndex(null)}
            />
          ))}
        </svg>
        {active && (
          <Tooltip
            label={active.label}
            value={active.value}
            share={active.share}
            // The pie's box is 1:1 with its coordinate system, so the anchor is
            // already in pixels.
            style={{ left: active.anchor.x, top: active.anchor.y - 8 }}
          />
        )}
      </div>
      <ul className="min-w-0 flex-1 space-y-1.5">
        {arcs.map((arc) => (
          <li
            key={`${arc.label}-${arc.index}`}
            className={clsx(
              "-mx-1 flex items-center gap-2 rounded px-1 text-xs",
              active?.index === arc.index && "bg-gray-50",
            )}
            onMouseEnter={() => setActiveIndex(arc.index)}
            onMouseLeave={() => setActiveIndex(null)}
          >
            <span
              className="h-2.5 w-2.5 shrink-0 rounded-sm"
              style={{ backgroundColor: arc.color }}
            />
            <span
              className="min-w-0 flex-1 truncate text-gray-600"
              title={arc.label}
            >
              {arc.label}
            </span>
            <span className="shrink-0 font-mono tabular-nums text-gray-700">
              {formatNumber(arc.value)}
            </span>
            <span className="w-12 shrink-0 text-right font-mono tabular-nums text-gray-400">
              {percent(arc.share)}
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
