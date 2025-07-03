import CodeMirror from "@uiw/react-codemirror";
import {
  DocumentIcon,
  FolderIcon,
  FolderOpenIcon,
} from "@heroicons/react/24/outline";
import clsx from "clsx";
import { useTranslation } from "next-i18next";
import { useCallback, useMemo, useState } from "react";
import { python } from "@codemirror/lang-python";
import { r } from "codemirror-lang-r";
import { gql } from "@apollo/client";
import { FilesEditor_FileFragment } from "./FilesEditor.generated";

const SUPPORTED_LANGUAGES = {
  ".py": "python",
  ".json": "json",
  ".r": "r",
  ".md": "markdown",
} as const;

const getLanguageFromPath = (path: string): string => {
  const extension = path.substring(path.lastIndexOf("."));
  return (
    SUPPORTED_LANGUAGES[extension as keyof typeof SUPPORTED_LANGUAGES] || "text"
  );
};

// TODO
const findAutoSelectedFile = (nodes: FileNode[]): FileNode | null => {
  for (const node of nodes) {
    if (node.type === "file" && node.autoSelect) {
      return node;
    }
    if (node.children) {
      const found = findAutoSelectedFile(node.children);
      if (found) return found;
    }
  }
  return null;
};

// TODO
const getExpandedFolders = (
  nodes: FileNode[],
  targetPath: string,
  currentPath = "",
): Set<string> => {
  const expandedFolders = new Set<string>();

  for (const node of nodes) {
    const nodePath = currentPath ? `${currentPath}/${node.name}` : node.name;

    if (targetPath.startsWith(nodePath + "/") || targetPath === nodePath) {
      if (node.type === "directory") {
        expandedFolders.add(nodePath);
      }

      if (node.children) {
        const childExpanded = getExpandedFolders(
          node.children,
          targetPath,
          nodePath,
        );
        childExpanded.forEach((path) => expandedFolders.add(path));
      }
    }
  }

  return expandedFolders;
};

// TODO
const FileTreeNode = ({
  node,
  level = 0,
  selectedFile,
  onFileSelect,
  expandedFolders,
  onToggleFolder,
}: {
  node: FileNode;
  level?: number;
  selectedFile: string | null;
  onFileSelect: (path: string, content: string) => void;
  expandedFolders: Set<string>;
  onToggleFolder: (path: string) => void;
}) => {
  const isExpanded = expandedFolders.has(node.path);
  const isSelected = selectedFile === node.path;

  if (node.type === "file") {
    return (
      <div
        className={clsx(
          "flex items-center cursor-pointer hover:bg-gray-50 px-2 py-1 text-sm",
          isSelected && "bg-blue-50 text-blue-700",
        )}
        style={{ paddingLeft: `${level * 16 + 8}px` }}
        onClick={() => onFileSelect(node.path, node.content || "")}
      >
        <DocumentIcon className="w-4 h-4 mr-2 text-gray-400" />
        <span>{node.name}</span>
      </div>
    );
  }

  return (
    <div>
      <div
        className="flex items-center cursor-pointer hover:bg-gray-50 px-2 py-1 text-sm"
        style={{ paddingLeft: `${level * 16 + 8}px` }}
        onClick={() => onToggleFolder(node.path)}
      >
        {isExpanded ? (
          <FolderOpenIcon className="w-4 h-4 mr-2 text-gray-400" />
        ) : (
          <FolderIcon className="w-4 h-4 mr-2 text-gray-400" />
        )}
        <span>{node.name}</span>
      </div>
      {isExpanded && node.children && (
        <div>
          {node.children.map((child) => (
            <FileTreeNode
              key={child.path}
              node={child}
              level={level + 1}
              selectedFile={selectedFile}
              onFileSelect={onFileSelect}
              expandedFolders={expandedFolders}
              onToggleFolder={onToggleFolder}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export type FileNode = FilesEditor_FileFragment & {
  children: FileNode[];
};

interface FilesEditorProps {
  name: string;
  files: FileNode[];
}
export const FilesEditor = ({ name, files }: FilesEditorProps) => {
  const { t } = useTranslation();
  const rootFiles = useMemo(() => {
    return files.filter((file) => !file.parentId);
  }, [files]);

  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [selectedContent, setSelectedContent] = useState<string>("");
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(
    new Set(),
  );

  useMemo(() => {
    if (files.length === 0) return;

    const autoSelectFile = findAutoSelectedFile(files);
    if (autoSelectFile && autoSelectFile.content) {
      setSelectedFile(autoSelectFile.path);
      setSelectedContent(autoSelectFile.content);

      const foldersToExpand = getExpandedFolders(files, autoSelectFile.path);
      setExpandedFolders(foldersToExpand);
    }
  }, [files]);

  const handleFileSelect = useCallback((path: string, content: string) => {
    setSelectedFile(path);
    setSelectedContent(content);
  }, []);

  const handleToggleFolder = useCallback((path: string) => {
    setExpandedFolders((prev) => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  }, []);

  const numberOfFiles = files.filter((file) => file.type === "file").length;

  return (
    <div className=" h-[80vh] flex border border-gray-200 rounded-lg overflow-hidden">
      <div className="w-80 bg-gray-50 border-r border-gray-200">
        <div className="p-3 border-b border-gray-200 bg-white">
          <h3 className="text-sm font-medium text-gray-900">
            {t("Files")} - {name}
          </h3>
          <div className="text-xs text-gray-500 mt-1">
            {numberOfFiles} {t("files")}
          </div>
        </div>
        <div className="py-2 overflow-y-auto">
          {rootFiles.map((node) => (
            <FileTreeNode
              key={node.path}
              node={node}
              selectedFile={selectedFile}
              onFileSelect={handleFileSelect}
              expandedFolders={expandedFolders}
              onToggleFolder={handleToggleFolder}
            />
          ))}
        </div>
      </div>

      <div className="flex-1 flex flex-col">
        {selectedFile ? (
          <>
            <div className="p-3 border-b border-gray-200 bg-white">
              <div className="text-sm font-medium text-gray-900">
                {selectedFile}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {getLanguageFromPath(selectedFile)} •{" "}
                {selectedContent.split("\n").length} lines
              </div>
            </div>
            <div className="overflow-y-auto border-b">
              <CodeMirror
                value={selectedContent}
                readOnly={true}
                extensions={[python(), r()]}
              />
            </div>
          </>
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <DocumentIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <div className="text-gray-500 text-lg mb-2">
                {t("Select a file to view")}
              </div>
              <div className="text-gray-400 text-sm">
                {t("Choose a file from the sidebar to view its contents")}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

FilesEditor.fragment = {
  files: gql`
    fragment FilesEditor_file on FileNode {
      id
      name
      path
      type
      content
      parentId
      autoSelect
    }
  `,
};
