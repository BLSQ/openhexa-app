import useCacheKey from "core/hooks/useCacheKey";
import { PipelineType } from "graphql/types";
import { useCallback, useState } from "react";
import { RunPipelineDialog_PipelineFragment } from "workspaces/features/RunPipelineDialog/RunPipelineDialog.generated";
import { RunPipelineInput } from "workspaces/features/RunPipelineDialog/useRunPipelineForm";
import { runPipeline } from "workspaces/helpers/pipelines";

export type TrackedRun = {
  id: string;
  startedAt: number;
  // Kept so "Run again" can relaunch with the exact same settings.
  launchInput: Partial<RunPipelineInput>;
};

export type LauncherPanel =
  | { view: "form" }
  | { view: "run"; runId: string }
  | null;

// The pipeline is optional so the hook can be called before the page's query
// has resolved.
const usePipelineRunLauncher = (
  pipeline?: Pick<RunPipelineDialog_PipelineFragment, "id" | "code" | "type">,
) => {
  const clearCache = useCacheKey(["pipelines", pipeline?.code]);
  const [trackedRuns, setTrackedRuns] = useState<TrackedRun[]>([]);
  const [panel, setPanel] = useState<LauncherPanel>(null);
  const [overlayDismissed, setOverlayDismissed] = useState(false);

  const launch = useCallback(
    async (input: Partial<RunPipelineInput> = {}) => {
      if (!pipeline) {
        throw new Error("Pipeline is not loaded");
      }
      const run = await runPipeline(
        pipeline.id,
        input.config,
        input.versionId,
        input.sendMailNotifications,
        input.enableDebugLogs,
      );
      setTrackedRuns((runs) => [
        ...runs,
        { id: run.id, startedAt: Date.now(), launchInput: input },
      ]);
      setPanel({ view: "run", runId: run.id });
      setOverlayDismissed(false);
      clearCache();
      return run;
    },
    [pipeline, clearCache],
  );

  const openRun = useCallback(() => {
    if (pipeline?.type === PipelineType.ZipFile) {
      setPanel({ view: "form" });
    } else {
      return launch();
    }
  }, [pipeline?.type, launch]);

  const rerun = useCallback(
    (runId: string) => {
      const tracked = trackedRuns.find((run) => run.id === runId);
      return launch(tracked?.launchInput);
    },
    [trackedRuns, launch],
  );

  const openDetails = useCallback(
    (runId: string) => setPanel({ view: "run", runId }),
    [],
  );
  const closePanel = useCallback(() => setPanel(null), []);
  const dismissOverlay = useCallback(() => setOverlayDismissed(true), []);

  return {
    trackedRuns,
    panel,
    overlayDismissed,
    launch,
    openRun,
    rerun,
    openDetails,
    closePanel,
    dismissOverlay,
  };
};

export type PipelineRunLauncher = ReturnType<typeof usePipelineRunLauncher>;

export default usePipelineRunLauncher;
