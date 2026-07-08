import { useCallback, useRef } from "react";
import { useExecuteWorkspaceSqlLazyQuery } from "./DataStudioEditor.generated";

type DataStudioQueryVariables = {
  workspaceSlug: string;
  query: string;
  maxRows: number;
};

// Owns the data orchestration for the SQL editor: running a query, retrying the
// exact one that failed, and exposing the derived result/loading/error state.
// Keeping this out of the component lets the run/retry semantics be tested on
// their own and keeps DataStudioEditor focused on presentation.
export const useDataStudioQuery = (workspaceSlug: string) => {
  // Results are large, ad-hoc, and never read from the cache elsewhere; skip
  // normalisation so big result sets are not retained for the page lifetime.
  const [execute, { data, loading, error }] = useExecuteWorkspaceSqlLazyQuery({
    fetchPolicy: "no-cache",
  });

  // The last executed variables, so Retry re-runs exactly what failed — which
  // may be a selection, and may differ from the current editor contents.
  // maxRows is captured here too: retry re-runs what failed, not whatever the
  // row selector happens to hold now.
  const lastRunRef = useRef<DataStudioQueryVariables | null>(null);

  const result = data?.workspace?.database?.executeSQL;
  const canExport = Boolean(result?.success && (result.rows?.length ?? 0) > 0);

  const run = useCallback(
    (sql: string, maxRows: number) => {
      const trimmed = sql.trim();
      if (loading || !trimmed) {
        return;
      }
      const variables = { workspaceSlug, query: trimmed, maxRows };
      lastRunRef.current = variables;
      execute({ variables });
    },
    [execute, loading, workspaceSlug],
  );

  const retry = useCallback(() => {
    if (loading || !lastRunRef.current) {
      return;
    }
    execute({ variables: lastRunRef.current });
  }, [execute, loading]);

  return { run, retry, result, loading, error, canExport };
};
