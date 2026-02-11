import { gql, useQuery } from "@apollo/client";
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
    const colsMapping: Record<string, string> = properties.columns ?? {};
    const columnOrder: string[] | undefined = properties.column_order;

    const orderedKeys = columnOrder ?? Object.keys(colsMapping);

    return orderedKeys
      .filter((colKey) => colKey in colsMapping)
      .map((colKey) => ({
        key: colKey,
        name: colsMapping[colKey],
        attributes: attributes.filter((attr) => attr.key.startsWith(colKey)),
      }));
  }, [data]);

  return {
    loading,
    error,
    columns,
    refetch,
  } as const;
}
