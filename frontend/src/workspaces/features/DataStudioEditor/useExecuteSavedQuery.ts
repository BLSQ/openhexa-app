import { useCallback, useRef } from "react";
import { useExecuteSavedQueryMutation } from "workspaces/features/SavedQueries/SavedQueries.generated";

type ExecuteSavedQueryVariables = {
  slug: string;
  parameters: Record<string, unknown>;
  maxRows: number;
};

// Runs a saved query by slug with caller-supplied parameters (the templated
// counterpart to useDataStudioQuery). Mirrors its run/retry/result surface so
// DataStudioEditor can swap between the two sources behind one results area.
export const useExecuteSavedQuery = (workspaceSlug: string) => {
  // Results are large and ad-hoc; keep them out of the normalized cache.
  const [execute, { data, loading, error }] = useExecuteSavedQueryMutation({
    fetchPolicy: "no-cache",
  });

  const lastRunRef = useRef<ExecuteSavedQueryVariables | null>(null);

  const result = data?.executeSavedQuery;
  const canExport = Boolean(result?.success && (result.rows?.length ?? 0) > 0);

  const run = useCallback(
    (slug: string, parameters: Record<string, unknown>, maxRows: number) => {
      if (loading) {
        return;
      }
      const variables = { slug, parameters, maxRows };
      lastRunRef.current = variables;
      execute({ variables: { input: { workspaceSlug, ...variables } } });
    },
    [execute, loading, workspaceSlug],
  );

  const retry = useCallback(() => {
    if (loading || !lastRunRef.current) {
      return;
    }
    execute({
      variables: { input: { workspaceSlug, ...lastRunRef.current } },
    });
  }, [execute, loading, workspaceSlug]);

  return { run, retry, result, loading, error, canExport };
};
