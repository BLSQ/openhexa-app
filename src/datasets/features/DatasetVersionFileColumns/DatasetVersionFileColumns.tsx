import { gql } from "@apollo/client";
import { PencilIcon } from "@heroicons/react/24/outline";
import Badge from "core/components/Badge";
import Button from "core/components/Button";
import Spinner from "core/components/Spinner";
import { Table, TableBody, TableCell, TableRow } from "core/components/Table";
import Title from "core/components/Title";
import { trackEvent } from "core/helpers/analytics";
import { percentage } from "datasets/helpers/dataset";
import useTabularFileMetadata, {
  TabularColumn,
} from "datasets/hooks/useTabularFileMetadata";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import ColumnMetadataDrawer from "../ColumnMetadataDrawer/ColumnMetadataDrawer";
import RenderColumnAttribute from "../RenderColumnAttribute";
import {
  DatasetVersionFileColumns_FileFragment,
  DatasetVersionFileColumns_VersionFragment,
} from "./DatasetVersionFileColumns.generated";

type DatasetVersionFileColumnsProps = {
  file: DatasetVersionFileColumns_FileFragment;
  version: DatasetVersionFileColumns_VersionFragment;
};

const DatasetVersionFileColumns = (props: DatasetVersionFileColumnsProps) => {
  const { t } = useTranslation();
  const { file, version } = props;
  const { columns, loading, refetch } = useTabularFileMetadata(file.id);

  const [selectedColumn, setSelectedColumn] = useState<TabularColumn | null>(
    null,
  );

  useEffect(() => {
    const { dataset } = version;
    if (dataset) {
      trackEvent("datasets.dataset_file_metadata_accessed", {
        dataset_id: dataset.slug,
        workspace: dataset?.workspace?.slug,
        dataset_version: version.name,
        filename: file.filename,
      });
    }
  }, []);

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

  const onDrawerClose = () => {
    setSelectedColumn(null);
    refetch();
  };

  return (
    <>
      <div className="divide-y divide-gray-200">
        {columns.map((column) => (
          <div
            key={column.key}
            className="hover:bg-gray-50 -mx-4 px-4 group relative py-4 first:pt-2"
          >
            {version.dataset?.permissions?.update && (
              <div className="absolute right-4 top-4 invisible group-hover:visible">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setSelectedColumn(column)}
                >
                  <PencilIcon className="h-4 w-4" />
                </Button>
              </div>
            )}
            <Title level={3} className="mt-0">
              {column.name}
            </Title>
            <div className="flex flex-row divide divide-x divide-gray-200">
              <div className="flex-1/3 grow-0">
                <Table>
                  <TableBody className="font-mono">
                    <TableRow>
                      <TableCell spacing="tight">{t("Distinct")}</TableCell>
                      <RenderColumnAttribute
                        column={column}
                        attributeKeys={["distinct_values", "count"]}
                      >
                        {(distinctValues, count) =>
                          distinctValues && (
                            <TableCell spacing="tight">
                              {distinctValues.value}
                              {count?.value && (
                                <span className="text-xs text-gray-500">
                                  &nbsp;(
                                  {percentage(
                                    distinctValues.value,
                                    count.value,
                                  )}
                                  %)
                                </span>
                              )}
                            </TableCell>
                          )
                        }
                      </RenderColumnAttribute>
                    </TableRow>
                    <TableRow>
                      <TableCell spacing="tight">{t("Missing")}</TableCell>
                      <RenderColumnAttribute
                        column={column}
                        attributeKeys={["missing_values", "count"]}
                      >
                        {(missingValues, count) =>
                          missingValues && (
                            <TableCell spacing="tight">
                              {missingValues.value}
                              {count?.value && (
                                <span className="text-xs text-gray-500">
                                  &nbsp;(
                                  {percentage(missingValues.value, count.value)}
                                  %)
                                </span>
                              )}
                            </TableCell>
                          )
                        }
                      </RenderColumnAttribute>
                    </TableRow>
                    <TableRow>
                      <TableCell spacing="tight">{t("Constant")}</TableCell>
                      <RenderColumnAttribute
                        column={column}
                        attributeKeys={["constant_values", "count"]}
                      >
                        {(constantValues, count) =>
                          constantValues && (
                            <TableCell spacing="tight">
                              {constantValues.value ? t("Yes") : t("No")}
                            </TableCell>
                          )
                        }
                      </RenderColumnAttribute>
                    </TableRow>
                  </TableBody>
                </Table>
              </div>
              <RenderColumnAttribute
                column={column}
                attributeKeys={"description"}
              >
                {(description) =>
                  description?.value && (
                    <div className="px-4">{description.value}</div>
                  )
                }
              </RenderColumnAttribute>
            </div>
            <div className="flex flex-wrap gap-2 mt-4 text-xs">
              <RenderColumnAttribute
                column={column}
                attributeKeys={"data_type"}
              >
                {(dataType) =>
                  dataType && (
                    <Badge
                      className="font-mono bg-amber-50 ring-amber-500/20"
                      size="xs"
                    >
                      {dataType.value}
                    </Badge>
                  )
                }
              </RenderColumnAttribute>
              {column.attributes
                .filter(
                  (attr) =>
                    !attr.system && attr.key !== `${column.key}.description`,
                )
                .map((attribute) => (
                  <Badge
                    key={attribute.key}
                    size="xs"
                    className="font-mono bg-slate-50 ring-slate-200"
                  >
                    {attribute.label}: {attribute.value}
                  </Badge>
                ))}
            </div>
          </div>
        ))}
      </div>
      <ColumnMetadataDrawer
        onClose={onDrawerClose}
        file={file}
        column={selectedColumn}
      />
    </>
  );
};

DatasetVersionFileColumns.fragments = {
  file: gql`
    fragment DatasetVersionFileColumns_file on DatasetVersionFile {
      id
      filename
      ...ColumnMetadataDrawer_file
    }
    ${ColumnMetadataDrawer.fragments.file}
  `,
  version: gql`
    fragment DatasetVersionFileColumns_version on DatasetVersion {
      name
      dataset {
        slug
        permissions {
          update
        }
        workspace {
          slug
        }
      }
    }
  `,
};

export default DatasetVersionFileColumns;
