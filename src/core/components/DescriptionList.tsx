import { InformationCircleIcon } from "@heroicons/react/20/solid";
import clsx from "clsx";
import React, { ReactNode } from "react";
import Tooltip from "./Tooltip";

const DescriptionList = ({
  children,
  className,
}: React.HTMLAttributes<HTMLDataListElement>) => {
  return <dl className={clsx("space-y-6", className)}>{children}</dl>;
};

DescriptionList.Item = function Item({
  children,
  label,
  help,
  className,
}: {
  label: ReactNode;
  children: ReactNode;
  help?: ReactNode;
  className?: string;
}) {
  return (
    <div className={clsx("grid grid-cols-5 gap-2 sm:gap-4", className)}>
      <dt className="col-span-1 text-sm font-medium text-gray-500">
        <span>{label}</span>
        {help && (
          <Tooltip
            placement="top"
            renderTrigger={(ref) => (
              <span ref={ref}>
                <InformationCircleIcon className="ml-1 h-3 w-3 cursor-pointer" />
              </span>
            )}
            label={help}
          />
        )}
      </dt>
      <dd className="col-span-4 text-sm text-gray-900">{children}</dd>
    </div>
  );
};

export default DescriptionList;
