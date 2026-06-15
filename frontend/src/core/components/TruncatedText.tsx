import clsx from "clsx";
import Tooltip from "core/components/Tooltip";
import { useEffect, useRef, useState } from "react";
import { useTranslation } from "next-i18next";

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
  expandable?: boolean;
};

const TruncatedText = ({
  children,
  lines = 3,
  className,
  tooltip = false,
  expandable = false,
}: Props) => {
  const { t } = useTranslation();
  const ref = useRef<HTMLSpanElement | null>(null);
  const [isTruncated, setIsTruncated] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const spanClass = clsx(
    "min-w-0 whitespace-normal break-words",
    !isExpanded && (LINE_CLAMP_CLASSES[lines] ?? "line-clamp-3"),
    className,
  );

  useEffect(() => {
    if (expandable && ref.current) {
      setIsTruncated(ref.current.scrollHeight > ref.current.clientHeight);
    }
  }, [children, expandable]);

  const checkTruncation = () => {
    if (ref.current) {
      setIsTruncated(ref.current.scrollHeight > ref.current.clientHeight);
    }
  };

  if (expandable) {
    return (
      <div>
        <span ref={ref} className={spanClass}>
          {children}
        </span>
        {(isTruncated || isExpanded) && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="cursor-pointer text-xs text-blue-600 hover:text-blue-800 hover:underline"
          >
            {isExpanded ? t("Show less") : t("Show more")}
          </button>
        )}
      </div>
    );
  }

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
      delayShow={300}
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
