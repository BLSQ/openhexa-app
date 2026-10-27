// Referenced both from the section's help menu and from the hint on the results
// card, which are the two ways a user finds the chart column conventions.
export const SQL_WIDGETS_DOCS_URL = "https://docs.openhexa.com/sql-widgets/";

// Row caps offered to an interactive run, in the editor and on a public
// query's page alike; the first one is the default.
export const MAX_ROWS_OPTIONS = [50, 100, 500, 1000, 10_000];

// Route builders for the Data Studio section. Centralised so the base path and
// its URL-encoding live in one place, shared by the layout, the saved-queries
// list, the editor hook and the pages.
export const dataStudioRoutes = (workspaceSlug: string) => {
  const base = `/workspaces/${encodeURIComponent(workspaceSlug)}/data-studio`;
  return {
    base,
    queries: `${base}/queries`,
    // Saved queries are addressed by slug: it is stable across renames and
    // readable in the URL, and it is the same identifier web apps use.
    query: (slug: string) => `${base}/queries/${encodeURIComponent(slug)}`,
  };
};
