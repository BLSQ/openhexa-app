import React, { useEffect } from "react";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import { Trans, useTranslation } from "next-i18next";
import { gql } from "@apollo/client";
import { PipelinesPageFragment } from "./PipelineResultTable.generated";
import PipelineRunStatusBadge from "pipelines/features/PipelineRunStatusBadge";
import WorkspaceDisplay from "./WorkspaceDisplay";
import Time from "core/components/Time";
import HighlightedLink from "./HighlightedLink";

type PipelineResultTableProps = {
  isActive: boolean;
  highlightedIndex: number;
  pipelinesPage?: PipelinesPageFragment;
  fetchData: (params: { page: number }) => void;
  setPage: (page: number) => void;
  pageSize: number;
};

const PipelineResultTable = ({
  isActive,
  highlightedIndex,
  pipelinesPage,
  fetchData,
  setPage,
  pageSize,
}: PipelineResultTableProps) => {
  const { t } = useTranslation();
  const { items, totalItems } = pipelinesPage || { items: [], totalItems: 0 };

  useEffect(() => {
    if (isActive) {
      setPage(1);
    }
  }, [isActive]);

  return (
    <DataGrid
      defaultPageSize={pageSize}
      data={items}
      totalItems={totalItems}
      fetchData={fetchData}
    >
      <BaseColumn id="name" label={t("Name")}>
        {(item) => (
          <HighlightedLink
            item={item}
            highlightedIndex={highlightedIndex}
            isActive={isActive}
            data={items}
          />
        )}
      </BaseColumn>
      <BaseColumn id="workspace" label={t("Workspace")}>
        {(item) => <WorkspaceDisplay workspace={item.pipeline.workspace} />}
      </BaseColumn>
      <TextColumn label={t("Description")} accessor="pipeline.description" />
      <BaseColumn id="updatedAt" label={t("Last updated")}>
        {(item) => (
          <Trans>
            Updated <Time datetime={item.pipeline.updatedAt} relative />
          </Trans>
        )}
      </BaseColumn>
      <BaseColumn label={t("Last Run")} id="lastRunStatus">
        {(item) => {
          if (item.pipeline.lastRuns.items.length > 0) {
            return (
              <PipelineRunStatusBadge
                run={item.pipeline.lastRuns.items[0]}
                polling={false}
              />
            );
          }
          return <p>{t("Not yet run")}</p>;
        }}
      </BaseColumn>
    </DataGrid>
  );
};

PipelineResultTable.fragments = {
  pipelinesPage: gql`
    fragment PipelinesPage on PipelineResultPage {
      items {
        pipeline {
          id
          code
          name
          description
          updatedAt
          workspace {
            slug
            ...WorkspaceDisplayFragment
          }
          lastRuns: runs(orderBy: EXECUTION_DATE_DESC, page: 1, perPage: 1) {
            items {
              ...PipelineRunStatusBadge_run
            }
          }
        }
        score
      }
      totalItems
      pageNumber
      totalPages
    }
  `,
};
export default PipelineResultTable;
