import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import { useCallback, useEffect, useRef } from "react";

export interface NavigationWarningProps {
  enabled: boolean;
  message?: string;
}

// Everything the listeners read. They subscribe once per route, so they cannot
// read props or state directly: `enabled` flips on every keystroke of an edited
// buffer, and re-subscribing on each one would be wasteful. They read this
// mutable record instead, which is refreshed in place on every render.
type GuardState = {
  enabled: boolean;
  message: string;
  path: string;
  // Set while the app navigates on its own behalf (see navigateWithoutWarning),
  // and while the guarded page is being left for a page that replaces it.
  bypassed: boolean;
  // History entry of the guarded page, replayed to restore the address bar when
  // the user cancels a back/forward: the browser has already moved it by then.
  historyEntry: History["state"];
};

// Deliberately outside the hook: at module scope these cannot reach a prop or a
// state value even by accident, which is what keeps them safe to call from
// listeners that were memoized on the first render. Inside the hook, one edit
// reading `enabled` directly would freeze the guard on its first-render value —
// silently, since this repo turns `react-hooks/exhaustive-deps` off.
const isGuarded = (state: GuardState) => state.enabled && !state.bypassed;

const userConfirmedLeave = (state: GuardState) =>
  window.confirm(state.message);

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

  const state = useRef<GuardState>({
    enabled,
    message: message || defaultMessage,
    path: router.asPath,
    bypassed: false,
    historyEntry: null,
  }).current;

  // Field by field: `bypassed` and `historyEntry` are driven by events rather
  // than by rendering, so replacing the whole record here would clobber them.
  useEffect(() => {
    state.enabled = enabled;
    state.message = message || defaultMessage;
    state.path = router.asPath;
  });

  const onWindowClose = useCallback(
    (event: BeforeUnloadEvent) => {
      if (!isGuarded(state)) {
        return;
      }
      event.preventDefault();
      // Ignored by current browsers, which show their own wording, but still the
      // trigger for older ones.
      event.returnValue = state.message;
    },
    [state],
  );

  const onNavigation = useCallback(
    (url: string, { shallow }: { shallow: boolean }) => {
      // A shallow navigation only rewrites the URL: the page stays mounted and
      // the buffer with it, so there is nothing to warn about.
      if (shallow || !isGuarded(state) || url === state.path) {
        return;
      }
      if (userConfirmedLeave(state)) {
        return;
      }
      router.events.emit("routeChangeError", state.message, url, { shallow });
      // The pages router has no cancel API: throwing out of the
      // routeChangeStart handler is the only way to abort the transition.
      throw "Route change aborted";
    },
    [router.events, state],
  );

  // `beforePopState` receives the popped history entry. Returning false makes
  // Next skip the route change, which is what keeps the current page rendered;
  // routeChangeStart never fires, so the abort above cannot cover this path.
  const onPopState = useCallback(
    ({ as }: { as: string }) => {
      if (!isGuarded(state) || as === state.path) {
        return true;
      }
      if (userConfirmedLeave(state)) {
        return true;
      }
      if (state.historyEntry) {
        window.history.pushState(state.historyEntry, "", state.path);
      }
      return false;
    },
    [state],
  );

  useEffect(() => {
    const captureHistoryEntry = () => {
      state.historyEntry = window.history.state;
    };
    captureHistoryEntry();

    window.addEventListener("beforeunload", onWindowClose);
    router.events.on("routeChangeStart", onNavigation);
    router.events.on("routeChangeComplete", captureHistoryEntry);
    router.beforePopState(onPopState);

    return () => {
      window.removeEventListener("beforeunload", onWindowClose);
      router.events.off("routeChangeStart", onNavigation);
      router.events.off("routeChangeComplete", captureHistoryEntry);
      // The router holds a single popstate callback and offers no way to
      // unregister it, so hand it back a pass-through on unmount.
      router.beforePopState(() => true);
    };
  }, [onNavigation, onPopState, onWindowClose, router, state]);

  const navigateWithoutWarning = useCallback(
    (url: string) => {
      state.bypassed = true;
      return router.push(url).finally(() => {
        state.bypassed = false;
      });
    },
    [router, state],
  );

  return { navigateWithoutWarning };
}
