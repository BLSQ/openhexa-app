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

const getLanguageFromPath = (path: string): string => {
  const SUPPORTED_LANGUAGES = {
    ".py": "python",
    ".json": "json",
    ".md": "markdown",
  } as const;

  const extension = path.substring(path.lastIndexOf("."));
  return (
    SUPPORTED_LANGUAGES[extension as keyof typeof SUPPORTED_LANGUAGES] || "text"
  );
};

interface PipelineVersionFile {
  name: string;
  path: string;
  type: "file" | "directory";
  content?: string;
}

interface FileNode {
  name: string;
  path: string;
  type: "file" | "folder";
  children?: FileNode[];
  content?: string;
}

interface FilesEditorProps {
  name: string;
  files: any;
}

const buildFileTree = (files: PipelineVersionFile[]): FileNode[] => {
  const root: FileNode[] = [];
  const allNodes: { [path: string]: FileNode } = {};

  // Create all nodes
  files.forEach((file) => {
    const parts = file.path.split("/").filter(Boolean);
    let currentPath = "";

    parts.forEach((part, index) => {
      const parentPath = currentPath;
      currentPath = currentPath ? `${currentPath}/${part}` : part;

      if (!allNodes[currentPath]) {
        const isFile = index === parts.length - 1 && file.type === "file";
        allNodes[currentPath] = {
          name: part,
          path: currentPath,
          type: isFile ? "file" : "folder",
          children: isFile ? undefined : [],
          content: isFile && file.content ? atob(file.content) : undefined,
        };
      }
    });
  });

  // Build tree structure
  Object.values(allNodes).forEach((node) => {
    const parentPath = node.path.substring(0, node.path.lastIndexOf("/"));

    if (parentPath && allNodes[parentPath]) {
      allNodes[parentPath].children!.push(node);
    } else {
      root.push(node);
    }
  });

  // Sort folders first, then files, both alphabetically
  const sortNodes = (nodes: FileNode[]) => {
    nodes.sort((a, b) => {
      if (a.type !== b.type) {
        return a.type === "folder" ? -1 : 1;
      }
      return a.name.localeCompare(b.name);
    });

    nodes.forEach((node) => {
      if (node.children) {
        sortNodes(node.children);
      }
    });
  };

  sortNodes(root);
  return root;
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

  const fileTree = useMemo(() => buildFileTree(files), [files]);

  // Auto-select the first Python file or main.py if available
  useMemo(() => {
    if (files.length === 0) return;

    const mainFile = files.find(
      (file: PipelineVersionFile) =>
        file.type === "file" &&
        (file.path.endsWith("main.py") || file.path.endsWith("__main__.py")),
    );
    const firstPythonFile = files.find(
      (file: PipelineVersionFile) =>
        file.type === "file" && file.path.endsWith(".py"),
    );
    const firstFile = files.find(
      (file: PipelineVersionFile) => file.type === "file",
    );

    const autoSelectFile = mainFile || firstPythonFile || firstFile;
    if (autoSelectFile && autoSelectFile.content) {
      setSelectedFile(autoSelectFile.path);
      setSelectedContent(atob(autoSelectFile.content));

      // Auto-expand folders leading to the selected file
      const pathParts = autoSelectFile.path.split("/");
      const foldersToExpand = new Set<string>();
      let currentPath = "";
      for (let i = 0; i < pathParts.length - 1; i++) {
        currentPath = currentPath
          ? `${currentPath}/${pathParts[i]}`
          : pathParts[i];
        foldersToExpand.add(currentPath);
      }
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

  return (
    <div className="flex h-screen border border-gray-200 rounded-lg overflow-hidden">
      <div className="w-80 bg-gray-50 border-r border-gray-200 overflow-y-auto">
        <div className="p-3 border-b border-gray-200 bg-white">
          <h3 className="text-sm font-medium text-gray-900">
            {t("Files")} - {name}
          </h3>
          <div className="text-xs text-gray-500 mt-1">
            {files.filter((f: PipelineVersionFile) => f.type === "file").length}{" "}
            {t("files")}
          </div>
        </div>
        <div className="py-2 h-screen">
          {fileTree.map((node) => (
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
            <div className="overflow-y-auto h-screen">
              <CodeMirror
                value={selectedContent}
                readOnly={false}
                height="100vh"
                extensions={[python()]}
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
