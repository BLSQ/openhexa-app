import React from "react";
import clsx from "clsx";
import Link from "core/components/Link";
import {
  BuildingOffice2Icon,
  ChevronLeftIcon,
  ChevronRightIcon,
} from "@heroicons/react/24/outline";
import { useTranslation } from "next-i18next";
import Badge from "core/components/Badge";

type SidebarProps = {
  organizations: {
    id: string;
    name: string;
    workspaces: { items: { slug: string; name: string }[] };
  }[];
  isSidebarOpen: boolean;
  setSidebarOpen: (newValue: boolean) => void;
};

const NavItem = (props: {
  label?: string;
  href: string;
  compact?: boolean;
  className?: string;
}) => {
  const { compact, label, href, className } = props;

  return (
    <Link
      href={href}
      noStyle
      className={clsx(
        className,
        "text-md group relative flex items-center gap-3 px-2 py-2 font-medium",
        " text-gray-300 hover:bg-gray-700 hover:text-white",
        compact && "justify-center ",
      )}
    >
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

const Sidebar = ({
  organizations,
  isSidebarOpen,
  setSidebarOpen,
}: SidebarProps) => {
  const { t } = useTranslation();
  return (
    <div
      className={clsx(
        "fixed h-full bg-gray-800 transition-all duration-200",
        isSidebarOpen ? "w-64 2xl:w-72" : "w-16",
      )}
    >
      <div className="relative z-20 flex h-full flex-col">
        <div className="flex h-full grow flex-col border-r border-gray-200 bg-gray-800">
          <div
            className={clsx(
              "h-16 text-gray-300 text-md group relative flex items-center gap-3 px-2 py-2 font-medium",
              !isSidebarOpen && "justify-center",
            )}
          >
            <BuildingOffice2Icon
              className={clsx(!isSidebarOpen ? "h-7 w-7" : "ml-1 h-5 w-5")}
            />
            {!isSidebarOpen ? (
              <div className="absolute inset-y-0 left-full ml-1.5 hidden h-full items-center text-xs opacity-0 transition-opacity group-hover:flex group-hover:opacity-100">
                <Badge className="bg-gray-800 ring-gray-500/20">
                  {t("Organizations")}
                </Badge>
              </div>
            ) : (
              t("Organizations")
            )}
          </div>
          <div className="mt-5 flex grow flex-col">
            {organizations.map((organization) => (
              <NavItem
                className="rounded-md text-wrap m-2"
                key={organization.id}
                href={"/organizations/" + organization.id}
                label={organization.name}
                compact={!isSidebarOpen}
              />
            ))}
          </div>
          <div className="mb-5 flex shrink-0 flex-col items-center px-4">
            <Link noStyle href="/" className="flex h-8 items-center">
              <img
                className="h-full"
                src={
                  isSidebarOpen
                    ? "/images/logo_with_text_white.svg"
                    : "/images/logo.svg"
                }
                alt="OpenHEXA logo"
              />
            </Link>
          </div>
        </div>
        <button
          onClick={() => setSidebarOpen(!isSidebarOpen)}
          className="group absolute inset-y-0 right-0 border-r-4 border-transparent after:absolute after:inset-y-0 after:-left-1.5 after:block after:w-5 after:content-[''] hover:border-r-gray-500"
        >
          <div className="relative h-full">
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center">
              <div className="pointer-events-auto invisible rounded-l-md bg-gray-500 p-1 pr-0.5 align-middle text-white group-hover:visible">
                {isSidebarOpen ? (
                  <ChevronLeftIcon className="h-5 w-5" />
                ) : (
                  <ChevronRightIcon className="h-5 w-5" />
                )}
              </div>
            </div>
          </div>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
