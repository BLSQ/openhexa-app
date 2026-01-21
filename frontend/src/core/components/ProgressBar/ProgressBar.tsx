import clsx from "clsx";
import { useMemo } from "react";

export type ProgressBarProps = {
  value: number;
  max: number;
  className?: string;
  showLabel?: boolean;
};

type UsageLevel = "normal" | "warning" | "critical";

const getUsageLevel = (percentage: number): UsageLevel => {
  if (percentage >= 90) return "critical";
  if (percentage >= 75) return "warning";
  return "normal";
};

const colorClasses: Record<UsageLevel, { bar: string; text: string }> = {
  normal: { bar: "bg-emerald-400", text: "text-emerald-400" },
  warning: { bar: "bg-amber-400", text: "text-amber-400" },
  critical: { bar: "bg-rose-800", text: "text-rose-800" },
};

const ProgressBar = (props: ProgressBarProps) => {
  const { value, max, className, showLabel = true } = props;

  const percentage = useMemo(() => {
    if (max <= 0) return 0;
    return Math.min(100, Math.round((value / max) * 100));
  }, [value, max]);

  const usageLevel = getUsageLevel(percentage);
  const colors = colorClasses[usageLevel];

  return (
    <div className={clsx("w-full", className)}>
      <div className="flex items-center gap-3">
        <div className="flex-1 bg-gray-200 rounded-full h-2.5">
          <div
            className={clsx(
              "h-2.5 rounded-full transition-all duration-300",
              colors.bar,
            )}
            style={{ width: `${percentage}%` }}
          />
        </div>
        {showLabel && (
          <span
            className={clsx(
              "text-sm font-medium whitespace-nowrap",
              colors.text,
            )}
          >
            {value} / {max}
          </span>
        )}
      </div>
    </div>
  );
};

export default ProgressBar;
