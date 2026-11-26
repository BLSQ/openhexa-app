import { gql, useApolloClient } from "@apollo/client";
import clsx from "clsx";
import { useCallback, useEffect, useRef, useState } from "react";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import {
  CheckCircleIcon,
  ExclamationCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  XCircleIcon,
} from "@heroicons/react/24/outline";
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
  WorkspaceCopyStepName,
  WorkspaceCopyStepStatus,
} from "graphql/types";
import { useDuplicateWorkspaceMutation } from "workspaces/graphql/mutations.generated";
import {
  ActiveWorkspaceCopyRunDocument,
  ActiveWorkspaceCopyRunQuery,
  WorkspaceCopyRunDocument,
  WorkspaceCopyRunQuery,
  WorkspaceCopyRunQueryVariables,
  WorkspaceDatabaseInUseDocument,
  WorkspaceDatabaseInUseQuery,
  WorkspaceDatabaseInUseQueryVariables,
} from "workspaces/graphql/queries.generated";
import {
  DuplicateWorkspaceDialog_RunFragment,
  DuplicateWorkspace_WorkspaceFragment,
} from "./DuplicateWorkspaceDialog.generated";

type DuplicateWorkspaceDialogProps = {
  open: boolean;
  onClose(): void;
  // Null when opened only to follow the running copy, e.g. from its banner.
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
  const [includeSecrets, setIncludeSecrets] = useState(false);
  const [allDatasetVersions, setAllDatasetVersions] = useState(false);
  const [databaseInUse, setDatabaseInUse] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [run, setRun] = useState<DuplicateWorkspaceDialog_RunFragment | null>(
    null,
  );
  const [isLoadingActiveRun, setIsLoadingActiveRun] = useState(false);
  const [logLines, setLogLines] = useState<string[]>([]);
  const logsOffset = useRef(0);
  const followedRunId = useRef<string | null>(null);
  const client = useApolloClient();

  const resourceLabels: Record<WorkspaceCopyResource, string> = {
    [WorkspaceCopyResource.Files]: t("Files"),
    [WorkspaceCopyResource.Database]: t("Workspace database"),
    [WorkspaceCopyResource.Datasets]: t("Datasets"),
    [WorkspaceCopyResource.Connections]: t("Connections"),
    [WorkspaceCopyResource.Pipelines]: t("Pipelines"),
    [WorkspaceCopyResource.Webapps]: t("Web apps"),
  };

  const stepLabels: Record<WorkspaceCopyStepName, string> = {
    [WorkspaceCopyStepName.Workspace]: t("Workspace"),
    [WorkspaceCopyStepName.Files]: t("Files"),
    [WorkspaceCopyStepName.Database]: t("Workspace database"),
    [WorkspaceCopyStepName.Datasets]: t("Datasets"),
    [WorkspaceCopyStepName.Connections]: t("Connections"),
    [WorkspaceCopyStepName.Pipelines]: t("Pipelines"),
    [WorkspaceCopyStepName.Webapps]: t("Web apps"),
  };

  const stepStatusLabels: Record<WorkspaceCopyStepStatus, string> = {
    [WorkspaceCopyStepStatus.Pending]: t("Waiting"),
    [WorkspaceCopyStepStatus.Running]: t("Copying…"),
    [WorkspaceCopyStepStatus.Success]: t("Done"),
    [WorkspaceCopyStepStatus.SuccessWithWarnings]: t("Done, with warnings"),
    [WorkspaceCopyStepStatus.SuccessWithErrors]: t(
      "Some items could not be copied",
    ),
    [WorkspaceCopyStepStatus.Failed]: t("Failed"),
  };

  // Settings never copied, whatever happens during the run.
  const resourceNotes: Partial<Record<WorkspaceCopyResource, string>> = {
    [WorkspaceCopyResource.Pipelines]: t(
      "Pipeline schedules are not copied: set them again in the new workspace once you have checked the pipelines.",
    ),
    [WorkspaceCopyResource.Webapps]: t(
      "Web app subdomains, custom domains and favorites are not copied: the public URLs of the web apps change.",
    ),
  };

  const followRun = useCallback(
    (next: DuplicateWorkspaceDialog_RunFragment | null) => {
      if ((next?.id ?? null) !== followedRunId.current) {
        followedRunId.current = next?.id ?? null;
        logsOffset.current = 0;
        setLogLines([]);
      }
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
    if (!open) return;
    if (workspace) {
      setName(t("Copy of {{name}}", { name: workspace.name }));
      setCountries(workspace.countries);
      setResources(ALL_RESOURCES);
      setIncludeSecrets(false);
      setAllDatasetVersions(false);
      setDatabaseInUse(false);
    }
    setSubmitError(null);
    loadActiveRun();
    // Only opening the dialog resets it: `t` is left out so that a change of
    // its identity never wipes what the user typed.
  }, [open, workspace, loadActiveRun]);

  // The database cannot be copied while anything is connected to it, so it is
  // offered only when nothing is.
  useEffect(() => {
    if (!open || !workspace) return;
    let cancelled = false;
    client
      .query<WorkspaceDatabaseInUseQuery, WorkspaceDatabaseInUseQueryVariables>(
        {
          query: WorkspaceDatabaseInUseDocument,
          variables: { slug: workspace.slug },
          fetchPolicy: "no-cache",
        },
      )
      .then(({ data }) => {
        if (cancelled || !data?.workspace?.databaseInUse) return;
        setDatabaseInUse(true);
        setResources((current) =>
          current.filter((r) => r !== WorkspaceCopyResource.Database),
        );
      })
      .catch(() => {
        // The mutation checks it again, so a failure here only loses the hint.
      });
    return () => {
      cancelled = true;
    };
  }, [open, workspace, client]);

  const runId = run?.id;
  const isFinished = !!run && FINISHED_STATUSES.includes(run.status);
  const sourceName = run?.sourceWorkspace?.name ?? run?.sourceWorkspaceSlug;
  // Opened from another workspace's Duplicate button while a copy runs.
  const isOtherWorkspaceCopy =
    !!run && !!workspace && run.sourceWorkspaceSlug !== workspace.slug;

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
  const selectableResources = databaseInUse
    ? ALL_RESOURCES.filter((r) => r !== WorkspaceCopyResource.Database)
    : ALL_RESOURCES;
  const allSelected = resources.length === selectableResources.length;

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
            allDatasetVersions:
              resources.includes(WorkspaceCopyResource.Datasets) &&
              allDatasetVersions,
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
      } else {
        const refusals: Partial<Record<DuplicateWorkspaceError, string>> = {
          [DuplicateWorkspaceError.WorkspacesLimitReached]: t(
            "You have reached the maximum number of workspaces for your plan.",
          ),
          [DuplicateWorkspaceError.PermissionDenied]: t(
            "You are not authorized to perform this action",
          ),
          [DuplicateWorkspaceError.WorkspaceNotFound]: t(
            "This workspace no longer exists or you no longer have access to it.",
          ),
          [DuplicateWorkspaceError.InvalidCountry]: t(
            "One of the selected countries is not recognized.",
          ),
          [DuplicateWorkspaceError.InvalidName]: t(
            "Enter a name of at most 255 characters.",
          ),
          [DuplicateWorkspaceError.DatabaseInUse]: t(
            "The workspace database is in use. Close the notebooks, pipelines and tools connected to it, or duplicate the workspace without its database.",
          ),
        };
        const error = result?.errors.find((code) => code in refusals);
        if (error === DuplicateWorkspaceError.DatabaseInUse) {
          setDatabaseInUse(true);
          setResources((current) =>
            current.filter((r) => r !== WorkspaceCopyResource.Database),
          );
        }
        setSubmitError(
          error ? refusals[error]! : t("An unexpected error occurred."),
        );
      }
    } catch {
      setSubmitError(t("An unexpected error occurred."));
    } finally {
      setIsSubmitting(false);
    }
  };

  const runNotes = Object.entries(resourceNotes)
    .filter(([resource]) =>
      run?.steps.some(
        (step) =>
          step.name === (resource as string) &&
          step.status !== WorkspaceCopyStepStatus.Pending,
      ),
    )
    .map(([, note]) => note);

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
      maxWidth="max-w-3xl"
    >
      <Dialog.Title onClose={onClose}>
        {run && !isFinished ? t("Copy in progress") : t("Duplicate workspace")}
      </Dialog.Title>
      {isLoadingActiveRun ? (
        <Dialog.Content className="flex justify-center py-10">
          <Spinner />
        </Dialog.Content>
      ) : !run && !workspace ? (
        <>
          <Dialog.Content>
            <p className="text-sm text-gray-600">
              {t("No copy is running anymore.")}
            </p>
          </Dialog.Content>
          <Dialog.Actions>
            <Button variant="white" onClick={onClose}>
              {t("Close")}
            </Button>
          </Dialog.Actions>
        </>
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
              maxLength={255}
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
                  onClick={() =>
                    setResources(allSelected ? [] : selectableResources)
                  }
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
                      disabled={
                        resource === WorkspaceCopyResource.Database &&
                        databaseInUse
                      }
                      description={
                        resource === WorkspaceCopyResource.Database &&
                        databaseInUse
                          ? t(
                              "The database is in use and cannot be copied. Close the notebooks, pipelines and tools connected to it, then reopen this dialog.",
                            )
                          : undefined
                      }
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
                    {resource === WorkspaceCopyResource.Datasets &&
                      resources.includes(resource) && (
                        <Checkbox
                          className="mt-3 ml-7"
                          name="allDatasetVersions"
                          checked={allDatasetVersions}
                          onChange={() =>
                            setAllDatasetVersions(!allDatasetVersions)
                          }
                          label={t("Copy all dataset versions")}
                          description={t(
                            "If unchecked, only the latest version of each dataset is copied.",
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
            {isOtherWorkspaceCopy && !isFinished && (
              <p className="rounded-md bg-blue-50 px-3 py-2 text-sm text-blue-800">
                {t(
                  "You can run one copy at a time. You can duplicate {{name}} once this one is done.",
                  { name: workspace?.name },
                )}
              </p>
            )}
            <div className="flex items-center gap-2 text-sm">
              {!isFinished && <Spinner size="xs" />}
              <span className="text-gray-700">
                {!isFinished
                  ? t(
                      "Copying {{source}} into {{name}}. You can close this dialog, the copy continues in the background.",
                      { source: sourceName, name: run.targetWorkspaceName },
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
            <ul
              data-testid="copy-steps"
              className="divide-y divide-gray-100 rounded-md border border-gray-200"
            >
              {run.steps.map((step) => (
                <li
                  key={step.name}
                  className="flex items-center justify-between px-4 py-2.5 text-sm"
                >
                  <span className="flex items-center gap-2 text-gray-900">
                    <StepIcon status={step.status} />
                    {stepLabels[step.name]}
                  </span>
                  <span
                    className={clsx(
                      "text-xs",
                      step.status === WorkspaceCopyStepStatus.Failed ||
                        step.status ===
                          WorkspaceCopyStepStatus.SuccessWithErrors
                        ? "text-red-600"
                        : step.status ===
                            WorkspaceCopyStepStatus.SuccessWithWarnings
                          ? "text-amber-600"
                          : "text-gray-500",
                    )}
                  >
                    {stepStatusLabels[step.status]}
                  </span>
                </li>
              ))}
            </ul>
            {isFinished && run.warnings.length > 0 && (
              <div className="rounded-md bg-amber-50 px-4 py-3 text-sm text-amber-800">
                <div className="mb-1 font-medium">
                  {t("Check these items in the new workspace:")}
                </div>
                <ul className="list-disc space-y-1 pl-5">
                  {run.warnings.map((warning, index) => (
                    <li key={index} className="break-words">
                      {warning}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {isFinished && runNotes.length > 0 && (
              <div className="flex gap-2 rounded-md bg-blue-50 px-4 py-3 text-sm text-blue-800">
                <InformationCircleIcon className="h-5 w-5 shrink-0" />
                <ul className="space-y-1">
                  {runNotes.map((note) => (
                    <li key={note}>{note}</li>
                  ))}
                </ul>
              </div>
            )}
            <details>
              <summary className="cursor-pointer text-sm text-gray-600 select-none">
                {t("Show details")}
              </summary>
              <div
                ref={logRef}
                data-testid="copy-logs"
                className="mt-2 h-72 overflow-y-auto rounded-md bg-gray-900 px-4 py-3 font-mono text-xs leading-relaxed"
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
            </details>
          </Dialog.Content>
          <Dialog.Actions>
            <Button variant="white" onClick={onClose}>
              {t("Close")}
            </Button>
            {isFinished && run?.workspace && (
              <Button onClick={openWorkspace}>
                {t("Open {{name}}", { name: run.workspace.name })}
              </Button>
            )}
          </Dialog.Actions>
        </>
      )}
    </Dialog>
  );
};

const StepIcon = ({ status }: { status: WorkspaceCopyStepStatus }) => {
  switch (status) {
    case WorkspaceCopyStepStatus.Running:
      return <Spinner size="xs" />;
    case WorkspaceCopyStepStatus.Success:
      return <CheckCircleIcon className="h-5 w-5 text-green-600" />;
    case WorkspaceCopyStepStatus.SuccessWithWarnings:
      return <ExclamationTriangleIcon className="h-5 w-5 text-amber-500" />;
    case WorkspaceCopyStepStatus.SuccessWithErrors:
      return <ExclamationCircleIcon className="h-5 w-5 text-red-500" />;
    case WorkspaceCopyStepStatus.Failed:
      return <XCircleIcon className="h-5 w-5 text-red-500" />;
    default:
      return <span className="h-5 w-5 rounded-full border-2 border-gray-200" />;
  }
};

DuplicateWorkspaceDialog.fragments = {
  run: gql`
    fragment DuplicateWorkspaceDialog_run on WorkspaceCopyRun {
      id
      status
      targetWorkspaceName
      sourceWorkspaceSlug
      sourceWorkspace {
        slug
        name
      }
      error
      steps {
        name
        status
      }
      warnings
      workspace {
        slug
        name
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
