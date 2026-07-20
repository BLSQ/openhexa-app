import { useTranslation } from "next-i18next";
import { useCallback, useRef, useState } from "react";
import { toast } from "react-toastify";
import { buildCsv, downloadCsvBlob } from "./csv";
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
  // True while a server-side (heavy) export is in flight; the client-side fast
  // path is synchronous and never sets it.
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

  // Export the query that produced the current result (which may be a selection,
  // and may differ from the editor contents). Two paths:
  //  - Fast: the interactive run returned the *whole* result (not truncated), so
  //    every row is already in memory. Build the CSV client-side — instant, no
  //    second DB round-trip, exports the exact on-screen snapshot, and cannot
  //    fail. Memory is bounded by the interactive row cap that produced it.
  //  - Heavy: the result was capped, so the full set is larger than we hold.
  //    Re-run server-side and stream the entire set to disk. maxRows (a
  //    display-only cap) is not forwarded.
  // Reading the ref at call time avoids depending on a re-render to see the
  // latest query.
  const downloadCsv = useCallback(async () => {
    const lastRun = lastRunRef.current;
    if (loading || exporting || !lastRun) {
      return;
    }
    if (result?.success && result.truncated === false) {
      downloadCsvBlob(
        "query-results.csv",
        buildCsv(result.columns ?? [], result.rows ?? []),
      );
      return;
    }
    // The heavy path streams via a hidden iframe, whose errors are otherwise
    // silent; downloadQueryCsv resolves only once the download starts and
    // rejects on failure, so surface that to the user.
    setExporting(true);
    try {
      await downloadQueryCsv(lastRun.workspaceSlug, lastRun.query);
    } catch {
      toast.error(t("Could not export the query results. Please try again."));
    } finally {
      setExporting(false);
    }
  }, [loading, exporting, result, t]);

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
