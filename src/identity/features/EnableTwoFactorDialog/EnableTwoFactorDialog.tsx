import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import { enableTwoFactor } from "identity/helpers/auth";
import { useRouter } from "next/router";
import Alert from "core/components/Alert";

import { useTranslation } from "react-i18next";
import useMe from "identity/hooks/useMe";

type EnableTwoFactorDialogProps = {
  open: boolean;
  onClose(): void;
};

const EnableTwoFactorDialog = (props: EnableTwoFactorDialogProps) => {
  const { open, onClose } = props;
  const { t } = useTranslation();
  const me = useMe();
  const router = useRouter();

  const onClick = async () => {
    try {
      await enableTwoFactor();
      onClose();
      router.reload();
    } catch (err) {}
  };

  if (me?.hasTwoFactorEnabled && open) {
    return (
      <Alert onClose={() => router.reload()} icon="error">
        {t("Two-Factor Authentication is already enabled for your account.")}
      </Alert>
    );
  }

  return (
    <Dialog open={open} onClose={onClose}>
      <Dialog.Title onClose={onClose}>
        {t("Enable Two-Factor Authentication")}
      </Dialog.Title>

      <Dialog.Content className="space-y-4">
        <p>
          {t(
            "This will enable the two-factor authentication using your email address. A one-time code will be sent to you every time you try to log in."
          )}
        </p>
        <p>{t("You will have to log in again ro your account.")}</p>
      </Dialog.Content>

      <Dialog.Actions>
        <Button variant="white" onClick={onClose}>
          {t("Cancel")}
        </Button>
        <Button variant="primary" onClick={onClick}>
          {t("Enable")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

export default EnableTwoFactorDialog;
