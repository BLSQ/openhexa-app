import { gql } from "@apollo/client";
import Dialog from "core/components/Dialog";
import useCacheKey from "core/hooks/useCacheKey";
import { useState } from "react";
import { useResendOrganizationInvitationMutation } from "../OrganizationInvitations.generated";
import { ResendOrganizationInvitationError } from "graphql/types";
import { useTranslation } from "next-i18next";
import Button from "core/components/Button/Button";
import Spinner from "core/components/Spinner";

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
  const [resendOrganizationInvitation] = useResendOrganizationInvitationMutation();
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

export default ResendOrganizationInvitationDialog;