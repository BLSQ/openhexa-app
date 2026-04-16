import { json } from "@codemirror/lang-json";
import { python } from "@codemirror/lang-python";
import { unifiedMergeView } from "@codemirror/merge";
import { EditorView } from "@codemirror/view";
import { DocumentIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import CodeMirrorClient from "core/components/CodeMirrorClient/CodeMirrorClient";
import { useTranslation } from "next-i18next";
import { useMemo } from "react";
import { r } from "codemirror-lang-r";
import { FileNode } from "./types";

type FileEditorPaneProps = {
  selectedFile: FileNode | null;
  currentFileContent: string;
  isEditable: boolean;
  currentFileIsModified: boolean;
  isSaving: boolean;
  saveError: string | null;
  proposedByKey: Map<string, string>;
  onContentChange: (content: string) => void;
  onSave: () => void;
  hasSaveHandler: boolean;
};

const FileEditorPane = ({
  selectedFile,
  currentFileContent,
  isEditable,
  currentFileIsModified,
  isSaving,
  saveError,
  proposedByKey,
  onContentChange,
  onSave,
  hasSaveHandler,
}: FileEditorPaneProps) => {
  const { t } = useTranslation();

  const isDiffMode = selectedFile !== null && proposedByKey.has(selectedFile.path);

  const extensions = useMemo(
    () => [
      python(),
      r(),
      json(),
      ...(isDiffMode
        ? [
            unifiedMergeView({
              original: selectedFile!.content ?? "",
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
    ],
    [isDiffMode, selectedFile?.content],
  );

  if (!selectedFile) {
    return (
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
    );
  }

  return (
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
        {isEditable && currentFileIsModified && hasSaveHandler && (
          <button
            onClick={onSave}
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
        <div className="absolute inset-0">
          <CodeMirrorClient
            key={selectedFile.id + (isDiffMode ? "-diff" : "")}
            value={currentFileContent}
            readOnly={!isEditable}
            onChange={onContentChange}
            extensions={extensions}
            height="100%"
            style={{ width: "100%", height: "100%" }}
          />
        </div>
      </div>
    </>
  );
};

export default FileEditorPane;
