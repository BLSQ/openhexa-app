import { gql, useLazyQuery } from "@apollo/client";
import { PipelineRunStatus } from "graphql/types";
import { useEffect } from "react";
import {
  PipelineRunPollerQuery,
  UsePipelineRunPoller_RunFragment,
} from "./usePipelineRunPoller.generated";

function usePipelineRunPoller(
  run: UsePipelineRunPoller_RunFragment,
  polling: boolean = true,
) {
  const [fetch] = useLazyQuery<PipelineRunPollerQuery>(gql`
    query PipelineRunPoller($runId: UUID!) {
      run: pipelineRun(id: $runId) {
        ...usePipelineRunPoller_run
        duration
        progress
      }
    }
    ${usePipelineRunPoller.fragments.run}
  `);

  useEffect(() => {
    if (!polling) {
      return;
    }

    let timeout: NodeJS.Timeout;
    if (
      [
        PipelineRunStatus.Queued,
        PipelineRunStatus.Running,
        PipelineRunStatus.Terminating,
      ].includes(run.status)
    ) {
      timeout = setInterval(() => {
        fetch({
          variables: { runId: run.id },
          fetchPolicy: "network-only",
        });
      }, 500);
    }

    return () => {
      clearInterval(timeout);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [run.status, polling]);
}

usePipelineRunPoller.fragments = {
  run: gql`
    fragment usePipelineRunPoller_run on PipelineRun {
      id
      status
    }
  `,
};

export default usePipelineRunPoller;
