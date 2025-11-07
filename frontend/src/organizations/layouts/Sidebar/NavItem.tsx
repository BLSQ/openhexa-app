import React, { useState, useEffect } from "react";
import clsx from "clsx";
import Link from "core/components/Link";
import Badge from "core/components/Badge";

type NavItemProps = {
  label?: string;
  href: string;
  Icon?: any;
  logo?: string | null;
  isCurrent?: boolean;
  compact?: boolean;
  className?: string;
  isCurrent?: boolean;
};

const NavItem = ({
  label,
  href,
  Icon,
  logo,
  isCurrent = false,
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
        isCurrent
          ? "text-white"
          : "text-gray-300 hover:bg-gray-700 hover:text-white",
        compact && "justify-center",
      )}
    >
      <div
        className={clsx(
          "absolute inset-y-0 left-0 w-1 bg-pink-500 transition-opacity",
          isCurrent ? "opacity-100" : "opacity-0",
        )}
      ></div>
      {logo ? (
        <img
          src={logo}
          alt={label || ""}
          className={clsx(
            "object-contain flex-shrink-0",
            compact ? "h-7 w-7" : "ml-1 h-5 w-5",
          )}
        />
      ) : Icon ? (
        <Icon className={clsx(compact ? "h-7 w-7" : "ml-1 h-5 w-5")} />
      ) : null}
      {compact ? (
        <div className="absolute inset-y-0 left-full ml-1.5 hidden h-full items-center text-xs opacity-0 transition-opacity group-hover:flex group-hover:opacity-100">
          <Badge className="bg-gray-800 ring-gray-500/20">{label}</Badge>
        </div>
      ) : (
        <span className="transition-opacity duration-200">{delayedLabel}</span>
      )}
    </Link>
  );
};

export default NavItem;
