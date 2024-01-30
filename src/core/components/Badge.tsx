import { ComponentPropsWithoutRef } from "react";
import clsx from "clsx";

export interface BadgeProps extends ComponentPropsWithoutRef<"span"> {
  borderColor?: string;
  size?: "xs" | "sm" | "md";
}

const Classes = {
  xs: "px-2 py-0.5 text-xs",
  sm: "px-2.5 py-1 text-sm",
  md: "px-2.5 pt-1 text-md",
};

const Badge = ({
  children,
  className,
  borderColor = "border-gray-500 border-opacity-10",
  size = "xs",
  ...delegated
}: BadgeProps) => {
  return (
    <span
      {...delegated}
      className={clsx(
        "inline-flex items-center truncate whitespace-nowrap rounded-md border  font-medium",
        size === "xs" && Classes.xs,
        size === "sm" && Classes.sm,
        size === "md" && Classes.md,
        borderColor,
        className,
      )}
    >
      {children}
    </span>
  );
};

export default Badge;
