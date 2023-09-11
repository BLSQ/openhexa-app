import clsx from "clsx";
import { useMemo } from "react";

export type ProgressPieProps = {
  progress?: number;
  background?: string;
  foreground?: string;
  textClassName?: string;
  className?: string;
};

const ProgressPie = (props: ProgressPieProps) => {
  const {
    progress,
    background = "stroke-gray-100",
    foreground = "stroke-gray-400",
    textClassName = "text-gray-400",
    className,
  } = props;

  const value = useMemo(
    () =>
      progress !== undefined ? Math.min(100, Math.max(0, progress)) : undefined,
    [progress],
  );
  return (
    <div
      className={clsx("relative flex items-center justify-center", className)}
    >
      <svg
        id="svg"
        viewBox="-1 -1 34 34"
        className="absolute inset-0 -rotate-90"
      >
        <circle
          cx="16"
          cy="16"
          r="15.9155"
          fill="none"
          strokeWidth="2"
          className={background}
        />

        <circle
          cx="16"
          cy="16"
          r="15.9155"
          strokeDasharray={"100 100"}
          strokeDashoffset={100 - (value ?? 0)}
          strokeLinecap="round"
          strokeWidth="2"
          fill="none"
          className={clsx(
            "transition-all duration-700 ease-in-out ",
            foreground,
          )}
        />
      </svg>
      {value !== undefined && (
        <div
          className={clsx("z-10 font-mono text-xs font-normal", textClassName)}
        >
          {value}%
        </div>
      )}
    </div>
  );
};

export default ProgressPie;
