import {
  CircleStackIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
} from "@heroicons/react/24/outline";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import useDebounce from "core/hooks/useDebounce";
import SearchInput from "core/features/SearchInput";
import { useState, useEffect } from "react";
import { useTranslation } from "next-i18next";
import {
  useOrganizationDatasetsQuery,
  OrganizationDatasetsQuery,
  OrganizationDataset_DatasetFragment,
} from "organizations/graphql/queries.generated";
import Block from "core/components/Block";
import Link from "core/components/Link";
import { DateTime } from "luxon";
import DatasetWorkspacesList from "./DatasetWorkspacesList";

const DEFAULT_PAGE_SIZE = 10;

// TODO : workspace tag
// TODO : SHaring icon
// TODO : Shared with

export default function OrganizationDatasets({
  organizationId,
}: {
  organizationId: string;
}) {
  const { t } = useTranslation();
  const [searchTerm, setSearchTerm] = useState("");
  const [previousData, setPreviousData] =
    useState<OrganizationDatasetsQuery | null>(null);

  const debouncedSearchTerm = useDebounce(searchTerm, 300);

  const { data, refetch, loading } = useOrganizationDatasetsQuery({
    variables: {
      id: organizationId,
      page: 1,
      perPage: DEFAULT_PAGE_SIZE,
      query: debouncedSearchTerm || undefined,
    },
    fetchPolicy: "cache-and-network",
    notifyOnNetworkStatusChange: true,
  });

  useEffect(() => {
    if (data && !loading) {
      setPreviousData(data);
    }
  }, [data, loading]);

  const onChangePage = ({ page }: { page: number }) => {
    refetch({
      page,
      id: organizationId,
      query: debouncedSearchTerm || undefined,
    }).then();
  };

  const displayData = data || previousData;
  const datasets = displayData?.organization?.datasets ?? {
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
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder={t("Search datasets...")}
          loading={loading}
          className="max-w-md"
          fitWidth
        />
      </div>
      <Block>
        <DataGrid
          defaultPageSize={DEFAULT_PAGE_SIZE}
          totalItems={datasets.totalItems}
          data={datasets.items}
          fetchData={onChangePage}
          className="min-h-30"
        >
          <BaseColumn label={t("Dataset")} id="dataset" minWidth={250}>
            {(dataset: OrganizationDataset_DatasetFragment) => (
              <Link
                href={`/workspaces/${dataset.workspace?.slug}/datasets/${dataset.slug}/from/${dataset.workspace?.slug}`}
                className="font-medium text-blue-600 hover:text-blue-800"
              >
                {dataset.name}
              </Link>
            )}
          </BaseColumn>
          <BaseColumn
            label={t("Source Workspace")}
            id="source_workspace"
            minWidth={150}
          >
            {(dataset: OrganizationDataset_DatasetFragment) => (
              <Link
                href={`/workspaces/${dataset.workspace?.slug}`}
                className="text-blue-600 hover:text-blue-800"
              >
                {dataset.workspace?.name}
              </Link>
            )}
          </BaseColumn>
          <BaseColumn label={t("Sharing")} id="sharing" minWidth={200}>
            {(dataset: OrganizationDataset_DatasetFragment) => (
              <div className="flex items-center gap-2">
                {dataset.sharedWithOrganization ? (
                  <div className="flex items-center gap-1 text-green-600">
                    <CheckCircleIcon className="w-4 h-4" />
                    <span className="text-sm">{t("Organization")}</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-1 text-orange-600">
                    <ExclamationCircleIcon className="w-4 h-4" />
                    <span className="text-sm">{t("Limited")}</span>
                  </div>
                )}
              </div>
            )}
          </BaseColumn>
          <BaseColumn
            label={t("Shared With")}
            id="shared_workspaces"
            minWidth={300}
          >
            {(dataset: OrganizationDataset_DatasetFragment) => (
              <DatasetWorkspacesList
                dataset={dataset}
                size="sm"
                maxVisible={2}
              />
            )}
          </BaseColumn>
          <DateColumn
            className="py-4"
            accessor="updatedAt"
            id="updatedAt"
            label={t("Last Updated")}
            format={DateTime.DATE_FULL}
          />
        </DataGrid>
      </Block>
    </>
  );
}
