import { gql } from "@apollo/client";
import Dialog from "core/components/Dialog";
import useCacheKey from "core/hooks/useCacheKey";
import { useState } from "react";
import { useDeleteOrganizationInvitationMutation } from "../OrganizationInvitations.generated";
import { DeleteOrganizationInvitationError } from "graphql/types";
import { useTranslation } from "next-i18next";
import Button from "core/components/Button/Button";
import Spinner from "core/components/Spinner";

type DeleteOrganizationInvitationProps = {
  onClose(): void;
  open: boolean;
  invitation: {
    id: string;
    email: string;
  };
};

const DeleteOrganizationInvitationDialog = (
  props: DeleteOrganizationInvitationProps,
) => {
  const { onClose, open, invitation } = props;
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { t } = useTranslation();
  const [deleteOrganizationInvitation] = useDeleteOrganizationInvitationMutation();
  const clearCache = useCacheKey("organization");

  const onSubmit = async () => {
    setIsSubmitting(true);
    const { data } = await deleteOrganizationInvitation({
      variables: {
        input: {
          id: invitation.id,
        },
      },
    });

    if (!data?.deleteOrganizationInvitation) {
      throw new Error("Unknown error.");
    }

    if (data.deleteOrganizationInvitation.success) {
      clearCache();
      setIsSubmitting(false);
      onClose();
    }

    if (
      data.deleteOrganizationInvitation.errors.includes(
        DeleteOrganizationInvitationError.PermissionDenied,
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

export default DeleteOrganizationInvitationDialog;