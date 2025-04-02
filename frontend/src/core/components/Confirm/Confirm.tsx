import { ReactNode, useState } from "react";
import Dialog from "../Dialog";
import Button from "../Button";
import { useTranslation } from "react-i18next";

type ConfirmProps = {
  title?: string;
  children: string | ReactNode | ReactNode[];
  onConfirm: () => void;
  onCancel?: () => void;
  confirmButtonText?: string;
  cancelButtonText?: string;
};

const Confirm: React.FC<ConfirmProps> = (props) => {
  const { t } = useTranslation();
  const {
    title,
    children,
    onConfirm,
    onCancel,
    confirmButtonText = t("Confirm"),
    cancelButtonText = t("Cancel"),
  } = props;

  const [open, setOpen] = useState(false);
  const handleClose = () => {
    setOpen(false);
    if (onCancel) {
      onCancel();
    }
  };
  return (
    <Dialog open={open} onClose={handleClose}>
      {title && <Dialog.Title onClose={handleClose}>{title}</Dialog.Title>}

      <Dialog.Content>{children}</Dialog.Content>

      <Dialog.Actions>
        {onCancel && (
          <Button onClick={onCancel} variant={"outlined"}>
            {cancelButtonText}
          </Button>
        )}
        <Button onClick={onConfirm}>{confirmButtonText}</Button>
      </Dialog.Actions>
    </Dialog>
  );
};

export default Confirm;
