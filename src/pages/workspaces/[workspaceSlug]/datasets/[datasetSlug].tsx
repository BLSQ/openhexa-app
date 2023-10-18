import {
  CloudArrowUpIcon,
  PlusIcon,
  TrashIcon,
} from "@heroicons/react/24/outline";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button/Button";
import DataCard from "core/components/DataCard";
import TextProperty from "core/components/DataCard/TextProperty";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import DatasetVersionFilesDataGrid from "datasets/features/DatasetVersionFilesDataGrid/DatasetVersionFilesDataGrid";
import DatasetVersionPicker from "datasets/features/DatasetVersionPicker/DatasetVersionPicker";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import {
  useWorkspaceDatasetPageQuery,
  WorkspaceDatasetPageDocument,
  WorkspaceDatasetPageQuery,
  WorkspaceDatasetPageQueryVariables,
} from "workspaces/graphql/queries.generated";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";
import DatasetLinksDataGrid from "../../../../datasets/features/DatasetLinksDataGrid";
import UserProperty from "../../../../core/components/DataCard/UserProperty";
import DateProperty from "../../../../core/components/DataCard/DateProperty";
import { useState } from "react";
import { updateDataset } from "datasets/helpers/dataset";
import UploadDatasetVersionDialog from "datasets/features/UploadDatasetVersionDialog";
import DescriptionList from "core/components/DescriptionList";
import Time from "core/components/Time";
import PinDatasetButton from "datasets/features/PinDatasetButton";
import LinkDatasetDialog from "datasets/features/LinkDatasetDialog";
import { LinkIcon } from "@heroicons/react/24/solid";
import useCacheKey from "core/hooks/useCacheKey";
import DeleteDatasetTrigger from "datasets/features/DeleteDatasetTrigger";
import RenderProperty from "core/components/DataCard/RenderProperty";
import Clipboard from "core/components/Clipboard";

type Props = {
  datasetSlug: string;
  workspaceSlug: string;
  versionId: string;
  isSpecificVersion: boolean;
};

const WorkspaceDatasetPage: NextPageWithLayout = (props: Props) => {
  const { datasetSlug, workspaceSlug, isSpecificVersion, versionId } = props;

  const { t } = useTranslation();
  const router = useRouter();
  const [isUploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [isLinkDialogOpen, setLinkDialogOpen] = useState(false);
  const { data, refetch } = useWorkspaceDatasetPageQuery({
    variables: {
      workspaceSlug,
      datasetSlug,
      versionId,
      isSpecificVersion,
    },
  });
  useCacheKey(["datasets"], () => refetch());

  const onChangeVersion: React.ComponentProps<
    typeof DatasetVersionPicker
  >["onChange"] = (version) => {
    router.push({
      pathname: router.pathname,
      query: { ...router.query, version: version?.id },
    });
  };

  if (!data?.datasetLink) {
    return null;
  }
  const { datasetLink } = data;
  const { dataset, workspace } = datasetLink;
  const isWorkspaceSource = workspace.slug === dataset.workspace?.slug;
  const version = dataset.version || dataset.latestVersion || null;

  const onSave = async (values: any) => {
    await updateDataset(datasetLink.dataset.id, values);
  };

  return (
    <Page title={datasetLink.dataset.name ?? t("Dataset")}>
      <WorkspaceLayout
        workspace={workspace}
        helpLinks={[
          {
            label: t("About datasets"),
            href: "https://github.com/BLSQ/openhexa/wiki/User-manual#datasets",
          },
          {
            label: t("Using the OpenHexa SDK with datasets"),
            href: "https://github.com/BLSQ/openhexa/wiki/Using-the-OpenHexa-SDK#working-with-datasets",
          },
        ]}
      >
        <WorkspaceLayout.Header className="flex items-center justify-between gap-2">
          <Breadcrumbs withHome={false} className="flex-1">
            <Breadcrumbs.Part
              isFirst
              href={`/workspaces/${encodeURIComponent(workspace.slug)}`}
            >
              {workspace.name}
            </Breadcrumbs.Part>
            <Breadcrumbs.Part
              href={`/workspaces/${encodeURIComponent(
                workspace.slug,
              )}/datasets`}
            >
              {t("Datasets")}
            </Breadcrumbs.Part>
            <Breadcrumbs.Part
              isLast
              href={`/workspaces/${encodeURIComponent(
                workspace.slug,
              )}/datasets/${encodeURIComponent(datasetLink.id)}`}
            >
              {datasetLink.dataset.name}
            </Breadcrumbs.Part>
          </Breadcrumbs>
          <PinDatasetButton link={datasetLink} />
          {isWorkspaceSource && datasetLink.dataset.permissions.delete && (
            <DeleteDatasetTrigger
              dataset={datasetLink.dataset}
              onDelete={() =>
                router.push({
                  pathname: "/workspaces/[workspaceSlug]/datasets",
                  query: { workspaceSlug: workspace.slug },
                })
              }
            >
              {({ onClick }) => (
                <Button
                  variant={"danger"}
                  size={"sm"}
                  onClick={onClick}
                  leadingIcon={<TrashIcon className="w-4" />}
                >
                  {t("Delete")}
                </Button>
              )}
            </DeleteDatasetTrigger>
          )}
        </WorkspaceLayout.Header>

        <WorkspaceLayout.PageContent className="space-y-6">
          <DataCard
            item={datasetLink.dataset}
            className="divide-y-2 divide-gray-100"
          >
            <DataCard.FormSection
              title={datasetLink.dataset.name}
              onSave={
                datasetLink.dataset.permissions.update && isWorkspaceSource
                  ? onSave
                  : undefined
              }
              collapsible={false}
            >
              <TextProperty
                id="name"
                accessor={"name"}
                label={t("Name")}
                visible={(_, isEditing) => isEditing}
              />
              <TextProperty
                id="description"
                accessor={"description"}
                label={t("Description")}
                defaultValue="Empty description"
                hideLabel
                markdown
              />
              <RenderProperty
                id="slug"
                accessor="slug"
                label={t("Identifier")}
                help={t(
                  "The identifier is used to reference the dataset in the SDK and notebooks",
                )}
                readonly
              >
                {(property) => (
                  <div className="font-mono">
                    <Clipboard value={property.displayValue}>
                      {property.displayValue}
                    </Clipboard>
                  </div>
                )}
              </RenderProperty>
              <DateProperty
                id={"createdAt"}
                label={t("Created at")}
                accessor={"createdAt"}
                readonly
              />
              <UserProperty
                id={"createdBy"}
                readonly
                label={t("Created by")}
                accessor={"createdBy"}
              />
              <TextProperty
                readonly
                id={"workspace"}
                accessor={"workspace.name"}
                label={t("Source workspace")}
              />
            </DataCard.FormSection>
            <DataCard.Section
              title={() => (
                <div className="flex flex-1 gap-2 items-center justify-between">
                  <h4 className="flex-1 font-medium">
                    {!version && t("Versions")}
                    {version &&
                      version.id === datasetLink.dataset.latestVersion?.id &&
                      t("Latest version")}
                    {version &&
                      version.id !== datasetLink.dataset.latestVersion?.id &&
                      t("Version {{version}}", { version: version.name })}
                  </h4>
                  {datasetLink.dataset.latestVersion && (
                    <DatasetVersionPicker
                      onChange={onChangeVersion}
                      dataset={datasetLink.dataset}
                      version={version}
                      className="w-40"
                    />
                  )}
                  {datasetLink.dataset.permissions.createVersion &&
                    isWorkspaceSource && (
                      <Button
                        leadingIcon={<PlusIcon className="h-4 w-4" />}
                        onClick={() => setUploadDialogOpen(true)}
                      >
                        {t("Create new version")}
                      </Button>
                    )}
                </div>
              )}
              collapsible={false}
            >
              {version ? (
                <>
                  <DescriptionList>
                    <DescriptionList.Item label={t("Name")}>
                      {version.name}
                    </DescriptionList.Item>
                    <DescriptionList.Item label={t("Created at")}>
                      <Time datetime={version.createdAt} />
                    </DescriptionList.Item>
                    <DescriptionList.Item label={t("Created by")}>
                      {version.createdBy?.displayName ?? "-"}
                    </DescriptionList.Item>
                  </DescriptionList>

                  <div className="mt-6 -mx-6">
                    <DatasetVersionFilesDataGrid
                      version={version}
                      perPage={10}
                    />
                  </div>
                </>
              ) : (
                <p className={"italic text-gray-500"}>
                  {t(
                    "This dataset has no version. Upload a new version using your browser or the SDK to see it here.",
                  )}
                </p>
              )}
            </DataCard.Section>
            {isWorkspaceSource ? (
              <DataCard.Section
                title={() => (
                  <div className={"flex items-center justify-between w-full"}>
                    <h4 className={"font-medium"}>{t("Access Management")}</h4>
                    {workspace.permissions.update && (
                      <Button
                        leadingIcon={<LinkIcon className={"h-4 w-4"} />}
                        onClick={() => setLinkDialogOpen(true)}
                      >
                        {t("Share with a workspace")}
                      </Button>
                    )}
                  </div>
                )}
                collapsible={false}
              >
                <div className={"-mx-6"}>
                  <DatasetLinksDataGrid dataset={datasetLink.dataset} />
                </div>
              </DataCard.Section>
            ) : null}
          </DataCard>
        </WorkspaceLayout.PageContent>
      </WorkspaceLayout>

      <UploadDatasetVersionDialog
        open={isUploadDialogOpen}
        onClose={() => setUploadDialogOpen(false)}
        datasetLink={datasetLink}
      />
      <LinkDatasetDialog
        dataset={datasetLink.dataset}
        open={isLinkDialogOpen}
        onClose={() => setLinkDialogOpen(false)}
      />
    </Page>
  );
};

WorkspaceDatasetPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    const versionId = (ctx.query.version as string) ?? "";

    const variables = {
      workspaceSlug: ctx.params!.workspaceSlug as string,
      datasetSlug: ctx.params!.datasetSlug as string,
      versionId: versionId,
      isSpecificVersion: Boolean(versionId),
    };

    const { data } = await client.query<
      WorkspaceDatasetPageQuery,
      WorkspaceDatasetPageQueryVariables
    >({
      query: WorkspaceDatasetPageDocument,
      variables,
    });

    if (!data.datasetLink) {
      return { notFound: true };
    }
    // If we have a versionId or there is a version in the dataset, prefetch the files
    if (versionId || data.datasetLink.dataset.latestVersion?.id) {
      await DatasetVersionFilesDataGrid.prefetch(client, {
        perPage: 10,
        versionId: (versionId ||
          data.datasetLink.dataset.latestVersion?.id) as string,
      });
    }

    return {
      props: variables,
    };
  },
});

export default WorkspaceDatasetPage;
