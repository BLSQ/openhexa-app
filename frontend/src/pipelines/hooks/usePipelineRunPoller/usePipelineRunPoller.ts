import { gql } from "@apollo/client";
import { PipelineRunStatus } from "graphql/types";
import { useEffect } from "react";
import { UsePipelineRunPoller_RunFragment } from "./usePipelineRunPoller.generated";
import { usePipelineRunPollerLazyQuery } from "pipelines/graphql/queries.generated";

function usePipelineRunPoller(
  run: UsePipelineRunPoller_RunFragment,
  polling: boolean = true,
) {
  const [fetch] = usePipelineRunPollerLazyQuery();

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
