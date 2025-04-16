import React from "react";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import { useTranslation } from "next-i18next";
import WorkspaceDisplay from "./WorkspaceDisplay";
import TypeBadge from "./TypeBadge";
import { getWorkspace } from "./mapper";
import HighlightedLink from "./HighlightedLink";
import PaginationItem from "core/components/Pagination/PaginationItem";
import { ChevronLeftIcon, ChevronRightIcon } from "@heroicons/react/20/solid";

type AllResultsTableProps = {
  isActive: boolean;
  combinedResults: Array<any>;
  highlightedIndex: number;
  hasPreviousPage: boolean;
  hasNextPage: boolean;
  fetchNextPage: () => void;
  fetchPreviousPage: () => void;
};

const AllResultsTable = ({
  isActive,
  combinedResults,
  highlightedIndex,
  hasPreviousPage,
  hasNextPage,
  fetchNextPage,
  fetchPreviousPage,
}: AllResultsTableProps) => {
  const { t } = useTranslation();

  return (
    <>
      <DataGrid data={combinedResults}>
        <BaseColumn id="name" label={t("Name")}>
          {(item) => (
            <HighlightedLink
              item={item}
              highlightedIndex={highlightedIndex}
              isActive={isActive}
              data={combinedResults}
            />
          )}
        </BaseColumn>
        <BaseColumn id="type" label={t("Type")}>
          {(item) => (
            <TypeBadge typeName={item.__typename} type={item.file?.type} />
          )}
        </BaseColumn>
        <BaseColumn id="workspace" label={t("Workspace")}>
          {(item) => <WorkspaceDisplay workspace={getWorkspace(item)} />}
        </BaseColumn>
      </DataGrid>
      {(hasPreviousPage || hasNextPage) && (
        <div className="flex justify-end p-3">
          <nav
            className="relative z-0 inline-flex -space-x-px rounded-md shadow-xs"
            aria-label="Pagination"
          >
            <PaginationItem
              onClick={fetchPreviousPage}
              disabled={!hasPreviousPage}
            >
              <span className="sr-only">{t("Previous")}</span>
              <ChevronLeftIcon className="h-5 w-5" aria-hidden="true" />
            </PaginationItem>

            <PaginationItem onClick={fetchNextPage} disabled={!hasNextPage}>
              <span className="sr-only">{t("Next")}</span>
              <ChevronRightIcon className="h-5 w-5" aria-hidden="true" />
            </PaginationItem>
          </nav>
        </div>
      )}
    </>
  );
};
export default AllResultsTable;
