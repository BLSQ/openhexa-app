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

const getLanguageFromPath = (path: string): string => {
  const SUPPORTED_LANGUAGES = {
    ".py": "python",
    ".json": "json",
    ".r": "r",
    ".md": "markdown",
  } as const;

  const extension = path.substring(path.lastIndexOf("."));
  return (
    SUPPORTED_LANGUAGES[extension as keyof typeof SUPPORTED_LANGUAGES] || "text"
  );
};

// TODO : clean this file
// TODO : clean backend resolver
// TODO : update backend test

interface FlatFileNode {
  id: string;
  name: string;
  path: string;
  type: "file" | "directory";
  content?: string | null;
  parentId?: string | null;
  autoSelect: boolean;
}

interface FileNode {
  name: string;
  path: string;
  type: "file" | "directory";
  children?: FileNode[];
  content?: string | null;
  autoSelect: boolean;
}

interface FilesEditorProps {
  name: string;
  files: FlatFileNode[];
}

// Reconstruct hierarchical tree from flattened data
const buildTreeFromFlatData = (flatNodes: FlatFileNode[]): FileNode[] => {
  const nodeMap = new Map<string, FileNode>();

  // Create all nodes first
  flatNodes.forEach((flatNode) => {
    nodeMap.set(flatNode.id, {
      name: flatNode.name,
      path: flatNode.path,
      type: flatNode.type,
      content: flatNode.content,
      autoSelect: flatNode.autoSelect,
      children: flatNode.type === "directory" ? [] : undefined,
    });
  });

  // Build tree structure
  const rootNodes: FileNode[] = [];

  flatNodes.forEach((flatNode) => {
    const node = nodeMap.get(flatNode.id)!;

    if (!flatNode.parentId) {
      // Root node
      rootNodes.push(node);
    } else {
      // Child node - add to parent
      const parentNode = nodeMap.get(flatNode.parentId);
      if (parentNode && parentNode.children) {
        parentNode.children.push(node);
      }
    }
  });

  // Sort nodes: directories first, then files, both alphabetically
  const sortNodes = (nodes: FileNode[]): void => {
    nodes.sort((a, b) => {
      if (a.type !== b.type) {
        return a.type === "directory" ? -1 : 1;
      }
      return a.name.toLowerCase().localeCompare(b.name.toLowerCase());
    });

    nodes.forEach((node) => {
      if (node.children) {
        sortNodes(node.children);
      }
    });
  };

  sortNodes(rootNodes);
  return rootNodes;
};

// Find auto-selected file in the tree structure
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

// Find all folders that need to be expanded to show a file
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

// Count total files in the tree
const countFiles = (nodes: FileNode[]): number => {
  let count = 0;
  for (const node of nodes) {
    if (node.type === "file") {
      count++;
    } else if (node.children) {
      count += countFiles(node.children);
    }
  }
  return count;
};

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

export const FilesEditor = ({ name, files }: FilesEditorProps) => {
  const { t } = useTranslation();
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [selectedContent, setSelectedContent] = useState<string>("");
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(
    new Set(),
  );

  // Reconstruct tree from flattened data
  const treeFiles = useMemo(() => {
    return buildTreeFromFlatData(files);
  }, [files]);

  // Auto-select file based on backend auto-selection
  useMemo(() => {
    if (treeFiles.length === 0) return;

    const autoSelectFile = findAutoSelectedFile(treeFiles);
    if (autoSelectFile && autoSelectFile.content) {
      setSelectedFile(autoSelectFile.path);
      setSelectedContent(autoSelectFile.content);

      // Auto-expand folders leading to the selected file
      const foldersToExpand = getExpandedFolders(
        treeFiles,
        autoSelectFile.path,
      );
      setExpandedFolders(foldersToExpand);
    }
  }, [treeFiles]);

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

  return (
    <div className=" h-[80vh] flex border border-gray-200 rounded-lg overflow-hidden">
      <div className="w-80 bg-gray-50 border-r border-gray-200">
        <div className="p-3 border-b border-gray-200 bg-white">
          <h3 className="text-sm font-medium text-gray-900">
            {t("Files")} - {name}
          </h3>
          <div className="text-xs text-gray-500 mt-1">
            {countFiles(treeFiles)} {t("files")}
          </div>
        </div>
        <div className="py-2 overflow-y-auto">
          {treeFiles.map((node) => (
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
            <div className="overflow-y-auto">
              <CodeMirror
                value={selectedContent}
                readOnly={false}
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
