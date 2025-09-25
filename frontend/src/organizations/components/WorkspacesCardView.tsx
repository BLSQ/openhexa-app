import React from "react";
import Button from "core/components/Button";
import Card from "core/components/Card";
import { useTranslation } from "next-i18next";
import { GearIcon } from "@radix-ui/react-icons";
import { TrashIcon, GlobeAltIcon } from "@heroicons/react/24/outline";
import Flag from "react-world-flags";
import { OrganizationWorkspace_WorkspaceFragment } from "organizations/graphql/queries.generated";
import { ArchiveWorkspace_WorkspaceFragment } from "workspaces/features/ArchiveWorkspaceDialog/ArchiveWorkspaceDialog.generated";
import router from "next/router";
import Pagination from "core/components/Pagination";

type WorkspacesCardViewProps = {
  items: OrganizationWorkspace_WorkspaceFragment[];
  page: number;
  setPage: (page: number) => void;
  perPage: number;
  totalPages: number;
  totalItems: number;
  canArchive: boolean;
  onArchiveClick: (workspace: ArchiveWorkspace_WorkspaceFragment) => void;
};

const WorkspacesCardView = ({
  items,
  page,
  setPage,
  perPage,
  totalPages,
  totalItems,
  canArchive,
  onArchiveClick,
}: WorkspacesCardViewProps) => {
  const { t } = useTranslation();

  return (
    <div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {items.map((ws) => (
          <Card
            key={ws.slug}
            href={{
              pathname: `/workspaces/[workspaceSlug]`,
              query: { workspaceSlug: ws.slug },
            }}
            title={
              <div className="flex items-center gap-2">
                <div className="flex h-full w-5 items-center">
                  {ws.countries && ws.countries.length === 1 ? (
                    <Flag
                      code={ws.countries[0].code}
                      className="w-5 shrink rounded-xs"
                    />
                  ) : (
                    <GlobeAltIcon className="w-5 shrink rounded-xs text-gray-400" />
                  )}
                </div>
                <span className="font-medium text-gray-800">{ws.name}</span>
              </div>
            }
          >
            <Card.Content>
              <div className="flex gap-2 justify-end">
                <Button
                  variant="outlined"
                  className="static"
                  onClick={async (e) => {
                    e.preventDefault();
                    await router.push({
                      pathname: `/workspaces/[workspaceSlug]/settings`,
                      query: { workspaceSlug: ws.slug },
                    });
                  }}
                  leadingIcon={<GearIcon className="w-4" />}
                >
                  {t("Settings")}
                </Button>
                <Button
                  variant="outlined"
                  className="static"
                  onClick={(e) => {
                    e.preventDefault();
                    onArchiveClick(ws);
                  }}
                  leadingIcon={<TrashIcon className="w-4" />}
                  disabled={!canArchive}
                >
                  {t("Archive")}
                </Button>
              </div>
            </Card.Content>
          </Card>
        ))}
      </div>
      <Pagination
        page={page}
        perPage={perPage}
        totalPages={totalPages}
        countItems={totalItems}
        totalItems={totalItems}
        onChange={setPage}
      />
    </div>
  );
};

export default WorkspacesCardView;
