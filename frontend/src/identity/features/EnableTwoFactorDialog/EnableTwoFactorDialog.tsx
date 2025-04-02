import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import {
  enableTwoFactor,
  generateChallenge,
  verifyDevice,
} from "identity/helpers/auth";
import { useRouter } from "next/router";

import useMe from "identity/hooks/useMe";
import { useEffect, useState } from "react";
import { useTranslation } from "next-i18next";
import Input from "core/components/forms/Input";
import { ErrorAlert } from "core/components/Alert";

type EnableTwoFactorDialogProps = {
  open: boolean;
  onClose(): void;
};

const EnableTwoFactorDialog = (props: EnableTwoFactorDialogProps) => {
  const { open, onClose } = props;
  const [isVerificationNeeded, setVerificationNeeded] = useState(false);
  const [token, setToken] = useState<string>("");
  const [error, setError] = useState<null | string>(null);
  const { t } = useTranslation();
  const me = useMe();
  const router = useRouter();

  useEffect(() => {
    if (open) {
      setToken("");
      setVerificationNeeded(false);
      setError(null);
    }
  }, [open]);

  const onEnableTwoFactor = async () => {
    const { success, verified } = await enableTwoFactor();
    if (!success) {
      throw new Error("Unable to enable two factor authentication");
    }
    if (verified) {
      router.reload();
    } else {
      setVerificationNeeded(true);
    }
  };

  const onConfirmToken = async () => {
    if (await verifyDevice(token)) {
      router.reload();
    } else {
      setError(t("Invalid code"));
    }
  };

  if (me?.hasTwoFactorEnabled && open) {
    return (
      <ErrorAlert onClose={() => router.reload()}>
        {t("Two-Factor Authentication is already enabled for your account.")}
      </ErrorAlert>
    );
  }

  return (
    <Dialog open={open} onClose={onClose}>
      <Dialog.Title onClose={onClose}>
        {t("Enable Two-Factor Authentication")}
      </Dialog.Title>

      {isVerificationNeeded ? (
        <Dialog.Content className="space-y-4">
          <p>
            {t(
              "Check your inbox and enter the token you received to enable the two-factor authentication.",
            )}
          </p>
          <Input
            placeholder="123456"
            data-testid="token-input"
            type="number"
            required
            value={token}
            onChange={(event) => setToken(event.target.value)}
          />
          <div className="flex items-center justify-between gap-2">
            {error && <span className="text-sm text-red-600">{error}</span>}
            <button
              type="button"
              className="text-blue-600"
              onClick={() => generateChallenge()}
            >
              {t("Send a new code")}
            </button>
          </div>
        </Dialog.Content>
      ) : (
        <Dialog.Content className="space-y-4">
          <p>
            {t(
              "This will enable the two-factor authentication using your email address. A one-time code will be sent to you every time you try to log in.",
            )}
          </p>
        </Dialog.Content>
      )}

      <Dialog.Actions>
        <Button variant="white" onClick={onClose}>
          {t("Cancel")}
        </Button>
        {isVerificationNeeded ? (
          <Button variant="primary" onClick={onConfirmToken} disabled={!token}>
            {t("Confirm")}
          </Button>
        ) : (
          <Button variant="primary" onClick={onEnableTwoFactor}>
            {t("Enable")}
          </Button>
        )}
      </Dialog.Actions>
    </Dialog>
  );
};

export default EnableTwoFactorDialog;
