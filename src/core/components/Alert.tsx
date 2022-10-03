import {
  ExclamationCircleIcon,
  InformationCircleIcon,
  XCircleIcon,
} from "@heroicons/react/24/outline";
import { useTranslation } from "next-i18next";
import { ReactNode, useEffect, useState } from "react";
import Button from "./Button";
import Dialog from "./Dialog";

type AlertProps = {
  icon: "warning" | "error" | "info";
  onClose: () => void;
  children: ReactNode;
};

const Alert = (props: AlertProps) => {
  const { icon, children, onClose } = props;
  const [open, setOpen] = useState(false);
  const { t } = useTranslation();

  useEffect(() => {
    if (!open) setOpen(true);
  }, [open]);

  return (
    <Dialog onClose={onClose} open={open}>
      <Dialog.Content className="flex items-center gap-4">
        {icon === "warning" && (
          <ExclamationCircleIcon className="h-16 w-16 text-amber-400" />
        )}
        {icon === "error" && <XCircleIcon className="h-16 w-16 text-red-400" />}
        {icon === "info" && (
          <InformationCircleIcon className="text-picton-blue h-16 w-16" />
        )}
        <div className="flex-1">{children}</div>
        <Button variant="white" onClick={onClose}>
          {t("Close")}
        </Button>
      </Dialog.Content>
    </Dialog>
  );
};

export default Alert;
