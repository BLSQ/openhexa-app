import { gql, useQuery } from "@apollo/client";
import { MetadataAttribute } from "graphql/types";
import { useMemo } from "react";
import {
  TabularFileMetadataQuery,
  TabularFileMetadataQueryVariables,
} from "./useTabularFileMetadata.generated";

export type TabularColumn = {
  key: string;
  name: string;
  attributes: NonNullable<
    TabularFileMetadataQuery["datasetVersionFile"]
  >["attributes"];
};

export default function useTabularFileMetadata(fileId: string) {
  const { data, loading, error, refetch } = useQuery<
    TabularFileMetadataQuery,
    TabularFileMetadataQueryVariables
  >(
    gql`
      query TabularFileMetadata($fileId: ID!) {
        datasetVersionFile(id: $fileId) {
          attributes {
            id
            key
            value
            label
            system
            createdAt
            updatedAt
            createdBy {
              displayName
            }
            updatedBy {
              displayName
            }
          }
          properties
          id
          targetId
        }
      }
    `,
    {
      variables: { fileId },
    },
  );

  const columns = useMemo(() => {
    if (!data?.datasetVersionFile?.attributes) {
      return [];
    }

    const { attributes, properties } = data.datasetVersionFile;
    const colsMapping = properties.columns ?? {};
    const columns: TabularColumn[] = [];
    for (const [colKey, colName] of Object.entries<string>(colsMapping)) {
      const colAttrs = attributes.filter((attr) => attr.key.startsWith(colKey));

      columns.push({
        key: colKey,
        name: colName,
        attributes: colAttrs,
      });
    }

    return columns;
  }, [data]);

  return {
    loading,
    error,
    columns,
    refetch,
  } as const;
}
