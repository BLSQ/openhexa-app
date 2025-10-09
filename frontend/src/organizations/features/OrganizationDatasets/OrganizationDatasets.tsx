import DataGrid, { BaseColumn } from "core/components/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import useDebounce from "core/hooks/useDebounce";
import SearchInput from "core/features/SearchInput";
import { useState, useEffect } from "react";
import { useTranslation } from "next-i18next";
import {
  useOrganizationDatasetsQuery,
  OrganizationDatasetsQuery,
  OrganizationDataset_LinkFragment,
} from "organizations/graphql/queries.generated";
import Block from "core/components/Block";
import Link from "core/components/Link";
import DatasetWorkspacesList from "./DatasetWorkspacesList";

const DEFAULT_PAGE_SIZE = 10;

// TODO : is the linked dataset showing ?
// TODO : avoid the double query
// TODO : index on updatedAt
// TODO : High query count
// TODO : url path

export default function OrganizationDatasets({
  organization,
}: {
  organization: OrganizationDatasetsQuery["organization"];
}) {
  const { t } = useTranslation();
  const { id: organizationId, datasetLinks: SRRDatasets } = organization || {};
  const [searchTerm, setSearchTerm] = useState("");
  const [page, setPage] = useState(1);
  const [previousData, setPreviousData] =
    useState<OrganizationDatasetsQuery | null>(null);

  const debouncedSearchTerm = useDebounce(searchTerm, 300);

  const { data, loading } = useOrganizationDatasetsQuery({
    variables: {
      id: organizationId,
      page: page,
      perPage: DEFAULT_PAGE_SIZE,
      query: debouncedSearchTerm,
    },
  });

  useEffect(() => {
    if (data && !loading) {
      setPreviousData(data);
    }
  }, [data, loading]);

  const displayData = data || previousData;
  const datasets = displayData?.organization?.datasetLinks ||
    SRRDatasets || {
      items: [],
      totalItems: 0,
      pageNumber: 1,
      totalPages: 1,
    };

  return (
    <>
      <div className="mb-4">
        <SearchInput
          name="search-datasets"
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setPage(1);
          }}
          placeholder={t("Search datasets...")}
          loading={loading}
          className="max-w-md"
          fitWidth
        />
      </div>
      <Block>
        <DataGrid
          defaultPageIndex={page - 1}
          defaultPageSize={DEFAULT_PAGE_SIZE}
          totalItems={datasets.totalItems}
          data={datasets.items}
          fetchData={({ page }) => setPage(page)}
          className="min-h-30"
        >
          <BaseColumn label={t("Dataset")} id="dataset" minWidth={250}>
            {(link: OrganizationDataset_LinkFragment) => (
              <Link
                href={`/workspaces/${link.dataset.workspace?.slug}/datasets/${link.dataset.slug}/from/${link.dataset.workspace?.slug}`}
                className="font-medium text-blue-600 hover:text-blue-800"
              >
                {link.dataset.name}{" "}
                <span className="text-xs text-gray-500 font-normal">
                  ({link.dataset.slug})
                </span>
              </Link>
            )}
          </BaseColumn>
          <BaseColumn
            label={t("Source workspace")}
            id="source_workspace"
            minWidth={150}
          >
            {(link: OrganizationDataset_LinkFragment) => (
              <Link
                href={`/workspaces/${link.dataset.workspace?.slug}`}
                className="text-blue-600 hover:text-blue-800"
              >
                {link.dataset.workspace?.name}
              </Link>
            )}
          </BaseColumn>
          <BaseColumn
            label={t("Shared With")}
            id="shared_workspaces"
            minWidth={300}
          >
            {(link: OrganizationDataset_LinkFragment) => (
              <DatasetWorkspacesList
                dataset={link.dataset}
                size="sm"
                maxVisible={2}
              />
            )}
          </BaseColumn>
          <DateColumn
            className="py-4"
            accessor="dataset.updatedAt"
            id="updatedAt"
            label={t("Last updated")}
            relative
          />
        </DataGrid>
      </Block>
    </>
  );
}
