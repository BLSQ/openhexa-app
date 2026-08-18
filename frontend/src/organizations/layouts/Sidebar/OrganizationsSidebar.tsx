import React, { useState } from "react";
import clsx from "clsx";
import { BuildingOffice2Icon, PlusIcon } from "@heroicons/react/24/outline";
import { OrganizationsQuery } from "organizations/graphql/queries.generated";
import SidebarToggleButton from "./SidebarToggleButton";
import UserMenu from "workspaces/features/UserMenu";
import NavItem from "./NavItem";
import { useTranslation } from "next-i18next";
import useSidebarOpen from "core/hooks/useSidebarOpen";
import useMe from "identity/hooks/useMe";
import CreateOrganizationDialog from "organizations/features/CreateOrganizationDialog";

type OrganizationsSidebarProps = {
  organizations: OrganizationsQuery["organizations"];
};

const OrganizationsSidebar = ({ organizations }: OrganizationsSidebarProps) => {
  const { t } = useTranslation();

  const [isSidebarOpen] = useSidebarOpen();
  const me = useMe();
  const [isCreateOpen, setCreateOpen] = useState(false);

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
          <div className="mt-5 flex grow flex-col overflow-y-auto scrollbar-visible">
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
            {me?.permissions.superUser && (
              <button
                type="button"
                onClick={() => setCreateOpen(true)}
                title={t("Create an organization")}
                className={clsx(
                  "text-md group m-2 flex items-center gap-3 rounded-md px-2 py-2 font-medium text-gray-300 hover:bg-gray-700 hover:text-white",
                  !isSidebarOpen && "justify-center",
                )}
              >
                <PlusIcon
                  className={clsx(!isSidebarOpen ? "h-7 w-7" : "ml-1 h-5 w-5")}
                />
                {isSidebarOpen && <span>{t("Create an organization")}</span>}
              </button>
            )}
          </div>
          <UserMenu compact={!isSidebarOpen} />
        </div>
        <SidebarToggleButton />
      </div>
      <CreateOrganizationDialog
        open={isCreateOpen}
        onClose={() => setCreateOpen(false)}
      />
    </div>
  );
};

export default OrganizationsSidebar;
