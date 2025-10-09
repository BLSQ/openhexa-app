import React from "react";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import Block from "core/components/Block";
import { useTranslation } from "next-i18next";
import Link from "core/components/Link";
import { formatPipelineSource } from "workspaces/helpers/pipelines";
import Badge from "core/components/Badge";
import PipelineRunStatusBadge from "../PipelineRunStatusBadge";
import { TagsCell, FunctionalTypeCell } from "../PipelineMetadataGrid";
import User from "core/features/User";

type GridViewProps = {
  items: any[];
  workspace: any;
  page: number;
  perPage: number;
  totalItems: number;
  setPage: (page: number) => void;
};

const GridView = ({
  items,
  workspace,
  page,
  perPage,
  totalItems,
  setPage,
}: GridViewProps) => {
  const { t } = useTranslation();

  return (
    <Block className="divide divide-y divide-gray-100 mt-4">
      <DataGrid
        data={items}
        defaultPageSize={perPage}
        totalItems={totalItems}
        defaultPageIndex={page - 1}
        fetchData={({ page }) => setPage(page)}
        fixedLayout={false}
      >
        <BaseColumn id="name" label={t("Name")}>
          {(pipeline) => (
            <Link
              href={`/workspaces/${encodeURIComponent(workspace.slug)}/pipelines/${pipeline.code}`}
            >
              {pipeline.name}
            </Link>
          )}
        </BaseColumn>
        <BaseColumn id="code" label={t("Code")}>
          {(pipeline) => <span>{pipeline.code}</span>}
        </BaseColumn>
        <BaseColumn id="version" label={t("Version")}>
          {(pipeline) => <span>{pipeline.currentVersion?.versionName}</span>}
        </BaseColumn>
        <BaseColumn id="source" label={t("Source")}>
          {(pipeline) => <Badge>{formatPipelineSource(pipeline.type, !!pipeline.sourceTemplate)}</Badge>}
        </BaseColumn>
        <BaseColumn id="tags" label={t("Tags")}>
          {(pipeline) => (
            <TagsCell
              tags={pipeline.tags}
              emptyText={t("No tags")}
              className="max-w-40"
            />
          )}
        </BaseColumn>
        <BaseColumn id="functionalType" label={t("Type")}>
          {(pipeline) => (
            <FunctionalTypeCell
              functionalType={pipeline.functionalType}
              emptyText={t("Not set")}
            />
          )}
        </BaseColumn>
        <BaseColumn label={t("Last Run")} id="lastRunStatus">
          {(pipeline) => {
            if (pipeline.lastRuns.items.length > 0) {
              return (
                <PipelineRunStatusBadge
                  run={pipeline.lastRuns.items[0]}
                  polling={false}
                />
              );
            }
            return <p>{t("Not yet run")}</p>;
          }}
        </BaseColumn>
        <DateColumn
          accessor="lastRuns.items.0.executionDate"
          label={t("Last Run Date")}
        />
        <BaseColumn label={t("Created By")} id="createdBy">
          {(pipeline) => {
            if (pipeline.currentVersion?.user) {
              return <User user={pipeline.currentVersion.user} />;
            }
            return <span className="text-gray-500 italic">{t("Unknown")}</span>;
          }}
        </BaseColumn>
        <BaseColumn id="description" label={t("Description")}>
          {(pipeline) => <span>{pipeline.description}</span>}
        </BaseColumn>
        <DateColumn
          accessor={"currentVersion.createdAt"}
          label={t("Created At")}
        />
      </DataGrid>
    </Block>
  );
};

export default GridView;
