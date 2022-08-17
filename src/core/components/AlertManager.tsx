import { Portal } from "@headlessui/react";
import { AlertType } from "core/helpers/alert";
import { useListener } from "core/hooks/useEmitter";
import { useMemo, useState } from "react";
import Alert from "./Alert";

const AlertManager = () => {
  const [alert, setAlert] = useState<null | {
    message: string;
    type?: AlertType;
  }>();

  useListener("displayAlert", (event) => {
    setAlert(event.detail);
  });
  const icon = useMemo(() => {
    switch (alert?.type) {
      case AlertType.error:
        return "error";
      case AlertType.warning:
        return "warning";
      default:
        return "info";
    }
  }, [alert]);

  if (!alert) return null;

  return (
    <Portal>
      <Alert icon={icon} onClose={() => setAlert(null)}>
        <p>{alert.message}</p>
      </Alert>
    </Portal>
  );
};

export default AlertManager;
