import { gql, useLazyQuery } from "@apollo/client";
import {
  ChevronRightIcon,
  FolderIcon,
  MagnifyingGlassIcon,
  PlusIcon,
  ArrowUpTrayIcon,
} from "@heroicons/react/24/outline";
import { HomeIcon } from "@heroicons/react/20/solid";
import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Input from "core/components/forms/Input";
import Spinner from "core/components/Spinner";
import Filesize from "core/components/Filesize";
import { BucketObjectType } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useEffect, useMemo, useState } from "react";
import clsx from "clsx";
import {
  FileBrowserDialogQuery,
  FileBrowserDialogQueryVariables,
  FileBrowserDialog_BucketObjectFragment,
  FileBrowserDialogDocument,
} from "./FileBrowserDialog.generated";
import { getFileIcon, getFileIconColor } from "./utils";

interface FileBrowserDialogProps {
  open: boolean;
  onClose: () => void;
  workspaceSlug: string;
  onSelect: (file: FileBrowserDialog_BucketObjectFragment) => void;
  selectedFile?: string | null;
}

const FileBrowserDialog: React.FC<FileBrowserDialogProps> = ({
  open,
  onClose,
  workspaceSlug,
  onSelect,
  selectedFile,
}) => {
  const { t } = useTranslation();
  const [prefix, _setPrefix] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [perPage, setPerPage] = useState(20);

  const [fetch, { data, previousData, loading }] = useLazyQuery<
    FileBrowserDialogQuery,
    FileBrowserDialogQueryVariables
  >(FileBrowserDialogDocument);

  useEffect(() => {
    if (open) {
      fetch({
        variables: {
          slug: workspaceSlug,
          prefix,
          page: 1,
          perPage,
        },
      });
    }
  }, [prefix, fetch, workspaceSlug, perPage, open]);

  const setPrefix = (prefix: string | null) => {
    setPerPage(20);
    _setPrefix(prefix);
  };

  const loadMore = () => {
    setPerPage((prev) => prev + 20);
  };

  const onItemClick = (item: FileBrowserDialog_BucketObjectFragment) => {
    if (item.type === BucketObjectType.Directory) {
      setPrefix(item.key);
    } else {
      onSelect(item);
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

  const bucket =
    data?.workspace?.bucket ?? previousData?.workspace?.bucket ?? null;

  const filteredItems = useMemo(() => {
    if (!bucket?.objects.items) return [];
    if (!searchQuery.trim()) return bucket.objects.items;

    return bucket.objects.items.filter((item) =>
      item.name.toLowerCase().includes(searchQuery.toLowerCase()),
    );
  }, [bucket?.objects.items, searchQuery]);

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString();
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="max-w-5xl"
      className="h-[85vh] sm:h-[80vh]"
    >
      <Dialog.Title onClose={onClose}>{t("Select Input File")}</Dialog.Title>

      <Dialog.Content className="flex flex-col space-y-4 h-full">
        {/* Breadcrumb Navigation */}
        <div className="flex items-center gap-1 text-sm text-gray-500 px-2 min-h-[2rem]">
          <button
            className="flex items-center hover:text-gray-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 rounded p-1"
            onClick={() => setPrefix(null)}
            aria-label={t("Go to root directory")}
          >
            <HomeIcon className="h-4 w-4" />
          </button>
          {prefixes.length > 0 && (
            <>
              {prefixes.length > 2 && (
                <>
                  <ChevronRightIcon className="h-3 w-3" />
                  <span className="hidden sm:inline">...</span>
                </>
              )}
              {prefixes.slice(-2).map((part, index) => (
                <div key={index} className="flex items-center">
                  <ChevronRightIcon className="h-3 w-3" />
                  <button
                    className="hover:text-gray-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 rounded px-1 py-0.5 max-w-[120px] sm:max-w-none truncate"
                    onClick={() => setPrefix(part.value)}
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
            onChange={(e) => setSearchQuery(e.target.value)}
            leading={<MagnifyingGlassIcon className="h-4 w-4" />}
          />
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-2 px-2">
          <Button
            variant="outlined"
            size="sm"
            leadingIcon={<PlusIcon className="h-4 w-4" />}
            className="justify-center sm:justify-start"
          >
            <span className="hidden sm:inline">{t("Create a folder")}</span>
            <span className="sm:hidden">{t("Create folder")}</span>
          </Button>
          <Button
            variant="outlined"
            size="sm"
            leadingIcon={<ArrowUpTrayIcon className="h-4 w-4" />}
            className="justify-center sm:justify-start"
          >
            <span className="hidden sm:inline">{t("Upload files")}</span>
            <span className="sm:hidden">{t("Upload")}</span>
          </Button>
        </div>

        {/* File List */}
        <div className="flex-1 overflow-auto">
          {loading && !previousData ? (
            <div className="flex justify-center items-center h-32">
              <Spinner size="lg" />
            </div>
          ) : (
            <div className="border rounded-lg">
              {/* Table Header */}
              <div className="hidden sm:grid sm:grid-cols-12 gap-4 p-3 bg-gray-50 border-b text-sm font-medium text-gray-700 rounded-t-lg">
                <div className="col-span-6">{t("Name")}</div>
                <div className="col-span-2">{t("Size")}</div>
                <div className="col-span-4">{t("Last Updated")}</div>
              </div>

              {/* Mobile Header */}
              <div className="sm:hidden p-3 bg-gray-50 border-b text-sm font-medium text-gray-700 rounded-t-lg">
                {t("Files and folders")}
              </div>

              {/* Table Body */}
              <div className="divide-y divide-gray-200">
                {filteredItems.length === 0 ? (
                  <div className="p-8 text-center text-gray-500">
                    {searchQuery
                      ? t("No files match your search")
                      : t("Empty directory")}
                  </div>
                ) : (
                  filteredItems.map((item, index) => (
                    <button
                      key={index}
                      className={clsx(
                        "w-full text-left hover:bg-gray-50 transition-colors focus:outline-none focus:bg-gray-50",
                        "sm:grid sm:grid-cols-12 sm:gap-4 sm:p-3",
                        "flex flex-col p-3 space-y-1 sm:space-y-0",
                        selectedFile === item.path &&
                          "bg-blue-50 hover:bg-blue-100",
                      )}
                      onClick={() => onItemClick(item)}
                      aria-label={
                        item.type === BucketObjectType.Directory
                          ? t("Open folder {{name}}", { name: item.name })
                          : t("Select file {{name}}", { name: item.name })
                      }
                    >
                      {/* Desktop Layout */}
                      <div className="hidden sm:contents">
                        <div className="col-span-6 flex items-center gap-2">
                          {item.type === BucketObjectType.Directory ? (
                            <FolderIcon className="h-5 w-5 text-blue-500" />
                          ) : (
                            (() => {
                              const IconComponent = getFileIcon(item.name);
                              const iconColor = getFileIconColor(item.name);
                              return (
                                <IconComponent
                                  className={clsx("h-5 w-5", iconColor)}
                                />
                              );
                            })()
                          )}
                          <span className="truncate font-medium">
                            {item.name}
                            {item.type === BucketObjectType.Directory && "/"}
                          </span>
                        </div>
                        <div className="col-span-2 text-gray-500 text-sm">
                          {item.type === BucketObjectType.Directory ? (
                            "-"
                          ) : (
                            <Filesize size={item.size} />
                          )}
                        </div>
                        <div className="col-span-4 text-gray-500 text-sm">
                          {item.updatedAt ? formatDate(item.updatedAt) : "-"}
                        </div>
                      </div>

                      {/* Mobile Layout */}
                      <div className="sm:hidden">
                        <div className="flex items-center gap-2">
                          {item.type === BucketObjectType.Directory ? (
                            <FolderIcon className="h-5 w-5 text-blue-500" />
                          ) : (
                            (() => {
                              const IconComponent = getFileIcon(item.name);
                              const iconColor = getFileIconColor(item.name);
                              return (
                                <IconComponent
                                  className={clsx("h-5 w-5", iconColor)}
                                />
                              );
                            })()
                          )}
                          <span className="truncate font-medium">
                            {item.name}
                            {item.type === BucketObjectType.Directory && "/"}
                          </span>
                        </div>
                        {item.type !== BucketObjectType.Directory && (
                          <div className="text-xs text-gray-500 ml-7 flex items-center gap-2">
                            <Filesize size={item.size} />
                            {item.updatedAt && (
                              <>
                                <span>•</span>
                                <span>{formatDate(item.updatedAt)}</span>
                              </>
                            )}
                          </div>
                        )}
                      </div>
                    </button>
                  ))
                )}
              </div>

              {/* Load More */}
              {bucket?.objects.hasNextPage && (
                <div className="p-4 border-t bg-gray-50 text-center">
                  <Button
                    variant="outlined"
                    size="sm"
                    onClick={loadMore}
                    disabled={loading}
                    className="min-w-[100px]"
                  >
                    {loading ? <Spinner size="xs" /> : t("Show more")}
                  </Button>
                </div>
              )}
            </div>
          )}
        </div>
      </Dialog.Content>

      <Dialog.Actions className="flex-shrink-0">
        <Button variant="outlined" onClick={onClose}>
          {t("Cancel")}
        </Button>
        {selectedFile && (
          <Button variant="primary" onClick={onClose}>
            {t("Select file")}
          </Button>
        )}
      </Dialog.Actions>
    </Dialog>
  );
};

export default FileBrowserDialog;
