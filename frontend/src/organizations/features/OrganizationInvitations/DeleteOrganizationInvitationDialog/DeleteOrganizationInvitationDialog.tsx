import Dialog from "core/components/Dialog";
import useCacheKey from "core/hooks/useCacheKey";
import { useState } from "react";
import { DeleteOrganizationInvitationError } from "graphql/types";
import { Trans, useTranslation } from "next-i18next";
import Button from "core/components/Button/Button";
import Spinner from "core/components/Spinner";
import { useMutation } from "@apollo/client/react";
import { graphql } from "graphql/gql";

const DeleteOrganizationInvitationDoc = graphql(`
mutation DeleteOrganizationInvitation($input: DeleteOrganizationInvitationInput!) {
  deleteOrganizationInvitation(input: $input) {
    success
    errors
  }
}
`);

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
  const [deleteOrganizationInvitation] =
    useMutation(DeleteOrganizationInvitationDoc);
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
        <Trans>
          By proceeding, the invitation link for <b>{invitation.email}</b> will
          no longer be usable.
        </Trans>
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
