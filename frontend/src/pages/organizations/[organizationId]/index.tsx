import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import OrganizationLayout from "organizations/layouts/OrganizationLayout";
import { useTranslation } from "next-i18next";
import Page from "core/components/Page";
import Flag from "react-world-flags";
import { GlobeAltIcon, PlusIcon, TrashIcon } from "@heroicons/react/24/outline";
import {
  OrganizationDocument,
  OrganizationQuery,
  useOrganizationQuery,
} from "organizations/graphql/queries.generated";
import CreateWorkspaceDialog from "workspaces/features/CreateWorkspaceDialog";
import ArchiveWorkspaceDialog from "workspaces/features/ArchiveWorkspaceDialog";
import { useState } from "react";
import { ArchiveWorkspace_WorkspaceFragment } from "workspaces/features/ArchiveWorkspaceDialog/ArchiveWorkspaceDialog.generated";
import Button from "core/components/Button";
import { GearIcon } from "@radix-ui/react-icons";
import Card from "core/components/Card";
import router from "next/router";
import useCacheKey from "core/hooks/useCacheKey";

type Props = {
  organization: OrganizationQuery["organization"];
};

const OrganizationPage: NextPageWithLayout<Props> = ({
  organization: SRROrganization,
}) => {
  const { t } = useTranslation();
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isArchiveDialogOpen, setIsArchiveDialogOpen] = useState(false);
  const [selectedWorkspace, setSelectedWorkspace] =
    useState<ArchiveWorkspace_WorkspaceFragment | null>(null);

  const { data, refetch } = useOrganizationQuery({
    variables: { id: SRROrganization?.id },
    fetchPolicy: "network-only",
    skip: !!SRROrganization,
  });
  const clearCache = useCacheKey(["organization", SRROrganization?.id], () =>
    refetch(),
  );

  const organization = data?.organization || SRROrganization;

  if (!organization) {
    return null;
  }

  const totalWorkspaces = organization.workspaces.items.length;

  const handleArchiveClick = (
    workspace: ArchiveWorkspace_WorkspaceFragment,
  ) => {
    setSelectedWorkspace(workspace);
    setIsArchiveDialogOpen(true);
  };

  return (
    <Page title={t("Organization")}>
      <OrganizationLayout organization={organization}>
        <div className="p-6">
          <div className="m-8 flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold">{organization.name}</h1>
              <p className="text-lg mt-2 text-gray-500">
                {totalWorkspaces}{" "}
                {totalWorkspaces > 1 ? t("workspaces") : t("workspace")}
              </p>
            </div>
            <Button
              variant="primary"
              className="static"
              onClick={() => setIsCreateDialogOpen(true)}
              leadingIcon={<PlusIcon className="w-4" />}
              disabled={!organization.permissions.createWorkspace}
            >
              {t("Create Workspace")}
            </Button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 m-8">
            {organization.workspaces.items.map((ws) => (
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
                        handleArchiveClick(ws);
                      }}
                      leadingIcon={<TrashIcon className="w-4" />}
                      disabled={!organization.permissions.archiveWorkspace}
                    >
                      {t("Archive")}
                    </Button>
                  </div>
                </Card.Content>
              </Card>
            ))}
          </div>
        </div>
      </OrganizationLayout>

      <CreateWorkspaceDialog
        organizationId={organization.id}
        open={isCreateDialogOpen}
        onClose={() => setIsCreateDialogOpen(false)}
      />

      {selectedWorkspace && (
        <ArchiveWorkspaceDialog
          workspace={selectedWorkspace}
          open={isArchiveDialogOpen}
          onArchive={() => {
            clearCache();
            setIsArchiveDialogOpen(false);
          }}
          onClose={() => setIsArchiveDialogOpen(false)}
        />
      )}
    </Page>
  );
};

OrganizationPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await OrganizationLayout.prefetch(ctx);
    const { data } = await client.query({
      query: OrganizationDocument,
      variables: {
        id: ctx.params?.organizationId as string,
      },
    });

    if (!data?.organization) {
      return {
        notFound: true,
      };
    }

    return {
      props: {
        organization: data.organization,
      },
    };
  },
});

export default OrganizationPage;
