import DataGrid, { BaseColumn } from "core/components/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import useDebounce from "core/hooks/useDebounce";
import SearchInput from "core/features/SearchInput";
import { useState, useEffect } from "react";
import { useTranslation } from "next-i18next";
import {
  OrganizationDatasetsQuery,
  OrganizationDataset_LinkFragment,
} from "organizations/graphql/queries.generated";
import Block from "core/components/Block";
import Link from "core/components/Link";
import DatasetWorkspacesList from "./DatasetWorkspacesList";
import { useQuery } from "@apollo/client/react";
import { graphql } from "graphql/gql";

const OrganizationDatasetsDoc = graphql(`
query OrganizationDatasets($id: UUID!, $page: Int = 1, $perPage: Int = 10, $query: String) {
  organization(id: $id) {
    ...Organization_organization
    datasetLinks(page: $page, perPage: $perPage, query: $query) {
      totalItems
      pageNumber
      totalPages
      items {
        ...OrganizationDataset_link
      }
    }
  }
}
`);

const DEFAULT_PAGE_SIZE = 10;

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

  const shouldUseSSRData = page === 1 && !debouncedSearchTerm;

  const { data, loading } = useQuery(OrganizationDatasetsDoc, {
    variables: {
      id: organizationId,
      page: page,
      perPage: DEFAULT_PAGE_SIZE,
      query: debouncedSearchTerm || undefined,
    },
    skip: shouldUseSSRData,
  });

  useEffect(() => {
    if (data && !loading) {
      setPreviousData(data);
    }
  }, [data, loading]);

  const displayData = data || previousData;
  const datasets = (!shouldUseSSRData &&
    displayData?.organization?.datasetLinks) ||
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
                href={`/workspaces/${link.workspace.slug}/datasets/${link.dataset.slug}/from/${link.dataset.workspace?.slug ?? link.workspace.slug}`}
                className="font-medium text-blue-600 hover:text-blue-800 truncate block"
                title={link.dataset.name}
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
