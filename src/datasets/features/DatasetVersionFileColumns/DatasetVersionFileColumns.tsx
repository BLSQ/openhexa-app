import { gql, useQuery } from "@apollo/client";
import { useMemo } from "react";
import Spinner from "core/components/Spinner";
import { MetadataAttribute } from "graphql/types";
import { camelCase } from "lodash";
import Card from "core/components/Card";
import DescriptionList from "core/components/DescriptionList";
import { useTranslation } from "react-i18next";
import Badge from "core/components/Badge";
import { percentage } from "datasets/helpers/dataset";

export type DatasetColumn = {
  id: string;
  columnName: string;
  constantValues?: boolean;
  dataType: string;
  distinctValues: number;
  key: string;
  missingValues: number;
  system: boolean;
  uniqueValues?: number;
  count: number;
};

type DatasetVersionFileColumnsProps = {
  file: any;
};

const DatasetVersionFileColumns = (props: DatasetVersionFileColumnsProps) => {
  const { t } = useTranslation();
  const { file } = props;
  const { data, loading } = useQuery(
    gql`
      query DatasetVersionFileColumnsMetadata($id: ID!) {
        datasetVersionFile(id: $id) {
          id
          attributes {
            id
            key
            value
            system
          }
        }
      }
    `,
    {
      variables: {
        id: file.id,
      },
    },
  );

  const { columns, total } = useMemo(() => {
    if (!data?.datasetVersionFile.attributes) {
      return { columns: [], total: 0 };
    }

    const { attributes } = data.datasetVersionFile;
    const res: Array<DatasetColumn> = Object.values(
      attributes.reduce((acc: any, item: MetadataAttribute) => {
        const [columnKey, property] = item.key.split(".");
        if (!acc[columnKey]) {
          acc[columnKey] = {
            id: item.id,
            key: columnKey,
            system: item.system,
          };
        }
        acc[columnKey][camelCase(property)] = item.value;
        return acc;
      }, {}),
    );

    return {
      columns: res,
      total: res.length ? res[0].count + res[0].missingValues : 0,
    };
  }, [data]);

  if (loading)
    return (
      <div className="flex justify-center items-center h-24 p-4">
        <Spinner size="md" />
      </div>
    );

  if (!columns.length) {
    return (
      <div className="text-sm text-gray-500 italic w-full flex justify-center p-4">
        {t("Columns metadata not available.")}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 2xl:grid-cols-2 gap-4">
      {columns.map((column: DatasetColumn) => (
        <Card
          key={column.key}
          title={
            <div className="flex justify-between">
              <span className="max-w-[80%] font-semibold text-sm font-mono">
                {column.columnName}
              </span>
              <div>
                <Badge className="text-xs bg-gray-100 font-mono">
                  {column.dataType}
                </Badge>
              </div>
            </div>
          }
        >
          <Card.Content>
            <DescriptionList compact>
              <DescriptionList.Item label={t("Distinct")}>
                <code className="font-mono text-sm text-gray-600">
                  {`${column.distinctValues} (${total ? `${percentage(column.distinctValues, total)}%` : "-"})`}
                </code>
              </DescriptionList.Item>
              <DescriptionList.Item label={t("Missing")} className="gap-4">
                <code className="font-mono text-sm text-gray-600 ">
                  {`${column.missingValues} (${total ? `${percentage(column.missingValues, total)}%` : "-"})`}
                </code>
              </DescriptionList.Item>
            </DescriptionList>
          </Card.Content>
        </Card>
      ))}
    </div>
  );
};

DatasetVersionFileColumns.fragments = {
  file: gql`
    fragment DatasetVersionFileColumns_file on DatasetVersionFile {
      id
    }
  `,
};

export default DatasetVersionFileColumns;
