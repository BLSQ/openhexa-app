import { InformationCircleIcon } from "@heroicons/react/20/solid";
import clsx from "clsx";
import React, { ReactNode } from "react";
import Tooltip from "../Tooltip";
import { ctx, DescriptionListDisplayMode, useDescriptionList } from "./helpers";

const COLUMNS = {
  1: "",
  2: "grid-cols-2",
  3: "grid-cols-3",
  4: "grid-cols-4",
};

export type DescriptionListProps = React.HTMLAttributes<HTMLDataListElement> & {
  displayMode?: DescriptionListDisplayMode;
  columns?: keyof typeof COLUMNS;
  compact?: boolean;
};

const DescriptionList = ({
  children,
  className,
  columns = 1,
  compact = false,
  displayMode = DescriptionListDisplayMode.LABEL_LEFT,
}: DescriptionListProps) => {
  return (
    <ctx.Provider value={{ displayMode, compact }}>
      <dl
        className={clsx(
          "grid",
          compact ? "gap-2" : "gap-4",
          COLUMNS[columns],
          className,
        )}
      >
        {children}
      </dl>
    </ctx.Provider>
  );
};

DescriptionList.Item = function Item({
  children,
  label,
  help,
  className,
  fullWidth,
  titleClassName,
  contentClassName,
}: {
  label: ReactNode;
  children: ReactNode;
  help?: ReactNode;
  className?: string;
  fullWidth?: boolean;
  titleClassName?: string;
  contentClassName?: string;
}) {
  const { displayMode } = useDescriptionList();
  return (
    <div
      className={clsx(
        displayMode === DescriptionListDisplayMode.LABEL_LEFT &&
          "grid grid-cols-5 gap-2 sm:gap-4",
        displayMode === DescriptionListDisplayMode.LABEL_ABOVE && "space-y-1",
        fullWidth && "col-span-full",
        className,
      )}
    >
      <dt
        className={clsx(
          "flex text-sm font-medium text-gray-500",
          displayMode === DescriptionListDisplayMode.LABEL_LEFT &&
            "col-span-1 items-center",
          displayMode === DescriptionListDisplayMode.LABEL_ABOVE &&
            "col-span-5",
          titleClassName,
        )}
      >
        <span className="inline">{label}</span>
        {help && (
          <Tooltip
            placement="top"
            renderTrigger={(ref) => (
              <span className="inline" ref={ref}>
                <InformationCircleIcon className="ml-1 h-3 w-3 cursor-pointer" />
              </span>
            )}
            label={help}
          />
        )}
      </dt>
      <dd
        className={clsx("col-span-4 text-sm text-gray-900", contentClassName)}
      >
        {children}
      </dd>
    </div>
  );
};

export default DescriptionList;
