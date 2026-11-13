import { Locator, Page } from "@playwright/test";

/**
 * The `<dd>` of a `<dt>`/`<dd>` pair, by its term: the cards' read-only
 * values, and the form controls that have no accessible name of their own.
 * `exact` matches the whole term, for one that is contained in another's.
 */
export function definition(
  scope: Page | Locator,
  term: string,
  { exact = false }: { exact?: boolean } = {},
): Locator {
  return scope
    .getByRole("term")
    .filter({
      hasText: exact
        ? new RegExp(`^${term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}$`)
        : term,
    })
    .locator("xpath=following-sibling::dd");
}
