import { Page, expect } from "@playwright/test";

/** What the app's mutations answer, next to whatever they return. */
export type MutationResult = { success: boolean; errors: string[] };

/**
 * Sends a GraphQL operation as the page's signed-in user, through the app's
 * own /graphql/ endpoint. The page must be on the app, for its CSRF cookie.
 * Fails the test on transport errors; returns `data` for the caller to check.
 * `T` is the shape the caller asked for, taken on trust.
 */
export async function graphql<T>(
  page: Page,
  query: string,
  variables: Record<string, unknown> = {},
): Promise<T> {
  const { status, text } = await page.evaluate(
    async ({ query, variables }) => {
      const csrf = document.cookie.match(/csrftoken=([^;]+)/)?.[1] ?? "";
      const res = await fetch("/graphql/", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrf },
        body: JSON.stringify({ query, variables }),
      });
      return { status: res.status, text: await res.text() };
    },
    { query, variables },
  );
  let response: { data: T; errors?: unknown };
  try {
    response = JSON.parse(text);
  } catch {
    throw new Error(
      `/graphql/ answered ${status} with something other than JSON: ${text.slice(0, 500)}`,
    );
  }
  expect(response.errors, JSON.stringify(response.errors)).toBeUndefined();
  return response.data;
}
