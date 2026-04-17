import { useEffect, useMemo, useState } from "react";
import { FileType } from "graphql/types";
import useNavigationWarning from "core/hooks/useNavigationWarning";
import useFilesEditorPanelOpen from "workspaces/hooks/useFilesEditorPanelOpen";
import { FilesEditor_FileFragment } from "./FilesEditor.generated";
import { AugmentedFile, FileNode, ProposedFile, SaveResult } from "./types";
import { buildFileTree } from "./buildFileTree";

interface UseFilesEditorStateParams {
  flatFiles: FilesEditor_FileFragment[];
  isEditable: boolean;
  proposedFiles?: ProposedFile[];
  onSave?: (
    modifiedFiles: Map<string, string>,
    allFiles: FilesEditor_FileFragment[],
  ) => Promise<SaveResult>;
}

export const useFilesEditorState = ({
  flatFiles,
  isEditable,
  proposedFiles,
  onSave,
}: UseFilesEditorStateParams) => {
  const [isPanelOpen, setIsPanelOpen] = useFilesEditorPanelOpen();
  const [selectedFile, setSelectedFile] = useState<FileNode | null>(null);
  const [modifiedFiles, setModifiedFiles] = useState<Map<string, string>>(
    new Map(),
  );
  const [currentFileContent, setCurrentFileContent] = useState<string>("");
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  // Synthetic file and folder nodes for files proposed by the agent that don't exist
  // yet in the current version. Paths are parsed so nested files (e.g. tests/__init__.py)
  // are placed under the correct folder in the tree rather than shown as flat names.
  const virtualFiles = useMemo<AugmentedFile[]>(() => {
    if (!proposedFiles) return [];

    const result: AugmentedFile[] = [];
    const virtualFolderIds = new Map<string, string>(); // dirPath -> id

    for (const pf of proposedFiles) {
      if (flatFiles.find((f) => f.path === pf.name)) continue;

      const parts = pf.name.split("/");
      const fileName = parts[parts.length - 1];
      if (!fileName) continue;
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
          const folderId = dirPath;
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
            isProposed: true,
          });
          virtualFolderIds.set(dirPath, folderId);
          parentId = folderId;
        }
      }

      result.push({
        __typename: "FileNode" as const,
        id: pf.name,
        name: fileName,
        path: pf.name,
        type: FileType.File,
        content: "",
        parentId,
        autoSelect: false,
        language: null,
        lineCount: null,
        isProposed: true,
      });
    }

    return result;
  }, [proposedFiles, flatFiles]);

  const augmentedFlatFiles = useMemo<AugmentedFile[]>(
    () => [...flatFiles, ...virtualFiles],
    [flatFiles, virtualFiles],
  );

  const files = useMemo(
    () => buildFileTree(augmentedFlatFiles),
    [augmentedFlatFiles],
  );

  const rootFiles = useMemo(
    () => files.filter((file) => !file.parentId),
    [files],
  );

  // Files present in the current version but absent from the proposal — the agent wants them deleted.
  const proposedDeletions = useMemo<Set<string>>(() => {
    if (!proposedFiles) return new Set();
    const proposedNames = new Set(proposedFiles.map((f) => f.name));
    return new Set(
      flatFiles
        .filter((f) => f.type === FileType.File && !proposedNames.has(f.path))
        .map((f) => f.path),
    );
  }, [proposedFiles, flatFiles]);

  // Maps file path → proposed content, but only for files that differ from the current version.
  // Unchanged files are excluded so they don't trigger diff highlighting or amber dots.
  // Deleted files are included with "" so the diff renders all lines as removed.
  const proposedByKey = useMemo(() => {
    const map = new Map<string, string>();
    for (const f of proposedFiles ?? []) {
      const existing = flatFiles.find((ef) => ef.path === f.name);
      if (!existing || f.content !== (existing.content ?? "")) {
        map.set(f.name, f.content);
      }
    }
    for (const path of Array.from(proposedDeletions)) {
      map.set(path, "");
    }
    return map;
  }, [proposedFiles, flatFiles, proposedDeletions]);

  // Subset of proposedDeletions where the user hasn't overridden the deletion by editing.
  const effectivelyDeletedPaths = useMemo<Set<string>>(() => {
    const result = new Set<string>();
    for (const path of Array.from(proposedDeletions)) {
      const file = flatFiles.find((f) => f.path === path);
      if (file && !modifiedFiles.get(file.id)) {
        result.add(path);
      }
    }
    return result;
  }, [proposedDeletions, modifiedFiles, flatFiles]);

  // Folders where every file descendant is effectively deleted.
  const effectivelyDeletedFolderPaths = useMemo<Set<string>>(() => {
    if (effectivelyDeletedPaths.size === 0) return new Set();
    const result = new Set<string>();
    const dirs = flatFiles.filter((f) => f.type === FileType.Directory);
    for (const dir of dirs) {
      const filesUnder = flatFiles.filter(
        (f) => f.type === FileType.File && f.path.startsWith(dir.path + "/"),
      );
      if (
        filesUnder.length > 0 &&
        filesUnder.every((f) => effectivelyDeletedPaths.has(f.path))
      ) {
        result.add(dir.path);
      }
    }
    return result;
  }, [flatFiles, effectivelyDeletedPaths]);

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

  useEffect(() => {
    setModifiedFiles(new Map());
  }, [flatFiles]);

  useEffect(() => {
    if (!proposedFiles) return;
    setModifiedFiles((prev) => {
      const next = new Map(prev);
      for (const proposed of proposedFiles) {
        const existing = flatFiles.find((f) => f.path === proposed.name);
        if (existing) {
          if (
            proposed.content !== (existing.content ?? "") &&
            !next.has(existing.id)
          ) {
            next.set(existing.id, proposed.content);
          }
        } else {
          if (!next.has(proposed.name)) {
            next.set(proposed.name, proposed.content);
          }
        }
      }
      // Seed deleted files with "" as the deletion marker so the diff shows all
      // lines removed. handleContentChange will overwrite this if the user edits.
      for (const path of Array.from(proposedDeletions)) {
        const existing = flatFiles.find((f) => f.path === path);
        if (existing && !next.has(existing.id)) {
          next.set(existing.id, "");
        }
      }
      return next;
    });
  }, [proposedFiles, flatFiles, proposedDeletions]);

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
      // For files proposed for deletion, always keep them in modifiedFiles so we
      // don't lose track of whether the user restored the file to its original content.
      if (
        content !== (selectedFile.content || "") ||
        proposedDeletions.has(selectedFile.path)
      ) {
        setModifiedFiles((prev) => new Map(prev).set(selectedFile.id, content));
      } else {
        setModifiedFiles((prev) => {
          const next = new Map(prev);
          next.delete(selectedFile.id);
          return next;
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
      const filesToSave = augmentedFlatFiles.filter(
        (f) => !effectivelyDeletedPaths.has(f.path),
      );
      const result = await onSave(modifiedFiles, filesToSave);
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

  return {
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
    effectivelyDeletedPaths,
    effectivelyDeletedFolderPaths,
    currentFileIsModified: selectedFile ? modifiedFiles.has(selectedFile.id) : false,
    numberOfFiles: files.filter((f) => f.type === FileType.File).length,
    handleContentChange,
    handleSave,
  };
};
