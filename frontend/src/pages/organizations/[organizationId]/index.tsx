import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import OrganizationLayout from "organizations/layouts/OrganizationLayout";
import { useTranslation } from "next-i18next";
import Page from "core/components/Page";
import { PlusIcon } from "@heroicons/react/24/outline";
import {
  OrganizationDocument,
  OrganizationQuery,
  useOrganizationWorkspacesQuery,
} from "organizations/graphql/queries.generated";
import CreateWorkspaceDialog from "workspaces/features/CreateWorkspaceDialog";
import ArchiveWorkspaceDialog from "workspaces/features/ArchiveWorkspaceDialog";
import { ArchiveWorkspace_WorkspaceFragment } from "workspaces/features/ArchiveWorkspaceDialog/ArchiveWorkspaceDialog.generated";
import { useState, useEffect } from "react";
import Button from "core/components/Button";
import useDebounce from "core/hooks/useDebounce";
import Spinner from "core/components/Spinner";
import WorkspacesHeader from "organizations/components/WorkspacesHeader";
import WorkspacesListView from "organizations/components/WorkspacesListView";
import WorkspacesCardView from "organizations/components/WorkspacesCardView";

type Props = {
  organization: OrganizationQuery["organization"];
};

// TODO : total should not change

const OrganizationPage: NextPageWithLayout<Props> = ({
  organization: SRROrganization,
}) => {
  const { t } = useTranslation();
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isArchiveDialogOpen, setIsArchiveDialogOpen] = useState(false);
  const [selectedWorkspace, setSelectedWorkspace] =
    useState<ArchiveWorkspace_WorkspaceFragment | null>(null);
  const [view, setView] = useState<"grid" | "card">("card");
  const [page, setPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearchQuery = useDebounce(searchQuery, 300);
  const perPage = 15;

  const { data, loading, refetch } = useOrganizationWorkspacesQuery({
    variables: {
      organizationId: SRROrganization?.id,
      page,
      perPage,
      query: debouncedSearchQuery,
    },
    fetchPolicy: "cache-and-network",
  });

  const [workspaces, setWorkspaces] = useState(data?.workspaces?.items || []);

  useEffect(() => {
    if (!loading && data?.workspaces?.items) {
      setWorkspaces(data.workspaces.items);
    }
  }, [loading, data]);

  useEffect(() => {
    setPage(1);
  }, [debouncedSearchQuery]);

  const organization = data?.organization || SRROrganization;

  if (!organization) {
    return null;
  }
  const totalWorkspaces = data?.workspaces?.totalItems ?? 0;

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

          <div className="m-8">
            <WorkspacesHeader
              searchQuery={searchQuery}
              setSearchQuery={setSearchQuery}
              view={view}
              setView={setView}
            />

            <div className="relative">
              {loading && (
                <div className="absolute inset-0 flex items-center justify-center backdrop-blur-xs z-10">
                  <Spinner />
                </div>
              )}
              {view === "card" ? (
                <WorkspacesCardView
                  items={workspaces}
                  page={page}
                  setPage={setPage}
                  perPage={perPage}
                  totalPages={data?.workspaces?.totalPages || 0}
                  totalItems={totalWorkspaces}
                  canArchive={organization.permissions.archiveWorkspace}
                  onArchiveClick={handleArchiveClick}
                />
              ) : (
                <WorkspacesListView
                  items={workspaces}
                  page={page}
                  setPage={setPage}
                  perPage={perPage}
                  totalPages={data?.workspaces?.totalPages || 0}
                  totalItems={totalWorkspaces}
                  canArchive={organization.permissions.archiveWorkspace}
                  onArchiveClick={handleArchiveClick}
                />
              )}
            </div>
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
            refetch().then();
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
