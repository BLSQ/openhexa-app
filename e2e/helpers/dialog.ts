import { Locator, Page } from "@playwright/test";

/**
 * The open dialog with this heading. Told apart by it because a closing
 * dialog stays in the DOM for its leave transition, next to the one opening.
 */
export function dialogTitled(page: Page, heading: string | RegExp): Locator {
  return page
    .getByRole("dialog")
    .filter({ has: page.getByRole("heading", { name: heading }) });
}
