import { ChevronDownIcon, XMarkIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";
import useInterval from "core/hooks/useInterval";
import { PipelineRunStatus } from "graphql/types";
import { useTranslation } from "next-i18next";
import { isTerminalStatus } from "pipelines/features/PipelineRunDetail/usePipelineRunDetail";
import PipelineRunStatusBadge from "pipelines/features/PipelineRunStatusBadge";
import {
  PipelineRunLauncherRunQuery,
  usePipelineRunLauncherRunQuery,
} from "pipelines/graphql/queries.generated";
import usePipelineRunPoller from "pipelines/hooks/usePipelineRunPoller";
import { useCallback, useEffect, useState } from "react";
import {
  formatElapsed,
  formatStartedAt,
  getRunElapsedSeconds,
} from "./helpers";
import { TrackedRun } from "./usePipelineRunLauncher";

// How long a finished run stays in the overlay before dropping off.
export const FINISHED_RUN_TTL_MS = 5000;

type WatchedRun = NonNullable<PipelineRunLauncherRunQuery["run"]>;

type WatcherState = { run: WatchedRun; finishedAt: number | null };

// Keeps a tracked run's status fresh even while the overlay is hidden (e.g.
// behind the details panel), so it knows when the run finished.
const TrackedRunWatcher = ({
  runId,
  onChange,
}: {
  runId: string;
  onChange: (runId: string, run: WatchedRun) => void;
}) => {
  const { data } = usePipelineRunLauncherRunQuery({ variables: { runId } });
  const run = data?.run;

  usePipelineRunPoller(
    { id: runId, status: run?.status ?? PipelineRunStatus.Queued },
    !!run && !isTerminalStatus(run.status),
  );

  useEffect(() => {
    if (run) {
      onChange(runId, run);
    }
  }, [run, runId, onChange]);

  return null;
};

type RunStatusOverlayProps = {
  pipelineName: string;
  trackedRuns: TrackedRun[];
  hidden: boolean;
  onOpenDetails: (runId: string) => void;
  onDismiss: () => void;
};

const RunStatusOverlay = ({
  pipelineName,
  trackedRuns,
  hidden,
  onOpenDetails,
  onDismiss,
}: RunStatusOverlayProps) => {
  const { t } = useTranslation();
  const [watched, setWatched] = useState<Record<string, WatcherState>>({});
  const [isExpanded, setExpanded] = useState(false);
  const [now, setNow] = useState(() => Date.now());

  const onChange = useCallback((runId: string, run: WatchedRun) => {
    setWatched((prev) => {
      const previous = prev[runId];
      const finishedAt = isTerminalStatus(run.status)
        ? (previous?.finishedAt ?? Date.now())
        : null;
      return { ...prev, [runId]: { run, finishedAt } };
    });
  }, []);

  const visible = [...trackedRuns]
    .sort((a, b) => b.startedAt - a.startedAt)
    .map((tracked) => watched[tracked.id])
    .filter(
      (entry): entry is WatcherState =>
        !!entry &&
        (entry.finishedAt === null ||
          now - entry.finishedAt < FINISHED_RUN_TTL_MS),
    );

  const isShown = !hidden && visible.length > 0;
  useInterval(() => setNow(Date.now()), visible.length ? 1000 : null);

  const [primary, ...others] = visible;

  return (
    <>
      {trackedRuns.map((tracked) => (
        <TrackedRunWatcher
          key={tracked.id}
          runId={tracked.id}
          onChange={onChange}
        />
      ))}
      {isShown && (
        <div
          data-testid="run-status-overlay"
          className="fixed right-6 top-[76px] z-40 w-[352px] overflow-hidden rounded-lg border border-gray-500/15 bg-white shadow-xl"
        >
          {visible.length > 1 && (
            <div className="px-3.5 pt-2 text-[11px] font-semibold uppercase tracking-wider text-gray-500">
              {t("{{count}} runs in progress", { count: visible.length })}
            </div>
          )}
          <div className="flex items-center gap-2.5 px-3.5 py-3">
            <PipelineRunStatusBadge run={primary.run} />
            <div className="min-w-0 flex-1">
              <div className="truncate text-sm font-medium text-gray-900">
                {pipelineName}
              </div>
              <div className="truncate text-xs text-gray-500">
                {[
                  primary.run.version?.versionName,
                  t("Manual"),
                  t("started {{time}}", {
                    time: formatStartedAt(primary.run.executionDate),
                  }),
                ]
                  .filter(Boolean)
                  .join(" · ")}
              </div>
            </div>
            <div className="flex-none font-mono text-[13px] text-gray-500">
              {formatElapsed(
                getRunElapsedSeconds(
                  primary.run,
                  primary.finishedAt !== null,
                  now,
                ),
              )}
            </div>
          </div>
          <div className="flex items-center pb-2 pl-3.5 pr-2">
            <button
              type="button"
              onClick={() => onOpenDetails(primary.run.id)}
              className="py-1 text-[13px] font-medium text-blue-600 hover:text-blue-700"
            >
              {t("View details")}
            </button>
            <div className="flex-1" />
            <button
              type="button"
              onClick={onDismiss}
              title={t("Hide until next run")}
              className="rounded-sm p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
            >
              <XMarkIcon className="h-4 w-4" />
            </button>
          </div>
          {others.length > 0 && (
            <div className="border-t border-gray-100">
              <button
                type="button"
                onClick={() => setExpanded((expanded) => !expanded)}
                className="flex w-full items-center justify-between px-3.5 py-2 text-xs font-medium text-gray-500 hover:bg-gray-50 hover:text-gray-700"
              >
                <span>
                  {t("{{count}} other runs", { count: others.length })}
                </span>
                <ChevronDownIcon
                  className={clsx(
                    "h-3.5 w-3.5 transition-transform",
                    isExpanded && "rotate-180",
                  )}
                />
              </button>
              {isExpanded && (
                <div className="pb-1.5">
                  {others.map(({ run, finishedAt }) => (
                    <div
                      key={run.id}
                      className="flex items-center gap-2 px-3.5 py-1.5"
                    >
                      <PipelineRunStatusBadge run={run} />
                      <span className="flex-1 truncate text-xs text-gray-500">
                        {t("started {{time}}", {
                          time: formatStartedAt(run.executionDate),
                        })}
                      </span>
                      <span className="font-mono text-xs text-gray-500">
                        {formatElapsed(
                          getRunElapsedSeconds(run, finishedAt !== null, now),
                        )}
                      </span>
                      <button
                        type="button"
                        onClick={() => onOpenDetails(run.id)}
                        className="py-0.5 text-xs font-medium text-blue-600 hover:text-blue-700"
                      >
                        {t("Details")}
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </>
  );
};

export default RunStatusOverlay;
