import { useRouter } from "next/router";
import { useCallback, useEffect } from "react";
import { useTranslation } from "react-i18next";

export interface NavigationWarningProps {
  when?: () => boolean;
  message?: string;
}

/**
 * Hook that warns users before navigating away when the `when` condition is met.
 * @example
 * useNavigationWarning({
 *   when: () => modifiedFiles.size > 0,
 *   message: t("You have unsaved changes. Leave anyway?"),
 * });
 */
export default function useNavigationWarning({
  when,
  message,
}: NavigationWarningProps) {
  const router = useRouter();
  const { t } = useTranslation();

  message = message || t("You have unsaved changes. Leave anyway?");

  const onWindowClose = useCallback(
    (e: BeforeUnloadEvent) => {
      if (!when || !when()) return;
      e.preventDefault();
      return message;
    },
    [when, message],
  );

  const onNavigation = useCallback((url: string, { shallow }: { shallow: boolean }) => {
    if (!when || !when()) return;
    if (window.confirm(message)) return;
    router.events.emit("routeChangeError", message, url, { shallow });
    throw "Route change aborted";
  }, [when, message, router.events]);

  useEffect(() => {
    window.addEventListener("beforeunload", onWindowClose);
    router.events.on("routeChangeStart", onNavigation);

    return () => {
      window.removeEventListener("beforeunload", onWindowClose);
      router.events.off("routeChangeStart", onNavigation);
    };
  }, [onNavigation, onWindowClose, router.events]);
}