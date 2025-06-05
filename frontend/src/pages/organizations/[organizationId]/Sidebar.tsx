import React from "react";
import clsx from "clsx";
import Link from "core/components/Link";
import { ChevronLeftIcon, ChevronRightIcon } from "@heroicons/react/24/outline";
import SpotlightSearch from "core/features/SpotlightSearch/SpotlightSearch";

type SidebarProps = {
  organization: {
    id: string;
    name: string;
    workspaces: { items: { slug: string; name: string }[] };
  };
  isSidebarOpen: boolean;
  setSidebarOpen: (newValue: boolean) => void;
};

const Sidebar = ({
  organization,
  isSidebarOpen,
  setSidebarOpen,
}: SidebarProps) => {
  return (
    <div
      className={clsx(
        "fixed h-full bg-gray-800 transition-all duration-200",
        isSidebarOpen ? "w-64 2xl:w-72" : "w-16",
      )}
    >
      <div className="relative z-20 flex h-full flex-col">
        <div className="flex h-full grow flex-col border-r border-gray-200 bg-gray-800">
          <SpotlightSearch isSidebarOpen={isSidebarOpen} isMac={true} />{" "}
          {/** TODO: Implement getIsMac() */}
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
