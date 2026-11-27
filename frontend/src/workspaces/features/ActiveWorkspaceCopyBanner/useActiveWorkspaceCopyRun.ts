import { useApolloClient } from "@apollo/client";
import { useTranslation } from "next-i18next";
import { useEffect, useRef } from "react";
import { toast } from "react-toastify";
import { WorkspaceCopyRunStatus } from "graphql/types";
import {
  FinishedWorkspaceCopyRunDocument,
  FinishedWorkspaceCopyRunQuery,
  FinishedWorkspaceCopyRunQueryVariables,
  useActiveWorkspaceCopyRunQuery,
} from "workspaces/graphql/queries.generated";

const POLL_INTERVAL_MS = 5000;

/**
 * The user's copy that is still queued or running, polled only while there is
 * one. When it ends, tells the user how it went and calls `onFinished`, so the
 * page can show the new workspace.
 */
const useActiveWorkspaceCopyRun = (onFinished: () => void) => {
  const { t } = useTranslation();
  const client = useApolloClient();
  const { data, refetch, startPolling, stopPolling } =
    useActiveWorkspaceCopyRunQuery({ fetchPolicy: "network-only" });
  const run = data?.activeWorkspaceCopyRun ?? null;
  const runId = run?.id;
  const previousRunId = useRef(runId);

  useEffect(() => {
    if (runId) {
      startPolling(POLL_INTERVAL_MS);
    } else {
      stopPolling();
    }
    const finishedRunId = previousRunId.current;
    previousRunId.current = runId;
    if (!finishedRunId || finishedRunId === runId) return;

    onFinished();
    // The active run query no longer returns it, so its outcome is fetched once.
    client
      .query<
        FinishedWorkspaceCopyRunQuery,
        FinishedWorkspaceCopyRunQueryVariables
      >({
        query: FinishedWorkspaceCopyRunDocument,
        variables: { id: finishedRunId },
        fetchPolicy: "no-cache",
      })
      .then(({ data }) => {
        const finished = data?.workspaceCopyRun;
        if (!finished) return;
        const name = finished.targetWorkspaceName;
        if (finished.status === WorkspaceCopyRunStatus.Success) {
          toast.success(t("{{name}} is ready.", { name }));
        } else if (
          finished.status === WorkspaceCopyRunStatus.SuccessWithErrors
        ) {
          toast.warning(
            t("{{name}} was created, but some resources could not be copied.", {
              name,
            }),
          );
        } else if (finished.status === WorkspaceCopyRunStatus.Failed) {
          toast.error(t("The duplication failed."));
        }
      })
      .catch(() => {
        // The banner is gone either way; the outcome is only a courtesy.
      });
    // `t` is left out, like in the dialog: its identity may change on renders.
  }, [runId, startPolling, stopPolling, onFinished, client]);

  return { run, refetch };
};

export default useActiveWorkspaceCopyRun;
