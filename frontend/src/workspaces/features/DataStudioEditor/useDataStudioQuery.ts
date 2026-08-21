import { useTranslation } from "next-i18next";
import { useCallback, useRef, useState } from "react";
import { toast } from "react-toastify";
import { useExecuteWorkspaceSqlLazyQuery } from "./DataStudioEditor.generated";
import { downloadQueryCsv } from "./downloadQueryCsv";

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
  const { t } = useTranslation();
  // Results are large, ad-hoc, and never read from the cache elsewhere; skip
  // normalisation so big result sets are not retained for the page lifetime.
  const [execute, { data, loading, error }] = useExecuteWorkspaceSqlLazyQuery({
    fetchPolicy: "no-cache",
  });
  // True while an export is in flight, driving the toolbar's in-progress affordance.
  const [exporting, setExporting] = useState(false);

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

  // Export the query that produced the current result (a selection may differ from
  // the editor contents; read the ref at call time to avoid needing a re-render).
  // The full result is re-run server-side (uncapped) and streamed straight to disk.
  // downloadQueryCsv resolves once the download starts and rejects on failure — the
  // hidden iframe it streams through is otherwise silent — so surface any error.
  const downloadCsv = useCallback(async () => {
    const lastRun = lastRunRef.current;
    if (loading || exporting || !lastRun) {
      return;
    }
    setExporting(true);
    try {
      await downloadQueryCsv(lastRun.workspaceSlug, lastRun.query);
    } catch {
      toast.error(t("Could not export the query results. Please try again."));
    } finally {
      setExporting(false);
    }
  }, [loading, exporting, t]);

  return {
    run,
    retry,
    downloadCsv,
    exporting,
    result,
    loading,
    error,
    canExport,
  };
};
