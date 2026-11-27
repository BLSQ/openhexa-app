import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import { useTranslation } from "next-i18next";
import { ReactNode } from "react";

type ConfirmSharingDialogProps = {
  open: boolean;
  title: ReactNode;
  confirmLabel: ReactNode;
  saving?: boolean;
  confirmDisabled?: boolean;
  onConfirm: () => void;
  onClose: () => void;
  children?: ReactNode;
};

// Changes in who can reach a resource (going public, breaking a link that may be
// in use, taking it from colleagues) are never one-click actions.
const ConfirmSharingDialog = ({
  open,
  title,
  confirmLabel,
  saving = false,
  confirmDisabled = false,
  onConfirm,
  onClose,
  children,
}: ConfirmSharingDialogProps) => {
  const { t } = useTranslation();
  const close = () => !saving && onClose();

  return (
    <Dialog open={open} onClose={close} maxWidth="max-w-lg">
      <Dialog.Title onClose={close}>{title}</Dialog.Title>
      <Dialog.Content className="space-y-4 text-sm text-gray-600">
        {children}
      </Dialog.Content>
      <Dialog.Actions>
        <Button variant="outlined" onClick={close} disabled={saving}>
          {t("Cancel")}
        </Button>
        <Button onClick={onConfirm} disabled={saving || confirmDisabled}>
          {confirmLabel}
        </Button>
      </Dialog.Actions>
    </Dialog>
  );
};

export default ConfirmSharingDialog;
