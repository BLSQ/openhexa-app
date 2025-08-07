import CodeMirror from "@uiw/react-codemirror";
import {
  ChevronDownIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  DocumentIcon,
  FolderIcon,
} from "@heroicons/react/24/outline";
import clsx from "clsx";
import { getCookie, hasCookie, setCookie } from "cookies-next";
import { CustomApolloClient } from "core/helpers/apollo";
import { GetServerSidePropsContext } from "next";
import { useTranslation } from "next-i18next";
import { useEffect, useMemo, useState } from "react";
import { python } from "@codemirror/lang-python";
import { json } from "@codemirror/lang-json";
import { r } from "codemirror-lang-r";
import { gql } from "@apollo/client";
import { FilesEditor_FileFragment } from "./FilesEditor.generated";
import { useUploadPipelineMutation } from "workspaces/graphql/mutations.generated";
import JSZip from "jszip";
import { FileType } from "graphql/types";

// TODO : flicker on save
// TODO : on route out
// TODO : move logic out
// TODO : add unit tests


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
}: {
  node: FileNode;
  level?: number;
  selectedFile: FileNode | null;
  setSelectedFile: (file: FileNode | null) => void;
  modifiedFiles: Map<string, string>;
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const isSelected = selectedFile?.id === node.id;
  const isModified = modifiedFiles.has(node.id);

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
          {isModified && (
            <span className="inline-block w-1.5 h-1.5 bg-blue-500 rounded-full" />
          )}
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

export let cookieFilesEditorPanelOpenState = true;

function getDefaultFilesEditorPanelOpen() {
  if (typeof window === "undefined") {
    return cookieFilesEditorPanelOpenState;
  } else if (hasCookie("files-editor-panel-open")) {
    return getCookie("files-editor-panel-open") === "true";
  } else {
    return true;
  }
}

interface FilesEditorProps {
  name: string;
  files: FilesEditor_FileFragment[];
  isEditable?: boolean;
  workspaceSlug?: string;
  pipelineCode?: string;
}
export const FilesEditor = ({ 
  name, 
  files: flatFiles, 
  isEditable = false, 
  workspaceSlug, 
  pipelineCode,
}: FilesEditorProps) => {
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

  const [isPanelOpen, setIsPanelOpen] = useState(getDefaultFilesEditorPanelOpen());
  const [isClient, setIsClient] = useState(false);
  
  const [modifiedFiles, setModifiedFiles] = useState<Map<string, string>>(new Map());
  const [currentFileContent, setCurrentFileContent] = useState<string>("");
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [uploadPipeline] = useUploadPipelineMutation({refetchQueries : ["WorkspacePipelineCodePage", "PipelineVersionPicker"]});

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    if (selectedFile) {
      const modifiedContent = modifiedFiles.get(selectedFile.id);
      setCurrentFileContent(modifiedContent || selectedFile.content || "");
    }
  }, [selectedFile, modifiedFiles]);

  const handlePanelToggle = (newState: boolean) => {
    setIsPanelOpen(newState);
    setCookie("files-editor-panel-open", newState);
  };

  const handleContentChange = (content: string) => {
    if (selectedFile && isEditable) {
      setCurrentFileContent(content);
      
      if (content !== (selectedFile.content || "")) {
        setModifiedFiles(prev => new Map(prev).set(selectedFile.id, content));
      } else {
        setModifiedFiles(prev => {
          const newMap = new Map(prev);
          newMap.delete(selectedFile.id);
          return newMap;
        });
      }
    }
  };

  const createZipFromFiles = async (files: FilesEditor_FileFragment[], modifications: Map<string, string>): Promise<string> => {
    const zip = new JSZip();
    
    files.forEach((file) => {
      if (file.type === FileType.File) {
        const content = modifications.get(file.id) || file.content || "";
        zip.file(file.path, content);
      }
    });

    const zipBlob = await zip.generateAsync({ type: "blob" });
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(zipBlob);
    });
  };

  const handleSave = async () => {
    if (!selectedFile || !isEditable || !workspaceSlug || !pipelineCode) return;
    
    setIsSaving(true);
    setSaveError(null);
    
    try {
      const zipBase64 = await createZipFromFiles(flatFiles, modifiedFiles);
      
      const result = await uploadPipeline({
        variables: {
          input: {
            workspaceSlug: workspaceSlug,
            pipelineCode: pipelineCode,
            zipfile: zipBase64,
            parameters: [],
          }
        }
      });

      if (result.data?.uploadPipeline.success) {
        setModifiedFiles(new Map());
      } else {
        const errors = result.data?.uploadPipeline.errors || ["Unknown error"];
        setSaveError(errors.join(", "));
        console.error("Save failed with errors:", errors);
      }
    } catch (error) {
      console.error("Save failed:", error);
      setSaveError(error instanceof Error ? error.message : "Failed to save");
      setCurrentFileContent(selectedFile.content || "");
    } finally {
      setIsSaving(false);
    }
  };

  const currentFileIsModified = selectedFile ? modifiedFiles.has(selectedFile.id) : false;

  const numberOfFiles = files.filter(
    (file) => file.type === FileType.File,
  ).length;

  return (
    <div className="relative flex border border-gray-200 rounded-lg overflow-hidden min-h-[400px] max-h-[75vh]">
      <div
        data-testid="files-panel"
        className={clsx(
          "relative bg-gray-50 border-r border-gray-200 flex flex-col transition-transform duration-300 ease-in-out w-80",
          !isPanelOpen && "-translate-x-full",
        )}
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
            />
          ))}
        </div>

        <button
          onClick={() => handlePanelToggle(false)}
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

      {!isPanelOpen && (
        <div
          className="group absolute left-0 top-0 z-30 h-full w-3 cursor-pointer"
          onClick={() => handlePanelToggle(true)}
        >
          <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center">
            <div className="pointer-events-auto invisible rounded-r-md bg-gray-400 p-0.5 pl-0.5 align-middle text-white group-hover:visible">
              <ChevronRightIcon className="h-5 w-5" />
            </div>
          </div>
        </div>
      )}

      <div 
        className={clsx(
          "flex-1 flex flex-col transition-[margin-left] duration-300 ease-in-out",
          !isPanelOpen && "-ml-80"
        )}
      >
        {selectedFile ? (
          <>
            <div className="p-3 border-b border-gray-200 bg-white flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-gray-900 flex items-center gap-2">
                  {selectedFile.name}
                  {currentFileIsModified && (
                    <span className="inline-block w-2 h-2 bg-blue-500 rounded-full" title={t("Modified")} />
                  )}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {selectedFile.language}
                  {" • "}
                  {selectedFile.lineCount}
                  {` ${t("lines")}`}
                  {currentFileIsModified && ` • ${t("Modified")}`}
                </div>
                {saveError && (
                  <div className="text-xs text-red-600 mt-1">
                    {t("Save error")}: {saveError}
                  </div>
                )}
              </div>
              {isEditable && currentFileIsModified && (
                <button
                  onClick={handleSave}
                  disabled={isSaving}
                  className={clsx(
                    "px-3 py-1 text-xs font-medium rounded-md transition-colors",
                    isSaving
                      ? "bg-gray-200 text-gray-500 cursor-not-allowed"
                      : "bg-blue-600 text-white hover:bg-blue-700"
                  )}
                >
                  {isSaving ? t("Saving...") : t("Save")}
                </button>
              )}
            </div>
            <div className="flex-1 overflow-hidden">
              {isClient ? (
                <CodeMirror
                  value={currentFileContent}
                  readOnly={!isEditable}
                  onChange={handleContentChange}
                  extensions={[python(), r(), json()]}
                  height="100%"
                  style={{ height: "100%" }}
                />
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

FilesEditor.prefetch = async (
  ctx: GetServerSidePropsContext,
  _client: CustomApolloClient,
) => {
  cookieFilesEditorPanelOpenState = (await hasCookie("files-editor-panel-open", ctx))
    ? (await getCookie("files-editor-panel-open", ctx)) === "true"
    : true;
};

export default FilesEditor;
