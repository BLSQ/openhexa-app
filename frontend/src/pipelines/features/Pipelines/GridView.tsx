import React from "react";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import Block from "core/components/Block";
import { useTranslation } from "next-i18next";
import Link from "core/components/Link";
import { formatPipelineSource, formatPipelineFunctionalType } from "workspaces/helpers/pipelines";
import Badge from "core/components/Badge";
import PipelineRunStatusBadge from "../PipelineRunStatusBadge";
import Tag from "core/features/Tag";
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
            <div className="flex flex-wrap gap-1 max-w-40">
              {pipeline.tags && pipeline.tags.length > 0 ? (
                pipeline.tags.map((tag: any) => (
                  <Tag key={tag.id} tag={tag} className="text-xs" />
                ))
              ) : (
                <span className="text-gray-500 text-sm italic">{t("No tags")}</span>
              )}
            </div>
          )}
        </BaseColumn>
        <BaseColumn id="functionalType" label={t("Type")}>
          {(pipeline) => (
            <span className="text-gray-600">
              {pipeline.functionalType ? formatPipelineFunctionalType(pipeline.functionalType) : t("Not set")}
            </span>
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
