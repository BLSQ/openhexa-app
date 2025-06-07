import React from "react";
import { ChevronLeftIcon, ChevronRightIcon } from "@heroicons/react/24/outline";

type SidebarToggleButtonProps = {
  isSidebarOpen: boolean;
  setSidebarOpen: (newValue: boolean) => void;
};

const SidebarToggleButton = ({
  isSidebarOpen,
  setSidebarOpen,
}: SidebarToggleButtonProps) => {
  return (
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
  );
};

export default SidebarToggleButton;
