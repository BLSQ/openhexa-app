import React from "react";
import clsx from "clsx";
import {
  HomeIcon,
  ChevronLeftIcon,
  UsersIcon,
  Square2StackIcon,
  Cog6ToothIcon,
} from "@heroicons/react/24/outline";
import { OrganizationQuery } from "organizations/graphql/queries.generated";
import NavItem from "./NavItem";
import SidebarToggleButton from "./SidebarToggleButton";
import UserMenu from "workspaces/features/UserMenu";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";

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
  const router = useRouter();

  if (!organization) {
    return null;
  }

  const currentPath = router.asPath;

  const homeHref = `/organizations/${organization.id}/`;
  const membersHref = `/organizations/${organization.id}/members`;
  const datasetsHref = `/organizations/${organization.id}/datasets`;
  const settingsHref = `/organizations/${organization.id}/settings`;

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
            className="h-16"
            key="organization"
            href="/organizations/"
            Icon={ChevronLeftIcon}
            logo={organization.logo}
            label={organization.shortName ?? organization.name}
            compact={!isSidebarOpen}
          />
          <div className="mt-5 flex grow flex-col overflow-y-auto scrollbar-visible">
            <nav className="flex-1 space-y-1 px-0 pb-4">
              <NavItem
                href={homeHref}
                Icon={HomeIcon}
                label={t("Workspaces")}
                isCurrent={currentPath === homeHref}
                compact={!isSidebarOpen}
              />
              {organization.permissions.manageMembers && (
                <NavItem
                  href={membersHref}
                  Icon={UsersIcon}
                  label={t("Members")}
                  isCurrent={currentPath.startsWith(membersHref)}
                  compact={!isSidebarOpen}
                />
              )}
              <NavItem
                href={datasetsHref}
                Icon={Square2StackIcon}
                label={t("Datasets")}
                isCurrent={currentPath.startsWith(datasetsHref)}
                compact={!isSidebarOpen}
              />
              {organization.permissions.update && (
                <NavItem
                  href={settingsHref}
                  Icon={Cog6ToothIcon}
                  label={t("Settings")}
                  isCurrent={currentPath.startsWith(settingsHref)}
                  compact={!isSidebarOpen}
                />
              )}
            </nav>
          </div>
          <UserMenu compact={!isSidebarOpen} />
        </div>
        <SidebarToggleButton
          isSidebarOpen={isSidebarOpen}
          setSidebarOpen={setSidebarOpen}
        />
      </div>
    </div>
  );
};

export default OrganizationSidebar;
