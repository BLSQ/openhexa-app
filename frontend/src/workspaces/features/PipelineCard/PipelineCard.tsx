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
import Tooltip from "core/components/Tooltip";
import UserAvatar from "identity/features/UserAvatar";
import { DateTime } from "luxon";
import MarkdownViewer from "../../../core/components/MarkdownViewer";
import React from "react";

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
      <Card.Content className="space-y-4" title={pipeline.description ?? ""}>
        <MarkdownViewer
            className={clsx("line-clamp-3", !pipeline.description && "italic")}
            markdown= {pipeline.description || t("No description")}
          />
        {pipeline.currentVersion?.user && (
          <div className="flex justify-end">
            <Tooltip
              label={t("Last version uploaded on {{date}} by {{name}}", {
                date: DateTime.fromISO(
                  pipeline.currentVersion.createdAt,
                ).toLocaleString(DateTime.DATE_FULL),
                name: pipeline.currentVersion.user.displayName,
              })}
            >
              <UserAvatar user={pipeline.currentVersion.user} size="sm" />
            </Tooltip>
          </div>
        )}
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
      currentVersion {
        user {
          ...User_user
        }
        createdAt
      }
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
