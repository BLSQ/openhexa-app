import { useTranslation } from "next-i18next";
import { useCallback, useRef, useState } from "react";
import { toast } from "react-toastify";
import { downloadCsvBlob } from "./csv";
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

  // Export the query that produced the current result (a selection may differ from
  // the editor contents; read the ref at call time to avoid needing a re-render).
  // Two paths, chosen by whether the interactive result was truncated:
  //  - Fast: full result already in memory — build the CSV client-side. Instant, no
  //    second round-trip, exports the on-screen snapshot, and cannot fail.
  //  - Heavy: result was capped — re-run server-side (uncapped) and stream to disk.
  const downloadCsv = useCallback(async () => {
    const lastRun = lastRunRef.current;
    if (loading || exporting || !lastRun) {
      return;
    }
    if (result?.success && result.truncated === false) {
      downloadCsvBlob(
        "query-results.csv",
        result.columns ?? [],
        result.rows ?? [],
      );
      return;
    }
    // The heavy path can be slow (`exporting` drives the toolbar affordance) and
    // streams via a hidden iframe whose errors are otherwise silent: downloadQueryCsv
    // resolves only once the download starts and rejects on failure, so surface that.
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
