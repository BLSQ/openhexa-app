import { PipelineRunStatus } from "graphql/types";
import usePipelineRunMessages from "pipelines/hooks/usePipelineRunMessages/usePipelineRunMessages";
import usePipelineRunPoller from "pipelines/hooks/usePipelineRunPoller";
import { useEffect } from "react";
import { useWorkspacePipelineRunPageQuery } from "workspaces/graphql/queries.generated";

export const TERMINAL_STATUSES = [
  PipelineRunStatus.Failed,
  PipelineRunStatus.Success,
  PipelineRunStatus.Stopped,
  PipelineRunStatus.Skipped,
];

export const isTerminalStatus = (status?: PipelineRunStatus | null) =>
  !!status && TERMINAL_STATUSES.includes(status);

const usePipelineRunDetail = (workspaceSlug: string, runId: string) => {
  const { data, refetch } = useWorkspacePipelineRunPageQuery({
    variables: { workspaceSlug, runId },
  });

  const run = data?.pipelineRun;
  const isFinished = isTerminalStatus(run?.status);

  usePipelineRunPoller(
    { id: run?.id ?? runId, status: run?.status ?? PipelineRunStatus.Queued },
    !isFinished && !!run,
  );

  useEffect(() => {
    if (isFinished) {
      refetch();
    }
  }, [isFinished]);

  const messageStream = usePipelineRunMessages(
    run?.id ?? runId,
    isFinished,
    refetch,
  );

  return { data, run, isFinished, refetch, messageStream };
};

export default usePipelineRunDetail;
