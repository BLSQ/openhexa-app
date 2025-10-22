import Dialog from "core/components/Dialog";
import useCacheKey from "core/hooks/useCacheKey";
import { useState } from "react";
import { ResendOrganizationInvitationError } from "graphql/types";
import { Trans, useTranslation } from "next-i18next";
import Button from "core/components/Button/Button";
import Spinner from "core/components/Spinner";
import { useMutation } from "@apollo/client/react";
import { graphql } from "graphql/gql";

const ResendOrganizationInvitationDoc = graphql(`
mutation ResendOrganizationInvitation($input: ResendOrganizationInvitationInput!) {
  resendOrganizationInvitation(input: $input) {
    success
    errors
  }
}
`);

type ResendOrganizationInvitationProps = {
  onClose(): void;
  open: boolean;
  invitation: {
    id: string;
    email: string;
  };
};

const ResendOrganizationInvitationDialog = (
  props: ResendOrganizationInvitationProps,
) => {
  const { onClose, open, invitation } = props;
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { t } = useTranslation();
  const [resendOrganizationInvitation] =
    useMutation(ResendOrganizationInvitationDoc);
  const clearCache = useCacheKey("organization");

  const onSubmit = async () => {
    setIsSubmitting(true);
    const { data } = await resendOrganizationInvitation({
      variables: {
        input: {
          id: invitation.id,
        },
      },
    });

    if (!data?.resendOrganizationInvitation) {
      throw new Error("Unknown error.");
    }

    if (data.resendOrganizationInvitation.success) {
      clearCache();
      setIsSubmitting(false);
      onClose();
    }

    if (
      data.resendOrganizationInvitation.errors.includes(
        ResendOrganizationInvitationError.PermissionDenied,
      )
    ) {
      throw new Error(t("You are not authorized to perform this action"));
    }
  };

  return (
    <Dialog maxWidth="max-w-xl" open={open} onClose={onClose}>
      <Dialog.Title>{t("Resend invitation")}</Dialog.Title>
      <Dialog.Content className="space-y-4">
        <Trans>
          Resend invitation to <b>{invitation.email}</b> ?
        </Trans>
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

export default ResendOrganizationInvitationDialog;
