import React, { useEffect } from "react";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import { useTranslation } from "next-i18next";
import { gql } from "@apollo/client";
import { DatabaseTablesPageFragment } from "./DatabaseTableResultTable.generated";
import WorkspaceDisplay from "./WorkspaceDisplay";
import { FileType } from "graphql/types";
import Filesize from "core/components/Filesize";
import DateColumn from "core/components/DataGrid/DateColumn";
import TypeBadge from "./TypeBadge";
import HighlightedLink from "./HighlightedLink";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import { getObject } from "./mapper";

type FileResultTableProps = {
  isActive: boolean;
  highlightedIndex: number;
  filesPage?: DatabaseTablesPageFragment;
  fetchData: (params: { page: number }) => void;
  setPage: (page: number) => void;
  pageSize: number;
};

const FileResultTable = ({
  isActive,
  highlightedIndex,
  filesPage,
  fetchData,
  setPage,
  pageSize,
}: FileResultTableProps) => {
  const { t } = useTranslation();
  const { items, totalItems } = filesPage || {
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
      <TextColumn label={t("Path")} accessor="file.path" />
      <BaseColumn id="type" label={t("Type")}>
        {(item) => (
          <TypeBadge
            typeName={item.__typename}
            type={item.file.type}
            name={getObject(item).name}
          />
        )}
      </BaseColumn>
      <BaseColumn id="workspace" label={t("Workspace")}>
        {(item) => <WorkspaceDisplay workspace={item.workspace} />}
      </BaseColumn>
      <BaseColumn id="size" label={t("Size")}>
        {(item) =>
          item.file.type === FileType.Directory ? (
            <span> - </span>
          ) : (
            <Filesize size={item.file.size} />
          )
        }
      </BaseColumn>
      <DateColumn
        accessor={"file.updated"}
        label={t("Last updated")}
        relative
      />
    </DataGrid>
  );
};

FileResultTable.fragments = {
  filesPage: gql`
    fragment FilesPage on FileResultPage {
      items {
        file {
          name
          path
          size
          updated
          type
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

export default FileResultTable;
