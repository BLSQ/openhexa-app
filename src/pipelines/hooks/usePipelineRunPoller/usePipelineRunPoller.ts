import { gql, useLazyQuery } from "@apollo/client";
import { PipelineRun, PipelineRunStatus } from "graphql-types";
import { useEffect } from "react";
import { PipelineRunPollerQuery } from "./usePipelineRunPoller.generated";

export function randomInterval(interval: number, factor: number) {
  const variable = Math.floor(Math.random() * factor * interval);
  return interval + variable * (Math.random() > 0.5 ? 1 : -1);
}

export default function usePipelineRunPoller(
  runId: PipelineRun["id"] | null,
  interval: number = 1000
) {
  const [_, { data, stopPolling, startPolling }] =
    useLazyQuery<PipelineRunPollerQuery>(
      gql`
        query PipelineRunPoller($runId: UUID!) {
          run: pipelineRun(id: $runId) {
            id
            status
            duration
            progress
          }
        }
      `,
      { variables: { runId } }
    );

  useEffect(() => {
    if (!runId) {
      stopPolling();
    } else if (!data) {
      startPolling(randomInterval(interval, 0.4));
    } else if (
      data.run &&
      [PipelineRunStatus.Queued, PipelineRunStatus.Running].includes(
        data.run.status
      )
    ) {
      startPolling(randomInterval(interval, 0.4));
    } else {
      stopPolling();
    }

    return () => stopPolling();
  }, [data, startPolling, stopPolling, runId, interval]);
}
