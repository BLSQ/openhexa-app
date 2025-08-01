import { useEffect, useMemo, useState } from "react";
import { gql, useLazyQuery } from "@apollo/client";
import {
  ChevronRightIcon,
  FolderIcon,
  MagnifyingGlassIcon,
  PlusIcon,
  ArrowUpTrayIcon,
} from "@heroicons/react/24/outline";
import { HomeIcon } from "@heroicons/react/20/solid";
import { BucketObjectType } from "graphql/types";
import { useTranslation } from "next-i18next";
import clsx from "clsx";

import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import DataGrid, { BaseColumn } from "core/components/DataGrid";
import Filesize from "core/components/Filesize";
import Input from "core/components/forms/Input";
import Spinner from "core/components/Spinner";

import {
  FileBrowserDialogQuery,
  FileBrowserDialogQueryVariables,
  FileBrowserDialog_BucketObjectFragment,
  FileBrowserDialogDocument,
} from "./FileBrowserDialog.generated";
import { getFileIcon, getFileIconColor } from "./utils";

type FileBrowserDialogProps = {
  open: boolean;
  onClose: () => void;
  workspaceSlug: string;
  onSelectFile: (file: FileBrowserDialog_BucketObjectFragment) => void;
};

const FileBrowserDialog = ({
  open,
  onClose,
  workspaceSlug,
  onSelectFile,
}: FileBrowserDialogProps) => {
  const { t } = useTranslation();

  const [prefix, _setPrefix] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [pageSize, setPageSize] = useState(20);
  const [currentSelectedFile, setCurrentSelectedFile] =
    useState<FileBrowserDialog_BucketObjectFragment | null>(null);

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
          perPage: pageSize,
        },
      });
      setCurrentSelectedFile(null);
    }
  }, [prefix, fetch, workspaceSlug, pageSize, open]);

  const setPrefix = (prefix: string | null) => {
    setPageSize(20);
    _setPrefix(prefix);
  };

  const fetchData = ({ page }: { page: number }) => {
    fetch({
      variables: {
        slug: workspaceSlug,
        prefix,
        page,
        perPage: pageSize,
      },
    });
  };

  const onItemClick = (item: FileBrowserDialog_BucketObjectFragment) => {
    if (item.type === BucketObjectType.Directory) {
      setPrefix(item.key);
    } else {
      setCurrentSelectedFile(item);
    }
  };

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString();
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
        <div className="flex items-center gap-1 text-sm text-gray-500 px-2 min-h-[2rem]">
          <button
            className="flex items-center hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 rounded p-1"
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
                  <span>...</span>
                </>
              )}
              {prefixes.slice(-2).map((part, index) => (
                <div key={index} className="flex items-center">
                  <ChevronRightIcon className="h-3 w-3" />
                  <button
                    className="hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 rounded px-1 py-0.5 truncate"
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
            <DataGrid
              data={filteredItems}
              defaultPageSize={pageSize}
              emptyLabel={
                searchQuery
                  ? t("No files match your search")
                  : t("Empty directory")
              }
              rowClassName={(item) =>
                clsx(
                  "cursor-pointer",
                  currentSelectedFile?.path === item.path
                    ? "bg-blue-100 hover:bg-blue-100 focus:bg-blue-100 font-medium"
                    : "hover:bg-gray-50 focus:bg-gray-50",
                )
              }
              className="border rounded-lg"
              onRowClick={(item) =>
                onItemClick(item as FileBrowserDialog_BucketObjectFragment)
              }
            >
              <BaseColumn id="name" label={t("Name")} minWidth={400}>
                {(item) => (
                  <div className="flex items-center gap-2">
                    {item.type === BucketObjectType.Directory ? (
                      <FolderIcon className="h-5 w-5 text-blue-500 flex-shrink-0" />
                    ) : (
                      (() => {
                        const IconComponent = getFileIcon(item.name);
                        const iconColor = getFileIconColor(item.name);
                        return (
                          <IconComponent
                            className={clsx("h-5 w-5 flex-shrink-0", iconColor)}
                          />
                        );
                      })()
                    )}
                    <span className="truncate">
                      {item.name}
                      {item.type === BucketObjectType.Directory && "/"}
                    </span>
                  </div>
                )}
              </BaseColumn>
              <BaseColumn id="size" label={t("Size")}>
                {(item) =>
                  item.type === BucketObjectType.Directory ? (
                    <span>-</span>
                  ) : (
                    <Filesize size={item.size} />
                  )
                }
              </BaseColumn>
              <BaseColumn id="lastUpdated" label={t("Last Updated")}>
                {(item) => (
                  <span>
                    {item.updatedAt ? formatDate(item.updatedAt) : "-"}
                  </span>
                )}
              </BaseColumn>
            </DataGrid>
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
