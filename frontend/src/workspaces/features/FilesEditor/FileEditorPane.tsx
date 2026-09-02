import { json } from "@codemirror/lang-json";
import { python } from "@codemirror/lang-python";
import { unifiedMergeView } from "@codemirror/merge";
import { EditorView } from "@codemirror/view";
import { DocumentIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import CodeMirrorClient from "core/components/CodeMirrorClient/CodeMirrorClient";
import { filesize } from "filesize";
import { FileEncoding } from "graphql/types";
import { useTranslation } from "next-i18next";
import { ReactNode, useMemo } from "react";
import { r } from "codemirror-lang-r";
import { FileNode } from "./types";

type FileEditorPaneProps = {
  selectedFile: FileNode | null;
  currentFileContent: string;
  isEditable: boolean;
  currentFileIsModified: boolean;
  hasPendingChanges: boolean;
  isSaving: boolean;
  saveError: string | null;
  proposedByKey: Map<string, string>;
  deletedFilePaths: Set<string>;
  headerActions?: ReactNode;
  onContentChange: (content: string) => void;
  onSave: () => void;
  canDelete: boolean;
  onRestore: (node: FileNode) => void;
  hasSaveHandler: boolean;
};

const FileEditorPane = ({
  selectedFile,
  currentFileContent,
  isEditable,
  currentFileIsModified,
  hasPendingChanges,
  isSaving,
  saveError,
  proposedByKey,
  deletedFilePaths,
  headerActions,
  onContentChange,
  onSave,
  canDelete,
  onRestore,
  hasSaveHandler,
}: FileEditorPaneProps) => {
  const { t } = useTranslation();

  const isEffectivelyDeleted =
    selectedFile !== null && deletedFilePaths.has(selectedFile.path);
  const isDiffMode =
    selectedFile !== null && proposedByKey.has(selectedFile.path);
  const canSave = isEditable && hasPendingChanges && hasSaveHandler;

  const saveButton = canSave ? (
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
  ) : null;

  const isTooLarge = selectedFile?.tooLarge === true;

  const fileTypeLabel =
    selectedFile?.language ??
    (selectedFile?.encoding === FileEncoding.Base64 ? t("Binary") : null);

  const lineCount = selectedFile?.lineCount;
  const size = selectedFile?.size;

  const metaParts = [
    fileTypeLabel,
    lineCount != null
      ? `${lineCount} ${lineCount > 1 ? t("lines") : t("line")}`
      : size != null
        ? filesize(size)
        : null,
    currentFileIsModified ? t("Modified") : null,
  ].filter(Boolean);

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
      <div className="relative flex items-center justify-center flex-1 min-h-[300px]">
        {(headerActions || saveButton) && (
          <div className="absolute top-3 right-3 flex items-center gap-2">
            {headerActions}
            {saveButton}
          </div>
        )}
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
      <div className="p-3 border-b border-gray-200 bg-white flex items-center justify-between gap-2">
        <div className="min-w-0">
          <div className="text-sm font-medium text-gray-900 flex items-center gap-2">
            {selectedFile.name}
            {currentFileIsModified && (
              <span
                className="inline-block w-2 h-2 bg-blue-500 rounded-full"
                title={t("Modified")}
              />
            )}
          </div>
          <div className="text-xs text-gray-500 mt-1 min-h-4">
            {metaParts.join(" • ")}
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
        <div className="flex items-center gap-2 shrink-0">
          {headerActions}
          {saveButton}
        </div>
      </div>
      {isEffectivelyDeleted && (
        <div className="shrink-0 flex items-center justify-between gap-2 border-b border-red-200 bg-red-50 px-3 py-2 text-sm">
          <span className="font-medium text-red-700">
            {t("This file will be deleted")}
          </span>
          {canDelete && (
            <button
              onClick={() => onRestore(selectedFile)}
              className="rounded-md border border-red-300 bg-white px-2 py-0.5 text-xs font-medium text-red-700 hover:bg-red-100"
            >
              {t("Undo delete")}
            </button>
          )}
        </div>
      )}
      {isTooLarge ? (
        <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
          <DocumentIcon className="w-12 h-12 text-gray-400 mb-4" />
          <div className="text-gray-500 text-lg mb-2">
            {t("This file is too large to display")}
          </div>
          <div className="text-gray-400 text-sm">
            {t(
              "It is served by the web app but cannot be opened in the editor.",
            )}
          </div>
        </div>
      ) : (
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
      )}
    </>
  );
};

export default FileEditorPane;
