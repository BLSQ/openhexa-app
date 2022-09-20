import { gql } from "@apollo/client";
import Badge from "core/components/Badge";
import { DagRunStatus } from "graphql-types";
import { formatDAGRunStatus } from "pipelines/helpers/format";
import { useMemo } from "react";
import { PipelineRunStatusBadge_DagRunFragment } from "./PipelineRunStatusBadge.generated";

type PipelineRunStatusBadgeProps = {
  dagRun: PipelineRunStatusBadge_DagRunFragment;
};

const PipelineRunStatusBadge = (props: PipelineRunStatusBadgeProps) => {
  const { dagRun } = props;
  let className = useMemo(() => {
    switch (dagRun.status) {
      case DagRunStatus.Failed:
        return "bg-red-100 text-red-500";
      case DagRunStatus.Queued:
        return "bg-gray-100 text-gray-600";
      case DagRunStatus.Running:
        return "bg-sky-100 text-sky-600";
      case DagRunStatus.Success:
        return "bg-emerald-50 text-emerald-500";
    }
  }, [dagRun.status]);
  return (
    <Badge className={className}>{formatDAGRunStatus(dagRun.status)}</Badge>
  );
};

PipelineRunStatusBadge.fragments = {
  dagRun: gql`
    fragment PipelineRunStatusBadge_dagRun on DAGRun {
      status
    }
  `,
};

export default PipelineRunStatusBadge;
