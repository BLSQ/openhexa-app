import React, { useState, useEffect } from "react";
import clsx from "clsx";
import Link from "core/components/Link";
import Badge from "core/components/Badge";

type NavItemProps = {
  label?: string;
  href: string;
  Icon?: any;
  logo?: string | null;
  compact?: boolean;
  className?: string;
};

const NavItem = ({
  label,
  href,
  Icon,
  logo,
  compact,
  className,
}: NavItemProps) => {
  const [delayedLabel, setDelayedLabel] = useState(compact ? "" : label);

  useEffect(() => {
    if (compact) {
      setDelayedLabel("");
    } else {
      const timer = setTimeout(() => {
        setDelayedLabel(label);
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [compact, label]);
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
      {logo ? (
        <img
          src={logo}
          alt={label || ""}
          className="h-7 w-7 object-contain flex-shrink-0"
        />
      ) : Icon ? (
        <Icon className={clsx("h-7 w-7 flex-shrink-0", !compact && "ml-1")} />
      ) : null}
      {compact ? (
        <div className="absolute inset-y-0 left-full ml-2.5 hidden h-full items-center text-xs opacity-0 transition-opacity group-hover:flex group-hover:opacity-100">
          <Badge className="bg-gray-800 ring-gray-500/20">{label}</Badge>
        </div>
      ) : (
        <span>{delayedLabel}</span>
      )}
    </Link>
  );
};

export default NavItem;
