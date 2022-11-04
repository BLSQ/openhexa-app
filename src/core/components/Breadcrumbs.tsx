import { HomeIcon } from "@heroicons/react/20/solid";
import { useTranslation } from "next-i18next";

import { ReactNode } from "react";
import { UrlObject } from "url";
import Link from "./Link";

export const Part = ({
  children,
  href,
}: {
  children: ReactNode;
  href?: UrlObject | string;
}) => {
  return (
    <li className="ml-3">
      <div className="flex items-center">
        <svg
          className="h-5 w-5 flex-shrink-0 text-gray-300"
          xmlns="http://www.w3.org/2000/svg"
          fill="currentColor"
          viewBox="0 0 20 20"
          aria-hidden="true"
        >
          <path d="M5.555 17.776l8-16 .894.448-8 16-.894-.448z" />
        </svg>
        <span className="ml-3 text-sm font-medium text-gray-500 hover:text-gray-700">
          {href ? (
            <Link customStyle="" href={href}>
              {children}
            </Link>
          ) : (
            children
          )}
        </span>
      </div>
    </li>
  );
};

const Breadcrumbs = (props: {
  children: ReactNode | ReactNode[];
  className?: string;
}) => {
  const { children, className } = props;
  const { t } = useTranslation();

  return (
    <nav className={className} aria-label={t("Breadcrumbs")}>
      <ol role="list" className="flex items-center">
        <li>
          <div>
            <Link href="/" customStyle="text-gray-400 hover:text-gray-500">
              <HomeIcon className="h-5 w-5 flex-shrink-0" />
              <span className="sr-only">{t("Home")}</span>
            </Link>
          </div>
        </li>
        {children}
      </ol>
    </nav>
  );
};

Breadcrumbs.Part = Part;

export default Breadcrumbs;
