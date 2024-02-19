export enum AlertType {
  success,
  error,
  info,
  warning,
}

export function displayAlert(message: string, type?: AlertType) {
  if (!window) {
    console.warn("displayAlert cannot be called on the server.");
    return;
  }
  const event = new CustomEvent("displayAlert", {
    detail: {
      message,
      type: type ?? AlertType.info,
    },
  });

  window.dispatchEvent(event);
}
