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
