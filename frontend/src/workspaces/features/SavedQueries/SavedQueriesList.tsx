import { ChevronRightIcon } from "@heroicons/react/20/solid";
import { TrashIcon } from "@heroicons/react/24/outline";
import Block from "core/components/Block";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import UserColumn from "core/components/DataGrid/UserColumn";
import SearchInput from "core/features/SearchInput";
import { SavedQueryOrderBy } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { SortingRule } from "react-table";
import DeleteSavedQueryTrigger from "workspaces/features/SavedQueries/DeleteSavedQueryTrigger";
import { SavedQueryListItem_SavedQueryFragment } from "workspaces/features/SavedQueries/SavedQueries.generated";
import { savedQuerySorting } from "workspaces/features/SavedQueries/sorting";
import { WorkspaceSavedQueriesPageQuery } from "workspaces/graphql/queries.generated";
import { dataStudioRoutes } from "workspaces/helpers/dataStudio";

type Workspace = NonNullable<WorkspaceSavedQueriesPageQuery["workspace"]>;

type SavedQueriesListProps = {
  workspace: Workspace;
  page: number;
  perPage: number;
  orderBy: SavedQueryOrderBy;
  loading?: boolean;
  searchValue: string;
  onSearchChange: (value: string) => void;
  onChange: (params: {
    page: number;
    perPage: number;
    orderBy: SavedQueryOrderBy;
  }) => void;
};

const SavedQueriesList = ({
  workspace,
  page,
  perPage,
  orderBy,
  loading,
  searchValue,
  onSearchChange,
  onChange,
}: SavedQueriesListProps) => {
  const { t } = useTranslation();
  const router = useRouter();
  const routes = dataStudioRoutes(workspace.slug);
  const { items, totalItems } = workspace.savedQueries;

  const openQuery = (id: string) => router.push(routes.query(id));

  const onFetchData = ({
    page: nextPage,
    pageSize,
    sortBy,
  }: {
    page: number;
    pageSize: number;
    sortBy: SortingRule<object>[];
  }) => {
    const nextOrderBy =
      savedQuerySorting.convertDataGridSort(sortBy) ?? orderBy;
    onChange({
      // A new sort re-deals every row, so the current page number is meaningless.
      page: nextOrderBy === orderBy ? nextPage : 1,
      perPage: pageSize,
      orderBy: nextOrderBy,
    });
  };

  return (
    <div className="h-full overflow-auto">
      <div className="py-6 xl:py-8">
        <div className="mx-auto px-4 md:px-6 xl:px-10 2xl:px-12">
          <div className="mb-4 max-w-[420px]">
            <SearchInput
              value={searchValue}
              onChange={(event) => onSearchChange(event.target.value)}
              loading={loading}
              fullWidth
              placeholder={t("Search saved queries…")}
            />
          </div>

          <Block>
            {/* Server-side pagination via the grid's built-in pager: `fetchData`
              reports page/size changes to the parent, and `defaultPageIndex`
              feeds the parent's current page back so the pager stays in sync
              with the fetched data (e.g. when a search resets to page 1).
              `skipPageReset` turns off react-table's autoResetPage: since the
              parent owns the page, resetting the internal index to 0 when new
              data arrives would bounce the pager (page 2 → 1 → 2) and fire a
              spurious refetch on every navigation. */}
            <DataGrid
              data={items}
              totalItems={totalItems}
              defaultPageSize={perPage}
              defaultPageIndex={page - 1}
              fetchData={onFetchData}
              sortable
              defaultSortBy={savedQuerySorting.convertToDataGridSort(orderBy)}
              skipPageReset
              fixedLayout={false}
              loading={loading}
              emptyLabel={t("No saved queries yet.")}
              onRowClick={(row) =>
                openQuery((row as SavedQueryListItem_SavedQueryFragment).id)
              }
              rowClassName="cursor-pointer items-center hover:bg-gray-50"
            >
              <BaseColumn<SavedQueryListItem_SavedQueryFragment>
                id="name"
                label={t("Name")}
              >
                {(item) => (
                  <span className="font-medium text-gray-800">{item.name}</span>
                )}
              </BaseColumn>
              <BaseColumn<SavedQueryListItem_SavedQueryFragment>
                id="description"
                label={t("Description")}
                disableSortBy
              >
                {(item) =>
                  item.description ? (
                    <span
                      className="block max-w-xs truncate text-gray-600"
                      title={item.description}
                    >
                      {item.description}
                    </span>
                  ) : (
                    <span className="text-gray-400">—</span>
                  )
                }
              </BaseColumn>
              <UserColumn
                accessor="createdBy"
                header={t("Created by")}
                disableSortBy
              />
              <DateColumn
                id="updatedAt"
                accessor="updatedAt"
                header={t("Last updated")}
                relative
              />
              <BaseColumn<SavedQueryListItem_SavedQueryFragment>
                id="actions"
                label={t("Actions")}
                hideLabel
                disableSortBy
              >
                {(item) => (
                  <div className="flex items-center justify-end gap-1 text-gray-400">
                    <DeleteSavedQueryTrigger savedQuery={item}>
                      {({ onClick }) => (
                        <button
                          onClick={(event) => {
                            event.stopPropagation();
                            onClick();
                          }}
                          title={t("Delete")}
                          className="rounded-sm p-1.5 hover:bg-gray-100 hover:text-red-600"
                        >
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      )}
                    </DeleteSavedQueryTrigger>
                    <ChevronRightIcon className="h-5 w-5" />
                  </div>
                )}
              </BaseColumn>
            </DataGrid>
          </Block>
        </div>
      </div>
    </div>
  );
};

export default SavedQueriesList;
