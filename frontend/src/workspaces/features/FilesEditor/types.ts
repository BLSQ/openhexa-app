import { FilesEditor_FileFragment } from "./FilesEditor.generated";

export type ProposedFile = { name: string; content: string };

export type InputFile = FilesEditor_FileFragment & { isBinary?: boolean };

export type AugmentedFile = InputFile & { isProposed?: boolean };

export type FileNode = InputFile & {
  children: FileNode[];
  isProposed?: boolean;
};

export interface SaveResult {
  success: boolean;
  error?: string;
}
