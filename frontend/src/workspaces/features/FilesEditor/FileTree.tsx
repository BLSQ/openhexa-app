import {
  ArrowUturnLeftIcon,
  ChevronDownIcon,
  ChevronRightIcon,
  DocumentIcon,
  FolderIcon,
  TrashIcon,
} from "@heroicons/react/24/outline";
import clsx from "clsx";
import { FileType } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useState } from "react";
import { FileNode } from "./types";

const FileTreeNode = ({
  node,
  level = 0,
  selectedFile,
  setSelectedFile,
  modifiedFiles,
  proposedByKey,
  deletedFilePaths,
  deletedFolderPaths,
  canDelete,
  onDelete,
  onRestore,
}: {
  node: FileNode;
  level?: number;
  selectedFile: FileNode | null;
  setSelectedFile: (file: FileNode | null) => void;
  modifiedFiles: Map<string, string>;
  proposedByKey: Map<string, string>;
  deletedFilePaths: Set<string>;
  deletedFolderPaths: Set<string>;
  canDelete: boolean;
  onDelete: (node: FileNode) => void;
  onRestore: (node: FileNode) => void;
}) => {
  const { t } = useTranslation();
  const [isExpanded, setIsExpanded] = useState(node.isProposed);
  const isSelected = selectedFile?.id === node.id;
  const isDeleted =
    node.type === FileType.File && deletedFilePaths.has(node.path);
  const isFolderDeleted =
    node.type === FileType.Directory && deletedFolderPaths.has(node.path);
  const isProposed =
    !isDeleted && node.type === FileType.File && proposedByKey.has(node.path);
  const isModified = !isProposed && !isDeleted && modifiedFiles.has(node.id);
  const markedForDeletion = isDeleted || isFolderDeleted;

  const deleteAction = canDelete ? (
    <button
      type="button"
      className={clsx(
        "ml-auto shrink-0 rounded p-0.5 transition-opacity hover:bg-gray-300 focus:opacity-100 group-hover:opacity-100",
        markedForDeletion
          ? "text-red-500 opacity-100 hover:text-red-700"
          : "text-gray-400 opacity-0 hover:text-gray-700",
      )}
      aria-label={
        markedForDeletion
          ? t("Restore {{name}}", { name: node.name })
          : t("Delete {{name}}", { name: node.name })
      }
      title={markedForDeletion ? t("Undo delete") : t("Delete")}
      onClick={(e) => {
        e.stopPropagation();
        if (markedForDeletion) {
          onRestore(node);
        } else {
          onDelete(node);
        }
      }}
    >
      {markedForDeletion ? (
        <ArrowUturnLeftIcon className="h-3.5 w-3.5" />
      ) : (
        <TrashIcon className="h-3.5 w-3.5" />
      )}
    </button>
  ) : null;

  if (node.type === FileType.File) {
    return (
      <div
        className={clsx(
          "group flex items-center cursor-pointer px-2 py-1 text-sm",
          isSelected
            ? isDeleted
              ? "bg-red-50 text-red-700"
              : "bg-blue-50 text-blue-700"
            : "hover:bg-gray-200",
        )}
        style={{ paddingLeft: `${level * 24 + 8}px` }}
        onClick={() => setSelectedFile(isSelected ? null : node)}
      >
        <DocumentIcon
          className={clsx(
            "w-4 h-4 mr-2 shrink-0",
            isDeleted ? "text-red-400" : "text-gray-400",
          )}
        />
        <span className="flex min-w-0 items-center gap-2">
          <span
            className={clsx(
              "truncate",
              isDeleted && "line-through text-red-500",
            )}
            title={node.name}
          >
            {node.name}
          </span>
          <span
            className={clsx(
              "inline-block w-1.5 h-1.5 shrink-0 rounded-full",
              isDeleted
                ? "visible bg-red-500"
                : isProposed
                  ? "visible bg-amber-400"
                  : isModified
                    ? "visible bg-blue-500"
                    : "invisible bg-blue-500",
            )}
          />
        </span>
        {deleteAction}
      </div>
    );
  }

  return (
    <div>
      <div
        className="group flex items-center cursor-pointer hover:bg-gray-200 px-2 py-1 text-sm"
        style={{ paddingLeft: `${level * 24 + 8}px` }}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        {isExpanded ? (
          <ChevronDownIcon
            className={clsx(
              "w-4 h-4 mr-2 shrink-0",
              isFolderDeleted ? "text-red-400" : "text-gray-400",
            )}
          />
        ) : (
          <ChevronRightIcon
            className={clsx(
              "w-4 h-4 mr-2 shrink-0",
              isFolderDeleted ? "text-red-400" : "text-gray-400",
            )}
          />
        )}
        <FolderIcon
          className={clsx(
            "w-4 h-4 mr-2 shrink-0",
            isFolderDeleted ? "text-red-400" : "text-gray-400",
          )}
        />
        <span
          className={clsx(
            "truncate",
            isFolderDeleted && "line-through text-red-500",
          )}
          title={node.name}
        >
          {node.name}
        </span>
        {deleteAction}
      </div>
      {isExpanded && (
        <div>
          {node.children.map((child) => (
            <FileTreeNode
              key={child.path}
              node={child}
              level={level + 1}
              selectedFile={selectedFile}
              setSelectedFile={setSelectedFile}
              modifiedFiles={modifiedFiles}
              proposedByKey={proposedByKey}
              deletedFilePaths={deletedFilePaths}
              deletedFolderPaths={deletedFolderPaths}
              canDelete={canDelete}
              onDelete={onDelete}
              onRestore={onRestore}
            />
          ))}
        </div>
      )}
    </div>
  );
};

type FileTreeProps = {
  name: string;
  numberOfFiles: number;
  rootFiles: FileNode[];
  selectedFile: FileNode | null;
  setSelectedFile: (file: FileNode | null) => void;
  modifiedFiles: Map<string, string>;
  proposedByKey: Map<string, string>;
  deletedFilePaths: Set<string>;
  deletedFolderPaths: Set<string>;
  canDelete: boolean;
  onDelete: (node: FileNode) => void;
  onRestore: (node: FileNode) => void;
};

const FileTree = ({
  name,
  numberOfFiles,
  rootFiles,
  selectedFile,
  setSelectedFile,
  modifiedFiles,
  proposedByKey,
  deletedFilePaths,
  deletedFolderPaths,
  canDelete,
  onDelete,
  onRestore,
}: FileTreeProps) => {
  const { t } = useTranslation();

  return (
    <div
      data-testid="files-panel"
      className="h-full w-full bg-gray-50 flex flex-col"
    >
      <div className="p-3 border-b border-gray-200 bg-white">
        <h3 className="truncate text-sm font-medium text-gray-900" title={name}>
          {t("Files")} - {name}
        </h3>
        <div className="text-xs text-gray-500 mt-1">
          {numberOfFiles} {t("files")}
        </div>
      </div>
      <div className="py-2 overflow-y-auto flex-1">
        {rootFiles.map((node) => (
          <FileTreeNode
            key={node.path}
            node={node}
            selectedFile={selectedFile}
            setSelectedFile={setSelectedFile}
            modifiedFiles={modifiedFiles}
            proposedByKey={proposedByKey}
            deletedFilePaths={deletedFilePaths}
            deletedFolderPaths={deletedFolderPaths}
            canDelete={canDelete}
            onDelete={onDelete}
            onRestore={onRestore}
          />
        ))}
      </div>
    </div>
  );
};

export default FileTree;
