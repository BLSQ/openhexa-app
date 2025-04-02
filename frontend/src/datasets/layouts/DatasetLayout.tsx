import { gql } from "@apollo/client";
import { PlusIcon, TrashIcon } from "@heroicons/react/24/outline";
import Block from "core/components/Block/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import LinkTabs from "core/components/Tabs/LinkTabs";
import Title from "core/components/Title";
import { trackEvent } from "core/helpers/analytics";
import { CustomApolloClient } from "core/helpers/apollo";
import { GetServerSidePropsContext } from "next";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";
import DatasetVersionPicker from "../features/DatasetVersionPicker";
import DeleteDatasetTrigger from "../features/DeleteDatasetTrigger";
import PinDatasetButton from "../features/PinDatasetButton";
import UploadDatasetVersionDialog from "../features/UploadDatasetVersionDialog";
import {
  DatasetLayout_DatasetLinkFragment,
  DatasetLayout_VersionFragment,
  DatasetLayout_WorkspaceFragment,
} from "./DatasetLayout.generated";

type DatasetLayoutProps = {
  datasetLink: DatasetLayout_DatasetLinkFragment;
  version: DatasetLayout_VersionFragment | null;
  workspace: DatasetLayout_WorkspaceFragment;
  tab?: string;
  extraBreadcrumbs?: { href: string; title: string }[];
  children: React.ReactNode;
};

const DatasetLayout = (props: DatasetLayoutProps) => {
  const {
    children,
    datasetLink,
    workspace,
    version,
    tab = "general",
    extraBreadcrumbs = [],
  } = props;

  const { t } = useTranslation();
  const router = useRouter();
  const [isUploadDialogOpen, setUploadDialogOpen] = useState(false);

  const onChangeVersion: React.ComponentProps<
    typeof DatasetVersionPicker
  >["onChange"] = (version) => {
    delete router.query["fileId"];
    router.push({
      pathname: router.pathname,
      query: { ...router.query, version: version?.id },
    });
  };

  useEffect(() => {
    trackEvent("datasets.dataset_open", {
      workspace: workspace.slug,
      dataset_id: datasetLink.dataset.slug,
      dataset_version: version?.name,
    });
  }, []);

  if (!datasetLink) {
    return null;
  }

  const { dataset } = datasetLink;
  const isWorkspaceSource = workspace.slug === dataset.workspace?.slug;

  return (
    <WorkspaceLayout
      workspace={workspace}
      helpLinks={[
        {
          label: t("About datasets"),
          href: "https://github.com/BLSQ/openhexa/wiki/User-manual#datasets",
        },
        {
          label: t("Using the OpenHEXA SDK with datasets"),
          href: "https://github.com/BLSQ/openhexa/wiki/Using-the-OpenHEXA-SDK#working-with-datasets",
        },
      ]}
      header={
        <>
          <Breadcrumbs withHome={false} className="flex-1">
            <Breadcrumbs.Part
              isFirst
              href={`/workspaces/${encodeURIComponent(workspace.slug)}`}
            >
              {workspace.name}
            </Breadcrumbs.Part>
            <Breadcrumbs.Part
              href={`/workspaces/${encodeURIComponent(workspace.slug)}/datasets`}
            >
              {t("Datasets")}
            </Breadcrumbs.Part>
            <Breadcrumbs.Part
              isLast={!extraBreadcrumbs.length}
              href={`/workspaces/${encodeURIComponent(
                workspace.slug,
              )}/datasets/${encodeURIComponent(dataset.slug)}`}
            >
              {dataset.name}
            </Breadcrumbs.Part>
            {extraBreadcrumbs.map(({ href, title }, index) => (
              <Breadcrumbs.Part
                key={index}
                isLast={extraBreadcrumbs.length - 1 == index}
                href={href}
              >
                {title}
              </Breadcrumbs.Part>
            ))}
          </Breadcrumbs>
          <PinDatasetButton link={datasetLink} />
          {dataset.permissions.createVersion && isWorkspaceSource && (
            <Button
              leadingIcon={<PlusIcon className="h-4 w-4" />}
              onClick={() => setUploadDialogOpen(true)}
            >
              {t("Create new version")}
            </Button>
          )}
          {isWorkspaceSource && dataset.permissions.delete && (
            <DeleteDatasetTrigger
              dataset={dataset}
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
                  onClick={onClick}
                  leadingIcon={<TrashIcon className="w-4" />}
                >
                  {t("Delete")}
                </Button>
              )}
            </DeleteDatasetTrigger>
          )}
        </>
      }
    >
      <WorkspaceLayout.PageContent>
        <Title level={2} className="flex items-center justify-between">
          {dataset.name}
          {version && (
            // Only show the version picker if we have a version
            <DatasetVersionPicker
              onChange={onChangeVersion}
              dataset={dataset}
              version={version}
              className="min-w-40"
            />
          )}
        </Title>
        <Block className="divide-y divide-gray-200">
          <LinkTabs
            className="mx-4 mt-2"
            tabs={[
              {
                label: t("General"),
                href: `/workspaces/${encodeURIComponent(workspace.slug)}/datasets/${encodeURIComponent(dataset.slug)}`,
                id: "general",
              },
              ...(version
                ? [
                    {
                      label: t("Files"),
                      href: `/workspaces/${encodeURIComponent(workspace.slug)}/datasets/${encodeURIComponent(dataset.slug)}/files`,
                      id: "files",
                    },
                  ]
                : []),
              {
                label: t("Access management"),
                href: `/workspaces/${encodeURIComponent(workspace.slug)}/datasets/${encodeURIComponent(dataset.slug)}/access`,
                id: "access",
              },
            ]}
            selected={tab}
          />
          {children}
        </Block>
      </WorkspaceLayout.PageContent>

      <UploadDatasetVersionDialog
        open={isUploadDialogOpen}
        onClose={() => setUploadDialogOpen(false)}
        datasetLink={datasetLink}
      />
    </WorkspaceLayout>
  );
};

DatasetLayout.fragments = {
  workspace: gql`
    fragment DatasetLayout_workspace on Workspace {
      ...WorkspaceLayout_workspace
      name
      slug
    }
    ${WorkspaceLayout.fragments.workspace}
  `,
  datasetLink: gql`
    fragment DatasetLayout_datasetLink on DatasetLink {
      ...UploadDatasetVersionDialog_datasetLink
      ...PinDatasetButton_link
      dataset {
        workspace {
          slug
        }
        slug
        permissions {
          delete
          createVersion
        }
      }
    }
    ${UploadDatasetVersionDialog.fragments.datasetLink}
    ${PinDatasetButton.fragments.link}
  `,

  version: gql`
    fragment DatasetLayout_version on DatasetVersion {
      id
      name
      ...DatasetVersionPicker_version
    }
    ${DatasetVersionPicker.fragments.version}
  `,
};

DatasetLayout.prefetch = async (
  ctx: GetServerSidePropsContext,
  client: CustomApolloClient,
) => {
  await WorkspaceLayout.prefetch(ctx, client);
};

export default DatasetLayout;
