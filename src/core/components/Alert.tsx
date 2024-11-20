import {
  CheckCircleIcon,
  ExclamationCircleIcon,
  InformationCircleIcon,
  XCircleIcon,
} from "@heroicons/react/24/outline";
import { useTranslation } from "next-i18next";
import { ReactNode, useEffect, useState } from "react";
import Button from "./Button/Button";
import Dialog from "./Dialog";

type AlertProps = {
  icon: ReactNode;
  onClose: () => void;
  children: ReactNode;
};

const Alert = ({ icon, children, onClose }: AlertProps) => {
  const [open, setOpen] = useState(false);
  const { t } = useTranslation();

  useEffect(() => {
    if (!open) setOpen(true);
  }, [open]);

  return (
    <Dialog onClose={onClose} open={open}>
      <Dialog.Content className="flex items-center gap-4">
        {icon}
        <div className="flex-1">{children}</div>
        <Button variant="white" onClick={onClose}>
          {t("Close")}
        </Button>
      </Dialog.Content>
    </Dialog>
  );
};

const createAlert = (icon: ReactNode) => {
  return function GenericAlert({
    children,
    ...otherProps
  }: Omit<AlertProps, "icon">) {
    return (
      <Alert {...otherProps} icon={icon}>
        {children}
      </Alert>
    );
  };
};

export const ErrorAlert = createAlert(
  <XCircleIcon className="h-16 w-16 text-red-400" />,
);
export const WarningAlert = createAlert(
  <ExclamationCircleIcon className="h-16 w-16 text-amber-400" />,
);
export const SuccessAlert = createAlert(
  <CheckCircleIcon className="h-16 w-16 text-green-400" />,
);
export const InfoAlert = createAlert(
  <InformationCircleIcon className="h-16 w-16 text-picton-blue" />,
);
