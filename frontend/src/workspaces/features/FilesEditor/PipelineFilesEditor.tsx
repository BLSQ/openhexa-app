import React, { useCallback } from "react";
import useCacheKey from "core/hooks/useCacheKey";
import { fileToBase64 } from "core/helpers/fileEncoding";
import { FileType, PipelineError } from "graphql/types";
import { useTranslation } from "react-i18next";
import { useUploadPipelineMutation } from "workspaces/graphql/mutations.generated";
import JSZip from "jszip";
import { FilesEditor, ProposedFile, SaveResult } from "./FilesEditor";
import { FilesEditor_FileFragment } from "./FilesEditor.generated";
import { PipelineVersionPicker_VersionFragment } from "../PipelineVersionPicker/PipelineVersionPicker.generated";

interface PipelineFilesEditorProps {
  name: string;
  files: FilesEditor_FileFragment[];
  isEditable?: boolean;
  proposedFiles?: ProposedFile[];
  proposedDeletedPaths?: string[];
  workspaceSlug: string;
  pipelineCode: string;
  pipelineId: string;
  onVersionCreated?: (version: PipelineVersionPicker_VersionFragment) => void;
}

export const PipelineFilesEditor = ({
  name,
  files,
  isEditable = false,
  proposedFiles,
  proposedDeletedPaths,
  workspaceSlug,
  pipelineCode,
  pipelineId,
  onVersionCreated,
}: PipelineFilesEditorProps) => {
  const [uploadPipeline] = useUploadPipelineMutation({
    refetchQueries: ["WorkspacePipelineCodePage"],
    awaitRefetchQueries: true,
  });
  const { t } = useTranslation();

  const clearCache = useCacheKey(["pipeline", pipelineId]);

  const createZipFromFiles = async (
    files: FilesEditor_FileFragment[],
    modifications: Map<string, string>,
  ): Promise<string> => {
    const zip = new JSZip();

    files.forEach((file) => {
      if (file.type === FileType.File) {
        const content = modifications.get(file.id) || file.content || "";
        zip.file(file.path, content);
      }
    });

    const zipBlob = await zip.generateAsync({ type: "blob" });
    return fileToBase64(zipBlob);
  };

  const handleSave = useCallback(
    async (
      modifiedFiles: Map<string, string>,
      allFiles: FilesEditor_FileFragment[],
    ): Promise<SaveResult> => {
      try {
        const zipBase64 = await createZipFromFiles(allFiles, modifiedFiles);

        const result = await uploadPipeline({
          variables: {
            input: {
              workspaceSlug: workspaceSlug,
              pipelineCode: pipelineCode,
              zipfile: zipBase64,
            },
          },
        });

        if (result.data?.uploadPipeline.success) {
          clearCache();

          const newVersion = result.data.uploadPipeline.pipelineVersion;
          if (newVersion && onVersionCreated) {
            onVersionCreated(newVersion);
          }

          return { success: true };
        } else if (
          result.data?.uploadPipeline.errors.includes(
            PipelineError.PipelineCodeParsingError,
          )
        ) {
          return {
            success: false,
            error: t("Error parsing your code ({{details}})", {
              details: result.data?.uploadPipeline.details,
            }),
          };
        } else if (
          result.data?.uploadPipeline.errors.includes(
            PipelineError.PipelineDoesNotSupportParameters,
          )
        ) {
          const missing = result.data.uploadPipeline.details
            ? result.data.uploadPipeline.details.split(", ")
            : [];
          return {
            success: false,
            error: t(
              "This pipeline is scheduled, so the required parameter {{parameters}} needs a default value. Give it one, or turn off the schedule before saving.",
              { count: missing.length, parameters: missing.join(", ") },
            ),
          };
        } else {
          const errors = result.data?.uploadPipeline.errors || [
            t("Unknown error"),
          ];
          return { success: false, error: errors.join(", ") };
        }
      } catch (error) {
        return {
          success: false,
          error: error instanceof Error ? error.message : t("Failed to save"),
        };
      }
    },
    [workspaceSlug, pipelineCode, uploadPipeline, clearCache, onVersionCreated],
  );

  return (
    <FilesEditor
      name={name}
      files={files}
      isEditable={isEditable}
      allowDelete
      proposedFiles={proposedFiles}
      proposedDeletedPaths={proposedDeletedPaths}
      onSave={handleSave}
    />
  );
};

export default PipelineFilesEditor;
