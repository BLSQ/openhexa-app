import { LinkIcon } from "@heroicons/react/24/outline";
import Block from "core/components/Block";
import Button from "core/components/Button";
import Callout from "core/components/Callout";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import DatasetLinksDataGrid from "datasets/features/DatasetLinksDataGrid";
import LinkDatasetDialog from "datasets/features/LinkDatasetDialog";
import DatasetVisibilityPicker from "datasets/features/DatasetSharing/DatasetVisibilityPicker";
import DatasetLayout from "datasets/layouts/DatasetLayout";
import { useTranslation } from "next-i18next";
import { useState } from "react";
import { DatasetVisibility } from "graphql/types";
import {
  useWorkspaceDatasetAccessPageQuery,
  WorkspaceDatasetAccessPageDocument,
  WorkspaceDatasetAccessPageQuery,
  WorkspaceDatasetAccessPageQueryVariables,
} from "workspaces/graphql/queries.generated";

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
  // Links grant nothing more while the whole organization has access.
  const isOrganizationWide =
    dataset.visibility !== DatasetVisibility.Workspace &&
    Boolean(dataset.workspace?.organization);

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
        {dataset.workspace?.organization && (
          <Block.Section title={t("Visibility")} collapsible={false}>
            <DatasetVisibilityPicker
              dataset={dataset}
              disabled={!isWorkspaceSource}
            />
          </Block.Section>
        )}
        {isOrganizationWide && (
          <Block.Content>
            <Callout>
              {t(
                "Every workspace of the organization can already access this dataset. The workspaces below keep their access if it is made private again.",
              )}
            </Callout>
          </Block.Content>
        )}
        <DatasetLinksDataGrid dataset={datasetLink.dataset} />
        <Block.Content className="flex justify-end">
          {workspace.permissions.update && (
            <Button
              leadingIcon={<LinkIcon className={"h-4 w-4"} />}
              onClick={() => setLinkDialogOpen(true)}
              disabled={isOrganizationWide}
            >
              {t("Share with a workspace")}
            </Button>
          )}
        </Block.Content>
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
