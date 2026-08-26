import { useEffect, useMemo, useRef, useState } from "react";
import { FileEncoding, FileType } from "graphql/types";
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
    deletedPaths: string[],
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
  const [userDeletedPaths, setUserDeletedPaths] = useState<Set<string>>(
    new Set(),
  );
  const [restoredPaths, setRestoredPaths] = useState<Set<string>>(new Set());
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
        .filter(
          (f) =>
            f.type === FileType.File &&
            !proposedNames.has(f.path) &&
            f.encoding !== FileEncoding.Base64,
        )
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
      if (!restoredPaths.has(path)) map.set(path, "");
    }
    return map;
  }, [proposedFiles, flatFiles, proposedDeletions, restoredPaths]);

  // Deletions that are still pending: files the agent dropped from its proposal (unless the
  // user overrode the deletion by editing them) plus files the user removed from the tree,
  // minus the ones the user explicitly restored.
  const effectivelyDeletedPaths = useMemo<Set<string>>(() => {
    const result = new Set<string>();
    for (const path of Array.from(proposedDeletions)) {
      const file = flatFiles.find((f) => f.path === path);
      if (file && !modifiedFiles.get(file.id)) {
        result.add(path);
      }
    }
    for (const path of Array.from(userDeletedPaths)) {
      result.add(path);
    }
    for (const path of Array.from(restoredPaths)) {
      result.delete(path);
    }
    return result;
  }, [
    proposedDeletions,
    modifiedFiles,
    flatFiles,
    userDeletedPaths,
    restoredPaths,
  ]);

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
    setUserDeletedPaths(new Set());
    setRestoredPaths(new Set());
  }, [flatFiles]);

  const prevProposedFilesRef = useRef<ProposedFile[] | undefined>(undefined);
  useEffect(() => {
    const prev = prevProposedFilesRef.current;
    prevProposedFilesRef.current = proposedFiles;

    if (prev && !proposedFiles) {
      setModifiedFiles(new Map());
      setRestoredPaths(new Set());
      return;
    }
    if (!proposedFiles) return;

    // When proposedFiles is a new reference (a new proposal from the agent),
    // overwrite previously seeded entries so the updated proposal is shown.
    // When it's the same reference re-running due to flatFiles/proposedDeletions
    // changing, preserve manual edits by only seeding missing entries.
    const isNewProposal = prev !== proposedFiles;

    setModifiedFiles((current) => {
      // New proposal: build fresh so stale entries from the previous proposal
      // are not carried over for files the new proposal reverted to original.
      // Same proposal re-running: patch so manual user edits are preserved.
      const next = isNewProposal ? new Map<string, string>() : new Map(current);

      for (const proposed of proposedFiles) {
        const existing = flatFiles.find((f) => f.path === proposed.name);
        if (existing) {
          if (proposed.content !== (existing.content ?? "")) {
            if (isNewProposal || !next.has(existing.id)) {
              next.set(existing.id, proposed.content);
            }
          }
        } else {
          if (isNewProposal || !next.has(proposed.name)) {
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

  const pendingModifiedFiles = useMemo(() => {
    const next = new Map(modifiedFiles);
    for (const path of Array.from(effectivelyDeletedPaths)) {
      const file = flatFiles.find((f) => f.path === path);
      next.delete(file ? file.id : path);
    }
    return next;
  }, [modifiedFiles, effectivelyDeletedPaths, flatFiles]);

  const hasPendingChanges =
    pendingModifiedFiles.size > 0 || effectivelyDeletedPaths.size > 0;

  useNavigationWarning({
    enabled: isEditable && hasPendingChanges,
  });

  const collectDeletablePaths = (node: FileNode): string[] => {
    if (node.type === FileType.File) return [node.path];
    return augmentedFlatFiles
      .filter(
        (f) => f.type === FileType.File && f.path.startsWith(node.path + "/"),
      )
      .map((f) => f.path);
  };

  const markDeleted = (node: FileNode) => {
    if (!isEditable) return;
    const paths = collectDeletablePaths(node);
    if (paths.length === 0) return;
    setRestoredPaths((prev) => {
      const next = new Set(prev);
      paths.forEach((path) => next.delete(path));
      return next;
    });
    setUserDeletedPaths((prev) => {
      const next = new Set(prev);
      paths.forEach((path) => next.add(path));
      return next;
    });
    // Select a deleted file so the pane shows the deletion notice and the save button.
    const target =
      node.type === FileType.File
        ? node
        : (files.find((f) => f.path === paths[0]) ?? null);
    if (target) setSelectedFile(target);
  };

  const restoreDeleted = (node: FileNode) => {
    const paths = collectDeletablePaths(node);
    if (paths.length === 0) return;
    setUserDeletedPaths((prev) => {
      const next = new Set(prev);
      paths.forEach((path) => next.delete(path));
      return next;
    });
    setRestoredPaths((prev) => {
      const next = new Set(prev);
      paths.forEach((path) => next.add(path));
      return next;
    });
    setModifiedFiles((prev) => {
      const next = new Map(prev);
      for (const path of paths) {
        const file = flatFiles.find((f) => f.path === path);
        // Drop the "" marker seeded for an agent-proposed deletion, otherwise restoring
        // the file would save it empty.
        if (file && next.get(file.id) === "") next.delete(file.id);
      }
      return next;
    });
  };

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
    if (!isEditable || !onSave || !hasPendingChanges) return;

    setIsSaving(true);
    setSaveError(null);

    try {
      const filesToSave = augmentedFlatFiles.filter(
        (f) => !effectivelyDeletedPaths.has(f.path),
      );
      const result = await onSave(
        pendingModifiedFiles,
        filesToSave,
        Array.from(effectivelyDeletedPaths),
      );
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
    currentFileIsModified: selectedFile
      ? pendingModifiedFiles.has(selectedFile.id)
      : false,
    hasPendingChanges,
    numberOfFiles: files.filter((f) => f.type === FileType.File).length,
    handleContentChange,
    handleSave,
    markDeleted,
    restoreDeleted,
  };
};
