import Card from "core/components/Card";
import { Dag, DagRun } from "graphql-types";
import PipelineRunStatusBadge from "pipelines/features/PipelineRunStatusBadge";

interface PipelineCardProps {
  workspaceId: string;
  dag: Pick<Dag, "id" | "label" | "description"> & {
    shortDescription: String;
    triggerInfo: String;
    runs: Array<
      Pick<DagRun, "id" | "triggerMode" | "status" | "executionDate">
    >;
  };
}

const PipelineCard = ({ dag, workspaceId }: PipelineCardProps) => {
  return (
    <Card
      href={{
        pathname: `/workspaces/[workspaceId]/pipelines/[pipelineId]`,
        query: { workspaceId: workspaceId, pipelineId: dag.id },
      }}
      title={
        <div className="flex justify-between">
          {dag.label}
          <PipelineRunStatusBadge dagRun={dag.runs[0]} />
        </div>
      }
      subtitle={<div className="flex justify-between">{dag.triggerInfo}</div>}
    >
      <Card.Content className="line-clamp-3" title={dag.description ?? ""}>
        {dag.shortDescription}
      </Card.Content>
    </Card>
  );
};

export default PipelineCard;
