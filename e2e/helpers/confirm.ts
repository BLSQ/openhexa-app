import { Page } from "@playwright/test";

/**
 * Several destructive actions in the app confirm with `window.confirm`.
 * Playwright dismisses native dialogs unless something handles them, which would
 * silently cancel the action, so arm this before clicking.
 */
export function acceptNextConfirm(page: Page) {
  page.once("dialog", (dialog) => dialog.accept());
}

/** A name unique to this run, so parallel runs and retries cannot collide. */
export function uniqueName(prefix: string) {
  return `${prefix}-${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}`;
}
