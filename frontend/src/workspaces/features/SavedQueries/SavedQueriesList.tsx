import { ChevronRightIcon } from "@heroicons/react/20/solid";
import { TrashIcon } from "@heroicons/react/24/outline";
import Block from "core/components/Block";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import UserColumn from "core/components/DataGrid/UserColumn";
import SearchInput from "core/features/SearchInput";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import DeleteSavedQueryTrigger from "workspaces/features/SavedQueries/DeleteSavedQueryTrigger";
import { SavedQueryListItem_SavedQueryFragment } from "workspaces/features/SavedQueries/SavedQueries.generated";
import { WorkspaceSavedQueriesPageQuery } from "workspaces/graphql/queries.generated";
import { dataStudioRoutes } from "workspaces/helpers/dataStudio";

type Workspace = NonNullable<WorkspaceSavedQueriesPageQuery["workspace"]>;

type SavedQueriesListProps = {
  workspace: Workspace;
  page: number;
  perPage: number;
  loading?: boolean;
  searchValue: string;
  onSearchChange: (value: string) => void;
  onChangePage: (params: { page: number; pageSize: number }) => void;
};

const SavedQueriesList = ({
  workspace,
  page,
  perPage,
  loading,
  searchValue,
  onSearchChange,
  onChangePage,
}: SavedQueriesListProps) => {
  const { t } = useTranslation();
  const router = useRouter();
  const routes = dataStudioRoutes(workspace.slug);
  const { items, totalItems } = workspace.savedQueries;

  const openQuery = (id: string) => router.push(routes.query(id));

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
              with the fetched data (e.g. when a search resets to page 1). */}
            <DataGrid
              data={items}
              totalItems={totalItems}
              defaultPageSize={perPage}
              defaultPageIndex={page - 1}
              fetchData={onChangePage}
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
              <UserColumn accessor="createdBy" header={t("Created by")} />
              <DateColumn
                accessor="updatedAt"
                header={t("Last updated")}
                relative
              />
              <BaseColumn<SavedQueryListItem_SavedQueryFragment>
                id="actions"
                label={t("Actions")}
                hideLabel
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
