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
import Tag from "core/features/Tag";
import { formatPipelineFunctionalType } from "workspaces/helpers/pipelines";

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
      <BaseColumn id="tags" label={t("Tags")}>
        {(item) => (
          <div className="flex flex-wrap gap-1 max-w-40">
            {item.pipeline.tags && item.pipeline.tags.length > 0 ? (
              item.pipeline.tags.map((tag: any) => (
                <Tag key={tag.id} tag={tag} className="text-xs" />
              ))
            ) : (
              <span className="text-gray-500 text-sm italic">{t("No tags")}</span>
            )}
          </div>
        )}
      </BaseColumn>
      <BaseColumn id="functionalType" label={t("Type")}>
        {(item) => (
          <div className="text-sm">
            {item.pipeline.functionalType ? (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                {formatPipelineFunctionalType(item.pipeline.functionalType)}
              </span>
            ) : (
              <span className="text-gray-500 text-sm italic">{t("No type")}</span>
            )}
          </div>
        )}
      </BaseColumn>
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
          functionalType
          tags {
            ...Tag_tag
          }
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
    ${Tag.fragments.tag}
  `,
};
export default PipelineResultTable;
