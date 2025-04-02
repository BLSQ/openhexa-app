import { gql } from "@apollo/client";
import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Field from "core/components/forms/Field";
import Input from "core/components/forms/Input";
import { useRouter } from "next/router";
import { FormEvent, useEffect, useState } from "react";
import { useTranslation } from "next-i18next";
import { createBucketFolder } from "workspaces/helpers/bucket";
import { CreateBucketFolderDialog_WorkspaceFragment } from "./CreateBucketFolderDialog.generated";
import { toast } from "react-toastify";

type CreateBucketFolderDialogProps = {
  workspace: CreateBucketFolderDialog_WorkspaceFragment;
  prefix?: string;
  open: boolean;
  onClose: () => void;
};

const CreateBucketFolderDialog = (props: CreateBucketFolderDialogProps) => {
  const { open, onClose, workspace, prefix } = props;
  const [folderName, setFolderName] = useState("");
  const router = useRouter();
  const { t } = useTranslation();

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      const folder = await createBucketFolder(
        workspace.slug,
        (prefix || "") + folderName,
      );
      await router.push(`/workspaces/${workspace.slug}/files/${folder.key}`);
      onClose();
    } catch (err) {
      toast.error(t("An error occurred while creating the folder"));
    }
  };

  useEffect(() => {
    if (!open) {
      setFolderName("");
    }
  }, [open]);

  return (
    <Dialog
      onSubmit={handleSubmit}
      open={open}
      onClose={onClose}
      maxWidth="max-w-2xl"
    >
      <Dialog.Title>{t("Create a folder")}</Dialog.Title>
      <Dialog.Content>
        <Field label={t("Folder name")} required name="folderName">
          <div className="flex w-full items-center gap-1.5">
            {prefix && (
              <span className="flex-1 rounded-md bg-gray-100 p-1 font-mono text-xs">
                {prefix}
              </span>
            )}
            <div className="w-64">
              <Input
                name="folderName"
                value={folderName}
                placeholder={t("my-folder")}
                onChange={(event) => setFolderName(event.target.value)}
                required
              />
            </div>
          </div>
        </Field>
      </Dialog.Content>
      <Dialog.Actions>
        <Button variant="white" onClick={onClose}>
          {t("Cancel")}
        </Button>
        <Button type="submit">{t("Create")}</Button>
      </Dialog.Actions>
    </Dialog>
  );
};

CreateBucketFolderDialog.fragments = {
  workspace: gql`
    fragment CreateBucketFolderDialog_workspace on Workspace {
      slug
      permissions {
        createObject
      }
      bucket {
        name
      }
    }
  `,
};

export default CreateBucketFolderDialog;
