import React from "react";
import clsx from "clsx";
import {
  ChevronLeftIcon,
  UsersIcon,
  Square2StackIcon,
} from "@heroicons/react/24/outline";
import SpotlightSearch from "core/features/SpotlightSearch/SpotlightSearch";
import { GetServerSidePropsContext } from "next";
import { OrganizationQuery } from "organizations/graphql/queries.generated";
import NavItem from "./NavItem";
import SidebarToggleButton from "./SidebarToggleButton";
import Logo from "./Logo";
import { useTranslation } from "next-i18next";
import { HomeIcon } from "@heroicons/react/20/solid";

type OrganizationSidebarProps = {
  organization: OrganizationQuery["organization"];
  isSidebarOpen: boolean;
  setSidebarOpen: (newValue: boolean) => void;
};

const OrganizationSidebar = ({
  organization,
  isSidebarOpen,
  setSidebarOpen,
}: OrganizationSidebarProps) => {
  const { t } = useTranslation();
  if (!organization) {
    return null;
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
            compact={!isSidebarOpen}
          />
          <SpotlightSearch
            isSidebarOpen={isSidebarOpen}
            organizationId={organization.id}
          />
          <div className="mt-5 flex grow flex-col gap-y-2">
            <NavItem
              href={`/organizations/${organization.id}`}
              Icon={HomeIcon}
              label={t("Workspaces")}
              compact={!isSidebarOpen}
            />
            {organization.permissions.manageMembers && (
              <NavItem
                href={`/organizations/${organization.id}/members`}
                Icon={UsersIcon}
                label={t("Members")}
                compact={!isSidebarOpen}
              />
            )}
            <NavItem
              href={`/organizations/${organization.id}/datasets`}
              Icon={Square2StackIcon}
              label={t("Datasets")}
              compact={!isSidebarOpen}
            />
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

OrganizationSidebar.prefetch = async (ctx: GetServerSidePropsContext) => {
  await SpotlightSearch.prefetch(ctx);
};

export default OrganizationSidebar;
