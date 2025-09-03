import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "next-i18next";
import { useLazyQuery } from "@apollo/client";

import {
  ArrowUpTrayIcon,
  ChevronRightIcon,
  FolderPlusIcon,
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

  // Inline folder creation state
  const [isCreatingFolder, setIsCreatingFolder] = useState(false);
  const [newFolderName, setNewFolderName] = useState("");
  const [isCreatingFolderLoading, setIsCreatingFolderLoading] = useState(false);

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
      setIsCreatingFolder(false);
      setNewFolderName("");
      setIsCreatingFolderLoading(false);
    }
  }, [open]);

  // Browsing or searching
  const [searchOrBrowseBucket, { data, previousData, loading }] = useLazyQuery<
    FileBrowserDialogQuery,
    FileBrowserDialogQueryVariables
  >(FileBrowserDialogDocument);

  useEffect(() => {
    if (open) {
      const variables: FileBrowserDialogQueryVariables = {
        slug: workspaceSlug,
        page: currentPage,
        perPage: PAGE_SIZE,
        useSearch: isSearchMode,
        // Search parameters (required by schema but ignored when useSearch=false)
        query: debouncedSearchQuery || "",
        workspaceSlugs: isSearchMode ? [workspaceSlug] : [],
        // Browse parameters (ignored when useSearch=true)
        prefix,
      };

      searchOrBrowseBucket({ variables });
      setIsSearching(false);
      setCurrentSelectedFile(null);
    }
  }, [
    open,
    debouncedSearchQuery,
    workspaceSlug,
    prefix,
    currentPage,
    searchOrBrowseBucket,
  ]);

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
  const onItemClick = (item: FileBrowserDialog_BucketObjectFragment) => {
    if (item.type === BucketObjectType.Directory) {
      setCurrentFolder(item.key);
    } else {
      setCurrentSelectedFile(item);
    }
  };

  // Uploading files
  const uploadFiles = useUploadFiles({
    workspace: {
      slug: workspaceSlug,
      permissions: { createObject: true }, // Assume permission for file browser dialog
    },
    prefix,
    onFileUploaded: () => {
      // Refetch the data to show newly uploaded files
      if (open) {
        const variables: FileBrowserDialogQueryVariables = {
          slug: workspaceSlug,
          page: currentPage,
          perPage: PAGE_SIZE,
          useSearch: isSearchMode,
          query: debouncedSearchQuery || "",
          workspaceSlugs: isSearchMode ? [workspaceSlug] : [],
          prefix,
        };
        searchOrBrowseBucket({ variables });
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
    // Reset the input so the same files can be selected again if needed
    event.target.value = "";
  };

  // Folder creation handlers
  const handleCreateFolderClick = () => {
    if (isSearchMode) return; // Disable in search mode
    setIsCreatingFolder(true);
    setNewFolderName("New folder");
  };

  const handleConfirmFolderCreation = async () => {
    if (!newFolderName.trim()) return;

    setIsCreatingFolderLoading(true);
    try {
      const folderKey = (prefix || "") + newFolderName.trim();
      await createBucketFolder(workspaceSlug, folderKey);

      // Refetch the data to show newly created folder
      const variables: FileBrowserDialogQueryVariables = {
        slug: workspaceSlug,
        page: currentPage,
        perPage: PAGE_SIZE,
        useSearch: isSearchMode,
        query: debouncedSearchQuery || "",
        workspaceSlugs: isSearchMode ? [workspaceSlug] : [],
        prefix,
      };
      await searchOrBrowseBucket({ variables });

      // Reset folder creation state
      setIsCreatingFolder(false);
      setNewFolderName("");
    } catch (err) {
      toast.error(t("An error occurred while creating the folder"));
    } finally {
      setIsCreatingFolderLoading(false);
    }
  };

  const handleCancelFolderCreation = () => {
    setIsCreatingFolder(false);
    setNewFolderName("");
    setIsCreatingFolderLoading(false);
  };

  const handleNewFolderNameChange = (name: string) => {
    setNewFolderName(name);
  };

  const prefixes = useMemo(() => generateBreadcrumbs(prefix), [prefix]);

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

  return (
    <Dialog open={open} onClose={onClose} maxWidth="max-w-5xl">
      <Dialog.Title onClose={onClose}>{t("Select Input File")}</Dialog.Title>
      <Dialog.Content className="flex flex-col space-y-4 h-full">
        {/* Breadcrumb Navigation */}
        <div
          className={clsx(
            "flex items-center gap-1 text-sm min-h-[2rem]",
            isSearchMode ? "text-gray-400" : "text-gray-500",
          )}
        >
          <button
            className={clsx(
              "flex items-center focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 rounded p-1",
              isSearchMode ? "cursor-not-allowed" : "hover:text-gray-700",
            )}
            onClick={() => !isSearchMode && setCurrentFolder(null)}
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
                    onClick={() =>
                      !isSearchMode && setCurrentFolder(part.value)
                    }
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
            <Button
              variant="secondary"
              leadingIcon={<FolderPlusIcon className="h-4 w-4" />}
              onClick={handleCreateFolderClick}
              disabled={isSearchMode}
            >
              {t("Create a folder")}
            </Button>
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
              data={normalizedItems as BucketObject[]}
              perPage={PAGE_SIZE}
              showPageSizeSelect={false}
              loading={isSearching || loading}
              displayField={isSearchMode ? "key" : "name"}
              rowClassName={(item: BucketObject) =>
                clsx(
                  "cursor-pointer",
                  currentSelectedFile?.path === item.path
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
              onRowClick={(item: BucketObject) =>
                onItemClick(item as FileBrowserDialog_BucketObjectFragment)
              }
              isCreatingFolder={isCreatingFolder}
              newFolderName={newFolderName}
              onNewFolderNameChange={handleNewFolderNameChange}
              onConfirmFolderCreation={handleConfirmFolderCreation}
              onCancelFolderCreation={handleCancelFolderCreation}
              folderCreationLoading={isCreatingFolderLoading}
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
