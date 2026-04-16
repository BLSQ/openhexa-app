import {
  ChevronDownIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  DocumentIcon,
  FolderIcon,
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
}: {
  node: FileNode;
  level?: number;
  selectedFile: FileNode | null;
  setSelectedFile: (file: FileNode | null) => void;
  modifiedFiles: Map<string, string>;
  proposedByKey: Map<string, string>;
}) => {
  const [isExpanded, setIsExpanded] = useState(node.isProposed);
  const isSelected = selectedFile?.id === node.id;
  const isProposed = node.type === FileType.File && proposedByKey.has(node.path);
  const isModified = !isProposed && modifiedFiles.has(node.id);

  if (node.type === FileType.File) {
    return (
      <div
        className={clsx(
          "flex items-center cursor-pointer px-2 py-1 text-sm",
          isSelected ? "bg-blue-50 text-blue-700" : "hover:bg-gray-200",
        )}
        style={{ paddingLeft: `${level * 24 + 8}px` }}
        onClick={() => setSelectedFile(isSelected ? null : node)}
      >
        <DocumentIcon className="w-4 h-4 mr-2 text-gray-400" />
        <span className="flex items-center gap-2">
          {node.name}
          <span
            className={clsx(
              "inline-block w-1.5 h-1.5 rounded-full",
              isProposed
                ? "visible bg-amber-400"
                : isModified
                  ? "visible bg-blue-500"
                  : "invisible bg-blue-500",
            )}
          />
        </span>
      </div>
    );
  }

  return (
    <div>
      <div
        className="flex items-center cursor-pointer hover:bg-gray-200 px-2 py-1 text-sm"
        style={{ paddingLeft: `${level * 24 + 8}px` }}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        {isExpanded ? (
          <ChevronDownIcon className="w-4 h-4 mr-2 text-gray-400" />
        ) : (
          <ChevronRightIcon className="w-4 h-4 mr-2 text-gray-400" />
        )}
        <FolderIcon className="w-4 h-4 mr-2 text-gray-400" />
        <span>{node.name}</span>
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
  onClose: () => void;
};

const FileTree = ({
  name,
  numberOfFiles,
  rootFiles,
  selectedFile,
  setSelectedFile,
  modifiedFiles,
  proposedByKey,
  onClose,
}: FileTreeProps) => {
  const { t } = useTranslation();

  return (
    <div
      data-testid="files-panel"
      className="relative bg-gray-50 border-r border-gray-200 flex flex-col transition-all duration-300 ease-in-out"
    >
      <div className="p-3 border-b border-gray-200 bg-white">
        <h3 className="text-sm font-medium text-gray-900">
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
          />
        ))}
      </div>
      <button
        onClick={onClose}
        className="group absolute inset-y-0 right-0 border-r-2 border-transparent after:absolute after:inset-y-0 after:-left-1.5 after:block after:w-3 after:content-[''] hover:border-r-gray-300"
        aria-label="Toggle file panel"
      >
        <div className="relative h-full">
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center">
            <div className="pointer-events-auto invisible rounded-l-md bg-gray-400 p-0.5 pr-0.5 align-middle text-white group-hover:visible">
              <ChevronLeftIcon className="h-5 w-5" />
            </div>
          </div>
        </div>
      </button>
    </div>
  );
};

export default FileTree;
