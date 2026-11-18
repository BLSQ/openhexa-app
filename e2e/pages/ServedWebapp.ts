import { Locator, Page } from "@playwright/test";

/**
 * Builds an index.html that shows `marker` and asks the OpenHEXA API, through
 * the web app's own /graphql/ proxy, who is signed in -- writing the outcome
 * into the page so a test can read whether API access was granted.
 */
export function staticAppHtml(marker: string): string {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>${marker}</title>
</head>
<body>
  <h1>${marker}</h1>
  <p id="api">API pending</p>
  <script>
    fetch("/graphql/", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: "{ me { user { email } } }" }),
    })
      .then(function (response) {
        return response.text().then(function (text) {
          var body;
          try { body = JSON.parse(text); } catch (e) { body = { errors: [{ message: text }] }; }
          document.getElementById("api").textContent = body.data
            ? "API user: " + body.data.me.user.email
            : "API error " + response.status + ": " + body.errors[0].message;
        });
      })
      .catch(function (error) {
        document.getElementById("api").textContent = "API failed: " + error;
      });
  </script>
</body>
</html>
`;
}

/**
 * Builds an index.html that shows `marker` and runs the saved query named in
 * its own address (`?query=<slug>`, with the query's parameter values as JSON
 * in `&parameters=` if it takes any) through the web app's /graphql/ proxy,
 * writing the names it got back, or why it got none, into the page.
 */
export function savedQueryAppHtml(marker: string): string {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>${marker}</title>
</head>
<body>
  <h1>${marker}</h1>
  <p id="api">API pending</p>
  <script>
    var search = new URLSearchParams(window.location.search);
    var slug = search.get("query");
    function show(text) {
      document.getElementById("api").textContent = text;
    }
    // The editor previews the app at its bare address, with no query to run.
    if (!slug) {
      show("No query asked for");
    } else {
      fetch("/graphql/", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: "query ($input: ExecuteSavedQueryInput!) { executeSavedQuery(input: $input) { success errors rows } }",
          variables: {
            input: {
              slug: slug,
              perPage: 100,
              parameters: JSON.parse(search.get("parameters") || "{}"),
            },
          },
        }),
      })
        .then(function (response) {
          return response.text().then(function (text) {
            var body;
            try { body = JSON.parse(text); } catch (e) { body = { errors: [{ message: text }] }; }
            var result = body.data && body.data.executeSavedQuery;
            show(!result
              ? "API error " + response.status + ": " + body.errors[0].message
              : result.success
                ? "Query rows (" + result.rows.length + "): " + result.rows.map(function (row) { return row.name; }).join(", ")
                : "Query refused: " + result.errors.join(", "));
          });
        })
        .catch(function (error) {
          show("API failed: " + error);
        });
    }
  </script>
</body>
</html>
`;
}

/** The address at which an app built by `savedQueryAppHtml` runs `slug`. */
export function savedQueryAppUrl(
  appUrl: string,
  slug: string,
  parameters?: Record<string, unknown>,
): string {
  const url = new URL(appUrl);
  url.searchParams.set("query", slug);
  if (parameters) {
    url.searchParams.set("parameters", JSON.stringify(parameters));
  }
  return url.href;
}

/** A static web app as its visitors see it, on its own subdomain. */
export class ServedWebapp {
  constructor(private readonly page: Page) {}

  async goto(url: string) {
    return this.page.goto(url);
  }

  heading(text: string): Locator {
    return this.page.getByRole("heading", { name: text, level: 1 });
  }

  text(text: string): Locator {
    return this.page.getByText(text);
  }

  /** Written by the script in `staticAppHtml` or `savedQueryAppHtml`. */
  get apiResult(): Locator {
    return this.page.locator("#api");
  }

  /** Added to public apps for visitors who are not signed in. */
  get poweredByBanner(): Locator {
    return this.page.getByRole("link", { name: "OpenHEXA" });
  }

  /** What the auth-token view answers a signed-in user without access. */
  get forbidden(): Locator {
    return this.page.getByText("Forbidden", { exact: true });
  }

  get loginHeading(): Locator {
    return this.page.getByRole("heading", { name: "Sign in" });
  }
}
