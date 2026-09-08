import clsx from "clsx";
import { ReactNode } from "react";

export type DetailBadgeColor = "indigo" | "emerald" | "amber" | "blue" | "gray";

const COLORS: Record<DetailBadgeColor, string> = {
  indigo: "bg-indigo-100 text-indigo-700 ring-indigo-700/15",
  emerald: "bg-emerald-100 text-emerald-700 ring-emerald-700/15",
  amber: "bg-amber-100 text-amber-800 ring-amber-700/15",
  blue: "bg-blue-100 text-blue-700 ring-blue-700/15",
  gray: "bg-gray-100 text-gray-700 ring-gray-700/15",
};

type DetailBadgeProps = {
  color?: DetailBadgeColor;
  icon?: ReactNode;
  className?: string;
  children: ReactNode;
};

const DetailBadge = ({
  color = "gray",
  icon,
  className,
  children,
}: DetailBadgeProps) => (
  <span
    className={clsx(
      "inline-flex h-5 flex-none items-center gap-1 rounded-md px-2 text-[11px] font-semibold ring-1 ring-inset",
      COLORS[color],
      className,
    )}
  >
    {icon}
    {children}
  </span>
);

export default DetailBadge;
