import CodeMirror from "@uiw/react-codemirror";
import {
  DocumentIcon,
  FolderIcon,
  FolderOpenIcon,
} from "@heroicons/react/24/outline";
import clsx from "clsx";
import { useTranslation } from "next-i18next";
import { useMemo, useState } from "react";
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

const buildTreeFromFlatData = (
  flatNodes: FilesEditor_FileFragment[],
): FileNode[] => {
  const nodeMap = new Map<string, FileNode>();

  flatNodes.forEach((flatNode) => {
    nodeMap.set(flatNode.id, {
      ...flatNode,
      children: [],
    });
  });

  flatNodes.forEach((flatNode) => {
    if (flatNode.parentId) {
      const parentNode = nodeMap.get(flatNode.parentId);
      parentNode?.children!.push(nodeMap.get(flatNode.id)!);
    }
  });

  nodeMap.forEach((node) => {
    node.children.sort((a, b) => a.name.localeCompare(b.name));
  });

  return Array.from(nodeMap.values());
};

// TODO : line count
// TODO : design hover etc

const FileTreeNode = ({
  node,
  level = 0,
  selectedFile,
  setSelectedFile,
}: {
  node: FileNode;
  level?: number;
  selectedFile: FileNode | null;
  setSelectedFile: (file: FileNode) => void;
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const isSelected = selectedFile?.id === node.id;

  if (node.type === "file") {
    return (
      <div
        className={clsx(
          "flex items-center cursor-pointer hover:bg-gray-50 px-2 py-1 text-sm",
          isSelected && "bg-blue-50 text-blue-700",
        )}
        style={{ paddingLeft: `${level * 16 + 8}px` }}
        onClick={() => setSelectedFile(node)}
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
        onClick={() => setIsExpanded(!isExpanded)}
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
              setSelectedFile={setSelectedFile}
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
  files: FilesEditor_FileFragment[];
}
export const FilesEditor = ({ name, files: flatFiles }: FilesEditorProps) => {
  const { t } = useTranslation();
  const files = useMemo(() => {
    return buildTreeFromFlatData(flatFiles);
  }, [flatFiles]);
  const rootFiles = useMemo(() => {
    return files.filter((file) => !file.parentId);
  }, [files]);

  const [selectedFile, setSelectedFile] = useState<FileNode | null>(
    files.filter((file) => file.autoSelect)[0] || null,
  );

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
              setSelectedFile={setSelectedFile}
            />
          ))}
        </div>
      </div>

      <div className="flex-1 flex flex-col">
        {selectedFile ? (
          <>
            <div className="p-3 border-b border-gray-200 bg-white">
              <div className="text-sm font-medium text-gray-900">
                {selectedFile.name}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {getLanguageFromPath(selectedFile.path)} •
                {selectedFile.content!.split("\n").length} lines
              </div>
            </div>
            <div className="overflow-y-auto border-b">
              <CodeMirror
                value={selectedFile.content!}
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
