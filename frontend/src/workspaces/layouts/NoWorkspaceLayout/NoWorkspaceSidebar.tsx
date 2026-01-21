import React from "react";
import clsx from "clsx";
import SidebarToggleButton from "organizations/layouts/Sidebar/SidebarToggleButton";
import UserMenu from "workspaces/features/UserMenu";
import useSidebarOpen from "core/hooks/useSidebarOpen";

const NoWorkspaceSidebar = () => {
  const [isSidebarOpen] = useSidebarOpen();

  return (
    <div
      className={clsx(
        "fixed h-full bg-gray-800 transition-all duration-75",
        isSidebarOpen ? "w-64 2xl:w-72" : "w-16",
      )}
    >
      <div className="relative z-20 flex h-full flex-col">
        <div className="flex h-full grow flex-col border-r border-gray-200 bg-gray-800">
          <div className="flex h-16 shrink-0 items-center justify-center px-4">
            <img
              className="h-8"
              src={
                isSidebarOpen
                  ? "/images/logo_with_text_white.svg"
                  : "/images/logo.svg"
              }
              alt="OpenHEXA"
            />
          </div>
          <div className="mt-5 flex grow flex-col" />
          <UserMenu compact={!isSidebarOpen} />
        </div>
        <SidebarToggleButton />
      </div>
    </div>
  );
};

export default NoWorkspaceSidebar;