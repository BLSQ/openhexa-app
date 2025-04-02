import { gql } from "@apollo/client";
import Dialog from "core/components/Dialog";
import useCacheKey from "core/hooks/useCacheKey";
import { useState } from "react";
import { useDeleteWorkspaceInvitationMutation } from "workspaces/graphql/mutations.generated";
import { DeleteWorkspaceInvitation_WorkspaceInvitationFragment } from "./DeleteWorkspaceInvitationDialog.generated";
import { DeleteWorkspaceInvitationError } from "graphql/types";
import { useTranslation } from "next-i18next";
import Button from "core/components/Button/Button";
import Spinner from "core/components/Spinner";

type DeleteWorkspaceInvitationProps = {
  onClose(): void;
  open: boolean;
  invitation: DeleteWorkspaceInvitation_WorkspaceInvitationFragment;
};

const DeleteWorkspaceInvitationDialog = (
  props: DeleteWorkspaceInvitationProps,
) => {
  const { onClose, open, invitation } = props;
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { t } = useTranslation();
  const [deleteWorkspaceInvitation] = useDeleteWorkspaceInvitationMutation();
  const clearCache = useCacheKey("workspace");

  const onSubmit = async () => {
    setIsSubmitting(true);
    const { data } = await deleteWorkspaceInvitation({
      variables: {
        input: {
          invitationId: invitation.id,
        },
      },
    });

    if (!data?.deleteWorkspaceInvitation) {
      throw new Error("Unknown error.");
    }

    if (data.deleteWorkspaceInvitation.success) {
      clearCache();
      setIsSubmitting(false);
      onClose();
    }

    if (
      data.deleteWorkspaceInvitation.errors.includes(
        DeleteWorkspaceInvitationError.PermissionDenied,
      )
    ) {
      throw new Error("You are not authorized to perform this action");
    }
  };

  return (
    <Dialog maxWidth="max-w-xl" open={open} onClose={onClose}>
      <Dialog.Title>{t("Delete invitation")}</Dialog.Title>
      <Dialog.Content className="space-y-4">
        <p>
          {t(
            "By proceeding, the invitation link for {{email}} will no longer be usable.",
            {
              email: invitation.email,
            },
          )}
        </p>
      </Dialog.Content>
      <Dialog.Actions>
        <Button variant="white" onClick={onClose}>
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

DeleteWorkspaceInvitationDialog.fragments = {
  invitation: gql`
    fragment DeleteWorkspaceInvitation_workspaceInvitation on WorkspaceInvitation {
      id
      email
    }
  `,
};

export default DeleteWorkspaceInvitationDialog;
