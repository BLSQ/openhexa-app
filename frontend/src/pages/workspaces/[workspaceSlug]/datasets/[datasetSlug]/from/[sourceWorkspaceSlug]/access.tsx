import { LinkIcon } from "@heroicons/react/24/outline";
import Block from "core/components/Block";
import Button from "core/components/Button";
import Switch from "core/components/Switch";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { updateDataset } from "datasets/helpers/dataset";
import DatasetLinksDataGrid from "datasets/features/DatasetLinksDataGrid";
import LinkDatasetDialog from "datasets/features/LinkDatasetDialog";
import DatasetLayout from "datasets/layouts/DatasetLayout";
import { useTranslation } from "next-i18next";
import { useState } from "react";
import { toast } from "react-toastify";
import {
  useWorkspaceDatasetAccessPageQuery,
  WorkspaceDatasetAccessPageDocument,
  WorkspaceDatasetAccessPageQuery,
  WorkspaceDatasetAccessPageQueryVariables,
} from "workspaces/graphql/queries.generated";
import useFeature from "identity/hooks/useFeature";

export type WorkspaceDatasetAccessPageProps = {
  isSpecificVersion: boolean;
  workspaceSlug: string;
  sourceWorkspaceSlug: string;
  datasetSlug: string;
  versionId: string;
};

const WorkspaceDatasetAccessPage: NextPageWithLayout = (
  props: WorkspaceDatasetAccessPageProps,
) => {
  const { t } = useTranslation();
  const { data } = useWorkspaceDatasetAccessPageQuery({
    variables: props,
  });
  const [isLinkDialogOpen, setLinkDialogOpen] = useState(false);
  const [organizationFeatureIsEnabled] = useFeature("organization");
  if (!data || !data.datasetLink || !data.workspace) {
    return null;
  }
  const { datasetLink, workspace } = data;
  const { dataset } = datasetLink;
  const sourceWorkspace = dataset.workspace!;
  const version = props.isSpecificVersion
    ? datasetLink.dataset.version
    : datasetLink.dataset.latestVersion;

  const isWorkspaceSource = sourceWorkspace.slug === workspace.slug;

  const handleOrganizationSharingChange = async (checked: boolean) => {
    try {
      if (dataset.permissions.update && isWorkspaceSource) {
        await updateDataset(dataset.id, {
          sharedWithOrganization: checked,
        });
      }
    } catch (error: any) {
      toast.error(error.message || t("Failed to update dataset sharing"));
    }
  };

  return (
    <Page title={dataset.name ?? t("Dataset")}>
      <DatasetLayout
        datasetLink={datasetLink}
        workspace={workspace}
        version={version ?? null}
        extraBreadcrumbs={[
          {
            title: t("Access management"),
            href: `/workspaces/${encodeURIComponent(
              workspace.slug,
            )}/datasets/${encodeURIComponent(datasetLink.dataset.slug)}/from/${encodeURIComponent(sourceWorkspace.slug)}/access`,
          },
        ]}
        tab="access"
      >
        {organizationFeatureIsEnabled &&
          dataset.workspace?.organization &&
          isWorkspaceSource && (
            <div>
              <div className="px-4 py-5 sm:p-6">
                <div className="mt-4">
                  <Switch
                    checked={dataset.sharedWithOrganization}
                    onChange={handleOrganizationSharingChange}
                    disabled={!dataset.permissions.update || !isWorkspaceSource}
                    label={t("Share with the whole Organization")}
                  />
                  {!dataset.sharedWithOrganization && (
                    <p className="mt-2 text-sm text-gray-500">
                      {t(
                        "Only accessible by the owner workspace and explicitly shared workspaces",
                      )}
                    </p>
                  )}
                </div>
                {dataset.sharedWithOrganization && (
                  <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <svg
                          className="h-5 w-5 text-green-400"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                            clipRule="evenodd"
                          />
                        </svg>
                      </div>
                      <div className="ml-3">
                        <h3 className="text-sm font-medium text-green-800">
                          {t("Shared with all workspaces")}
                        </h3>
                        <div className="mt-1 text-sm text-green-700">
                          {t(
                            "This dataset is available to all workspaces in your organization.",
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        {(!organizationFeatureIsEnabled ||
          !dataset.sharedWithOrganization ||
          !dataset.workspace?.organization ||
          !isWorkspaceSource) && (
          <>
            <DatasetLinksDataGrid dataset={datasetLink.dataset} />
            <Block.Content className="flex justify-end">
              {workspace.permissions.update && (
                <Button
                  leadingIcon={<LinkIcon className={"h-4 w-4"} />}
                  onClick={() => setLinkDialogOpen(true)}
                >
                  {t("Share with a workspace")}
                </Button>
              )}
            </Block.Content>
          </>
        )}
      </DatasetLayout>
      <LinkDatasetDialog
        dataset={datasetLink.dataset}
        open={isLinkDialogOpen}
        onClose={() => setLinkDialogOpen(false)}
      />
    </Page>
  );
};

WorkspaceDatasetAccessPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await DatasetLayout.prefetch(ctx, client);
    const versionId = (ctx.query.version as string) ?? "";

    const variables = {
      workspaceSlug: ctx.params!.workspaceSlug as string,
      sourceWorkspaceSlug: (ctx.params!.sourceWorkspaceSlug ||
        ctx.params!.workspaceSlug) as string,
      datasetSlug: ctx.params!.datasetSlug as string,
      versionId: versionId,
      isSpecificVersion: Boolean(versionId),
    };

    const { data } = await client.query<
      WorkspaceDatasetAccessPageQuery,
      WorkspaceDatasetAccessPageQueryVariables
    >({
      query: WorkspaceDatasetAccessPageDocument,
      variables,
    });

    if (!data.datasetLink || !data.workspace) {
      return { notFound: true };
    }

    return {
      props: variables,
    };
  },
});

export default WorkspaceDatasetAccessPage;
