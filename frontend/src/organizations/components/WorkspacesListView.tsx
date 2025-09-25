import React from "react";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import Block from "core/components/Block";
import Button from "core/components/Button";
import Link from "core/components/Link";
import { useTranslation } from "next-i18next";
import { GearIcon } from "@radix-ui/react-icons";
import {
  TrashIcon,
  GlobeAltIcon,
  UsersIcon,
} from "@heroicons/react/24/outline";
import Flag from "react-world-flags";
import { OrganizationWorkspace_WorkspaceFragment } from "organizations/graphql/queries.generated";
import { ArchiveWorkspace_WorkspaceFragment } from "workspaces/features/ArchiveWorkspaceDialog/ArchiveWorkspaceDialog.generated";
import router from "next/router";
import UserAvatar from "identity/features/UserAvatar";

type WorkspacesListViewProps = {
  items: OrganizationWorkspace_WorkspaceFragment[];
  page: number;
  setPage: (page: number) => void;
  perPage: number;
  totalPages: number;
  totalItems: number;
  canArchive: boolean;
  onArchiveClick: (workspace: ArchiveWorkspace_WorkspaceFragment) => void;
};

const WorkspacesListView = ({
  items,
  page,
  setPage,
  perPage,
  totalItems,
  canArchive,
  onArchiveClick,
}: WorkspacesListViewProps) => {
  const { t } = useTranslation();

  return (
    <Block className="divide divide-y divide-gray-100 mt-4">
      <DataGrid
        data={items}
        defaultPageIndex={page - 1}
        defaultPageSize={perPage}
        totalItems={totalItems}
        fetchData={({ page }) => setPage(page)}
        fixedLayout={false}
      >
        <BaseColumn id="name" label={t("Name")}>
          {(workspace) => (
            <div className="flex items-center gap-2">
              <div className="flex h-full w-5 items-center">
                {workspace.countries && workspace.countries.length === 1 ? (
                  <Flag
                    code={workspace.countries[0].code}
                    className="w-5 shrink rounded-xs"
                  />
                ) : (
                  <GlobeAltIcon className="w-5 shrink rounded-xs text-gray-400" />
                )}
              </div>
              <Link
                href={{
                  pathname: `/workspaces/[workspaceSlug]`,
                  query: { workspaceSlug: workspace.slug },
                }}
                className="font-medium text-gray-800"
              >
                {workspace.name}
              </Link>
            </div>
          )}
        </BaseColumn>
        <BaseColumn id="members" label={t("Members")}>
          {(workspace) => (
            <div className="flex items-center gap-1 text-sm text-gray-600">
              <UsersIcon className="h-4 w-4" />
              <span>{workspace.members?.totalItems || 0}</span>
            </div>
          )}
        </BaseColumn>
        <BaseColumn id="createdBy" label={t("Created by")}>
          {(workspace) => (
            <div className={"flex space-x-1"}>
              <UserAvatar user={workspace.createdBy} size="xs" />
              <p>{workspace.createdBy?.displayName}</p>
            </div>
          )}
        </BaseColumn>
        <DateColumn accessor="createdAt" label={t("Created")} relative />
        <BaseColumn id="actions" className="text-right">
          {(workspace) => (
            <div className="space-x-1">
              <Button
                variant="outlined"
                size="sm"
                onClick={async (e) => {
                  e.preventDefault();
                  await router.push({
                    pathname: `/workspaces/[workspaceSlug]/settings`,
                    query: { workspaceSlug: workspace.slug },
                  });
                }}
                leadingIcon={<GearIcon className="w-4 h-4" />}
              >
                {t("Settings")}
              </Button>
              {canArchive && (
                <Button
                  variant="outlined"
                  size="sm"
                  onClick={(e) => {
                    e.preventDefault();
                    onArchiveClick(workspace);
                  }}
                  leadingIcon={<TrashIcon className="h-4 w-4" />}
                >
                  {t("Archive")}
                </Button>
              )}
            </div>
          )}
        </BaseColumn>
      </DataGrid>
    </Block>
  );
};

export default WorkspacesListView;
