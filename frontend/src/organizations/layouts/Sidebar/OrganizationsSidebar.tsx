import React from "react";
import clsx from "clsx";
import { BuildingOffice2Icon } from "@heroicons/react/24/outline";
import { OrganizationsQuery } from "organizations/graphql/queries.generated";
import Badge from "core/components/Badge";
import SidebarToggleButton from "./SidebarToggleButton";
import Logo from "./Logo";
import NavItem from "./NavItem";

type OrganizationsSidebarProps = {
  organizations: OrganizationsQuery["organizations"];
  isSidebarOpen: boolean;
  setSidebarOpen: (newValue: boolean) => void;
};

const OrganizationsSidebar = ({
  organizations,
  isSidebarOpen,
  setSidebarOpen,
}: OrganizationsSidebarProps) => {
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
                  Organizations
                </Badge>
              </div>
            ) : (
              "Organizations"
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
          <Logo isSidebarOpen={isSidebarOpen} />
        </div>
        <SidebarToggleButton
          isSidebarOpen={isSidebarOpen}
          setSidebarOpen={setSidebarOpen}
        />
      </div>
    </div>
  );
};

export default OrganizationsSidebar;
