import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Input from "core/components/forms/Input";
import { disableTwoFactor, generateChallenge } from "identity/helpers/auth";
import useMe from "identity/hooks/useMe";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import { useTranslation } from "next-i18next";
import { ErrorAlert } from "core/components/Alert";

type DisableTwoFactorDialogProps = {
  open: boolean;
  onClose(): void;
};

const DisableTwoFactorDialog = (props: DisableTwoFactorDialogProps) => {
  const { open, onClose } = props;
  const { t } = useTranslation();
  const me = useMe();
  const router = useRouter();
  const [challengeGenerated, setChallengeGenerated] = useState(false);
  const [token, setToken] = useState<string>("");

  useEffect(() => {
    if (open) {
      setToken("");
      setChallengeGenerated(false);
    }
  }, [open]);

  const onDisableClick = async () => {
    if (!challengeGenerated) {
      await generateChallenge();
      setChallengeGenerated(true);
    } else if (token) {
      await disableTwoFactor(token);
      onClose();
      await router.reload();
    }
  };

  if (!me?.hasTwoFactorEnabled && open) {
    return (
      <ErrorAlert onClose={() => router.reload()}>
        {t("Two-Factor Authentication is not enabled for your account")}
      </ErrorAlert>
    );
  }
  return (
    <Dialog open={open} onClose={onClose}>
      <Dialog.Title onClose={onClose}>
        {t("Disable Two-Factor Authentication")}
      </Dialog.Title>
      {!challengeGenerated ? (
        <Dialog.Content>
          <p>
            {t(
              "Are you sure to disable the two-factor authentication for your account?",
            )}
          </p>
        </Dialog.Content>
      ) : (
        <Dialog.Content className="space-y-4">
          <p>
            {t(
              "Check your inbox and type the token you received to disable the two-factor authentication.",
            )}
          </p>
          <Input
            placeholder="123456"
            type="number"
            required
            value={token}
            onChange={(event) => setToken(event.target.value)}
          />
        </Dialog.Content>
      )}
      <Dialog.Actions>
        <Button variant="white" onClick={onClose}>
          {t("Cancel")}
        </Button>
        <Button
          variant="primary"
          onClick={onDisableClick}
          disabled={challengeGenerated && !token}
        >
          {t("Disable")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

export default DisableTwoFactorDialog;
