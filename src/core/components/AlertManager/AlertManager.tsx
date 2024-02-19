import { Portal } from "@headlessui/react";
import { AlertType } from "core/helpers/alert";
import { useListener } from "core/hooks/useEmitter";
import { useState } from "react";
import Alert from "../Alert";

const AlertManager = () => {
  const [alert, setAlert] = useState<null | {
    message: string;
    type?: AlertType;
  }>();

  useListener("displayAlert", (event) => {
    setAlert(event.detail);
  });

  if (!alert) return null;

  return (
    <Portal>
      <Alert type={alert.type} onClose={() => setAlert(null)}>
        <p>{alert.message}</p>
      </Alert>
    </Portal>
  );
};

export default AlertManager;
