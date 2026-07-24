import { PlusIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import Page from "core/components/Page";
import { createGetServerSideProps } from "core/helpers/page";
import { NextPageWithLayout } from "core/helpers/types";
import useCacheKey from "core/hooks/useCacheKey";
import useDebounce from "core/hooks/useDebounce";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useState } from "react";
import SavedQueriesList from "workspaces/features/SavedQueries/SavedQueriesList";
import { dataStudioRoutes } from "workspaces/helpers/dataStudio";
import {
  useWorkspaceSavedQueriesPageQuery,
  WorkspaceSavedQueriesPageDocument,
  WorkspaceSavedQueriesPageQuery,
  WorkspaceSavedQueriesPageQueryVariables,
} from "workspaces/graphql/queries.generated";
import DataStudioLayout from "workspaces/layouts/DataStudioLayout";

const DEFAULT_PER_PAGE = 15;

type Props = {
  workspaceSlug: string;
  page: number;
  perPage: number;
};

const WorkspaceSavedQueriesPage: NextPageWithLayout = (props: Props) => {
  const { t } = useTranslation();
  const router = useRouter();
  const [page, setPage] = useState(props.page);
  const [perPage, setPerPage] = useState(props.perPage);
  const [searchInput, setSearchInput] = useState("");
  const debouncedSearch = useDebounce(searchInput, 300);
  const query = debouncedSearch.trim() || undefined;

  const { data, previousData, loading, refetch } =
    useWorkspaceSavedQueriesPageQuery({
      variables: { workspaceSlug: props.workspaceSlug, page, perPage, query },
      notifyOnNetworkStatusChange: true,
    });

  useCacheKey(["savedQueries"], () => refetch());

  // Fall back to previousData so the page doesn't unmount while a new search
  // (or page) is in flight: Apollo blanks `data` on cache-miss variable changes.
  const displayData = data ?? previousData;
  if (!displayData?.workspace) {
    return null;
  }
  const { workspace } = displayData;
  const routes = dataStudioRoutes(workspace.slug);

  return (
    <Page title={t("Saved queries")}>
      <DataStudioLayout
        workspace={workspace}
        currentTab="saved"
        headerActions={
          workspace.permissions.createSavedQuery && (
            <Button
              leadingIcon={<PlusIcon className="h-4 w-4" />}
              onClick={() => router.push(routes.base)}
            >
              {t("New query")}
            </Button>
          )
        }
      >
        <SavedQueriesList
          workspace={workspace}
          page={page}
          perPage={perPage}
          loading={loading}
          searchValue={searchInput}
          onSearchChange={(value) => {
            setSearchInput(value);
            // A new search always narrows to the first page of results.
            setPage(1);
          }}
          onChangePage={({ page, pageSize }) => {
            setPage(page);
            setPerPage(pageSize);
          }}
        />
      </DataStudioLayout>
    </Page>
  );
};

WorkspaceSavedQueriesPage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await DataStudioLayout.prefetch(ctx, client);
    const page = ctx.query.page ? parseInt(ctx.query.page as string, 10) : 1;
    const perPage = DEFAULT_PER_PAGE;
    const { data } = await client.query<
      WorkspaceSavedQueriesPageQuery,
      WorkspaceSavedQueriesPageQueryVariables
    >({
      query: WorkspaceSavedQueriesPageDocument,
      variables: {
        workspaceSlug: ctx.params?.workspaceSlug as string,
        page,
        perPage,
      },
    });

    if (!data.workspace) {
      return {
        notFound: true,
      };
    }
    return {
      props: { workspaceSlug: data.workspace.slug, page, perPage },
    };
  },
});

export default WorkspaceSavedQueriesPage;
