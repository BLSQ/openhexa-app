import { useMemo } from "react";

export type ProgressPieProps = {
  progress: number;
  background?: string;
  foreground?: string;
  size?: number;
};

const ProgressPie = (props: ProgressPieProps) => {
  const {
    progress,
    background = "fill-gray-100",
    foreground = "stroke-gray-400",
    size = 20,
  } = props;

  const value = useMemo(() => Math.min(100, Math.max(0, progress)), [progress]);
  return (
    <svg height={size} width={size} viewBox="0 0 20 20">
      <circle r="10" cx="10" cy="10" id="" className={background} />
      <circle
        r="5"
        cx="10"
        cy="10"
        fill="transparent"
        className={foreground}
        stroke-width="10"
        stroke-dasharray={`calc(${value} * 31.4 / 100) 31.4`}
        transform="rotate(-90) translate(-20)"
      />
    </svg>
  );
};

export default ProgressPie;
