import clsx from "clsx";
import { HTMLAttributes } from "react";

function BlockHeader({
  className,
  children,
}: HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3
      className={clsx(
        "px-4 py-5 pt-7 text-lg font-medium leading-4 text-gray-900 sm:px-6",
        className,
      )}
    >
      {children}
    </h3>
  );
}

export default BlockHeader;
