import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useCallback, useEffect, useRef } from "react";

// Next emits `routeChangeStart` outside its own try/catch, so aborting from a
// listener always surfaces as an unhandled rejection on the promise returned by
// `router.push`. That is expected rather than a fault, and is filtered out in
// sentry.client.config.ts by this message.
export class NavigationAbortedError extends Error {
  constructor() {
    super("Route change aborted by the unsaved changes guard");
    this.name = "NavigationAbortedError";
  }
}

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

  const path = router.asPath;
  const warning = message || t("You have unsaved changes. Leave anyway?");

  // Driven by events rather than by rendering, so neither can be a plain value:
  // `bypassed` is flipped around a navigation the app performs itself, and
  // `historyEntry` is read off the browser as it moves.
  const bypassed = useRef(false);
  const historyEntry = useRef<History["state"]>(null);

  useEffect(() => {
    // Nothing is registered while there is nothing to lose. A `beforeunload`
    // listener alone makes the page ineligible for the browser's back/forward
    // cache in some browsers, which would cost every visitor a slower Back.
    if (!enabled) {
      return;
    }

    const captureHistoryEntry = () => {
      historyEntry.current = window.history.state;
    };
    captureHistoryEntry();

    const onWindowClose = (event: BeforeUnloadEvent) => {
      if (bypassed.current) {
        return;
      }
      event.preventDefault();
      // Ignored by current browsers, which show their own wording, but still the
      // trigger for older ones.
      event.returnValue = warning;
    };

    const onNavigation = (url: string, { shallow }: { shallow: boolean }) => {
      // A shallow navigation only rewrites the URL: the page stays mounted and
      // the buffer with it, so there is nothing to warn about.
      if (bypassed.current || shallow || url === path) {
        return;
      }
      if (window.confirm(warning)) {
        return;
      }
      router.events.emit("routeChangeError", warning, url, { shallow });
      // The pages router has no cancel API: throwing out of the
      // routeChangeStart handler is the only way to abort the transition.
      throw new NavigationAbortedError();
    };

    // `beforePopState` receives the popped history entry. Returning false makes
    // Next skip the route change, which is what keeps the current page rendered;
    // routeChangeStart never fires, so the abort above cannot cover this path.
    const onPopState = ({ as }: { as: string }) => {
      if (bypassed.current || as === path) {
        return true;
      }
      if (window.confirm(warning)) {
        return true;
      }
      // The browser has already moved, so put the guarded entry back to keep the
      // address bar in step with what is still on screen.
      window.history.pushState(historyEntry.current, "", path);
      return false;
    };

    window.addEventListener("beforeunload", onWindowClose);
    router.events.on("routeChangeStart", onNavigation);
    router.events.on("routeChangeComplete", captureHistoryEntry);
    router.beforePopState(onPopState);

    return () => {
      window.removeEventListener("beforeunload", onWindowClose);
      router.events.off("routeChangeStart", onNavigation);
      router.events.off("routeChangeComplete", captureHistoryEntry);
      // The router holds a single popstate callback and offers no way to
      // unregister it, so hand it back a pass-through.
      router.beforePopState(() => true);
    };
    // `react-hooks/exhaustive-deps` is off in this repo, so anything the
    // listeners read out of a render has to be listed here by hand. Miss one and
    // the guard silently keeps acting on the values it saw when it was armed.
  }, [enabled, warning, path, router]);

  const navigateWithoutWarning = useCallback(
    (url: string) => {
      bypassed.current = true;
      return router.push(url).finally(() => {
        bypassed.current = false;
      });
    },
    [router],
  );

  return { navigateWithoutWarning };
}
