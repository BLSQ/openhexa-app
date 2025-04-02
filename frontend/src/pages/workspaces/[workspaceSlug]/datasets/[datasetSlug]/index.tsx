import Badge from "core/components/Badge";
import Clipboard from "core/components/Clipboard";
import DateProperty from "core/components/DataCard/DateProperty";
import FormSection from "core/components/DataCard/FormSection";
import RenderProperty from "core/components/DataCard/RenderProperty";
import TextProperty from "core/components/DataCard/TextProperty";
import UserProperty from "core/components/DataCard/UserProperty";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { ItemProvider } from "core/hooks/useItemContext";
import { updateDataset, updateDatasetVersion } from "datasets/helpers/dataset";
import DatasetLayout from "datasets/layouts/DatasetLayout";
import { useTranslation } from "next-i18next";
import {
  useWorkspaceDatasetIndexPageQuery,
  WorkspaceDatasetIndexPageDocument,
  WorkspaceDatasetIndexPageQuery,
  WorkspaceDatasetIndexPageQueryVariables,
} from "workspaces/graphql/queries.generated";

export type WorkspaceDatasetPageProps = {
  isSpecificVersion: boolean;
  workspaceSlug: string;
  datasetSlug: string;
  versionId: string;
};

const WorkspaceDatasetPage: NextPageWithLayout = (
  props: WorkspaceDatasetPageProps,
) => {
  const { t } = useTranslation();
  const { data } = useWorkspaceDatasetIndexPageQuery({
    variables: props,
  });
  const { isSpecificVersion } = props;
  if (!data || !data.datasetLink || !data.workspace) {
    return null;
  }
  const { datasetLink, workspace } = data;
  const { dataset } = datasetLink;
  const version = isSpecificVersion
    ? datasetLink.dataset.version
    : datasetLink.dataset.latestVersion;

  const isWorkspaceSource = workspace.slug === dataset.workspace?.slug;

  const onSave = async (values: any) => {
    await updateDataset(dataset.id, values);
  };

  const onSaveVersion = async (values: any) => {
    if (!version) {
      throw new Error("Version not found");
    }
    await updateDatasetVersion(version.id, values);
  };

  return (
    <Page title={dataset.name ?? t("Dataset")}>
      <DatasetLayout
        datasetLink={datasetLink}
        workspace={workspace}
        version={version ?? null}
      >
        <ItemProvider item={dataset}>
          <FormSection
            onSave={
              dataset.permissions.update && isWorkspaceSource
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
            <RenderProperty
              // visible={(_, isEditing) => isEditing && !isWorkspaceSource}
              id={"workspace"}
              accessor={"workspace.name"}
              label={t("Source workspace")}
            >
              {(property) => <Badge>{property.displayValue}</Badge>}
            </RenderProperty>
          </FormSection>
        </ItemProvider>
        {version && (
          <ItemProvider item={version}>
            <FormSection
              title={
                <div className="w-full">
                  {isSpecificVersion
                    ? t("Version {{version}}", {
                        version: version.name,
                      })
                    : t("Current version")}
                </div>
              }
              onSave={version?.permissions.update ? onSaveVersion : undefined}
              collapsible={false}
            >
              <TextProperty
                id="changelog"
                accessor="changelog"
                label={t("Changelog")}
                hideLabel
                rows={8}
                markdown
                sm
              />
              <TextProperty
                id="name"
                accessor="name"
                label={t("Name")}
                visible={({ isEditing }) => isEditing || isSpecificVersion}
              />
              <DateProperty
                id="createdAt"
                accessor="createdAt"
                label={t("Created at")}
                readonly
              />
              <UserProperty
                id="createdBy"
                accessor="createdBy"
                label={t("Created by")}
                readonly
              />
            </FormSection>
          </ItemProvider>
        )}
      </DatasetLayout>
    </Page>
  );
};

WorkspaceDatasetPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await DatasetLayout.prefetch(ctx, client);
    const versionId = (ctx.query.version as string) ?? "";

    const variables = {
      workspaceSlug: ctx.params!.workspaceSlug as string,
      datasetSlug: ctx.params!.datasetSlug as string,
      versionId: versionId,
      isSpecificVersion: Boolean(versionId),
    };

    const { data } = await client.query<
      WorkspaceDatasetIndexPageQuery,
      WorkspaceDatasetIndexPageQueryVariables
    >({
      query: WorkspaceDatasetIndexPageDocument,
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

export default WorkspaceDatasetPage;
