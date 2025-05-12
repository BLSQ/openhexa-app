import React, { useEffect } from "react";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import { Trans, useTranslation } from "next-i18next";
import { gql } from "@apollo/client";
import { PipelineTemplatesPageFragment } from "./PipelineTemplateResultTable.generated";
import Time from "core/components/Time";
import HighlightedLink from "./HighlightedLink";

type PipelineTemplateResultTableProps = {
  isActive: boolean;
  highlightedIndex: number;
  pipelineTemplatesPage?: PipelineTemplatesPageFragment;
  fetchData: (params: { page: number }) => void;
  setPage: (page: number) => void;
  pageSize: number;
};

const PipelineTemplateResultTable = ({
  isActive,
  highlightedIndex,
  pipelineTemplatesPage,
  fetchData,
  setPage,
  pageSize,
}: PipelineTemplateResultTableProps) => {
  const { t } = useTranslation();
  const { items, totalItems } = pipelineTemplatesPage || {
    items: [],
    totalItems: 0,
  };

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
      <TextColumn
        label={t("Version number")}
        accessor="pipelineTemplate.currentVersion.versionNumber"
      />
      <TextColumn
        label={t("Description")}
        accessor="pipelineTemplate.description"
      />
      <BaseColumn id="updatedAt" label={t("Last updated")}>
        {(item) => (
          <Trans>
            Updated <Time datetime={item.pipelineTemplate.updatedAt} relative />
          </Trans>
        )}
      </BaseColumn>
    </DataGrid>
  );
};

PipelineTemplateResultTable.fragments = {
  pipelineTemplatesPage: gql`
    fragment PipelineTemplatesPage on PipelineTemplateResultPage {
      items {
        pipelineTemplate {
          id
          code
          name
          description
          workspace {
            slug
            ...WorkspaceDisplayFragment
          }
          currentVersion {
            id
            versionNumber
          }
          updatedAt
        }
        score
      }
      totalItems
      pageNumber
      totalPages
    }
  `,
};
export default PipelineTemplateResultTable;
