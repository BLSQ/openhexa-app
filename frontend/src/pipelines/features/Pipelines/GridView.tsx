import React from "react";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import Block from "core/components/Block";
import { useTranslation } from "next-i18next";
import Link from "core/components/Link";
import { formatPipelineType } from "workspaces/helpers/pipelines";
import Badge from "core/components/Badge";
import PipelineRunStatusBadge from "../PipelineRunStatusBadge";

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
        <BaseColumn id="type" label={t("Type")}>
          {(pipeline) => <Badge>{formatPipelineType(pipeline.type)}</Badge>}
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
