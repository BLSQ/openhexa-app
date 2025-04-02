import { gql } from "@apollo/client";
import {
  CircleStackIcon,
  DocumentIcon,
  ExclamationTriangleIcon,
  Square2StackIcon,
} from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import Link from "core/components/Link";
import { useCallback, useMemo } from "react";
import { useTranslation } from "next-i18next";
import DownloadBucketObject from "../DownloadBucketObject";
import {
  RunOutputsTable_RunFragment,
  RunOutputsTable_WorkspaceFragment,
} from "./RunOutputsTable.generated";
import { renderOutputType } from "workspaces/helpers/pipelines";

type RunOutputsTableProps = {
  run: RunOutputsTable_RunFragment;
  workspace: RunOutputsTable_WorkspaceFragment;
};

const RunOutputsTable = (props: RunOutputsTableProps) => {
  const { run, workspace } = props;
  const { t } = useTranslation();

  const renderOutputAction = useCallback(
    (output: any) => {
      switch (output.__typename) {
        case "BucketObject":
          return (
            <DownloadBucketObject
              variant="outlined"
              size="sm"
              workspace={workspace}
              object={output}
            />
          );
        case "DatabaseTable":
          return (
            <Link
              noStyle
              href={{
                pathname: "/workspaces/[workspaceSlug]/databases/[table]",
                query: {
                  workspaceSlug: workspace.slug,
                  table: output.tableName,
                },
              }}
            >
              <Button variant="outlined" size="sm">
                {t("View")}
              </Button>
            </Link>
          );

        case "DatasetVersion":
          return (
            <Link
              noStyle
              href={{
                pathname: "/workspaces/[workspaceSlug]/datasets/[dataset]",
                query: {
                  workspaceSlug: workspace.slug,
                  dataset: output.dataset.slug,
                },
              }}
            >
              <Button variant="outlined" size="sm">
                {t("View")}
              </Button>
            </Link>
          );

        default:
          return null;
      }
    },
    [workspace, t],
  );

  const renderOutputIcon = useCallback((typename: string | undefined) => {
    switch (typename) {
      case "BucketObject":
        return <DocumentIcon className="w-4" />;
      case "DatabaseTable":
        return <CircleStackIcon className="w-4" />;
      case "DatasetVersion":
        return <Square2StackIcon className="w-4" />;
      default:
        return <ExclamationTriangleIcon className="w-4" />;
    }
  }, []);

  const data = useMemo(() => {
    return [...run.outputs, ...run.datasetVersions];
  }, [run.outputs, run.datasetVersions]);

  if (!data.length) {
    return null;
  }

  return (
    <DataGrid
      data={data}
      defaultPageSize={data.length}
      totalItems={data.length}
      className="rounded-md border"
      fixedLayout={false}
    >
      <BaseColumn label={t("Name")}>
        {(output) => {
          return (
            <div className="flex h-full items-center gap-1.5 text-gray-600">
              {renderOutputIcon(output.__typename)}
              {output.__typename == "DatabaseTable" && output.tableName}
              {output.__typename == "BucketObject" &&
                output.path.slice(workspace.bucket.name.length + 1)}
              {output.__typename == "DatasetVersion" && (
                <>
                  {output.name}
                  <span className="text-gray-400 text-sm">
                    {output.dataset.name}
                  </span>
                </>
              )}
              {output.__typename == "GenericOutput" && output.genericName}
            </div>
          );
        }}
      </BaseColumn>
      <BaseColumn id="type" label={t("Type")}>
        {(output) => (
          <div className="flex h-full items-center gap-1.5 text-gray-600">
            {renderOutputType(output.__typename)}
          </div>
        )}
      </BaseColumn>
      <BaseColumn id="actions" className="text-right">
        {(output) => renderOutputAction(output)}
      </BaseColumn>
    </DataGrid>
  );
};

RunOutputsTable.fragments = {
  workspace: gql`
    fragment RunOutputsTable_workspace on Workspace {
      ...DownloadBucketObject_workspace
      slug
      bucket {
        name
      }
    }
  `,

  run: gql`
    fragment RunOutputsTable_run on PipelineRun {
      id
      outputs {
        __typename
        ... on GenericOutput {
          genericName: name
          genericType: type
          genericUri: uri
        }
        ... on BucketObject {
          name
          key
          path
          type
        }

        ... on DatabaseTable {
          tableName: name
        }
      }
      datasetVersions {
        name
        dataset {
          slug
          name
        }
      }
    }
  `,
};

export default RunOutputsTable;
