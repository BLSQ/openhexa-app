import { ChevronRightIcon } from "@heroicons/react/24/outline";
import { gql } from "@apollo/client";
import { FilesEditor_FileFragment } from "./FilesEditor.generated";
import { ProposedFile, SaveResult } from "./types";
import { useFilesEditorState } from "./useFilesEditorState";
import FileTree from "./FileTree";
import FileEditorPane from "./FileEditorPane";

export type { ProposedFile, SaveResult, FileNode } from "./types";

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
  const {
    isPanelOpen,
    setIsPanelOpen,
    selectedFile,
    setSelectedFile,
    modifiedFiles,
    currentFileContent,
    isSaving,
    saveError,
    rootFiles,
    proposedByKey,
    currentFileIsModified,
    numberOfFiles,
    handleContentChange,
    handleSave,
  } = useFilesEditorState({ flatFiles, isEditable, proposedFiles, onSave });

  return (
    <div className="relative flex border border-gray-200 rounded-lg overflow-hidden min-h-[60vh] h-full max-w-full">
      {isPanelOpen && (
        <FileTree
          name={name}
          numberOfFiles={numberOfFiles}
          rootFiles={rootFiles}
          selectedFile={selectedFile}
          setSelectedFile={setSelectedFile}
          modifiedFiles={modifiedFiles}
          proposedByKey={proposedByKey}
          onClose={() => setIsPanelOpen(false)}
        />
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
        <FileEditorPane
          selectedFile={selectedFile}
          currentFileContent={currentFileContent}
          isEditable={isEditable}
          currentFileIsModified={currentFileIsModified}
          isSaving={isSaving}
          saveError={saveError}
          proposedByKey={proposedByKey}
          onContentChange={handleContentChange}
          onSave={handleSave}
          hasSaveHandler={!!onSave}
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
      parentId
      autoSelect
      language
      lineCount
    }
  `,
};

export default FilesEditor;
