import { gql } from "@apollo/client";
import clsx from "clsx";
import Card from "core/components/Card";
import { useTranslation } from "next-i18next";
import PipelineRunStatusBadge from "pipelines/features/PipelineRunStatusBadge";
import { formatPipelineType } from "workspaces/helpers/pipelines";
import {
  PipelineCard_PipelineFragment,
  PipelineCard_WorkspaceFragment,
} from "./PipelineCard.generated";

interface PipelineCardProps {
  workspace: PipelineCard_WorkspaceFragment;
  pipeline: PipelineCard_PipelineFragment;
}

const PipelineCard = ({ pipeline, workspace }: PipelineCardProps) => {
  const { t } = useTranslation();
  return (
    <Card
      href={{
        pathname: `/workspaces/[workspaceSlug]/pipelines/[pipelineCode]`,
        query: { workspaceSlug: workspace.slug, pipelineCode: pipeline.code },
      }}
      title={
        <div className="flex justify-between">
          <span className="max-w-[80%]">{pipeline.name}</span>
          <div>
            {pipeline.lastRuns.items[0] && (
              <PipelineRunStatusBadge run={pipeline.lastRuns.items[0]} />
            )}
          </div>
        </div>
      }
      subtitle={
        <div className="flex justify-between">
          {formatPipelineType(pipeline.type)}
        </div>
      }
    >
      <Card.Content
        className={clsx(
          "line-clamp-3",
          !pipeline.description && "italic text-gray-300",
        )}
        title={pipeline.description ?? ""}
      >
        {pipeline.description || t("No description")}
      </Card.Content>
    </Card>
  );
};

PipelineCard.fragments = {
  pipeline: gql`
    fragment PipelineCard_pipeline on Pipeline {
      id
      code
      name
      schedule
      description
      type
      lastRuns: runs(orderBy: EXECUTION_DATE_DESC, page: 1, perPage: 1) {
        items {
          ...PipelineRunStatusBadge_run
        }
      }
    }
    ${PipelineRunStatusBadge.fragments.pipelineRun}
  `,
  workspace: gql`
    fragment PipelineCard_workspace on Workspace {
      slug
    }
  `,
};

export default PipelineCard;
