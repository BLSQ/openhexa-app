import { gql } from "@apollo/client";
import clsx from "clsx";
import Card from "core/components/Card";
import { useTranslation } from "next-i18next";
import {
  TemplateCard_TemplateFragment,
  TemplateCard_WorkspaceFragment,
} from "./TemplateCard.generated";
import Tooltip from "core/components/Tooltip";
import { DateTime } from "luxon";
import UserAvatar from "identity/features/UserAvatar";
import React from "react";
import Button from "core/components/Button";
import router from "next/router";
import User from "core/features/User";
import { stripMarkdown } from "core/helpers";
import PipelineMetadataDisplay from "pipelines/features/PipelineMetadataDisplay";
import TemplateBadge from "pipelines/features/TemplateBadge";

interface TemplateCardProps {
  workspace: TemplateCard_WorkspaceFragment;
  template: TemplateCard_TemplateFragment;
  onCreate?: () => void;
}

const TemplateCard = ({ template, workspace, onCreate }: TemplateCardProps) => {
  const { t } = useTranslation();
  return (
    <Card
      href={{
        pathname: `/workspaces/[workspaceSlug]/templates/[templateCode]`,
        query: { workspaceSlug: workspace.slug, templateCode: template.code },
      }}
      title={
        <div className="flex justify-between items-start">
          <span className="max-w-[80%]">{template.name}</span>
          <TemplateBadge
            organization={template.organization}
            validatedAt={template.validatedAt}
            size="sm"
          />
        </div>
      }
    >
      <Card.Content
        className="space-y-4 min-h-20 min-w-20"
        title={template.description ?? ""}
      >
        <div className={clsx("line-clamp-3")}>
          {stripMarkdown(template.description ?? "")}
        </div>
        <div className="flex items-center justify-between">
          <PipelineMetadataDisplay metadata={template} size="sm" />
          {template.pipelinesCount !== undefined && (
            <div className="text-xs text-gray-500 flex items-center gap-1">
              <span className="font-medium">{template.pipelinesCount}</span>
              <span>{template.pipelinesCount === 1 ? t("pipeline") : t("pipelines")}</span>
            </div>
          )}
        </div>
        {template.currentVersion?.user && (
          <div className="flex justify-end">
            <Tooltip
              label={t("Last version uploaded on {{date}} by {{name}}", {
                date: DateTime.fromISO(
                  template.currentVersion.createdAt,
                ).toLocaleString(DateTime.DATE_FULL),
                name: template.currentVersion.user.displayName,
              })}
            >
              <UserAvatar user={template.currentVersion.user} size="sm" />
            </Tooltip>
          </div>
        )}
      </Card.Content>
      <Card.Actions>
        <Button
          variant="secondary"
          size="md"
          onClick={(event) => {
            event.preventDefault();
            onCreate?.();
          }}
        >
          {t("Create pipeline")}
        </Button>
        <Button
          variant="secondary"
          size="md"
          onClick={(event) => {
            event.preventDefault();
            router.push(
              `/workspaces/${workspace.slug}/templates/${template.code}`,
            );
          }}
        >
          {t("Details")}
        </Button>
      </Card.Actions>
    </Card>
  );
};

TemplateCard.fragments = {
  template: gql`
    fragment TemplateCard_template on PipelineTemplate {
      id
      code
      name
      description
      publisher
      validatedAt
      pipelinesCount
      organization {
        name
        logo
      }
      ...PipelineMetadataDisplay_template
      currentVersion {
        id
        createdAt
        user {
          ...User_user
        }
      }
    }
    ${User.fragments.user}
    ${PipelineMetadataDisplay.fragments.template}
  `,
  workspace: gql`
    fragment TemplateCard_workspace on Workspace {
      slug
    }
  `,
};

export default TemplateCard;
