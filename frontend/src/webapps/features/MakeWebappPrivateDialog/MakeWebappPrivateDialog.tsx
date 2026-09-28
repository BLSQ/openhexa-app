import { ExclamationTriangleIcon } from "@heroicons/react/24/outline";
import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Spinner from "core/components/Spinner";
import { Trans, useTranslation } from "next-i18next";
import { useState } from "react";

type MakeWebappPrivateDialogProps = {
  open: boolean;
  onClose: () => void;
  onConfirm: () => Promise<void>;
  webapp: {
    name: string;
  };
};

const MakeWebappPrivateDialog = ({
  open,
  onClose,
  onConfirm,
  webapp,
}: MakeWebappPrivateDialogProps) => {
  const { t } = useTranslation();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleConfirm = async () => {
    setIsSubmitting(true);
    try {
      await onConfirm();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <Dialog.Title>{t("Make this web app private")}</Dialog.Title>
      <Dialog.Content>
        <div className="flex gap-3 rounded-md border border-amber-200 bg-amber-50 p-3">
          <ExclamationTriangleIcon className="h-5 w-5 flex-none text-amber-600" />
          <div className="space-y-1 text-sm text-amber-900">
            <p className="font-medium">
              <Trans>
                <b>{webapp.name}</b> will no longer be accessible to users
                without an OpenHEXA account.
              </Trans>
            </p>
            <p>
              {t(
                "Visitors will have to sign in to open it. Anyone you shared the public link with will lose access.",
              )}
            </p>
          </div>
        </div>
      </Dialog.Content>
      <Dialog.Actions>
        <Button variant="white" onClick={onClose} disabled={isSubmitting}>
          {t("Cancel")}
        </Button>
        <Button onClick={handleConfirm} disabled={isSubmitting}>
          {isSubmitting && <Spinner size="xs" className="mr-1" />}
          {t("Make private")}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

export default MakeWebappPrivateDialog;
