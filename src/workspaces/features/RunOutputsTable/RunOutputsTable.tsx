import { gql } from "@apollo/client";
import { CircleStackIcon, DocumentIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import Link from "core/components/Link";
import { PipelineRunOutput } from "graphql-types";
import { useCallback } from "react";
import { useTranslation } from "react-i18next";
import DownloadBucketObject from "../DownloadBucketObject";
import {
  RunOutputsTable_RunFragment,
  RunOutputsTable_WorkspaceFragment,
} from "./RunOutputsTable.generated";

type RunOutputsTableProps = {
  run: RunOutputsTable_RunFragment;
  workspace: RunOutputsTable_WorkspaceFragment;
};

const RunOutputsTable = (props: RunOutputsTableProps) => {
  const { run, workspace } = props;
  const { t } = useTranslation();

  const renderOutputAction = useCallback(
    (output: PipelineRunOutput) => {
      switch (output.type) {
        case "file":
          return (
            <DownloadBucketObject
              variant="outlined"
              size="sm"
              workspace={workspace}
              object={{
                key: output.uri.split(`gs://${workspace.bucket.name}/`)[1],
              }}
            />
          );
        case "db":
          return (
            <Link
              noStyle
              href={{
                pathname: "/workspaces/[workspaceSlug]/databases/[table]",
                query: { workspaceSlug: workspace.slug, table: output.name },
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
    [workspace, t]
  );

  const renderOutputIcon = useCallback((type: string) => {
    switch (type) {
      case "file":
        return <DocumentIcon className="w-4" />;
      case "db":
        return <CircleStackIcon className="w-4" />;
      default:
        return null;
    }
  }, []);

  const getDirectory = useCallback((path: string) => {
    const parts = path.split("/");
    parts.pop();
    return parts.join("/");
  }, []);

  if (!run.outputs.length) {
    return null;
  }

  return (
    <DataGrid
      data={run.outputs}
      defaultPageSize={run.outputs.length}
      totalItems={run.outputs.length}
      className="rounded-md border"
    >
      <BaseColumn label={t("Name")}>
        {(output) => (
          <div className="flex h-full items-center gap-1.5 text-gray-600">
            {renderOutputIcon(output.type)}
            {output.name}
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
        name
        type
        uri
      }
    }
  `,
};

export default RunOutputsTable;
