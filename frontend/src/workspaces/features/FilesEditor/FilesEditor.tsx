import { json } from "@codemirror/lang-json";
import { python } from "@codemirror/lang-python";
import { unifiedMergeView } from "@codemirror/merge";
import { EditorView } from "@codemirror/view";
import CodeMirror from "@uiw/react-codemirror";
import {
  ChevronDownIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  DocumentIcon,
  FolderIcon,
} from "@heroicons/react/24/outline";
import { gql } from "@apollo/client";
import clsx from "clsx";
import useNavigationWarning from "core/hooks/useNavigationWarning";
import { FileType } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useEffect, useMemo, useState } from "react";
import { r } from "codemirror-lang-r";
import useFilesEditorPanelOpen from "workspaces/hooks/useFilesEditorPanelOpen";
import { FilesEditor_FileFragment } from "./FilesEditor.generated";

export type ProposedFile = { name: string; content: string };

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
  const [isExpanded, setIsExpanded] = useState(
    node.id.startsWith("proposed-dir-"),
  );
  const isSelected = selectedFile?.id === node.id;

  const proposedContent =
    node.type === "file"
      ? (proposedByKey.get(node.path) ?? proposedByKey.get(node.name))
      : undefined;
  const isProposed =
    proposedContent !== undefined && proposedContent !== (node.content ?? "");
  const isModified = !isProposed && modifiedFiles.has(node.id);

  if (node.type === "file") {
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
      {isExpanded && node.children && (
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

export type FileNode = FilesEditor_FileFragment & {
  children: FileNode[];
};

export interface SaveResult {
  success: boolean;
  error?: string;
}

interface FilesEditorProps {
  name: string;
  files: FilesEditor_FileFragment[];
  isEditable?: boolean;
  proposedFiles?: ProposedFile[];
  onSave?: (
    modifiedFiles: Map<string, string>,
    allFiles: FilesEditor_FileFragment[],
  ) => Promise<SaveResult>;
}
export const FilesEditor = ({
  name,
  files: flatFiles,
  isEditable = false,
  proposedFiles,
  onSave,
}: FilesEditorProps) => {
  const { t } = useTranslation();
  // Synthetic file and folder nodes for files proposed by the agent that don't exist
  // yet in the current version. Paths are parsed so nested files (e.g. tests/__init__.py)
  // are placed under the correct folder in the tree rather than shown as flat names.
  const virtualFiles = useMemo<FilesEditor_FileFragment[]>(() => {
    if (!proposedFiles) return [];

    const result: FilesEditor_FileFragment[] = [];
    const virtualFolderIds = new Map<string, string>(); // dirPath -> id

    for (const pf of proposedFiles) {
      if (flatFiles.find((f) => f.path === pf.name || f.name === pf.name)) continue;

      const parts = pf.name.split("/");
      const fileName = parts[parts.length - 1];
      let parentId: string | null = null;

      for (let i = 0; i < parts.length - 1; i++) {
        const dirPath = parts.slice(0, i + 1).join("/");
        const dirName = parts[i];

        const existing = flatFiles.find(
          (f) => f.type === FileType.Directory && f.path === dirPath,
        );

        if (existing) {
          parentId = existing.id;
        } else if (virtualFolderIds.has(dirPath)) {
          parentId = virtualFolderIds.get(dirPath)!;
        } else {
          const folderId = `proposed-dir-${dirPath}`;
          result.push({
            __typename: "FileNode" as const,
            id: folderId,
            name: dirName,
            path: dirPath,
            type: FileType.Directory,
            content: null,
            parentId,
            autoSelect: false,
            language: null,
            lineCount: null,
          });
          virtualFolderIds.set(dirPath, folderId);
          parentId = folderId;
        }
      }

      result.push({
        __typename: "FileNode" as const,
        id: `proposed-${pf.name}`,
        name: fileName,
        path: pf.name,
        type: FileType.File,
        content: "",
        parentId,
        autoSelect: false,
        language: null,
        lineCount: null,
      });
    }

    return result;
  }, [proposedFiles, flatFiles]);

  const augmentedFlatFiles = useMemo(
    () => [...flatFiles, ...virtualFiles],
    [flatFiles, virtualFiles],
  );

  const files = useMemo(() => {
    return buildTreeFromFlatData(augmentedFlatFiles);
  }, [augmentedFlatFiles]);
  const rootFiles = useMemo(() => {
    return files.filter((file) => !file.parentId);
  }, [files]);

  const [selectedFile, setSelectedFile] = useState<FileNode | null>(
    files.filter((file) => file.autoSelect)[0] || null,
  );

  useEffect(() => {
    if (files.length === 0) {
      setSelectedFile(null);
      return;
    }
    if (!selectedFile) {
      const autoSelected = files.find((file) => file.autoSelect);
      setSelectedFile(autoSelected ?? null);
      return;
    }
    const matchingFile = files.find((f) => f.id === selectedFile.id);
    if (!matchingFile) {
      const autoSelected = files.find((file) => file.autoSelect);
      setSelectedFile(autoSelected ?? null);
    } else if (matchingFile !== selectedFile) {
      setSelectedFile(matchingFile);
    }
  }, [files, selectedFile]);

  const proposedByKey = useMemo(() => {
    const map = new Map<string, string>();
    for (const f of proposedFiles ?? []) {
      map.set(f.name, f.content);
    }
    return map;
  }, [proposedFiles]);

  useEffect(() => {
    if (!proposedFiles || proposedFiles.length === 0) return;
    setModifiedFiles((prev) => {
      const next = new Map(prev);
      for (const proposed of proposedFiles) {
        const existing = flatFiles.find(
          (f) => f.path === proposed.name || f.name === proposed.name,
        );
        if (existing) {
          if (proposed.content !== (existing.content ?? "") && !next.has(existing.id)) {
            next.set(existing.id, proposed.content);
          }
        } else {
          // New file proposed by the agent — stored under its virtual id
          const virtualId = `proposed-${proposed.name}`;
          if (!next.has(virtualId)) {
            next.set(virtualId, proposed.content);
          }
        }
      }
      return next;
    });
  }, [proposedFiles, flatFiles]);

  const [isPanelOpen, setIsPanelOpen] = useFilesEditorPanelOpen();
  const [isClient, setIsClient] = useState(false);

  const [modifiedFiles, setModifiedFiles] = useState<Map<string, string>>(
    new Map(),
  );
  const [currentFileContent, setCurrentFileContent] = useState<string>("");
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  useEffect(() => {
    setModifiedFiles(new Map());
  }, [flatFiles]);

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    if (selectedFile) {
      const modifiedContent = modifiedFiles.get(selectedFile.id);
      setCurrentFileContent(modifiedContent ?? selectedFile.content ?? "");
    }
  }, [selectedFile, modifiedFiles]);

  useNavigationWarning({
    when: () => isEditable && modifiedFiles.size > 0,
  });

  const handleContentChange = (content: string) => {
    if (selectedFile && isEditable) {
      setCurrentFileContent(content);

      if (content !== (selectedFile.content || "")) {
        setModifiedFiles((prev) => new Map(prev).set(selectedFile.id, content));
      } else {
        setModifiedFiles((prev) => {
          const newMap = new Map(prev);
          newMap.delete(selectedFile.id);
          return newMap;
        });
      }
    }
  };

  const handleSave = async () => {
    if (!selectedFile || !isEditable || !onSave || modifiedFiles.size === 0)
      return;

    setIsSaving(true);
    setSaveError(null);

    try {
      const result = await onSave(modifiedFiles, augmentedFlatFiles);

      if (!result.success) {
        setSaveError(result.error || "Save failed");
      }
    } catch (error) {
      console.error("Save failed:", error);
      setSaveError(error instanceof Error ? error.message : "Failed to save");
    } finally {
      setIsSaving(false);
    }
  };

  const currentFileIsModified = selectedFile
    ? modifiedFiles.has(selectedFile.id)
    : false;

  const numberOfFiles = files.filter(
    (file) => file.type === FileType.File,
  ).length;

  return (
    <div className="relative flex border border-gray-200 rounded-lg overflow-hidden min-h-[60vh] h-full max-w-full">
      {isPanelOpen && (
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
            onClick={() => setIsPanelOpen(false)}
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
      )}

      {!isPanelOpen && (
        <div
          className="group absolute left-0 top-0 z-30 h-full w-3 cursor-pointer"
          onClick={() => setIsPanelOpen(true)}
        >
          <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center">
            <div className="pointer-events-auto invisible rounded-r-md bg-gray-400 p-0.5 pl-0.5 align-middle text-white group-hover:visible">
              <ChevronRightIcon className="h-5 w-5" />
            </div>
          </div>
        </div>
      )}

      <div className="flex-1 flex flex-col transition-all duration-300 ease-in-out">
        {selectedFile ? (
          <>
            <div className="p-3 border-b border-gray-200 bg-white flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-gray-900 flex items-center gap-2">
                  {selectedFile.name}
                  {currentFileIsModified && (
                    <span
                      className="inline-block w-2 h-2 bg-blue-500 rounded-full"
                      title={t("Modified")}
                    />
                  )}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {selectedFile.language}
                  {" • "}
                  {selectedFile.lineCount}
                  {` ${(selectedFile.lineCount ?? 0) > 1 ? t("lines") : t("line")}`}
                  {currentFileIsModified && ` • ${t("Modified")}`}
                  {saveError && (
                    <>
                      {" • "}
                      <span className="text-xs text-red-600 mt-1">
                        {`${t("Save error")}: ${saveError}`}
                      </span>
                    </>
                  )}
                </div>
              </div>
              {isEditable && currentFileIsModified && onSave && (
                <button
                  onClick={handleSave}
                  disabled={isSaving}
                  className={clsx(
                    "px-3 py-1 text-xs font-medium rounded-md transition-colors",
                    isSaving
                      ? "bg-gray-200 text-gray-500 cursor-not-allowed"
                      : "bg-blue-600 text-white hover:bg-blue-700",
                  )}
                >
                  {isSaving ? t("Saving...") : t("Save")}
                </button>
              )}
            </div>
            <div className="flex-1 relative overflow-hidden h-full">
              {isClient ? (
                <div className="absolute inset-0">
                  <CodeMirror
                    key={selectedFile.id}
                    value={currentFileContent}
                    readOnly={!isEditable}
                    onChange={handleContentChange}
                    extensions={[
                      python(),
                      r(),
                      json(),
                      ...(proposedByKey.has(selectedFile.path) ||
                      proposedByKey.has(selectedFile.name)
                        ? [
                            unifiedMergeView({
                              original: selectedFile.content ?? "",
                              mergeControls: false,
                            }),
                            EditorView.theme({
                              ".cm-changedText": {
                                textDecoration: "none",
                                background: "rgba(0, 0, 0, 0.15)",
                              },
                              ".cm-insertedLine .cm-changedText": {
                                textDecoration: "none",
                                background: "rgba(0, 160, 0, 0.25)",
                              },
                            }),
                          ]
                        : []),
                    ]}
                    height="100%"
                    style={{ width: "100%", height: "100%" }}
                  />
                </div>
              ) : (
                <div className="flex items-center justify-center h-full bg-gray-50">
                  <div className="text-gray-500">{t("Loading editor...")}</div>
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="flex items-center justify-center flex-1 min-h-[300px]">
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
      language
      lineCount
    }
  `,
};

export default FilesEditor;
