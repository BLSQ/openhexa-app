import { ReactNode, useCallback, useEffect, useRef, useState } from "react";
import { useTranslation } from "next-i18next";
import { toast } from "react-toastify";
import { FilesEditor } from "workspaces/features/FilesEditor/FilesEditor";
import { FilesEditor_FileFragment } from "workspaces/features/FilesEditor/FilesEditor.generated";
import { useUpdateWebappMutation } from "webapps/graphql/mutations.generated";
import { useWebappFilesLazyQuery } from "webapps/graphql/queries.generated";
import Spinner from "core/components/Spinner";
import { ArrowUpTrayIcon, FolderPlusIcon } from "@heroicons/react/24/outline";

type WebappFilesEditorProps = {
  webappId: string;
  workspaceSlug: string;
  webappSlug: string;
  isEditable: boolean;
  versionRef?: string;
  versionPicker?: ReactNode;
  onSaveSuccess?: () => void;
  onBusyChange?: (busy: boolean) => void;
};

const WebappFilesEditor = ({
  webappId,
  workspaceSlug,
  webappSlug,
  isEditable,
  versionRef,
  versionPicker,
  onSaveSuccess,
  onBusyChange,
}: WebappFilesEditorProps) => {
  const { t } = useTranslation();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const folderInputRef = useRef<HTMLInputElement>(null);
  const [files, setFiles] = useState<FilesEditor_FileFragment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);

  const [fetchFiles] = useWebappFilesLazyQuery({
    fetchPolicy: "no-cache",
  });
  const [updateWebapp] = useUpdateWebappMutation();

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    fetchFiles({
      variables: { workspaceSlug, webappSlug, ref: versionRef },
    }).then(({ data }) => {
      if (!cancelled) {
        setFiles(data?.webapp?.files ?? []);
        setIsLoading(false);
      }
    });
    return () => {
      cancelled = true;
    };
  }, [fetchFiles, workspaceSlug, webappSlug, versionRef]);

  const handleUpload = useCallback(
    async (fileList: FileList) => {
      setIsUploading(true);
      onBusyChange?.(true);
      try {
        const uploadedFiles = await Promise.all(
          Array.from(fileList).map(async (file) => ({
            path: file.webkitRelativePath || file.name,
            content: await file.text(),
          })),
        );
        const { data } = await updateWebapp({
          variables: {
            input: {
              id: webappId,
              files: uploadedFiles,
            },
          },
          refetchQueries: ["WebappVersions"],
          awaitRefetchQueries: true,
        });
        if (data?.updateWebapp?.success) {
          toast.success(t("Files uploaded successfully"));
          onSaveSuccess?.();
        } else {
          toast.error(t("Failed to upload files"));
        }
      } catch {
        toast.error(t("An error occurred while uploading files"));
      } finally {
        setIsUploading(false);
        onBusyChange?.(false);
      }
    },
    [webappId, updateWebapp, onSaveSuccess, t],
  );

  const handleSave = async (
    modifiedFiles: Map<string, string>,
    allFiles: FilesEditor_FileFragment[],
  ) => {
    const fileInputs = Array.from(modifiedFiles.entries()).map(
      ([fileId, content]) => {
        const file = allFiles.find((f) => f.id === fileId);
        return {
          path: file?.path ?? fileId,
          content,
        };
      },
    );

    setIsLoading(true);
    onBusyChange?.(true);
    try {
      const { data } = await updateWebapp({
        variables: {
          input: {
            id: webappId,
            files: fileInputs,
          },
        },
        refetchQueries: ["WebappVersions"],
        awaitRefetchQueries: true,
      });

      if (data?.updateWebapp?.success) {
        toast.success(t("Web app saved successfully"));
        onSaveSuccess?.();
        return { success: true };
      } else {
        const error = data?.updateWebapp?.errors?.[0] ?? "Save failed";
        return { success: false, error: String(error) };
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Save failed",
      };
    } finally {
      setIsLoading(false);
      onBusyChange?.(false);
    }
  };

  return (
    <div>
      <div className="mb-3 flex items-center justify-between">
        {versionPicker && <div className="w-96">{versionPicker}</div>}
        {isEditable && (
          <div className="flex items-center gap-2">
            <input
              ref={fileInputRef}
              type="file"
              multiple
              className="hidden"
              aria-hidden="true"
              onChange={(e) => {
                if (e.target.files?.length) {
                  handleUpload(e.target.files).then();
                  e.target.value = "";
                }
              }}
            />
            <input
              ref={folderInputRef}
              type="file"
              className="hidden"
              aria-hidden="true"
              onChange={(e) => {
                if (e.target.files?.length) {
                  handleUpload(e.target.files).then();
                  e.target.value = "";
                }
              }}
              {...({ webkitdirectory: "", directory: "" } as Record<
                string,
                string
              >)}
            />
            <button
              className="inline-flex items-center gap-1.5 rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
            >
              {isUploading ? (
                <Spinner size="xs" className="text-gray-500" />
              ) : (
                <ArrowUpTrayIcon className="h-4 w-4 text-gray-500" />
              )}
              {isUploading ? t("Uploading...") : t("Upload files")}
            </button>
            <button
              className="inline-flex items-center gap-1.5 rounded-md border border-gray-300 bg-white px-3 py-1.5 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              onClick={() => folderInputRef.current?.click()}
              disabled={isUploading}
            >
              {isUploading ? (
                <Spinner size="xs" className="text-gray-500" />
              ) : (
                <FolderPlusIcon className="h-4 w-4 text-gray-500" />
              )}
              {isUploading ? t("Uploading...") : t("Upload folder")}
            </button>
          </div>
        )}
      </div>
      <div className="relative">
        {isLoading && (
          <div className="absolute inset-0 z-10 flex items-center justify-center backdrop-blur-xs">
            <Spinner size="md" />
          </div>
        )}
        <FilesEditor
          key={versionRef}
          name={t("Web app")}
          files={files}
          isEditable={isEditable}
          onSave={handleSave}
        />
      </div>
    </div>
  );
};

export default WebappFilesEditor;
