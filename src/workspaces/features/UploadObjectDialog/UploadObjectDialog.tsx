import { gql } from "@apollo/client";
import { ArrowUpTrayIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Dropzone from "core/components/Dropzone";
import { uploader } from "core/helpers/files";
import useCacheKey from "core/hooks/useCacheKey";
import useForm from "core/hooks/useForm";
import { useEffect, useState } from "react";
import { useTranslation } from "next-i18next";
import { getBucketObjectUploadUrl } from "workspaces/helpers/bucket";
import { UploadObjectDialog_WorkspaceFragment } from "./UploadObjectDialog.generated";

type UploadObjectDialogProps = {
  open: boolean;
  onClose: () => void;
  prefix?: string;
  workspace: UploadObjectDialog_WorkspaceFragment;
};

const UploadObjectDialog = (props: UploadObjectDialogProps) => {
  const { open, onClose, prefix, workspace } = props;
  const [progress, setProgress] = useState(0);
  const { t } = useTranslation();
  const clearCache = useCacheKey(["workspace", "files", prefix]);
  const form = useForm<{ files: File[] }>({
    validate(values) {
      const errors = {} as any;
      if (!values.files?.length) {
        errors.files = t("Select files");
      }

      return errors;
    },
    async onSubmit(values) {
      await uploader.createUploadJob({
        files: values.files,
        async getXHROptions(file) {
          const contentType = file.type || "application/octet-stream";
          const url = await getBucketObjectUploadUrl(
            workspace.slug,
            (prefix ?? "") + file.name,
            contentType,
          );

          return {
            url,
            method: "PUT",
            headers: { "Content-Type": contentType },
          };
        },
        onProgress: setProgress,
      });
      clearCache();
      handleClose();
    },
  });

  useEffect(() => {
    if (open) {
      setProgress(0);
    }
  }, [open]);

  const handleClose = () => {
    form.resetForm();
    onClose();
  };

  return (
    <Dialog
      maxWidth="max-w-3xl"
      onSubmit={form.handleSubmit}
      open={open}
      onClose={handleClose}
    >
      <Dialog.Title onClose={handleClose}>
        {t("Upload files in workspace")}
      </Dialog.Title>
      <Dialog.Content>
        <Dropzone
          className="h-80"
          onChange={(files) => form.setFieldValue("files", files)}
          disabled={form.isSubmitting}
          label={t("Drop files here or click to select")}
        />
        {form.submitError && (
          <p className={"text-sm text-red-600"}>{form.submitError}</p>
        )}
      </Dialog.Content>
      <Dialog.Actions className="justify-between">
        <div className="flex items-center justify-between gap-3">
          <Button
            variant="white"
            onClick={handleClose}
            disabled={form.isSubmitting}
          >
            {t("Cancel")}
          </Button>
          <Button
            type="submit"
            disabled={!form.isDirty || form.isSubmitting}
            leadingIcon={<ArrowUpTrayIcon className="h-4 w-4" />}
          >
            {form.isSubmitting
              ? t("Uploading: {{progress}}%", { progress })
              : t("Upload")}
          </Button>
        </div>
      </Dialog.Actions>
    </Dialog>
  );
};

UploadObjectDialog.fragments = {
  workspace: gql`
    fragment UploadObjectDialog_workspace on Workspace {
      slug
      permissions {
        createObject
      }
    }
  `,
};

export default UploadObjectDialog;
