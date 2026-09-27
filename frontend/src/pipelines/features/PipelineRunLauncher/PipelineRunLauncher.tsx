import SidePanel from "core/components/SidePanel";
import { useRef } from "react";
import { RunPipelineDialog_PipelineFragment } from "workspaces/features/RunPipelineDialog/RunPipelineDialog.generated";
import RunDetailsPanel from "./RunDetailsPanel";
import RunPipelinePanel from "./RunPipelinePanel";
import RunStatusOverlay from "./RunStatusOverlay";
import { PipelineRunLauncher as Launcher } from "./usePipelineRunLauncher";

type PipelineRunLauncherProps = {
  launcher: Launcher;
  pipeline: RunPipelineDialog_PipelineFragment & { name?: string | null };
  workspaceSlug: string;
};

const PipelineRunLauncher = ({
  launcher,
  pipeline,
  workspaceSlug,
}: PipelineRunLauncherProps) => {
  const { panel } = launcher;
  // Keep rendering the last view while the panel slides out.
  const lastPanel = useRef(panel);
  if (panel) {
    lastPanel.current = panel;
  }
  const shownPanel = panel ?? lastPanel.current;
  const pipelineName = pipeline.name ?? pipeline.code;

  return (
    <>
      <SidePanel open={panel !== null} onClose={launcher.closePanel}>
        {shownPanel?.view === "form" && (
          <RunPipelinePanel
            pipeline={pipeline}
            onClose={launcher.closePanel}
            onLaunch={launcher.launch}
          />
        )}
        {shownPanel?.view === "run" && (
          <RunDetailsPanel
            workspaceSlug={workspaceSlug}
            pipelineCode={pipeline.code}
            pipelineName={pipelineName}
            runId={shownPanel.runId}
            canRun={pipeline.permissions.run}
            onClose={launcher.closePanel}
            onRunAgain={() => launcher.rerun(shownPanel.runId)}
          />
        )}
      </SidePanel>
      <RunStatusOverlay
        pipelineName={pipelineName}
        trackedRuns={launcher.trackedRuns}
        hidden={panel !== null || launcher.overlayDismissed}
        onOpenDetails={launcher.openDetails}
        onDismiss={launcher.dismissOverlay}
      />
    </>
  );
};

export default PipelineRunLauncher;
