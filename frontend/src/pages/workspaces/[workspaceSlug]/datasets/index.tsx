import { CloudArrowUpIcon, PlusIcon } from "@heroicons/react/24/outline";
import Block from "core/components/Block/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import { BaseColumn } from "core/components/DataGrid";
import ChevronLinkColumn from "core/components/DataGrid/ChevronLinkColumn";
import DataGrid from "core/components/DataGrid/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import Page from "core/components/Page";
import Pagination from "core/components/Pagination";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useState } from "react";
import {
  useWorkspaceDatasetsPageQuery,
  WorkspaceDatasetsPageDocument,
  WorkspaceDatasetsPageQuery,
  WorkspaceDatasetsPageQueryVariables,
} from "workspaces/graphql/queries.generated";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";
import CreateDatasetDialog from "datasets/features/CreateDatasetDialog";
import DatasetCard from "datasets/features/DatasetCard";
import Title from "core/components/Title";
import PinDatasetButton from "datasets/features/PinDatasetButton";
import useCacheKey from "core/hooks/useCacheKey";
import clsx from "clsx";
import Link from "core/components/Link";

type Props = {
  page: number;
  perPage: number;
  workspaceSlug: string;
  query: string;
};

const WorkspaceDatasetsPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const { page, perPage, workspaceSlug, query } = props;
  const [isDialogOpen, setDialogOpen] = useState(false);
  const router = useRouter();
  const { data, refetch } = useWorkspaceDatasetsPageQuery({
    variables: {
      workspaceSlug,
      page,
      perPage,
      query,
    },
  });

  useCacheKey(["datasets"], () => refetch());

  if (!data?.workspace) {
    return null;
  }

  const onPaginate: React.ComponentProps<typeof DataGrid>["fetchData"] = ({
    page,
    pageSize,
  }) => {
    router.push({
      pathname: "/workspaces/[workspaceSlug]/datasets",
      query: {
        page,
        perPage: pageSize,
        workspaceSlug,
        query,
      },
    });
  };

  const { workspace } = data;

  return (
    <Page title={workspace.name}>
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
                isLast
                href={`/workspaces/${encodeURIComponent(
                  workspace.slug,
                )}/datasets`}
              >
                {t("Datasets")}
              </Breadcrumbs.Part>
            </Breadcrumbs>

            {workspace.permissions.createDataset && (
              <>
                <Button
                  leadingIcon={<PlusIcon className="h-4 w-4" />}
                  onClick={() => setDialogOpen(true)}
                >
                  {t("Create")}
                </Button>
              </>
            )}
          </>
        }
      >
        <WorkspaceLayout.PageContent className="flex flex-col">
          {workspace.pinnedDatasets.items.length > 0 && (
            <>
              <div
                className={clsx(
                  "grid gap-4 mb-6",
                  workspace?.pinnedDatasets.items.length < 3
                    ? "grid-cols-3"
                    : "grid-cols-6",
                )}
              >
                {workspace.pinnedDatasets.items.map((link) => (
                  <DatasetCard key={link.id} link={link} />
                ))}
              </div>
              <Title level={2}>{t("All datasets")}</Title>
            </>
          )}
          <Block>
            <DataGrid
              data={workspace.datasets.items}
              sortable={false}
              fetchData={onPaginate}
              totalItems={workspace.datasets.totalItems}
              defaultPageSize={perPage}
              fixedLayout={false}
              rowClassName={"items-center"}
            >
              <BaseColumn className="py-3" id="name" label={t("Name")}>
                {(value) => (
                  <div className={"min-w-0 flex items-center gap-2"}>
                    <PinDatasetButton link={value} />
                    <Link
                      customStyle="font-medium text-gray-600 hover:text-gray-800 text-ellipsis overflow-hidden"
                      href={{
                        pathname:
                          "/workspaces/[workspaceSlug]/datasets/[datasetSlug]",
                        query: {
                          workspaceSlug: workspace.slug,
                          datasetSlug: value.dataset.slug,
                        },
                      }}
                    >
                      {value.dataset.name}
                    </Link>
                  </div>
                )}
              </BaseColumn>
              <DateColumn
                accessor="dataset.updatedAt"
                header={t("Last updated")}
                className={"py-3"}
                relative
              />
              <TextColumn
                accessor="dataset.createdBy.displayName"
                header={t("Created by")}
              />
              <TextColumn
                accessor="dataset.workspace.name"
                header={t("Workspace")}
              />
              <ChevronLinkColumn
                url={(item) => ({
                  pathname:
                    "/workspaces/[workspaceSlug]/datasets/[datasetSlug]",
                  query: {
                    workspaceSlug: workspace.slug,
                    datasetSlug: item.dataset.slug,
                  },
                })}
              />
            </DataGrid>
          </Block>
          <Pagination
            onChange={(page, perPage) =>
              router.push({
                pathname: "/workspaces/[workspaceSlug]/datasets",
                query: {
                  page,
                  perPage,
                  workspaceSlug,
                },
              })
            }
            page={page}
            perPage={perPage}
            totalItems={0}
            countItems={0}
          />
        </WorkspaceLayout.PageContent>
      </WorkspaceLayout>

      <CreateDatasetDialog
        workspace={workspace}
        onClose={() => setDialogOpen(false)}
        open={isDialogOpen}
      />
    </Page>
  );
};

WorkspaceDatasetsPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    const { workspaceSlug } = ctx.params!;

    const variables = {
      page: parseInt((ctx.query.page as string) ?? "1", 10),
      perPage: parseInt((ctx.query.perPage as string) ?? "15", 10),
      workspaceSlug: workspaceSlug as string,
    } as any;
    if (ctx.query.query) {
      variables.query = ctx.query.query as string;
    }

    await WorkspaceLayout.prefetch(ctx, client);
    const { data } = await client.query<
      WorkspaceDatasetsPageQuery,
      WorkspaceDatasetsPageQueryVariables
    >({
      query: WorkspaceDatasetsPageDocument,
      variables,
    });

    if (!data.workspace) {
      return { notFound: true };
    }
    return {
      props: variables,
    };
  },
});

export default WorkspaceDatasetsPage;
