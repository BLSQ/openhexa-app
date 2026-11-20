import { gql, useApolloClient } from "@apollo/client";
import clsx from "clsx";
import { useCallback, useEffect, useRef, useState } from "react";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import Button from "core/components/Button";
import Dialog from "core/components/Dialog";
import Field from "core/components/forms/Field";
import Checkbox from "core/components/forms/Checkbox/Checkbox";
import Spinner from "core/components/Spinner";
import CountryPicker from "core/features/CountryPicker";
import { CountryPicker_CountryFragment } from "core/features/CountryPicker/CountryPicker.generated";
import useCacheKey from "core/hooks/useCacheKey";
import {
  DuplicateWorkspaceError,
  WorkspaceCopyResource,
  WorkspaceCopyRunStatus,
} from "graphql/types";
import { useDuplicateWorkspaceMutation } from "workspaces/graphql/mutations.generated";
import {
  ActiveWorkspaceCopyRunDocument,
  ActiveWorkspaceCopyRunQuery,
  WorkspaceCopyRunDocument,
  WorkspaceCopyRunQuery,
  WorkspaceCopyRunQueryVariables,
} from "workspaces/graphql/queries.generated";
import {
  DuplicateWorkspaceDialog_RunFragment,
  DuplicateWorkspace_WorkspaceFragment,
} from "./DuplicateWorkspaceDialog.generated";

type DuplicateWorkspaceDialogProps = {
  open: boolean;
  onClose(): void;
  workspace: DuplicateWorkspace_WorkspaceFragment | null;
};

const POLL_INTERVAL_MS = 2000;

// The full log stays in the admin; the dialog shows where the copy is at.
const MAX_LOG_LINES = 500;

const FINISHED_STATUSES = [
  WorkspaceCopyRunStatus.Success,
  WorkspaceCopyRunStatus.SuccessWithErrors,
  WorkspaceCopyRunStatus.Failed,
];

const ALL_RESOURCES = Object.values(WorkspaceCopyResource);

const DuplicateWorkspaceDialog = ({
  open,
  onClose,
  workspace,
}: DuplicateWorkspaceDialogProps) => {
  const { t } = useTranslation();
  const router = useRouter();
  const clearCache = useCacheKey(["workspaces"]);
  const [duplicateWorkspace] = useDuplicateWorkspaceMutation();

  const [name, setName] = useState("");
  const [countries, setCountries] = useState<CountryPicker_CountryFragment[]>(
    [],
  );
  const [resources, setResources] = useState<WorkspaceCopyResource[]>([]);
  const [includeSecrets, setIncludeSecrets] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [run, setRun] = useState<DuplicateWorkspaceDialog_RunFragment | null>(
    null,
  );
  const [isLoadingActiveRun, setIsLoadingActiveRun] = useState(false);
  const [logLines, setLogLines] = useState<string[]>([]);
  const logsOffset = useRef(0);
  const client = useApolloClient();

  const resourceLabels: Record<WorkspaceCopyResource, string> = {
    [WorkspaceCopyResource.Files]: t("Files"),
    [WorkspaceCopyResource.Database]: t("Workspace database"),
    [WorkspaceCopyResource.Datasets]: t("Datasets"),
    [WorkspaceCopyResource.Connections]: t("Connections"),
    [WorkspaceCopyResource.Pipelines]: t("Pipelines"),
    [WorkspaceCopyResource.Webapps]: t("Web apps"),
  };

  const followRun = useCallback(
    (next: DuplicateWorkspaceDialog_RunFragment | null) => {
      logsOffset.current = 0;
      setLogLines([]);
      setRun(next);
    },
    [],
  );

  // A copy started earlier is shown again, even after a page reload: the user
  // can have only one at a time, so it is the one they would come back for.
  const loadActiveRun = useCallback(async () => {
    setIsLoadingActiveRun(true);
    try {
      const { data } = await client.query<ActiveWorkspaceCopyRunQuery>({
        query: ActiveWorkspaceCopyRunDocument,
        fetchPolicy: "no-cache",
      });
      followRun(data?.activeWorkspaceCopyRun ?? null);
    } finally {
      setIsLoadingActiveRun(false);
    }
  }, [client, followRun]);

  useEffect(() => {
    if (open && workspace) {
      setName(t("Copy of {{name}}", { name: workspace.name }));
      setCountries(workspace.countries);
      setResources(ALL_RESOURCES);
      setIncludeSecrets(true);
      setSubmitError(null);
      loadActiveRun();
    }
    // Only opening the dialog resets it: `t` is left out so that a change of
    // its identity never wipes what the user typed.
  }, [open, workspace, loadActiveRun]);

  const runId = run?.id;
  const isFinished = !!run && FINISHED_STATUSES.includes(run.status);

  // Polls only while the dialog is open, and asks each time for the log lines
  // added since the previous answer.
  useEffect(() => {
    if (!open || !runId || isFinished) return;
    let cancelled = false;
    let inFlight = false;
    const poll = async () => {
      if (inFlight) return;
      inFlight = true;
      try {
        const { data } = await client.query<
          WorkspaceCopyRunQuery,
          WorkspaceCopyRunQueryVariables
        >({
          query: WorkspaceCopyRunDocument,
          variables: { id: runId, logsOffset: logsOffset.current },
          fetchPolicy: "no-cache",
        });
        const fetched = data?.workspaceCopyRun;
        if (cancelled || !fetched) return;
        const { logs, ...rest } = fetched;
        logsOffset.current = logs.nextOffset;
        const newLines = logs.text.split("\n").filter(Boolean);
        if (newLines.length) {
          setLogLines((lines) => [...lines, ...newLines].slice(-MAX_LOG_LINES));
        }
        setRun(rest);
      } catch {
        // A failed poll is retried on the next tick.
      } finally {
        inFlight = false;
      }
    };
    poll();
    const timer = setInterval(poll, POLL_INTERVAL_MS);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, [open, runId, isFinished, client]);

  useEffect(() => {
    if (isFinished) clearCache();
  }, [isFinished, clearCache]);

  const logRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [logLines]);

  const toggleResource = (resource: WorkspaceCopyResource) =>
    setResources((current) =>
      current.includes(resource)
        ? current.filter((r) => r !== resource)
        : [...current, resource],
    );
  const allSelected = resources.length === ALL_RESOURCES.length;

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!workspace || !name.trim()) return;
    setIsSubmitting(true);
    setSubmitError(null);
    try {
      const { data } = await duplicateWorkspace({
        variables: {
          input: {
            workspaceSlug: workspace.slug,
            name: name.trim(),
            countries: countries.map((c) => ({ code: c.code })),
            resources,
            includeConnectionSecrets:
              resources.includes(WorkspaceCopyResource.Connections) &&
              includeSecrets,
          },
        },
      });
      const result = data?.duplicateWorkspace;
      if (result?.success && result.run) {
        followRun(result.run);
      } else if (
        result?.errors.includes(DuplicateWorkspaceError.CopyAlreadyRunning)
      ) {
        // Started in another tab meanwhile: show that copy instead.
        await loadActiveRun();
      } else if (
        result?.errors.includes(DuplicateWorkspaceError.WorkspacesLimitReached)
      ) {
        setSubmitError(
          t("You have reached the maximum number of workspaces for your plan."),
        );
      } else if (
        result?.errors.includes(DuplicateWorkspaceError.PermissionDenied)
      ) {
        setSubmitError(t("You are not authorized to perform this action"));
      } else {
        setSubmitError(t("An unexpected error occurred."));
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const openWorkspace = async () => {
    if (!run?.workspace) return;
    onClose();
    await router.push({
      pathname: "/workspaces/[workspaceSlug]",
      query: { workspaceSlug: run.workspace.slug },
    });
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      onSubmit={run ? undefined : onSubmit}
      maxWidth="max-w-xl"
    >
      <Dialog.Title onClose={onClose}>{t("Duplicate workspace")}</Dialog.Title>
      {isLoadingActiveRun ? (
        <Dialog.Content className="flex justify-center py-10">
          <Spinner />
        </Dialog.Content>
      ) : !run ? (
        <>
          <Dialog.Content className="space-y-4">
            <p className="text-sm text-gray-600">
              {t(
                "Create a copy of {{name}}. Choose which resources to copy into the new workspace.",
                { name: workspace?.name },
              )}
            </p>
            <Field
              name="name"
              required
              label={t("New workspace name")}
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoComplete="off"
              fullWidth
            />
            <Field name="countries" label={t("Countries")}>
              <CountryPicker
                withPortal
                multiple
                value={countries}
                onChange={(value) =>
                  setCountries((value as CountryPicker_CountryFragment[]) ?? [])
                }
              />
            </Field>
            <div>
              <div className="mb-2 flex items-center justify-between">
                <span className="text-sm font-medium text-gray-900">
                  {t("Resources to copy")}
                </span>
                <button
                  type="button"
                  className="text-sm font-medium text-blue-600 hover:text-blue-500"
                  onClick={() => setResources(allSelected ? [] : ALL_RESOURCES)}
                >
                  {allSelected ? t("Deselect all") : t("Select all")}
                </button>
              </div>
              <div className="divide-y divide-gray-100 rounded-md border border-gray-200">
                {ALL_RESOURCES.map((resource) => (
                  <div key={resource} className="px-4 py-3">
                    <Checkbox
                      name={`resource-${resource}`}
                      checked={resources.includes(resource)}
                      onChange={() => toggleResource(resource)}
                      label={resourceLabels[resource]}
                    />
                    {resource === WorkspaceCopyResource.Connections &&
                      resources.includes(resource) && (
                        <Checkbox
                          className="mt-3 ml-7"
                          name="includeConnectionSecrets"
                          checked={includeSecrets}
                          onChange={() => setIncludeSecrets(!includeSecrets)}
                          label={t("Include connection secrets")}
                          description={t(
                            "If unchecked, connections are copied without their secrets.",
                          )}
                        />
                      )}
                  </div>
                ))}
              </div>
              <p className="mt-2 text-xs text-gray-500">
                {t(
                  "Members are not copied. You will be the only member of the new workspace and the creator of all its resources.",
                )}
              </p>
            </div>
            {submitError && (
              <div className="text-danger text-sm">{submitError}</div>
            )}
          </Dialog.Content>
          <Dialog.Actions>
            <Button variant="white" onClick={onClose}>
              {t("Cancel")}
            </Button>
            <Button type="submit" disabled={isSubmitting || !name.trim()}>
              {isSubmitting && <Spinner size="xs" className="mr-1" />}
              {t("Duplicate")}
            </Button>
          </Dialog.Actions>
        </>
      ) : (
        <>
          <Dialog.Content className="space-y-3">
            <div className="flex items-center gap-2 text-sm">
              {!isFinished && <Spinner size="xs" />}
              <span className="text-gray-700">
                {!isFinished
                  ? t(
                      "Copying resources into {{name}}. You can close this dialog, the copy continues in the background.",
                      { name: run.targetWorkspaceName },
                    )
                  : run.status === WorkspaceCopyRunStatus.Failed
                    ? t("The duplication failed.")
                    : run.status === WorkspaceCopyRunStatus.SuccessWithErrors
                      ? t(
                          "{{name}} was created, but some resources could not be copied.",
                          { name: run.targetWorkspaceName },
                        )
                      : t("{{name}} is ready.", {
                          name: run.targetWorkspaceName,
                        })}
              </span>
            </div>
            {run.error && (
              <div className="text-danger text-sm whitespace-pre-line">
                {run.error}
              </div>
            )}
            <div
              ref={logRef}
              data-testid="copy-logs"
              className="h-60 overflow-y-auto rounded-md bg-gray-900 px-4 py-3 font-mono text-xs leading-relaxed"
            >
              {logLines.length === 0 && (
                <div className="text-gray-500">
                  {t("Waiting for the copy to start…")}
                </div>
              )}
              {logLines.map((line, index) => (
                <div
                  key={index}
                  className={clsx(
                    "whitespace-pre-wrap break-words",
                    line.includes("[ERROR]")
                      ? "text-red-400"
                      : line.includes("[WARNING]")
                        ? "text-amber-300"
                        : "text-gray-300",
                  )}
                >
                  {line}
                </div>
              ))}
            </div>
          </Dialog.Content>
          <Dialog.Actions>
            <Button variant="white" onClick={onClose}>
              {t("Close")}
            </Button>
            {isFinished && run?.workspace && (
              <Button onClick={openWorkspace}>{t("Open workspace")}</Button>
            )}
          </Dialog.Actions>
        </>
      )}
    </Dialog>
  );
};

DuplicateWorkspaceDialog.fragments = {
  run: gql`
    fragment DuplicateWorkspaceDialog_run on WorkspaceCopyRun {
      id
      status
      targetWorkspaceName
      error
      workspace {
        slug
      }
    }
  `,
  workspace: gql`
    fragment DuplicateWorkspace_workspace on Workspace {
      slug
      name
      countries {
        ...CountryPicker_country
      }
      permissions {
        duplicate
      }
    }
    ${CountryPicker.fragments.country}
  `,
};

export default DuplicateWorkspaceDialog;
