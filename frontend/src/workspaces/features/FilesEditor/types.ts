import { FilesEditor_FileFragment } from "./FilesEditor.generated";

export type ProposedFile = { name: string; content: string };

export type AugmentedFile = FilesEditor_FileFragment & { isProposed?: boolean };

export type FileNode = FilesEditor_FileFragment & {
  children: FileNode[];
  isProposed?: boolean;
};

export interface SaveResult {
  success: boolean;
  error?: string;
}
