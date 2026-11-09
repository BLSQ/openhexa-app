import Button from "core/components/Button";
import {
  CursorTypes,
  FlameChartContainer,
  FlameChartPlugin,
  RegionTypes,
  TimeGridPlugin,
  TogglePlugin,
} from "flame-chart-js";
import { useTranslation } from "next-i18next";
import { useEffect, useRef, useState } from "react";
import {
  buildTimeline,
  formatSeconds,
  getLaneDuration,
  Profile,
  ProfileSpan,
  TimelineNode,
} from "./profile";

// Larger than flame-chart-js's defaults, to make frames easier to read and click.
const BLOCK_HEIGHT = 24;
const FONT = "12px sans-serif";
// flame-chart-js draws blocks with a 1px gap.
const ROW_HEIGHT = BLOCK_HEIGHT + 1;
// The font height and a 10px padding.
const TIME_GRID_HEIGHT = 24;
// Imports and library internals make stacks deeper than this: the rest of the stack is reached
// by dragging the lane up.
const MAX_LANE_ROWS = 20;

// A lane title that collapses the lane when clicked. TogglePlugin also lets users resize lanes,
// and its collapsing leaves the canvas at its previous height: collapsed lanes are left out of the
// chart instead.
class LaneTitlePlugin extends TogglePlugin {
  constructor(
    title: string,
    seconds: number,
    private collapsed: boolean,
    private onToggle: () => void,
  ) {
    super(title, { styles: { height: BLOCK_HEIGHT, font: FONT } });
    // The chart takes its time range from its plugins: without it, it loops forever when all
    // lanes are collapsed.
    this.min = 0;
    this.max = seconds;
  }

  init(
    renderEngine: Parameters<TogglePlugin["init"]>[0],
    interactionsEngine: Parameters<TogglePlugin["init"]>[1],
  ) {
    this.renderEngine = renderEngine;
    this.interactionsEngine = interactionsEngine;
    if (!this.collapsed) {
      this.getNextEngine().setFlexible();
    }
    this.interactionsEngine.on("click", (region) => {
      if (region?.type === "toggle" && region.data === this.renderEngine.id) {
        this.onToggle();
      }
    });
  }

  render() {
    const { styles } = this;
    this.renderEngine.setCtxFont(styles.font);
    this.renderEngine.setCtxValue("fillStyle", styles.color);
    this.renderEngine.fillRect(0, 0, this.renderEngine.width, styles.height);
    this.renderEngine.setCtxValue("fillStyle", styles.fontColor);
    const textX = styles.leftPadding + styles.triangleWidth + 6;
    this.renderEngine.addText({
      text: this.title,
      x: textX,
      y: 0,
      w: this.renderEngine.width,
    });
    this.renderEngine.renderTriangle({
      color: styles.triangleColor,
      x: styles.leftPadding,
      y: (styles.height - styles.triangleHeight) / 2,
      width: styles.triangleWidth,
      height: styles.triangleHeight,
      direction: this.collapsed ? "right" : "bottom",
    });
    const { width } = this.renderEngine.ctx.measureText(this.title);
    // flame-chart-js declares these enums as const, which cannot be imported at runtime.
    this.interactionsEngine.addHitRegion(
      "toggle" as RegionTypes,
      this.renderEngine.id,
      0,
      0,
      textX + width,
      styles.height,
      "pointer" as CursorTypes,
    );
  }
}

function getDepth(spans: ProfileSpan[]): number {
  return spans.reduce(
    (depth, span) => Math.max(depth, 1 + getDepth(span[3])),
    0,
  );
}

type TimelineChartProps = {
  profile: Profile;
};

const TimelineChart = ({ profile }: TimelineChartProps) => {
  const { t } = useTranslation();
  const boxRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<FlameChartContainer | null>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const zoomRef = useRef<{ start: number; end: number } | null>(null);
  const [collapsed, setCollapsed] = useState<number[]>([]);
  const seconds = profile.duration / 1000;

  useEffect(() => {
    const box = boxRef.current;
    const canvas = canvasRef.current;
    if (!box || !canvas || !box.clientWidth) {
      return;
    }
    const showTooltip = (
      node: TimelineNode | undefined,
      mouse: { x: number; y: number } | null,
    ) => {
      const tooltip = tooltipRef.current;
      if (!tooltip) {
        return;
      }
      if (!node || !mouse) {
        tooltip.hidden = true;
        return;
      }
      const [frame, duration] = Array.from(tooltip.children);
      frame.textContent = node.frame;
      duration.textContent = t("{{duration}}, from {{start}}", {
        duration: formatSeconds(node.duration),
        start: formatSeconds(node.start),
      });
      tooltip.hidden = false;
      const rect = canvas.getBoundingClientRect();
      const x = rect.left + mouse.x + 12;
      const y = rect.top + mouse.y + 12;
      const { offsetWidth: width, offsetHeight: height } = tooltip;
      tooltip.style.left = `${Math.min(x, window.innerWidth - width - 8)}px`;
      tooltip.style.top = `${y + height > window.innerHeight ? y - height - 24 : y}px`;
    };
    const hideTooltip = () => showTooltip(undefined, null);
    canvas.addEventListener("mouseleave", hideTooltip);
    const toggle = (index: number) =>
      setCollapsed((current) =>
        current.includes(index)
          ? current.filter((i) => i !== index)
          : [...current, index],
      );
    const lanes = profile.lanes.map((lane, index) => {
      const { nodes } = lane;
      const isCollapsed = collapsed.includes(index);
      const duration = getLaneDuration(profile, nodes);
      const title = new LaneTitlePlugin(
        duration ? `${lane.name} · ${formatSeconds(duration)}` : lane.name,
        seconds,
        isCollapsed,
        () => toggle(index),
      );
      if (isCollapsed) {
        return { title, plugin: null, height: 0 };
      }
      const plugin = new FlameChartPlugin({
        name: lane.name,
        data: buildTimeline(profile, nodes),
      });
      const rows = Math.min(Math.max(1, getDepth(nodes)), MAX_LANE_ROWS);
      const height = rows * ROW_HEIGHT + 1;
      (plugin as { height: number | "flexible" }).height = height;
      return { title, plugin, height };
    });
    const plugins = [
      new TimeGridPlugin({ styles: { font: FONT } }),
      ...lanes.flatMap(({ title, plugin }) =>
        plugin ? [title, plugin] : [title],
      ),
    ];
    const height =
      TIME_GRID_HEIGHT +
      lanes.reduce((total, lane) => total + ROW_HEIGHT + lane.height, 0);
    canvas.width = box.clientWidth;
    canvas.height = height;
    const chart = new FlameChartContainer({
      canvas,
      plugins,
      settings: {
        options: {
          timeUnits: "s",
          tooltip: (region, _, mouse) =>
            showTooltip(region?.data?.source, mouse),
        },
        styles: {
          main: { blockHeight: BLOCK_HEIGHT, font: FONT },
          timeGrid: { font: FONT },
        },
      },
    });
    chartRef.current = chart;
    if (zoomRef.current) {
      chart.setZoom(zoomRef.current.start, zoomRef.current.end);
    }
    for (const { plugin } of lanes) {
      plugin?.on("select", ({ node }) => {
        if (node) {
          const { start, duration } = node.source;
          chart.setZoom(start, start + duration);
        }
      });
    }
    const observer = new ResizeObserver(() =>
      chart.resize(box.clientWidth, height),
    );
    observer.observe(box);
    return () => {
      const { positionX, width, zoom } = chart.renderEngine;
      zoomRef.current = { start: positionX, end: positionX + width / zoom };
      observer.disconnect();
      canvas.removeEventListener("mouseleave", hideTooltip);
      hideTooltip();
      chart.interactionsEngine.destroy();
      chartRef.current = null;
    };
  }, [profile, collapsed, seconds, t]);

  return (
    <div className="space-y-2">
      <div className="flex justify-end">
        <Button
          size="sm"
          variant="white"
          onClick={() => chartRef.current?.setZoom(0, seconds)}
        >
          {t("Reset zoom")}
        </Button>
      </div>
      <div ref={boxRef} className="w-full">
        <canvas ref={canvasRef} />
      </div>
      <div
        ref={tooltipRef}
        hidden
        className="pointer-events-none fixed z-50 max-w-md rounded-sm bg-white px-2 py-1 text-xs shadow-md ring-1 ring-black/10"
      >
        <div className="font-medium text-gray-900" />
        <div className="text-gray-600" />
      </div>
    </div>
  );
};

export default TimelineChart;
