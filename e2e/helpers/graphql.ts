import { Page, expect } from "@playwright/test";

/**
 * Sends a GraphQL operation as the page's signed-in user, through the app's
 * own /graphql/ endpoint. The page must be on the app, for its CSRF cookie.
 * Fails the test on transport errors; returns `data` for the caller to check.
 */
export async function graphql<T = any>(
  page: Page,
  query: string,
  variables: Record<string, unknown> = {},
): Promise<T> {
  const response = await page.evaluate(
    async ({ query, variables }) => {
      const csrf = document.cookie.match(/csrftoken=([^;]+)/)?.[1] ?? "";
      const res = await fetch("/graphql/", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrf },
        body: JSON.stringify({ query, variables }),
      });
      return res.json();
    },
    { query, variables },
  );
  expect(response?.errors, JSON.stringify(response?.errors)).toBeUndefined();
  return response.data;
}
