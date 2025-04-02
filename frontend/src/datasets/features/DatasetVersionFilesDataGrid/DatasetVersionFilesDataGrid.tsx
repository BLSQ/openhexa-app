import { gql, useQuery } from "@apollo/client";
import DataGrid from "core/components/DataGrid/DataGrid";
import {
  DatasetVersionFilesDataGrid_VersionFragment,
  DatasetVersionFilesDataGridDocument,
  DatasetVersionFilesDataGridQuery,
  DatasetVersionFilesDataGridQueryVariables,
} from "./DatasetVersionFilesDataGrid.generated";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import { useTranslation } from "next-i18next";
import { BaseColumn } from "core/components/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import DownloadVersionFile from "../DownloadVersionFile/DownloadVersionFile";
import { useState } from "react";
import { CustomApolloClient } from "core/helpers/apollo";

type DatasetVersionFilesDataGridProps = {
  perPage: number;
  version: DatasetVersionFilesDataGrid_VersionFragment;
};

const DatasetVersionFilesDataGrid = (
  props: DatasetVersionFilesDataGridProps,
) => {
  const { version, perPage } = props;
  const { t } = useTranslation();
  const [page, setPage] = useState(1);

  const { data, previousData } = useQuery<
    DatasetVersionFilesDataGridQuery,
    DatasetVersionFilesDataGridQueryVariables
  >(
    gql`
      query DatasetVersionFilesDataGrid(
        $versionId: ID!
        $page: Int = 1
        $perPage: Int!
      ) {
        datasetVersion(id: $versionId) {
          id
          files(page: $page, perPage: $perPage) {
            items {
              ...DownloadVersionFile_file
              id
              contentType
              createdAt
              uri
              filename
            }
            totalPages
            totalItems
            pageNumber
          }
        }
      }
      ${DownloadVersionFile.fragments.file}
    `,
    { variables: { versionId: version.id, page, perPage } },
  );

  const onFetchData: React.ComponentProps<typeof DataGrid>["fetchData"] = ({
    page,
  }) => {
    setPage(page);
  };

  const files = (data || previousData)?.datasetVersion?.files;
  if (!files) {
    return null;
  }

  return (
    <DataGrid
      data={files.items}
      totalItems={files.totalItems}
      defaultPageSize={perPage}
      fetchData={onFetchData}
      fixedLayout={false}
    >
      <TextColumn label={t("Filename")} accessor="filename" />
      <DateColumn label={t("Created at")} accessor="createdAt" />
      <TextColumn label={t("Content type")} accessor="contentType" />
      {version.permissions.download && (
        <BaseColumn className="text-right">
          {(item) => (
            <DownloadVersionFile file={item} variant="outlined" size="sm" />
          )}
        </BaseColumn>
      )}
    </DataGrid>
  );
};

DatasetVersionFilesDataGrid.fragments = {
  version: gql`
    fragment DatasetVersionFilesDataGrid_version on DatasetVersion {
      id
      name
      permissions {
        download
      }
    }
  `,
};

DatasetVersionFilesDataGrid.prefetch = async (
  client: CustomApolloClient,
  variables: {
    versionId: string;
    perPage: number;
  },
) => {
  return client.query({
    query: DatasetVersionFilesDataGridDocument,
    variables: { ...variables, page: 1 },
  });
};
export default DatasetVersionFilesDataGrid;
