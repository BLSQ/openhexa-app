import { Locator, Page } from "@playwright/test";

/**
 * A toast with this text. Toasts auto-close after two seconds and then animate
 * out, so a message raised twice in a row briefly exists twice; the newest one
 * is the one the action just produced.
 */
export function toast(
  page: Page,
  text: string | RegExp,
  { exact = true }: { exact?: boolean } = {},
): Locator {
  return page.getByText(text, { exact }).last();
}
