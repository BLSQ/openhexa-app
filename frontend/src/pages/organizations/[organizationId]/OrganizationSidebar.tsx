import React from "react";
import clsx from "clsx";
import Link from "core/components/Link";
import { ChevronLeftIcon, ChevronRightIcon } from "@heroicons/react/24/outline";
import SpotlightSearch from "core/features/SpotlightSearch/SpotlightSearch";
import Badge from "core/components/Badge";
import { GetServerSidePropsContext } from "next";
import { OrganizationQuery } from "organizations/graphql/queries.generated";

export let isMac = false;

function getIsMac() {
  if (typeof window === "undefined") {
    return isMac;
  }
  const userAgent = window.navigator.userAgent;
  return userAgent.includes("Mac");
}

type OrganizationSidebarProps = {
  organization: OrganizationQuery["organization"];
  isSidebarOpen: boolean;
  setSidebarOpen: (newValue: boolean) => void;
};

const NavItem = (props: {
  Icon: any;
  label?: string;
  href: string;
  isCurrent: boolean;
  compact?: boolean;
  className?: string;
}) => {
  const { Icon, compact, label, href, isCurrent, className } = props;

  return (
    <Link
      href={href}
      noStyle
      className={clsx(
        className,
        "text-md group relative flex items-center gap-3 px-2 py-2 font-medium",
        isCurrent
          ? "text-white"
          : " text-gray-300 hover:bg-gray-700 hover:text-white",
        compact && "justify-center ",
      )}
    >
      <div
        className={clsx(
          "absolute inset-y-0 left-0 w-1 bg-pink-500 transition-opacity",
          isCurrent ? "opacity-100" : "opacity-0",
        )}
      ></div>
      <Icon className={clsx(compact ? "h-7 w-7" : "ml-1 h-5 w-5")} />
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

const OrganizationSidebar = ({
  organization,
  isSidebarOpen,
  setSidebarOpen,
}: OrganizationSidebarProps) => {
  if (!organization) {
    return null; // or handle loading state
  }
  return (
    <div
      className={clsx(
        "fixed h-full bg-gray-800 transition-all duration-200",
        isSidebarOpen ? "w-64 2xl:w-72" : "w-16",
      )}
    >
      <div className="relative z-20 flex h-full flex-col">
        <div className="flex h-full grow flex-col border-r border-gray-200 bg-gray-800">
          <NavItem
            className="h-16"
            key="organization"
            href="/organizations/"
            Icon={ChevronLeftIcon}
            label={organization.shortName ?? organization.name}
            isCurrent={false}
            compact={!isSidebarOpen}
          />
          <SpotlightSearch
            isSidebarOpen={isSidebarOpen}
            isMac={getIsMac()}
            organizationId={organization.id}
          />
          <div className="mt-5 flex grow flex-col"></div>
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

OrganizationSidebar.prefetch = async (ctx: GetServerSidePropsContext) => {
  isMac = ctx.req.headers["user-agent"]?.includes("Mac") ?? false;
};

export default OrganizationSidebar;
