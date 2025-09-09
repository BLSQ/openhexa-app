import React from "react";
import { useTranslation } from "next-i18next";
import clsx from "clsx";

import { FolderIcon } from "@heroicons/react/24/outline";
import { BucketObject, BucketObjectType } from "graphql/types";

import DataGrid, { BaseColumn } from "core/components/DataGrid";
import Filesize from "core/components/Filesize";
import Link from "core/components/Link";
import SimplePagination from "core/components/Pagination/SimplePagination";
import Pagination from "core/components/Pagination/Pagination";
import DropzoneOverlay from "core/components/DropzoneOverlay";
import Time from "core/components/Time";

import { getFileIconAndColor } from "workspaces/features/FileBrowserDialog/utils";

export interface FileSystemDataGridSimplePagination {
  hasNextPage: boolean;
  hasPreviousPage: boolean;
  pageNumber: number;
}

export interface FileSystemDataGridFullPagination {
  totalItems: number;
  totalPages: number;
  pageNumber: number;
}

export type FileSystemDataGridPagination =
  | FileSystemDataGridSimplePagination
  | FileSystemDataGridFullPagination;

const isFullPagination = (
  pagination: FileSystemDataGridPagination,
): pagination is FileSystemDataGridFullPagination => {
  return "totalItems" in pagination && "totalPages" in pagination;
};

export interface FileSystemDataGridProps {
  data: BucketObject[];
  loading?: boolean;
  fixedLayout?: boolean;
  pagination: FileSystemDataGridPagination;
  perPage: number;
  rowClassName?: string | ((row: BucketObject | object) => string);
  actionsRenderer?: (item: BucketObject) => React.ReactElement | null;
  directoryLinkGenerator?: (item: BucketObject) => string;
  onChangePage: (page: number, perPage: number) => void;
  onDroppingFiles?: (files: File[]) => void;
  onRowClick?: (item: BucketObject | object) => void;
  showPageSizeSelect?: boolean;
  displayField?: "name" | "key";
}

const FileSystemDataGrid: React.FC<FileSystemDataGridProps> = ({
  data,
  loading = false,
  fixedLayout = false,
  pagination,
  perPage,
  rowClassName,
  actionsRenderer,
  directoryLinkGenerator,
  onChangePage,
  onDroppingFiles,
  onRowClick,
  showPageSizeSelect = true,
  displayField = "name",
}) => {
  const { t } = useTranslation();

  const renderNameColumn = (item: BucketObject) => {
    const isDirectory = item.type === BucketObjectType.Directory;

    let IconComponent;
    let iconColor = "";

    if (isDirectory) {
      IconComponent = FolderIcon;
      iconColor = "text-blue-500";
    } else {
      const { icon, color } = getFileIconAndColor(item.name);
      IconComponent = icon;
      iconColor = color;
    }

    const iconElement = (
      <IconComponent className={clsx("h-5 w-5 flex-shrink-0", iconColor)} />
    );

    const displayText = displayField === "key" ? item.key : item.name;

    // If directory and link generator provided, wrap in Link
    if (isDirectory && directoryLinkGenerator) {
      return (
        <Link
          noStyle
          href={directoryLinkGenerator(item)}
          className="flex items-center gap-1.5 font-medium text-gray-700 hover:text-gray-800"
        >
          {iconElement}
          {displayText}
        </Link>
      );
    }

    const textElement = (
      <span className="truncate">
        {displayText}
        {isDirectory && "/"}
      </span>
    );

    return (
      <div className="flex items-center gap-2">
        {iconElement} {textElement}
      </div>
    );
  };

  const dataGridContent = (
    <DataGrid
      data={data}
      defaultPageSize={perPage}
      fixedLayout={fixedLayout}
      loading={loading}
      rowClassName={rowClassName}
      onRowClick={onRowClick}
    >
      <BaseColumn id="name" label={t("Name")}>
        {renderNameColumn}
      </BaseColumn>

      <BaseColumn id="size" label={t("Size")}>
        {(item: BucketObject) => {
          return item.type === BucketObjectType.Directory ? (
            <span>-</span>
          ) : (
            <Filesize size={item.size} />
          );
        }}
      </BaseColumn>

      <BaseColumn id="updatedAt" label={t("Last updated")}>
        {(item: BucketObject) => {
          return (
            <Time
              className="truncate"
              datetime={item.updatedAt}
              relative={true}
            />
          );
        }}
      </BaseColumn>

      {actionsRenderer && (
        <BaseColumn id="actions">{actionsRenderer}</BaseColumn>
      )}
    </DataGrid>
  );

  const contentWithPagination = (
    <>
      {dataGridContent}
      {data.length > 0 && (
        <div className={actionsRenderer && "px-4"}>
          {isFullPagination(pagination) ? (
            <Pagination
              page={pagination.pageNumber}
              perPage={perPage}
              perPageOptions={
                showPageSizeSelect ? [10, 20, 50, 100] : undefined
              }
              totalPages={pagination.totalPages}
              countItems={data.length}
              totalItems={pagination.totalItems}
              onChange={onChangePage}
              loading={loading}
            />
          ) : (
            <SimplePagination
              hasNextPage={pagination.hasNextPage}
              hasPreviousPage={pagination.hasPreviousPage}
              page={pagination.pageNumber}
              perPage={perPage}
              perPageOptions={
                showPageSizeSelect ? [10, 20, 50, 100] : undefined
              }
              onChange={onChangePage}
            />
          )}
        </div>
      )}
    </>
  );

  // Wrap with dropzone if handler provided
  if (onDroppingFiles) {
    return (
      <DropzoneOverlay onDroppingFiles={onDroppingFiles}>
        {contentWithPagination}
      </DropzoneOverlay>
    );
  }

  return contentWithPagination;
};

export default FileSystemDataGrid;
