import { HomeIcon } from "@heroicons/react/20/solid";
import clsx from "clsx";
import { useTranslation } from "next-i18next";

import { ReactNode } from "react";
import { UrlObject } from "url";
import Link from "./Link";

export const Part = ({
  children,
  href,
  isLast = false,
  isFirst = false,
  small = false,
}: {
  children: ReactNode;
  isFirst?: boolean;
  isLast?: boolean;
  small?: boolean;
  href?: UrlObject | string;
}) => {
  return (
    <li
      className={clsx(
        "flex min-w-0 items-center",
        isLast ? "shrink min-w-16" : "shrink-0 max-w-1/3",
        !isFirst && !small && "ml-2",
      )}
    >
      {!isFirst && (
        <svg
          className="h-5 w-5 shrink-0 text-gray-300"
          xmlns="http://www.w3.org/2000/svg"
          fill="currentColor"
          viewBox="0 0 20 20"
          aria-hidden="true"
        >
          <path d="M5.555 17.776l8-16 .894.448-8 16-.894-.448z" />
        </svg>
      )}
      <span
        title={typeof children === "string" ? children : undefined}
        className={clsx(
          !isFirst && !small && "ml-3",
          "truncate text-sm hover:text-gray-700",
          isLast ? "font-semibold text-gray-800" : "font-medium text-gray-500",
        )}
      >
        {href ? (
          <Link noStyle href={href}>
            {children}
          </Link>
        ) : (
          children
        )}
      </span>
    </li>
  );
};

const Breadcrumbs = (props: {
  children: ReactNode | ReactNode[];
  className?: string;
  withHome?: boolean;
}) => {
  const { children, className, withHome = true } = props;
  const { t } = useTranslation();

  return (
    <nav
      className={clsx("min-w-0 overflow-hidden", className)}
      aria-label={t("Breadcrumbs")}
    >
      <ol role="list" className="flex min-w-0 items-center">
        {withHome && (
          <li className="shrink-0">
            <div>
              <Link href="/" customStyle="text-gray-400 hover:text-gray-500">
                <HomeIcon className="h-5 w-5 shrink-0" />
                <span className="sr-only">{t("Home")}</span>
              </Link>
            </div>
          </li>
        )}
        {children}
      </ol>
    </nav>
  );
};

Breadcrumbs.Part = Part;

export default Breadcrumbs;
