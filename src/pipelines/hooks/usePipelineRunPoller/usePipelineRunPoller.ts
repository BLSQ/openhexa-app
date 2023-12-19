import { gql, useLazyQuery } from "@apollo/client";
import Backoff from "core/helpers/backoff";
import { PipelineRun, PipelineRunStatus } from "graphql-types";
import { useCallback, useEffect, useRef } from "react";
import { PipelineRunPollerQuery } from "./usePipelineRunPoller.generated";

export default function usePipelineRunPoller(runId: PipelineRun["id"] | null) {
  const backoffRef = useRef(
    new Backoff({ min: 400, max: 10000, factor: 2, jitter: 0.2 }),
  );
  const [fetch] = useLazyQuery<PipelineRunPollerQuery>(
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
    { variables: { runId } },
  );

  const retry = useCallback(async () => {
    const { data } = await fetch({ fetchPolicy: "network-only" });
    if (
      data?.run &&
      [PipelineRunStatus.Queued, PipelineRunStatus.Running].includes(
        data.run.status,
      )
    ) {
      setTimeout(() => retry(), backoffRef.current.duration());
    }
  }, [fetch]);

  useEffect(() => {
    backoffRef.current.reset();
    if (runId) {
      retry();
    }
  }, [runId, retry]);
}
