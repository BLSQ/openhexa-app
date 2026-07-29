import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useCallback, useEffect, useRef } from "react";

export interface NavigationWarningProps {
  enabled: boolean;
  message?: string;
}

/**
 * Warns the user before leaving the page while `enabled` is true, covering
 * in-app navigation, browser back/forward and tab close/reload.
 *
 * Returns `navigateWithoutWarning` for navigations the app performs itself and
 * must not be prompted about (e.g. redirecting to a page right after saving).
 *
 * @example
 * const { navigateWithoutWarning } = useNavigationWarning({
 *   enabled: modifiedFiles.size > 0,
 *   message: t("You have unsaved changes. Leave anyway?"),
 * });
 */
export default function useNavigationWarning({
  enabled,
  message,
}: NavigationWarningProps) {
  const router = useRouter();
  const { t } = useTranslation();

  const defaultMessage = t("You have unsaved changes. Leave anyway?");

  // Listeners subscribe once per route and read the latest values through refs:
  // `enabled` flips on every keystroke of an edited buffer, so keeping it in the
  // effect dependencies would re-subscribe on each one.
  const enabledRef = useRef(enabled);
  const messageRef = useRef(message || defaultMessage);
  const pathRef = useRef(router.asPath);
  const bypassRef = useRef(false);
  // History entry of the guarded page, replayed to restore the address bar when
  // the user cancels a back/forward: the browser has already moved it by then.
  const historyStateRef = useRef<History["state"]>(null);

  useEffect(() => {
    enabledRef.current = enabled;
    messageRef.current = message || defaultMessage;
    pathRef.current = router.asPath;
  });

  const isGuarded = () => enabledRef.current && !bypassRef.current;
  const userConfirmedLeave = () => window.confirm(messageRef.current);

  const onWindowClose = useCallback((event: BeforeUnloadEvent) => {
    if (!isGuarded()) {
      return;
    }
    event.preventDefault();
    // Ignored by current browsers, which show their own wording, but still the
    // trigger for older ones.
    event.returnValue = messageRef.current;
  }, []);

  const onNavigation = useCallback(
    (url: string, { shallow }: { shallow: boolean }) => {
      // A shallow navigation only rewrites the URL: the page stays mounted and
      // the buffer with it, so there is nothing to warn about.
      if (shallow || !isGuarded() || url === pathRef.current) {
        return;
      }
      if (userConfirmedLeave()) {
        return;
      }
      router.events.emit("routeChangeError", messageRef.current, url, {
        shallow,
      });
      // The pages router has no cancel API: throwing out of the
      // routeChangeStart handler is the only way to abort the transition.
      throw "Route change aborted";
    },
    [router.events],
  );

  // `beforePopState` receives the popped history entry. Returning false makes
  // Next skip the route change, which is what keeps the current page rendered;
  // routeChangeStart never fires, so the abort above cannot cover this path.
  const onPopState = useCallback(({ as }: { as: string }) => {
    if (!isGuarded() || as === pathRef.current) {
      return true;
    }
    if (userConfirmedLeave()) {
      return true;
    }
    if (historyStateRef.current) {
      window.history.pushState(historyStateRef.current, "", pathRef.current);
    }
    return false;
  }, []);

  useEffect(() => {
    const captureHistoryState = () => {
      historyStateRef.current = window.history.state;
    };
    captureHistoryState();

    window.addEventListener("beforeunload", onWindowClose);
    router.events.on("routeChangeStart", onNavigation);
    router.events.on("routeChangeComplete", captureHistoryState);
    router.beforePopState(onPopState);

    return () => {
      window.removeEventListener("beforeunload", onWindowClose);
      router.events.off("routeChangeStart", onNavigation);
      router.events.off("routeChangeComplete", captureHistoryState);
      // The router holds a single popstate callback and offers no way to
      // unregister it, so hand it back a pass-through on unmount.
      router.beforePopState(() => true);
    };
  }, [onNavigation, onPopState, onWindowClose, router]);

  const navigateWithoutWarning = useCallback(
    (url: string) => {
      bypassRef.current = true;
      return router.push(url).finally(() => {
        bypassRef.current = false;
      });
    },
    [router],
  );

  return { navigateWithoutWarning };
}
