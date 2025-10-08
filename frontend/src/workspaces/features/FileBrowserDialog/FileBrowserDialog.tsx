import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "next-i18next";
import { useLazyQuery } from "@apollo/client";

import {
  ArrowUpTrayIcon,
  ChevronRightIcon,
  HomeIcon,
  MagnifyingGlassIcon,
} from "@heroicons/react/24/outline";
import { BucketObject, BucketObjectType, FileType } from "graphql/types";
import clsx from "clsx";

import Dialog from "core/components/Dialog";
import Button from "core/components/Button";
import Input from "core/components/forms/Input";
import Spinner from "core/components/Spinner";
import useDebounce from "core/hooks/useDebounce";
import { generateBreadcrumbs } from "../../helpers/breadcrumbs";

import {
  FileBrowserDialogQuery,
  FileBrowserDialogQueryVariables,
  FileBrowserDialog_BucketObjectFragment,
  FileBrowserDialogDocument,
} from "./FileBrowserDialog.generated";
import FileSystemDataGrid, {
  FileSystemDataGridPagination,
} from "../../components/FileSystemDataGrid";
import { useUploadFiles } from "../../hooks/useUploadFiles";
import { createBucketFolder } from "../../helpers/bucket";
import { toast } from "react-toastify";
import CreateFolderButton from "./CreateFolderButton";

const PAGE_SIZE = 10;

type FileBrowserDialogProps = {
  open: boolean;
  onClose: () => void;
  workspaceSlug: string;
  onSelectFile: (file: FileBrowserDialog_BucketObjectFragment) => void;
};

const FileBrowserDialog = (props: FileBrowserDialogProps) => {
  const { open, onClose, workspaceSlug, onSelectFile } = props;
  const { t } = useTranslation();

  const [prefix, setPrefix] = useState<string | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [currentSelectedFile, setCurrentSelectedFile] =
    useState<FileBrowserDialog_BucketObjectFragment | null>(null);

  const debouncedSearchQuery = useDebounce(searchQuery, 500);
  const isSearchMode = Boolean(debouncedSearchQuery);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Reset dialog when it closes
  useEffect(() => {
    if (!open) {
      setPrefix(null);
      setIsSearching(false);
      setSearchQuery("");
      setCurrentPage(1);
      setCurrentSelectedFile(null);
    }
  }, [open]);

  // Browsing or searching
  const [searchOrBrowseBucket, { data, previousData, loading }] = useLazyQuery<
    FileBrowserDialogQuery,
    FileBrowserDialogQueryVariables
  >(FileBrowserDialogDocument);

  const getQueryVariables = useCallback(
    (): FileBrowserDialogQueryVariables => ({
      slug: workspaceSlug,
      page: currentPage,
      perPage: PAGE_SIZE,
      useSearch: isSearchMode,
      query: debouncedSearchQuery || "",
      workspaceSlugs: isSearchMode ? [workspaceSlug] : [],
      prefix,
    }),
    [workspaceSlug, currentPage, isSearchMode, debouncedSearchQuery, prefix],
  );

  useEffect(() => {
    if (open) {
      searchOrBrowseBucket({ variables: getQueryVariables() });
      setIsSearching(false);
      setCurrentSelectedFile(null);
    }
  }, [open, getQueryVariables, searchOrBrowseBucket]);

  const updateSearchQuery = useCallback(
    (searchValue: string) => {
      setIsSearching(true);
      setCurrentPage(1);
      setSearchQuery(searchValue);
      setPrefix(null); // Search is across the entire bucket
    },
    [setIsSearching, setSearchQuery],
  );

  const setCurrentFolder = (prefix: string | null) => {
    setSearchQuery("");
    setCurrentPage(1);
    setPrefix(prefix);
  };

  // File or folder selection
  const onItemClick = (item: BucketObject) => {
    if (item.type === BucketObjectType.Directory) {
      setCurrentFolder(item.key);
    } else {
      setCurrentSelectedFile(item);
    }
  };

  // Uploading files
  const uploadFiles = useUploadFiles({
    workspaceSlug,
    prefix,
    onFileUploaded: () => {
      // Refetch the data to show newly uploaded files
      if (open) {
        searchOrBrowseBucket({
          variables: getQueryVariables(),
          fetchPolicy: "network-only",
        });
      }
    },
  });

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      uploadFiles(Array.from(files));
    }
    event.target.value = "";
  };

  // Creating folders
  const handleCreateFolder = async (folderName: string) => {
    try {
      await createBucketFolder(workspaceSlug, folderName, prefix || "");

      // Refetch the data to show newly created folder
      await searchOrBrowseBucket({
        variables: getQueryVariables(),
        fetchPolicy: "network-only",
      });
    } catch (err) {
      toast.error(
        (err as Error).message ??
          t("An error occurred while creating the folder."),
      );
    }
  };

  const prefixes = useMemo(() => generateBreadcrumbs(prefix), [prefix]);

  // Get data from combined query
  const searchResults =
    data?.searchResults ?? previousData?.searchResults ?? null;
  const bucket =
    data?.workspace?.bucket ?? previousData?.workspace?.bucket ?? null;

  const displayedBucketObjects = useMemo(() => {
    if (isSearchMode && searchResults) {
      return searchResults.items.map((result) => ({
        ...result.file,
        type:
          result.file.type === FileType.Directory
            ? BucketObjectType.Directory
            : BucketObjectType.File,
      }));
    } else if (bucket?.objects.items) {
      return bucket.objects.items;
    }
    return [];
  }, [isSearchMode, searchResults, bucket?.objects.items]);

  return (
    <Dialog open={open} onClose={onClose} maxWidth="max-w-5xl">
      <Dialog.Title onClose={onClose}>{t("Select file")}</Dialog.Title>
      <Dialog.Content className="flex flex-col space-y-4 h-full">
        {/* Breadcrumb Navigation */}
        <div className="flex items-center gap-1 text-sm min-h-[2rem] text-gray-500">
          {prefixes.length > 0 && (
            <>
              <button
                className="p-1 hover:text-gray-700 cursor-pointer"
                onClick={() => setCurrentFolder(null)}
                disabled={isSearchMode}
                aria-label={t("Go to root directory")}
              >
                <HomeIcon className="h-4 w-4" />
              </button>
              {prefixes.length > 6 && (
                <>
                  <ChevronRightIcon className="h-3 w-3" />
                  <span>...</span>
                </>
              )}
              {prefixes.slice(-6).map((part, index) => (
                <div key={index} className="flex items-center">
                  <ChevronRightIcon className="h-3 w-3" />
                  <button
                    className="px-1 py-0.5 truncate hover:text-gray-700 cursor-pointer"
                    onClick={() => setCurrentFolder(part.value)}
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

        <div className="flex items-center justify-between gap-2">
          <Input
            placeholder={t("Search files...")}
            value={searchQuery}
            onChange={(e) => updateSearchQuery(e.target.value)}
            leading={<MagnifyingGlassIcon className="h-4 w-4" />}
          />

          <div className="flex items-center justify-end gap-2">
            <CreateFolderButton
              disabled={isSearchMode}
              onCreateFolder={handleCreateFolder}
            />
            <Button
              variant="primary"
              leadingIcon={<ArrowUpTrayIcon className="h-4 w-4" />}
              onClick={handleUploadClick}
            >
              {t("Upload files")}
            </Button>
            {/* Hidden file input for upload */}
            <input
              ref={fileInputRef}
              type="file"
              multiple
              className="hidden"
              onChange={handleFileSelect}
            />
          </div>
        </div>

        {/* File List */}
        <div className="flex-1 overflow-auto">
          {loading && !previousData ? (
            <div className="flex justify-center items-center h-32">
              <Spinner size="lg" />
            </div>
          ) : (
            <FileSystemDataGrid
              data={displayedBucketObjects as BucketObject[]}
              perPage={PAGE_SIZE}
              showPageSizeSelect={false}
              loading={isSearching || loading}
              displayField={isSearchMode ? "key" : "name"}
              rowClassName={(item) =>
                clsx(
                  "cursor-pointer",
                  currentSelectedFile?.path === (item as BucketObject).path
                    ? "bg-blue-100 hover:bg-blue-100 focus:bg-blue-100 font-medium"
                    : "hover:bg-gray-50 focus:bg-gray-50",
                )
              }
              pagination={
                isSearchMode && searchResults
                  ? {
                      totalItems: searchResults.totalItems,
                      totalPages: searchResults.totalPages,
                      pageNumber: searchResults.pageNumber,
                    }
                  : (bucket?.objects as FileSystemDataGridPagination)
              }
              onChangePage={(page: number) => setCurrentPage(page)}
              onDroppingFiles={uploadFiles}
              onRowClick={(item) => onItemClick(item as BucketObject)}
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
