import React from "react";
import clsx from "clsx";
import Link from "core/components/Link";
import Badge from "core/components/Badge";

type NavItemProps = {
  label?: string;
  href: string;
  Icon?: any;
  compact?: boolean;
  className?: string;
};

const NavItem = ({ label, href, Icon, compact, className }: NavItemProps) => {
  return (
    <Link
      href={href}
      noStyle
      className={clsx(
        className,
        "text-md group relative flex items-center gap-3 px-2 py-2 font-medium",
        "text-gray-300 hover:bg-gray-700 hover:text-white",
        compact && "justify-center",
      )}
    >
      {Icon && <Icon className={clsx(compact ? "h-7 w-7" : "ml-1 h-5 w-5")} />}
      {compact ? (
        <div className="absolute inset-y-0 left-full ml-1.5 hidden h-full items-center text-xs opacity-0 transition-opacity group-hover:flex group-hover:opacity-100">
          <Badge className="bg-gray-800 ring-gray-500/20">{label}</Badge>
        </div>
      ) : (
        label
      )}
    </Link>
  );
};

export default NavItem;
