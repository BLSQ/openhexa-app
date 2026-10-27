import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Spinner from "core/components/Spinner";
import { WebappType } from "graphql/types";
import { useTranslation } from "next-i18next";
import { useState } from "react";

type MakeWebappPrivateDialogProps = {
  open: boolean;
  onClose: () => void;
  onConfirm: () => Promise<void>;
  webapp: {
    type: WebappType;
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
    <Dialog open={open} onClose={onClose} maxWidth="max-w-xl">
      <Dialog.Title onClose={onClose}>
        {t("Make this web app private?")}
      </Dialog.Title>
      <Dialog.Content className="space-y-3 text-sm text-gray-700">
        <p>
          {t(
            "The public link will stop working: visitors without an OpenHEXA account will be asked to sign in. Workspace members keep access.",
          )}
        </p>
        {webapp.type === WebappType.Static && (
          <p>
            {t(
              "API requests will again run on behalf of the signed-in member, limited to the operations enabled under Workspace permissions.",
            )}
          </p>
        )}
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
