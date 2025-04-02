import { gql } from "@apollo/client";
import Dialog from "core/components/Dialog";
import useCacheKey from "core/hooks/useCacheKey";
import { useState } from "react";
import { useResendWorkspaceInvitationMutation } from "workspaces/graphql/mutations.generated";

import { ResendWorkspaceInvitationError } from "graphql/types";
import { useTranslation } from "next-i18next";
import Button from "core/components/Button/Button";
import Spinner from "core/components/Spinner";
import { ResendWorkspaceInvitation_WorkspaceInvitationFragment } from "./ResendWorskspaceInvitationDialog.generated";

type ResendWorkspaceInvitationProps = {
  onClose(): void;
  open: boolean;
  invitation: ResendWorkspaceInvitation_WorkspaceInvitationFragment;
};

const ResendWorkspaceInvitationDialog = (
  props: ResendWorkspaceInvitationProps,
) => {
  const { onClose, open, invitation } = props;
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { t } = useTranslation();
  const [resendWorkspaceInvitation] = useResendWorkspaceInvitationMutation();
  const clearCache = useCacheKey("workspace");

  const onSubmit = async () => {
    setIsSubmitting(true);
    const { data } = await resendWorkspaceInvitation({
      variables: {
        input: {
          invitationId: invitation.id,
        },
      },
    });

    if (!data?.resendWorkspaceInvitation) {
      throw new Error("Unknown error.");
    }

    if (data.resendWorkspaceInvitation.success) {
      clearCache();
      setIsSubmitting(false);
      onClose();
    }

    if (
      data.resendWorkspaceInvitation.errors.includes(
        ResendWorkspaceInvitationError.PermissionDenied,
      )
    ) {
      throw new Error("You are not authorized to perform this action");
    }
  };

  return (
    <Dialog maxWidth="max-w-xl" open={open} onClose={onClose}>
      <Dialog.Title>{t("Resend invitation")}</Dialog.Title>
      <Dialog.Content className="space-y-4">
        <p>
          {t("Resend invitation for {{email}} ?", {
            email: invitation.email,
          })}
        </p>
      </Dialog.Content>
      <Dialog.Actions>
        <Button variant="white" onClick={onClose}>
          {t("Cancel")}
        </Button>
        <Button onClick={onSubmit}>
          {isSubmitting && <Spinner size="xs" className="mr-1" />}
          {t("Resend")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

ResendWorkspaceInvitationDialog.fragments = {
  invitation: gql`
    fragment ResendWorkspaceInvitation_workspaceInvitation on WorkspaceInvitation {
      id
      email
    }
  `,
};

export default ResendWorkspaceInvitationDialog;
