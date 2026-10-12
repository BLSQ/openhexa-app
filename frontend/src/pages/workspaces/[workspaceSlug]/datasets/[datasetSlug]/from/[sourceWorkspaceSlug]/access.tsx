import { LinkIcon } from "@heroicons/react/24/outline";
import Block from "core/components/Block";
import Button from "core/components/Button";
import Clipboard from "core/components/Clipboard";
import Dialog from "core/components/Dialog";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import DatasetLinksDataGrid from "datasets/features/DatasetLinksDataGrid";
import {
  DatasetVisibilityBadge,
  DatasetVisibilityPicker,
  getPublicDatasetPath,
  useDatasetVisibilityOption,
} from "datasets/features/DatasetVisibility";
import LinkDatasetDialog from "datasets/features/LinkDatasetDialog";
import { updateDataset } from "datasets/helpers/dataset";
import DatasetLayout from "datasets/layouts/DatasetLayout";
import { DatasetVisibility } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useEffect, useState } from "react";
import { toast } from "react-toastify";
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
  // Going public is the one change that opens the dataset to the whole internet,
  // so it waits for a confirmation instead of applying on click.
  const [isPublishDialogOpen, setPublishDialogOpen] = useState(false);
  const [isSaving, setSaving] = useState(false);
  // The permalink needs the browser's origin, which is unknown during SSR.
  const [origin, setOrigin] = useState("");
  useEffect(() => {
    setOrigin(window.location.origin);
  }, []);

  const visibility = data?.datasetLink?.dataset.visibility;
  const currentOption = useDatasetVisibilityOption(
    visibility ?? DatasetVisibility.Private,
  );

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
  const hasOrganization = Boolean(dataset.workspace?.organization);
  const isPublic = dataset.visibility === DatasetVisibility.Public;
  const canEditVisibility = dataset.permissions.update && isWorkspaceSource;
  const publicUrl = `${origin}${getPublicDatasetPath(dataset.id)}`;

  const applyVisibility = async (next: DatasetVisibility) => {
    setSaving(true);
    try {
      await updateDataset(dataset.id, { visibility: next });
    } catch (error: any) {
      toast.error(error.message || t("Failed to update dataset visibility"));
    } finally {
      setSaving(false);
    }
  };

  const handleVisibilityChange = (next: DatasetVisibility) => {
    if (next === dataset.visibility) {
      return;
    }
    if (next === DatasetVisibility.Public) {
      setPublishDialogOpen(true);
      return;
    }
    applyVisibility(next);
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
        {hasOrganization && (
          <div className="px-4 py-5 sm:p-6 space-y-4">
            {isWorkspaceSource ? (
              <div>
                <h3 className="text-sm font-medium text-gray-800 mb-2">
                  {t("Visibility")}
                </h3>
                <DatasetVisibilityPicker
                  value={dataset.visibility}
                  onChange={handleVisibilityChange}
                  disabled={!canEditVisibility || isSaving}
                  canMakePublic={dataset.permissions.makePublic}
                />
              </div>
            ) : (
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <DatasetVisibilityBadge
                  visibility={dataset.visibility}
                  size="sm"
                />
                <span>{currentOption.description}</span>
              </div>
            )}
            {isPublic && (
              <div className="rounded-lg border border-blue-200 bg-blue-50 p-4">
                <h3 className="text-sm font-medium text-blue-800">
                  {t("Public link")}
                </h3>
                <p className="mt-1 text-sm text-blue-700">
                  {t(
                    "Anyone with this link can view and download the dataset without logging in. The link stays valid even if the dataset is renamed.",
                  )}
                </p>
                <div className="mt-2 font-mono text-sm text-blue-900 break-all">
                  <Clipboard value={publicUrl}>{publicUrl}</Clipboard>
                </div>
              </div>
            )}
          </div>
        )}
        {(dataset.visibility === DatasetVisibility.Private ||
          !hasOrganization) && (
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
      <Dialog
        open={isPublishDialogOpen}
        onClose={() => !isSaving && setPublishDialogOpen(false)}
        maxWidth="max-w-md"
      >
        <Dialog.Title onClose={() => setPublishDialogOpen(false)}>
          {t("Make this dataset public?")}
        </Dialog.Title>
        <Dialog.Content>
          <p className="text-sm text-gray-600">
            {t(
              "Anyone with the link will be able to view and download every version of this dataset, without an OpenHEXA account. You can make it private again at any time.",
            )}
          </p>
        </Dialog.Content>
        <Dialog.Actions>
          <Button
            variant="outlined"
            onClick={() => setPublishDialogOpen(false)}
            disabled={isSaving}
          >
            {t("Cancel")}
          </Button>
          <Button
            onClick={async () => {
              setPublishDialogOpen(false);
              await applyVisibility(DatasetVisibility.Public);
            }}
            disabled={isSaving}
          >
            {t("Make public")}
          </Button>
        </Dialog.Actions>
      </Dialog>
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
