import { gql } from "@apollo/client";
import clsx from "clsx";
import Badge from "core/components/Badge";
import Spinner from "core/components/Spinner";
import { DagRunStatus } from "graphql-types";
import { formatDAGRunStatus } from "pipelines/helpers/format";
import { useMemo } from "react";
import {
  PipelineRunStatusBadge_DagRunFragment,
  PipelineRunStatusBadge_RunFragment,
} from "./PipelineRunStatusBadge.generated";
import usePipelineRunPoller from "pipelines/hooks/usePipelineRunPoller";

type PipelineRunStatusBadgeProps = {
  run:
    | PipelineRunStatusBadge_DagRunFragment
    | PipelineRunStatusBadge_RunFragment;
  polling?: boolean;
};

const PipelineRunStatusBadge = (props: PipelineRunStatusBadgeProps) => {
  const { run, polling = true } = props;
  usePipelineRunPoller(polling ? (run as any).id : null);
  let className = useMemo(() => {
    switch (run.status) {
      case DagRunStatus.Failed:
        return "bg-red-100 text-red-500";
      case DagRunStatus.Queued:
        return "bg-gray-100 text-gray-600";
      case DagRunStatus.Running:
        return "bg-sky-100 text-sky-600";
      case DagRunStatus.Success:
        return "bg-emerald-50 text-emerald-500";
    }
  }, [run.status]);
  return (
    <Badge className={clsx(className, "flex items-center")}>
      {run.status === DagRunStatus.Running && (
        <Spinner className="mr-1" size="xs" />
      )}
      {formatDAGRunStatus(run.status)}
    </Badge>
  );
};

PipelineRunStatusBadge.fragments = {
  dagRun: gql`
    fragment PipelineRunStatusBadge_dagRun on DAGRun {
      status
    }
  `,
  pipelineRun: gql`
    fragment PipelineRunStatusBadge_run on PipelineRun {
      id
      status
    }
  `,
};

export default PipelineRunStatusBadge;
