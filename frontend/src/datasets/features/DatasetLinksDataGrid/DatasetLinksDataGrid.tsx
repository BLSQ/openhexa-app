import { gql, useQuery } from "@apollo/client";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import DateColumn from "core/components/DataGrid/DateColumn";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import { DateTime } from "luxon";
import { useTranslation } from "next-i18next";
import Button from "core/components/Button";
import { useState } from "react";
import {
  DatasetLinksDataGrid_DatasetFragment,
  DatasetLinksDataGridQuery,
  DatasetLinksDataGridQueryVariables,
} from "datasets/features/DatasetLinksDataGrid/DatasetLinksDataGrid.generated";
import DeleteDatasetLinkTrigger from "datasets/features/DeleteDatasetLinkTrigger";
import useCacheKey from "core/hooks/useCacheKey";

type DatasetLinksDataGridProps = {
  dataset: DatasetLinksDataGrid_DatasetFragment;
};

const DatasetLinksDataGrid = (props: DatasetLinksDataGridProps) => {
  const { dataset } = props;
  const { t } = useTranslation();
  const [page, setPage] = useState(1);
  const { data, previousData, refetch } = useQuery<
    DatasetLinksDataGridQuery,
    DatasetLinksDataGridQueryVariables
  >(
    gql`
      query DatasetLinksDataGrid($datasetId: ID!, $page: Int) {
        dataset(id: $datasetId) {
          links(page: $page, perPage: 6) {
            totalItems
            items {
              ...DeleteDatasetLinkTrigger_datasetLink
              permissions {
                delete
              }
              workspace {
                slug
                name
              }
              createdBy {
                displayName
              }
              createdAt
            }
          }
        }
      }
      ${DeleteDatasetLinkTrigger.fragments.datasetLink}
    `,
    { variables: { datasetId: dataset.id, page } },
  );

  useCacheKey(["datasets"], () => refetch());

  const links = (data || previousData)?.dataset?.links;

  if (!links) {
    return null;
  }

  return (
    <DataGrid
      data={links.items}
      totalItems={links.totalItems}
      defaultPageSize={6}
      fetchData={({ page }) => setPage(page)}
      emptyLabel={t("Not shared with any workspace yet.")}
    >
      <TextColumn accessor={"workspace.name"} label={t("Workspace")} />
      <TextColumn accessor={"createdBy.displayName"} label={t("Shared by")} />
      <DateColumn
        accessor={"createdAt"}
        label={t("Since")}
        format={DateTime.DATE_MED}
      />
      <BaseColumn className={"text-right"}>
        {(item) =>
          item.permissions.delete && (
            <DeleteDatasetLinkTrigger datasetLink={item}>
              {({ onClick }) => (
                <Button
                  size={"sm"}
                  variant={"outlined"}
                  className="text-red-600"
                  onClick={onClick}
                >
                  {t("Revoke")}
                </Button>
              )}
            </DeleteDatasetLinkTrigger>
          )
        }
      </BaseColumn>
    </DataGrid>
  );
};

DatasetLinksDataGrid.fragments = {
  dataset: gql`
    fragment DatasetLinksDataGrid_dataset on Dataset {
      id
      name
    }
  `,
};

export default DatasetLinksDataGrid;
