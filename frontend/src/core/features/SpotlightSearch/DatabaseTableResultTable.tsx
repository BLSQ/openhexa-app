import React, { useEffect } from "react";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import { useTranslation } from "next-i18next";
import { gql } from "@apollo/client";
import { DatabaseTablesPageFragment } from "./DatabaseTableResultTable.generated";
import WorkspaceDisplay from "./WorkspaceDisplay";
import HighlightedLink from "./HighlightedLink";

type DatabaseTableResultTableProps = {
  isActive: boolean;
  highlightedIndex: number;
  databaseTablesPage?: DatabaseTablesPageFragment;
  fetchData: (params: { page: number }) => void;
  setPage: (page: number) => void;
  pageSize: number;
};

const DatabaseTableResultTable = ({
  isActive,
  highlightedIndex,
  databaseTablesPage,
  fetchData,
  setPage,
  pageSize,
}: DatabaseTableResultTableProps) => {
  const { t } = useTranslation();
  const { items, totalItems } = databaseTablesPage || {
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
      <BaseColumn id="workspace" label={t("Workspace")}>
        {(item) => <WorkspaceDisplay workspace={item.workspace} />}
      </BaseColumn>
      <TextColumn label={t("Count")} accessor="databaseTable.count" />
    </DataGrid>
  );
};

DatabaseTableResultTable.fragments = {
  databaseTablesPage: gql`
    fragment DatabaseTablesPage on DatabaseTableResultPage {
      items {
        databaseTable {
          name
          count
        }
        score
        workspace {
          slug
          ...WorkspaceDisplayFragment
        }
      }
      totalItems
      pageNumber
      totalPages
    }
  `,
};

export default DatabaseTableResultTable;
