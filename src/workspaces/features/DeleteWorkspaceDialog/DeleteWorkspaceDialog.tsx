import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Spinner from "core/components/Spinner";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useRouter } from "next/router";
import { useDeleteWorkspaceMutation } from "workspaces/graphql/mutations.generated";
import useCacheKey from "core/hooks/useCacheKey";
import { gql } from "@apollo/client";
import { DeleteWorkspace_WorkspaceFragment } from "./DeleteWorkspaceDialog.generated";
import { DeleteWorkspaceError } from "graphql-types";

type DeleteWorkspaceDialogProps = {
  onClose(): void;
  open: boolean;
  workspace: DeleteWorkspace_WorkspaceFragment;
};

const DeleteWorkspaceDialog = (props: DeleteWorkspaceDialogProps) => {
  const router = useRouter();
  const { t } = useTranslation();
  const { open, onClose, workspace } = props;
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [deleteWorkspace] = useDeleteWorkspaceMutation();
  const clearCache = useCacheKey(["workspaces", workspace.slug]);

  const onSubmit = async () => {
    setIsSubmitting(true);
    const { data } = await deleteWorkspace({
      variables: {
        input: {
          slug: workspace.slug,
        },
      },
    });

    if (!data?.deleteWorkspace) {
      throw new Error("Unknown error.");
    }

    if (data.deleteWorkspace.success) {
      clearCache();
      setIsSubmitting(false);
      router.push("/");
    }
    if (
      data.deleteWorkspace.errors.includes(
        DeleteWorkspaceError.PermissionDenied
      )
    ) {
      throw new Error("You are not authorized to perform this action");
    }
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <Dialog.Title>
        {t("Delete {{name}}", { name: workspace.name })}
      </Dialog.Title>
      <Dialog.Content className="space-y-4">
        <p>{t("You're about to delete this workspace and all its content.")}</p>
      </Dialog.Content>
      <Dialog.Actions>
        <Button variant="white" type="button" onClick={onClose}>
          {t("Cancel")}
        </Button>
        <Button onClick={onSubmit}>
          {isSubmitting && <Spinner size="xs" className="mr-1" />}
          {t("Delete")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

DeleteWorkspaceDialog.fragments = {
  workspace: gql`
    fragment DeleteWorkspace_workspace on Workspace {
      slug
      name
    }
  `,
};

export default DeleteWorkspaceDialog;
