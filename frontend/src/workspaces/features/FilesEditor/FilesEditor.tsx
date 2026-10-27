import { ReactNode } from "react";
import { gql } from "@apollo/client";
import { useTranslation } from "next-i18next";
import ResizablePanel from "core/components/ResizablePanel";
import { FilesEditor_FileFragment } from "./FilesEditor.generated";
import { ProposedFile, SaveResult } from "./types";
import { useFilesEditorState } from "./useFilesEditorState";
import FileTree from "./FileTree";
import FileEditorPane from "./FileEditorPane";

export type { ProposedFile, SaveResult, FileNode } from "./types";

const SIDEBAR_DEFAULT_WIDTH = 240;
const SIDEBAR_MIN_WIDTH = 160;
const SIDEBAR_MAX_WIDTH = 640;
const EDITOR_MIN_WIDTH = 320;

interface FilesEditorProps {
  name: string;
  files: FilesEditor_FileFragment[];
  isEditable?: boolean;
  allowDelete?: boolean;
  proposedFiles?: ProposedFile[];
  proposedDeletedPaths?: string[];
  headerActions?: ReactNode;
  flush?: boolean;
  onSave?: (
    modifiedFiles: Map<string, string>,
    allFiles: FilesEditor_FileFragment[],
    deletedPaths: string[],
  ) => Promise<SaveResult>;
  saveDisabledReason?: string;
}

export const FilesEditor = ({
  name,
  files: flatFiles,
  isEditable = false,
  allowDelete = false,
  proposedFiles,
  proposedDeletedPaths,
  headerActions,
  flush = false,
  onSave,
  saveDisabledReason,
}: FilesEditorProps) => {
  const { t } = useTranslation();
  const {
    selectedFile,
    setSelectedFile,
    modifiedFiles,
    currentFileContent,
    isSaving,
    saveError,
    rootFiles,
    proposedByKey,
    effectivelyDeletedPaths,
    effectivelyDeletedFolderPaths,
    currentFileIsModified,
    hasPendingChanges,
    numberOfFiles,
    handleContentChange,
    handleSave,
    markDeleted,
    restoreDeleted,
  } = useFilesEditorState({
    flatFiles,
    isEditable,
    proposedFiles,
    proposedDeletedPaths,
    onSave,
  });

  return (
    <div
      className={
        flush
          ? "relative flex overflow-hidden h-full min-h-0 max-w-full"
          : "relative flex border border-gray-200 rounded-lg overflow-hidden min-h-[60vh] h-full max-w-full"
      }
    >
      <ResizablePanel
        side="left"
        label={t("File list")}
        defaultSize={SIDEBAR_DEFAULT_WIDTH}
        minSize={SIDEBAR_MIN_WIDTH}
        maxSize={SIDEBAR_MAX_WIDTH}
        reserve={EDITOR_MIN_WIDTH}
      >
        <FileTree
          name={name}
          numberOfFiles={numberOfFiles}
          rootFiles={rootFiles}
          selectedFile={selectedFile}
          setSelectedFile={setSelectedFile}
          modifiedFiles={modifiedFiles}
          proposedByKey={proposedByKey}
          deletedFilePaths={effectivelyDeletedPaths}
          deletedFolderPaths={effectivelyDeletedFolderPaths}
          canDelete={isEditable && allowDelete}
          onDelete={markDeleted}
          onRestore={restoreDeleted}
        />
      </ResizablePanel>

      <div className="flex-1 min-w-0 flex flex-col transition-all duration-300 ease-in-out">
        <FileEditorPane
          selectedFile={selectedFile}
          currentFileContent={currentFileContent}
          isEditable={isEditable}
          currentFileIsModified={currentFileIsModified}
          hasPendingChanges={hasPendingChanges}
          isSaving={isSaving}
          saveError={saveError}
          proposedByKey={proposedByKey}
          deletedFilePaths={effectivelyDeletedPaths}
          headerActions={headerActions}
          onContentChange={handleContentChange}
          onSave={handleSave}
          canDelete={isEditable && allowDelete}
          onRestore={restoreDeleted}
          hasSaveHandler={!!onSave}
          saveDisabledReason={saveDisabledReason}
        />
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
      encoding
      parentId
      autoSelect
      language
      lineCount
      size
      tooLarge
    }
  `,
};

export default FilesEditor;
