import React from "react";
import clsx from "clsx";
import { BuildingOffice2Icon } from "@heroicons/react/24/outline";
import { OrganizationsQuery } from "organizations/graphql/queries.generated";
import SidebarToggleButton from "./SidebarToggleButton";
import UserMenu from "workspaces/features/UserMenu";
import NavItem from "./NavItem";
import { useTranslation } from "next-i18next";
import useSidebarOpen from "core/hooks/useSidebarOpen";

type OrganizationsSidebarProps = {
  organizations: OrganizationsQuery["organizations"];
};

const OrganizationsSidebar = ({ organizations }: OrganizationsSidebarProps) => {
  const { t } = useTranslation();

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
          <NavItem
            className="h-16  pointer-events-none"
            key="organizations-header"
            href="/organizations/"
            Icon={BuildingOffice2Icon}
            label={t("Organizations")}
            compact={!isSidebarOpen}
          />
          <div className="mt-5 flex grow flex-col">
            {organizations.map((organization) => (
              <NavItem
                Icon={BuildingOffice2Icon}
                logo={organization.logo}
                className="rounded-md text-wrap m-2"
                key={organization.id}
                href={"/organizations/" + organization.id}
                label={organization.name}
                compact={!isSidebarOpen}
              />
            ))}
          </div>
          <UserMenu compact={!isSidebarOpen} />
        </div>
        <SidebarToggleButton />
      </div>
    </div>
  );
};

export default OrganizationsSidebar;
