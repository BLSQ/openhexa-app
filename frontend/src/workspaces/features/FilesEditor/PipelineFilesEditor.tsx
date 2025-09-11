import React, { useCallback } from "react";
import { useUploadPipelineMutation } from "workspaces/graphql/mutations.generated";
import JSZip from "jszip";
import { FilesEditor, SaveResult } from "./FilesEditor";
import { FilesEditor_FileFragment } from "./FilesEditor.generated";
import { FileType, PipelineError } from "graphql/types";
import { PipelineVersionPicker_VersionFragment } from "../PipelineVersionPicker/PipelineVersionPicker.generated";
import useCacheKey from "core/hooks/useCacheKey";
import { toast } from "react-toastify";
import { useTranslation } from "react-i18next";

interface PipelineFilesEditorProps {
  name: string;
  files: FilesEditor_FileFragment[];
  isEditable?: boolean;
  workspaceSlug: string;
  pipelineCode: string;
  pipelineId: string;
  onVersionCreated?: (version: PipelineVersionPicker_VersionFragment) => void;
}

export const PipelineFilesEditor = ({
  name,
  files,
  isEditable = false,
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
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        const base64 = result.split(",")[1];
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(zipBlob);
    });
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
          result.data?.uploadPipeline.errors?.includes(
            PipelineError.PipelineParametersImpossibleToExtract,
          )
        ) {
          const message = t(
            "The pipeline parameters could not be extracted. Please ensure that the pipeline code is correct and try again.",
          );
          return { success: false, error: message };
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
      onSave={handleSave}
    />
  );
};

export default PipelineFilesEditor;
