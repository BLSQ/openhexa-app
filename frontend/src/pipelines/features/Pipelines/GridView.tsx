import React, { useMemo } from "react";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import Block from "core/components/Block";
import { useTranslation } from "next-i18next";
import Link from "core/components/Link";
import {
  formatPipelineSource,
  getCronExpressionDescription,
} from "workspaces/helpers/pipelines";
import Badge from "core/components/Badge";
import PipelineRunStatusBadge from "../PipelineRunStatusBadge";
import { TagsCell, FunctionalTypeCell } from "../PipelineMetadataGrid";
import { PipelineOrderBy } from "graphql/types";
import { SortingRule } from "react-table";
import { pipelineSorting } from "pipelines/config/sorting";

type GridViewProps = {
  items: any[];
  workspace: any;
  page: number;
  perPage: number;
  totalItems: number;
  setPage: (page: number) => void;
  onSort?: (params: {
    page: number;
    pageSize: number;
    pageIndex: number;
    sortBy: SortingRule<object>[];
  }) => void;
  currentSort?: PipelineOrderBy;
};

const GridView = ({
  items,
  workspace,
  page,
  perPage,
  totalItems,
  setPage,
  onSort,
  currentSort,
}: GridViewProps) => {
  const { t } = useTranslation();

  const defaultSortBy = useMemo(
    () => pipelineSorting.convertToDataGridSort(currentSort),
    [currentSort],
  );

  return (
    <Block className="divide divide-y divide-gray-100 mt-4">
      <DataGrid
        key={currentSort}
        data={items}
        defaultPageSize={perPage}
        totalItems={totalItems}
        defaultPageIndex={page - 1}
        fetchData={onSort || (({ page }) => setPage(page))}
        sortable={Boolean(onSort)}
        defaultSortBy={defaultSortBy}
        fixedLayout={false}
      >
        <BaseColumn id="name" label={t("Name")}>
          {(pipeline) => (
            <div className="flex flex-col">
              <Link
                href={`/workspaces/${encodeURIComponent(workspace.slug)}/pipelines/${pipeline.code}`}
              >
                {pipeline.name}
              </Link>
              <span className="text-sm text-gray-500">
                {pipeline.code}
                {pipeline.currentVersion?.versionName &&
                  ` · ${pipeline.currentVersion.versionName}`}
              </span>
            </div>
          )}
        </BaseColumn>
        <BaseColumn id="source" label={t("Source")} disableSortBy={true}>
          {(pipeline) => <Badge>{formatPipelineSource(pipeline.type, !!pipeline.sourceTemplate)}</Badge>}
        </BaseColumn>
        <BaseColumn id="tags" label={t("Tags")} disableSortBy={true}>
          {(pipeline) => (
            <TagsCell
              tags={pipeline.tags}
              emptyText={t("No tags")}
              className="max-w-40"
            />
          )}
        </BaseColumn>
        <BaseColumn id="functionalType" label={t("Type")} disableSortBy={true}>
          {(pipeline) => (
            <FunctionalTypeCell
              functionalType={pipeline.functionalType}
              emptyText={t("Not set")}
            />
          )}
        </BaseColumn>
        <BaseColumn label={t("Last Run")} id="lastRunStatus" disableSortBy={true}>
          {(pipeline) => {
            if (pipeline.lastRuns.items.length > 0) {
              return (
                <PipelineRunStatusBadge
                  run={pipeline.lastRuns.items[0]}
                />
              );
            }
            return <p>{t("Not yet run")}</p>;
          }}
        </BaseColumn>
        <DateColumn
          id="lastRunDate"
          accessor="lastRuns.items.0.executionDate"
          label={t("Last Run Date")}
        />
        <BaseColumn id="schedule" label={t("Schedule")} disableSortBy={true}>
          {(pipeline) =>
            pipeline.schedule ? (
              <span
                className="font-mono text-sm"
                title={
                  getCronExpressionDescription(pipeline.schedule) ?? undefined
                }
              >
                {pipeline.schedule}
              </span>
            ) : (
              <span className="text-gray-400">&mdash;</span>
            )
          }
        </BaseColumn>
        <DateColumn
          id="createdAt"
          accessor={"createdAt"}
          label={t("Created At")}
        />
      </DataGrid>
    </Block>
  );
};

export default GridView;
