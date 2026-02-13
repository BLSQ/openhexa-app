import { useRef } from "react";
import { Id, toast } from "react-toastify";
import { useTranslation } from "next-i18next";

import { constructFolderKey, uploader } from "core/helpers/files";
import useCacheKey from "core/hooks/useCacheKey";
import { getBucketObjectUploadUrl } from "workspaces/helpers/bucket";

type UseUploadFilesProps = {
  workspaceSlug: string;
  prefix?: string | null;
  onProgress?: (progress: number) => void;
  onFileUploaded?: () => void;
};

export const useUploadFiles = ({
  prefix,
  workspaceSlug,
  onFileUploaded,
  onProgress,
}: UseUploadFilesProps) => {
  const toastId = useRef<Id | null>(null);
  const { t } = useTranslation();
  const clearCache = useCacheKey(["workspace", "files", prefix]);
  return (files: File[]) => {
    toastId.current = toast(t("Upload in progress..."), {
      isLoading: true,
    });
    uploader
      .createUploadJob({
        files,
        async getXHROptions(file) {
          const contentType = file.type || "application/octet-stream";
          const { uploadUrl, headers } = await getBucketObjectUploadUrl(
            workspaceSlug,
            constructFolderKey(file.path ?? file.name, prefix || ""),
            contentType,
          );

          return {
            url: uploadUrl,
            method: "PUT",
            headers: { "Content-Type": contentType, ...headers },
          };
        },
        onProgress,
      })
      .then(() => {
        setTimeout(
          () =>
            toast.update(toastId.current as Id, {
              type: "success",
              render: t("Upload successful!") + " 🎉",
              isLoading: false,
            }),
          500,
        );
        clearCache();
      })
      .catch((error) => {
        toast.update(toastId.current as Id, {
          type: "error",
          render:
            (error as Error).message ?? t("An unexpected error occurred."),
          isLoading: false,
          autoClose: 5000,
        });
      })
      .finally(onFileUploaded);
  };
};
