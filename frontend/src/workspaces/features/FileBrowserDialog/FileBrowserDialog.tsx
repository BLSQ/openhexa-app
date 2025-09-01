import { useCallback, useEffect, useMemo, useState } from "react";
import { useTranslation } from "next-i18next";
import { useLazyQuery } from "@apollo/client";

import {
  ArrowUpTrayIcon,
  ChevronRightIcon,
  HomeIcon,
  MagnifyingGlassIcon,
  PlusIcon,
} from "@heroicons/react/24/outline";
import { BucketObject, BucketObjectType, FileType } from "graphql/types";
import clsx from "clsx";

import Dialog from "core/components/Dialog";
import Button from "core/components/Button";
import Input from "core/components/forms/Input";
import Spinner from "core/components/Spinner";
import useDebounce from "core/hooks/useDebounce";

import {
  FileBrowserDialogQuery,
  FileBrowserDialogQueryVariables,
  FileBrowserDialog_BucketObjectFragment,
  FileBrowserDialogDocument,
} from "./FileBrowserDialog.generated";
import FileSystemDataGrid, {
  FileSystemDataGridPagination,
} from "../../components/FileSystemDataGrid";

type FileBrowserDialogProps = {
  open: boolean;
  onClose: () => void;
  workspaceSlug: string;
  onSelectFile: (file: FileBrowserDialog_BucketObjectFragment) => void;
};

const FileBrowserDialog = (props: FileBrowserDialogProps) => {
  const { open, onClose, workspaceSlug, onSelectFile } = props;
  const { t } = useTranslation();

  const [prefix, _setPrefix] = useState<string | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearchQuery = useDebounce(searchQuery, 500);
  const [isSearchMode, setIsSearchMode] = useState(false);
  const [pageSize, setPageSize] = useState(10);
  const [currentPage, setCurrentPage] = useState(1);
  const [currentSelectedFile, setCurrentSelectedFile] =
    useState<FileBrowserDialog_BucketObjectFragment | null>(null);

  const [fetch, { data, previousData, loading }] = useLazyQuery<
    FileBrowserDialogQuery,
    FileBrowserDialogQueryVariables
  >(FileBrowserDialogDocument);

  // Mode detection logic
  useEffect(() => {
    const newIsSearchMode = Boolean(debouncedSearchQuery.trim());
    if (newIsSearchMode !== isSearchMode) {
      setIsSearchMode(newIsSearchMode);
      // Reset pagination when switching modes
      setCurrentPage(1);
    }
  }, [debouncedSearchQuery, isSearchMode]);

  useEffect(() => {
    if (open) {
      const variables: FileBrowserDialogQueryVariables = {
        slug: workspaceSlug,
        page: currentPage,
        perPage: pageSize,
        useSearch: isSearchMode && Boolean(debouncedSearchQuery),
        // Search parameters (required by schema but ignored when useSearch=false)
        query: debouncedSearchQuery || "",
        workspaceSlugs: isSearchMode ? [workspaceSlug] : [],
        // Browse parameters (ignored when useSearch=true)
        prefix,
      };

      fetch({ variables });
      setIsSearching(false);
      setCurrentSelectedFile(null);
    }
  }, [
    open,
    isSearchMode,
    debouncedSearchQuery,
    workspaceSlug,
    prefix,
    currentPage,
    pageSize,
    fetch,
  ]);

  const updateSearchQuery = useCallback(
    (searchValue: string) => {
      setIsSearching(true);
      setSearchQuery(searchValue);
    },
    [setIsSearching, setSearchQuery],
  );

  const setPrefix = (prefix: string | null) => {
    setPageSize(20);
    setCurrentPage(1);
    _setPrefix(prefix);
  };

  const fetchData = useCallback(
    (page: number, newPageSize?: number) => {
      if (newPageSize && newPageSize !== pageSize) {
        setPageSize(newPageSize);
      }
      setCurrentPage(page);
    },
    [pageSize],
  );

  const onItemClick = (item: FileBrowserDialog_BucketObjectFragment) => {
    if (item.type === BucketObjectType.Directory) {
      setPrefix(item.key);
    } else {
      setCurrentSelectedFile(item);
    }
  };

  const prefixes: { label: string; value: string }[] = useMemo(() => {
    const arr = [] as any[];
    let last = "";
    prefix
      ?.split("/")
      .filter(Boolean)
      .forEach((part) => {
        last = last ? last + "/" + part : part;
        arr.push({
          label: part,
          value: last + "/",
        });
      });
    return arr;
  }, [prefix]);

  // Get data from combined query
  const searchResults =
    data?.searchResults ?? previousData?.searchResults ?? null;
  const bucket =
    data?.workspace?.bucket ?? previousData?.workspace?.bucket ?? null;

  // Normalize and combine data from both sources
  const normalizedItems = useMemo(() => {
    if (isSearchMode && searchResults) {
      // Convert search results to bucket object format
      return searchResults.items.map((result) => ({
        ...result.file,
        // Map search result fields to bucket object fields
        updatedAt: result.file.updated,
        type:
          result.file.type === FileType.Directory
            ? BucketObjectType.Directory
            : BucketObjectType.File,
      }));
    } else if (bucket?.objects.items) {
      return bucket.objects.items;
    }
    return [];
  }, [isSearchMode, searchResults, bucket?.objects.items, searchQuery]);

  // Calculate item counts - use server totals for search, estimation for browse
  const itemCounts = useMemo(() => {
    if (isSearchMode && searchResults) {
      // For search mode, we have the actual total from the server
      return {
        total: searchResults.totalItems,
        showTotal: true,
        mode: "search" as const,
      };
    } else if (bucket?.objects) {
      // For browse mode, estimate based on pagination since we don't have server totals
      const currentPageItems = normalizedItems.length;
      const hasMore = bucket.objects.hasNextPage;
      const pageNumber = bucket.objects.pageNumber;

      // If we're on first page and there are no more items, we know the exact total
      if (pageNumber === 1 && !hasMore) {
        return {
          total: currentPageItems,
          showTotal: true,
          mode: "browse" as const,
        };
      }

      // Otherwise, show estimated count
      const estimatedMinTotal = (pageNumber - 1) * pageSize + currentPageItems;
      return {
        estimatedMinTotal,
        hasMore,
        showTotal: false,
        mode: "browse" as const,
      };
    }
    return { total: 0, showTotal: false, mode: "none" as const };
  }, [
    isSearchMode,
    searchResults,
    bucket?.objects,
    normalizedItems.length,
    pageSize,
  ]);

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="max-w-5xl"
      className="h-[80vh]"
    >
      <Dialog.Title onClose={onClose}>{t("Select Input File")}</Dialog.Title>
      <Dialog.Content className="flex flex-col space-y-4 h-full">
        {/* Breadcrumb Navigation */}
        <div
          className={clsx(
            "flex items-center gap-1 text-sm px-2 min-h-[2rem]",
            isSearchMode ? "text-gray-400" : "text-gray-500",
          )}
        >
          <button
            className={clsx(
              "flex items-center focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 rounded p-1",
              isSearchMode ? "cursor-not-allowed" : "hover:text-gray-700",
            )}
            onClick={() => !isSearchMode && setPrefix(null)}
            disabled={isSearchMode}
            aria-label={t("Go to root directory")}
          >
            <HomeIcon className="h-4 w-4" />
          </button>
          {prefixes.length > 0 && (
            <>
              {prefixes.length > 2 && (
                <>
                  <ChevronRightIcon className="h-3 w-3" />
                  <span>...</span>
                </>
              )}
              {prefixes.slice(-2).map((part, index) => (
                <div key={index} className="flex items-center">
                  <ChevronRightIcon className="h-3 w-3" />
                  <button
                    className={clsx(
                      "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 rounded px-1 py-0.5 truncate",
                      isSearchMode
                        ? "cursor-not-allowed"
                        : "hover:text-gray-700",
                    )}
                    onClick={() => !isSearchMode && setPrefix(part.value)}
                    disabled={isSearchMode}
                    title={part.label}
                  >
                    {part.label}
                  </button>
                </div>
              ))}
            </>
          )}
        </div>

        {/* Search Bar */}
        <div className="px-2">
          <Input
            placeholder={t("Search files...")}
            value={searchQuery}
            onChange={(e) => updateSearchQuery(e.target.value)}
            leading={<MagnifyingGlassIcon className="h-4 w-4" />}
          />
        </div>

        {/* Item Count Display */}
        {!loading && itemCounts.mode !== "none" && (
          <div className="px-2">
            <div className="text-xs text-gray-600">
              {itemCounts.mode === "search" && itemCounts.showTotal
                ? t("{{count}} total results", { count: itemCounts.total })
                : itemCounts.mode === "browse" && itemCounts.showTotal
                  ? t("{{count}} total items", { count: itemCounts.total })
                  : itemCounts.mode === "browse" &&
                      "estimatedMinTotal" in itemCounts
                    ? itemCounts.hasMore
                      ? t("{{count}}+ items", {
                          count: itemCounts.estimatedMinTotal,
                        })
                      : t("{{count}} items", {
                          count: itemCounts.estimatedMinTotal,
                        })
                    : null}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-2 px-2">
          <Button
            variant="outlined"
            size="sm"
            leadingIcon={<PlusIcon className="h-4 w-4" />}
          >
            {t("Create a folder")}
          </Button>
          <Button
            variant="outlined"
            size="sm"
            leadingIcon={<ArrowUpTrayIcon className="h-4 w-4" />}
          >
            {t("Upload files")}
          </Button>
        </div>

        {/* File List */}
        <div className="flex-1 overflow-auto">
          {loading && !previousData ? (
            <div className="flex justify-center items-center h-32">
              <Spinner size="lg" />
            </div>
          ) : (
            <FileSystemDataGrid
              data={normalizedItems as BucketObject[]}
              perPage={pageSize}
              showPageSizeSelect={false}
              loading={isSearching || loading}
              rowClassName={(item: BucketObject) =>
                clsx(
                  "cursor-pointer",
                  currentSelectedFile?.path === item.path
                    ? "bg-blue-100 hover:bg-blue-100 focus:bg-blue-100 font-medium"
                    : "hover:bg-gray-50 focus:bg-gray-50",
                )
              }
              pagination={bucket?.objects as FileSystemDataGridPagination}
              onChangePage={fetchData}
              onRowClick={(item: BucketObject) =>
                onItemClick(item as FileBrowserDialog_BucketObjectFragment)
              }
            />
          )}
        </div>
      </Dialog.Content>
      <Dialog.Actions className="flex-shrink-0">
        <Button variant="outlined" onClick={onClose}>
          {t("Cancel")}
        </Button>
        <Button
          variant="primary"
          onClick={() => {
            onSelectFile(
              currentSelectedFile as FileBrowserDialog_BucketObjectFragment,
            );
            onClose();
          }}
          disabled={!currentSelectedFile}
        >
          {t("Select file")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

export default FileBrowserDialog;
