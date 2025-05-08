import React, { useEffect } from "react";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import { Trans, useTranslation } from "next-i18next";
import { gql } from "@apollo/client";
import { DatasetsPageFragment } from "./DatasetResultTable.generated";
import Time from "core/components/Time";
import UserAvatar from "identity/features/UserAvatar";
import WorkspaceDisplay from "./WorkspaceDisplay";
import HighlightedLink from "./HighlightedLink";

type DatasetResultTableProps = {
  isActive: boolean;
  highlightedIndex: number;
  datasetsPage?: DatasetsPageFragment;
  fetchData: (params: { page: number }) => void;
  setPage: (page: number) => void;
  pageSize: number;
};

const DatasetResultTable = ({
  isActive,
  highlightedIndex,
  datasetsPage,
  fetchData,
  setPage,
  pageSize,
}: DatasetResultTableProps) => {
  const { t } = useTranslation();
  const { items, totalItems } = datasetsPage || { items: [], totalItems: 0 };

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
        {(item) => <WorkspaceDisplay workspace={item.dataset.workspace} />}
      </BaseColumn>
      <TextColumn label={t("Description")} accessor="dataset.description" />
      <BaseColumn id="createdBy" label={t("Created by")}>
        {(item) => (
          <div className={"flex space-x-1"}>
            <UserAvatar user={item.dataset.createdBy} size="xs" />
            <p>{item.dataset.createdBy.displayName}</p>
          </div>
        )}
      </BaseColumn>
      <BaseColumn id="updatedAt" label={t("Last updated")}>
        {(item) => (
          <Trans>
            Updated <Time datetime={item.dataset.updatedAt} relative />
          </Trans>
        )}
      </BaseColumn>
    </DataGrid>
  );
};

DatasetResultTable.fragments = {
  datasetsPage: gql`
    fragment DatasetsPage on DatasetResultPage {
      items {
        dataset {
          id
          slug
          name
          description
          workspace {
            slug
            ...WorkspaceDisplayFragment
          }
          createdBy {
            id
            displayName
            ...UserAvatar_user
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
export default DatasetResultTable;
