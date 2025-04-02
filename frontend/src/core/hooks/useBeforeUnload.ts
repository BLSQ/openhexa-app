import { useRouter } from "next/router";
import { useCallback, useEffect } from "react";

const useBeforeUnload = (cancel: () => void | true | false | string) => {
  // prompt the user if they try and leave with unsaved changes
  const router = useRouter();
  const defaultMessage =
    "You may lose unsaved changes if you leave this page. Are you sure you wish to leave this page?";

  const onWindowClose = useCallback(
    (e: BeforeUnloadEvent) => {
      const cancelMessage = cancel();
      if (!cancelMessage) {
        return;
      }
      e.preventDefault();
      e.returnValue = cancelMessage || defaultMessage;
      return e;
    },
    [cancel],
  );

  const onNavigation = useCallback(() => {
    const cancelMessage = cancel();
    if (!cancelMessage) return;

    if (
      window.confirm(
        typeof cancelMessage === "string" ? cancelMessage : defaultMessage,
      )
    )
      return;
    router.events.emit("routeChangeError");
    throw "Route change aborted";
  }, [cancel, router.events]);

  useEffect(() => {
    window.addEventListener("beforeunload", onWindowClose);
    router.events.on("routeChangeStart", onNavigation);

    return () => {
      window.removeEventListener("beforeunload", onWindowClose);
      router.events.off("routeChangeStart", onNavigation);
    };
  }, [onNavigation, onWindowClose, router.events]);
};

export default useBeforeUnload;
