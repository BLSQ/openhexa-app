import React, { useRef, useEffect, useState } from "react";
import { useTranslation } from "next-i18next";
import clsx from "clsx";

import { FolderIcon } from "@heroicons/react/24/outline";
import { BucketObject, BucketObjectType } from "graphql/types";

import DataGrid, { BaseColumn } from "core/components/DataGrid";
import DateColumn from "core/components/DataGrid/DateColumn";
import Filesize from "core/components/Filesize";
import Link from "core/components/Link";
import SimplePagination from "core/components/Pagination/SimplePagination";
import Pagination from "core/components/Pagination/Pagination";
import DropzoneOverlay from "core/components/DropzoneOverlay";
import Input from "core/components/forms/Input";
import Spinner from "core/components/Spinner";
import Time from "core/components/Time";

import { getFileIconAndColor } from "../../features/FileBrowserDialog/utils";

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
  rowClassName?: string | ((row: BucketObject) => string);
  actionsRenderer?: (item: BucketObject) => React.ReactElement | null;
  directoryLinkGenerator?: (item: BucketObject) => string;
  onChangePage: (page: number, perPage: number) => void;
  onDroppingFiles?: (files: File[]) => void;
  onRowClick?: (item: BucketObject) => void;
  showPageSizeSelect?: boolean;
  displayField?: "name" | "key";
  // Folder creation props
  isCreatingFolder?: boolean;
  onConfirmFolderCreation: (folderName: string) => void;
  onCancelFolderCreation: () => void;
  folderCreationLoading: boolean;
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
  // Folder creation props
  isCreatingFolder = false,
  onConfirmFolderCreation,
  onCancelFolderCreation,
  folderCreationLoading = false,
}) => {
  const { t } = useTranslation();
  const inputRef = useRef<HTMLInputElement>(null);

  // Internal state for folder name
  const NEW_FOLDER_NAME = t("New folder");
  const [newFolderName, setNewFolderName] = useState(NEW_FOLDER_NAME);

  // Auto-focus and select text when creating folder
  useEffect(() => {
    if (isCreatingFolder && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isCreatingFolder]);

  // Component for folder creation row
  const FolderCreationRow: React.FC = () => {
    const handleKeyDown = (e: React.KeyboardEvent) => {
      if (e.key === "Enter") {
        e.preventDefault();
        if (newFolderName.trim()) {
          onConfirmFolderCreation(newFolderName.trim());
          setNewFolderName(NEW_FOLDER_NAME);
        }
      } else if (e.key === "Escape") {
        e.preventDefault();
        onCancelFolderCreation();
        setNewFolderName(NEW_FOLDER_NAME);
      }
    };

    return (
      <div className="flex items-center gap-2">
        <FolderIcon className="h-5 w-5 flex-shrink-0 text-blue-500" />
        <div className="flex-1">
          {folderCreationLoading ? (
            <div className="flex items-center gap-2">
              <Spinner size="sm" />
              <span className="text-gray-500">{t("Creating folder...")}</span>
            </div>
          ) : (
            <Input
              ref={inputRef}
              value={newFolderName}
              onChange={(e) => setNewFolderName(e.target.value)}
              onKeyDown={handleKeyDown}
              onBlur={onCancelFolderCreation}
              className="text-sm"
              placeholder={t("Folder name")}
            />
          )}
        </div>
      </div>
    );
  };

  // Component for regular file/folder rows
  const RegularFileRow: React.FC<{ item: BucketObject }> = ({ item }) => {
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

  // Unified row renderer that decides between folder creation or regular row
  const renderRow = (
    item: BucketObject,
    columnType: "name" | "size" | "date" | "actions",
  ) => {
    const isTempRow = (item as any).isTemporaryFolderCreation;

    if (isTempRow) {
      switch (columnType) {
        case "name":
          return <FolderCreationRow />;
        case "size":
        case "date":
          return <span>-</span>;
        case "actions":
          return null;
        default:
          return null;
      }
    }

    // Regular row rendering
    switch (columnType) {
      case "name":
        return <RegularFileRow item={item} />;
      case "size":
        return item.type === BucketObjectType.Directory ? (
          <span>-</span>
        ) : (
          <Filesize size={item.size} />
        );
      case "date":
        return (
          <Time
            className="truncate"
            datetime={item.updatedAt}
            relative={true}
          />
        );
      case "actions":
        return actionsRenderer?.(item) || null;
      default:
        return null;
    }
  };

  // Create temporary folder creation object for the DataGrid
  const temporaryFolderRow = isCreatingFolder
    ? ({
        key: "__temp_folder_creation__",
        name: "",
        type: BucketObjectType.Directory,
        size: 0,
        updatedAt: new Date().toISOString(),
        path: "",
        isTemporaryFolderCreation: true,
      } as BucketObject & { isTemporaryFolderCreation: boolean })
    : null;

  // Prepend temporary row to data when creating folder
  const displayData =
    isCreatingFolder && temporaryFolderRow
      ? [temporaryFolderRow as BucketObject, ...data]
      : data;

  const dataGridContent = (
    <DataGrid
      data={displayData}
      defaultPageSize={perPage}
      fixedLayout={fixedLayout}
      loading={loading}
      rowClassName={(item) => {
        // Special styling for temporary folder creation row
        if ((item as any).isTemporaryFolderCreation) {
          return "bg-blue-50 hover:bg-blue-50";
        }
        return typeof rowClassName === "function"
          ? rowClassName(item as BucketObject)
          : rowClassName || "";
      }}
      onRowClick={(item) => {
        // Don't trigger row click for temporary folder creation row
        if ((item as any).isTemporaryFolderCreation) return;
        onRowClick?.(item as BucketObject);
      }}
    >
      <BaseColumn id="name" label={t("Name")}>
        {(item: BucketObject) => renderRow(item, "name")}
      </BaseColumn>

      <BaseColumn id="size" label={t("Size")}>
        {(item: BucketObject) => renderRow(item, "size")}
      </BaseColumn>

      <BaseColumn id="updatedAt" label={t("Last Updated")}>
        {(item: BucketObject) => renderRow(item, "date")}
      </BaseColumn>

      {actionsRenderer && (
        <BaseColumn id="actions">
          {(item: BucketObject) => renderRow(item, "actions")}
        </BaseColumn>
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
