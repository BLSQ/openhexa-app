import clsx from "clsx";
import Tooltip from "core/components/Tooltip";
import { useRef, useState } from "react";

const LINE_CLAMP_CLASSES: Record<number, string> = {
  1: "line-clamp-1",
  2: "line-clamp-2",
  3: "line-clamp-3",
  4: "line-clamp-4",
  5: "line-clamp-5",
  6: "line-clamp-6",
};

type Props = {
  children: string;
  lines?: number;
  className?: string;
  tooltip?: boolean;
};

const TruncatedText = ({ children, lines = 3, className, tooltip = false }: Props) => {
  const ref = useRef<HTMLSpanElement | null>(null);
  const [isTruncated, setIsTruncated] = useState(false);

  const spanClass = clsx(
    "min-w-0 whitespace-normal break-words",
    LINE_CLAMP_CLASSES[lines] ?? "line-clamp-3",
    className,
  );

  const checkTruncation = () => {
    if (ref.current) {
      setIsTruncated(ref.current.scrollHeight > ref.current.clientHeight);
    }
  };

  if (!tooltip) {
    return (
      <span ref={ref} className={spanClass}>
        {children}
      </span>
    );
  }

  return (
    <Tooltip
      label={isTruncated ? children : null}
      renderTrigger={(tooltipRef) => (
        <span
          ref={(el) => {
            ref.current = el;
            if (typeof tooltipRef === "function") tooltipRef(el);
          }}
          className={spanClass}
          onMouseEnter={checkTruncation}
        >
          {children}
        </span>
      )}
    />
  );
};

export default TruncatedText;
