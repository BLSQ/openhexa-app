import { TableCellsIcon } from "@heroicons/react/24/outline";
import Breadcrumbs from "core/components/Breadcrumbs";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import ChevronLinkColumn from "core/components/DataGrid/ChevronLinkColumn";
import Link from "core/components/Link";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import {
  useWorkspaceDatabasesPageQuery,
  WorkspaceDatabasesPageDocument,
} from "workspaces/graphql/queries.generated";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  page: number;
  perPage: number;
};

const WorkspaceDatabasesPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const router = useRouter();

  const workspaceSlug = router.query.workspaceSlug as string;
  const { data, refetch } = useWorkspaceDatabasesPageQuery({
    variables: { workspaceSlug: workspaceSlug },
  });

  const onChangePage = ({ page }: { page: number }) => {
    refetch({
      workspaceSlug: workspaceSlug,
      page,
    });
  };

  if (!data?.workspace) {
    return null;
  }
  const { workspace } = data;
  const { tables } = workspace.database;

  return (
    <Page title={t("Workspace")}>
      <WorkspaceLayout.Header>
        <Breadcrumbs withHome={false}>
          <Breadcrumbs.Part
            isFirst
            href={`/workspaces/${encodeURIComponent(workspace.slug)}`}
          >
            {workspace.name}
          </Breadcrumbs.Part>
          <Breadcrumbs.Part
            isLast
            href={`/workspaces/${encodeURIComponent(workspace.slug)}/databases`}
          >
            {t("Database")}
          </Breadcrumbs.Part>
        </Breadcrumbs>
      </WorkspaceLayout.Header>
      <WorkspaceLayout.PageContent className="space-y-8">
        <DataGrid
          className="overflow-hidden rounded-md bg-white shadow"
          data={tables.items}
          defaultPageSize={15}
          sortable
          totalItems={tables.totalItems}
          fixedLayout={false}
          fetchData={onChangePage}
        >
          <BaseColumn
            className="max-w-[50ch] py-3"
            textClassName="font-medium text-gray-600"
            id="name"
            label="Name"
          >
            {(value) => (
              <Link
                href={{
                  pathname: "/workspaces/[workspaceSlug]/databases/[tableId]",
                  query: { workspaceSlug: workspace.slug, tableId: value.name },
                }}
              >
                <div className="flex items-center gap-3">
                  <TableCellsIcon className="h-6 w-6 text-gray-500" />
                  <span className="font-medium text-gray-700">
                    {value.name}
                  </span>
                </div>
              </Link>
            )}
          </BaseColumn>
          <BaseColumn
            className="py-3"
            accessor="count"
            id="content"
            label={t("# Rows")}
          >
            {(value) => (
              <span>
                {t("Approx. {{count}} row", {
                  count: value,
                  plural: "Approx. {{count}} rows",
                })}
              </span>
            )}
          </BaseColumn>
          <ChevronLinkColumn
            maxWidth="100"
            accessor="name"
            url={(value: any) => ({
              pathname: `/workspaces/${encodeURIComponent(
                workspace.slug
              )}/databases/[tableId]`,
              query: { tableId: value },
            })}
          />
        </DataGrid>
      </WorkspaceLayout.PageContent>
    </Page>
  );
};

WorkspaceDatabasesPage.getLayout = (page, pageProps) => {
  return <WorkspaceLayout pageProps={pageProps}>{page}</WorkspaceLayout>;
};

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    const { data } = await client.query({
      query: WorkspaceDatabasesPageDocument,
      variables: { workspaceSlug: ctx.params?.workspaceSlug },
    });

    if (!data.workspace) {
      return {
        notFound: true,
      };
    }
  },
});

export default WorkspaceDatabasesPage;
