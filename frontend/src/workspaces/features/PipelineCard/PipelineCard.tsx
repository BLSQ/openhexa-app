import { gql } from "@apollo/client";
import Card from "core/components/Card";
import Tooltip from "core/components/Tooltip";
import Badge from "core/components/Badge";
import { stripMarkdown } from "core/helpers";
import UserAvatar from "identity/features/UserAvatar";
import { DateTime } from "luxon";
import { useTranslation } from "next-i18next";
import PipelineRunStatusBadge from "pipelines/features/PipelineRunStatusBadge";
import { formatPipelineType } from "workspaces/helpers/pipelines";
import Tag from "core/features/Tag";
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
      title={pipeline.name}
      subtitle={
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Badge className="bg-gray-50 ring-gray-500/20">
              {formatPipelineType(pipeline.type)}
            </Badge>
            <span className="text-sm text-gray-500">•</span>
            <span className="text-sm text-gray-600 font-mono">{pipeline.code}</span>
          </div>
          {pipeline.currentVersion?.versionName && (
            <span className="text-sm text-gray-500">
              v{pipeline.currentVersion.versionName}
            </span>
          )}
        </div>
      }
    >
      <Card.Content className="flex flex-col h-full" title={pipeline.description ?? ""}>
        <div className="space-y-4 flex-1">
          {pipeline.description && (
            <div className="line-clamp-3 text-gray-700">
              {stripMarkdown(pipeline.description)}
            </div>
          )}

          <div className="min-h-[24px]">
            {pipeline.tags && pipeline.tags.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {pipeline.tags.map((tag) => (
                  <Tag key={tag.id} tag={tag} className="text-xs" />
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">{t("Last run")}:</span>
            {pipeline.lastRuns.items[0] ? (
              <PipelineRunStatusBadge run={pipeline.lastRuns.items[0]} />
            ) : (
              <span className="text-sm text-gray-400">{t("Not yet run")}</span>
            )}
          </div>

          {pipeline.currentVersion?.user && (
            <Tooltip
              label={t("Last version uploaded on {{date}} by {{name}}", {
                date: DateTime.fromISO(
                  pipeline.currentVersion.createdAt,
                ).toLocaleString(DateTime.DATE_FULL),
                name: pipeline.currentVersion.user.displayName,
              })}
            >
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-500">
                  {DateTime.fromISO(pipeline.currentVersion.createdAt).toRelative()}
                </span>
                <UserAvatar user={pipeline.currentVersion.user} size="sm" />
              </div>
            </Tooltip>
          )}
        </div>
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
      tags {
        ...Tag_tag
      }
      currentVersion {
        user {
          ...User_user
        }
        versionName
        createdAt
      }
      lastRuns: runs(orderBy: EXECUTION_DATE_DESC, page: 1, perPage: 1) {
        items {
          ...PipelineRunStatusBadge_run
        }
      }
    }
    ${PipelineRunStatusBadge.fragments.pipelineRun}
    ${Tag.fragments.tag}
  `,
  workspace: gql`
    fragment PipelineCard_workspace on Workspace {
      slug
    }
  `,
};

export default PipelineCard;
