import {
  ExclamationCircleIcon,
  PlayIcon,
  TrashIcon,
} from "@heroicons/react/24/outline";
import Badge from "core/components/Badge";
import Block from "core/components/Block/Block";
import Breadcrumbs from "core/components/Breadcrumbs";
import Button from "core/components/Button";
import Clipboard from "core/components/Clipboard";
import DataCard from "core/components/DataCard";
import RenderProperty from "core/components/DataCard/RenderProperty";
import SwitchProperty from "core/components/DataCard/SwitchProperty";
import TextProperty from "core/components/DataCard/TextProperty";
import { BaseColumn } from "core/components/DataGrid";
import ChevronLinkColumn from "core/components/DataGrid/ChevronLinkColumn";
import DataGrid from "core/components/DataGrid/DataGrid";
import { TextColumn } from "core/components/DataGrid/TextColumn";
import UserColumn from "core/components/DataGrid/UserColumn";
import DescriptionList from "core/components/DescriptionList/DescriptionList";
import Link from "core/components/Link";
import Page from "core/components/Page";
import Spinner from "core/components/Spinner";
import Time from "core/components/Time/Time";
import Title from "core/components/Title";
import { createGetServerSideProps } from "core/helpers/page";
import { formatDuration } from "core/helpers/time";
import { NextPageWithLayout } from "core/helpers/types";
import {
  PipelineRecipient,
  PipelineRunTrigger,
  PipelineType,
} from "graphql/types";
import useFeature from "identity/hooks/useFeature";
import { useTranslation } from "next-i18next";
import { useRouter } from "next/router";
import DownloadPipelineVersion from "pipelines/features/DownloadPipelineVersion/DownloadPipelineVersion";
import PipelineRunStatusBadge from "pipelines/features/PipelineRunStatusBadge";
import { useState } from "react";
import CronProperty from "workspaces/features/CronProperty";
import DeletePipelineDialog from "workspaces/features/DeletePipelineDialog";
import RunPipelineDialog from "workspaces/features/RunPipelineDialog";
import WorkspaceMemberProperty from "workspaces/features/WorkspaceMemberProperty/";
import {
  WorkspacePipelinePageDocument,
  WorkspacePipelinePageQuery,
  WorkspacePipelinePageQueryVariables,
  useWorkspacePipelinePageQuery,
} from "workspaces/graphql/queries.generated";
import {
  formatPipelineType,
  updatePipeline,
} from "workspaces/helpers/pipelines";
import WorkspaceLayout from "workspaces/layouts/WorkspaceLayout";

type Props = {
  page: number;
  perPage: number;
  pipelineCode: string;
  workspaceSlug: string;
};

const WorkspacePipelinePage: NextPageWithLayout = (props: Props) => {
  const { pipelineCode, workspaceSlug, page, perPage } = props;
  const { t } = useTranslation();
  const router = useRouter();
  const [isDeletePipelineDialogOpen, setDeletePipelineDialogOpen] =
    useState(false);
  const [isWebhookFeatureEnabled] = useFeature("pipeline_webhook");
  const { data } = useWorkspacePipelinePageQuery({
    variables: {
      workspaceSlug,
      pipelineCode,
      page,
      perPage,
    },
  });
  if (!data?.workspace || !data?.pipeline) {
    return null;
  }
  const { workspace, pipeline } = data;

  const onSavePipeline = async (values: any) => {
    await updatePipeline(pipeline.id, {
      name: values.name,
      description: values.description,
    });
  };

  const onSaveScheduling = async (values: any) => {
    await updatePipeline(pipeline.id, {
      schedule: values.enableScheduling ? values.schedule : null,
      recipientIds:
        values.recipients?.map((r: PipelineRecipient) => r.user.id) ?? [],
    });
  };

  const onSaveWebhook = async (values: any) => {
    await updatePipeline(pipeline.id, {
      webhookEnabled: values.webhookEnabled,
    });
  };

  return (
    <Page title={pipeline.name ?? t("Pipeline run")}>
      <WorkspaceLayout
        workspace={workspace}
        helpLinks={[
          {
            label: t("About pipelines"),
            href: "https://github.com/BLSQ/openhexa/wiki/User-manual#using-pipelines",
          },
          {
            label: t("Writing OpenHEXA pipelines"),
            href: "https://github.com/BLSQ/openhexa/wiki/Writing-OpenHEXA-pipelines",
          },
        ]}
      >
        <WorkspaceLayout.Header>
          <div className="flex items-center justify-between">
            <Breadcrumbs withHome={false}>
              <Breadcrumbs.Part
                isFirst
                href={`/workspaces/${encodeURIComponent(workspace.slug)}`}
              >
                {workspace.name}
              </Breadcrumbs.Part>
              <Breadcrumbs.Part
                href={`/workspaces/${encodeURIComponent(
                  workspace.slug,
                )}/pipelines`}
              >
                {t("Pipelines")}
              </Breadcrumbs.Part>
              <Breadcrumbs.Part
                isLast
                href={`/workspaces/${encodeURIComponent(
                  workspace.slug,
                )}/pipelines/${encodeURIComponent(pipeline.code)}`}
              >
                {pipeline.name}
              </Breadcrumbs.Part>
            </Breadcrumbs>
            <div className="flex items-center gap-2">
              {pipeline.currentVersion && (
                <DownloadPipelineVersion version={pipeline.currentVersion}>
                  {({ onClick, isDownloading }) => (
                    <Button onClick={onClick} variant="secondary">
                      {isDownloading && <Spinner size="sm" />}
                      {t("Download code")}
                    </Button>
                  )}
                </DownloadPipelineVersion>
              )}
              {pipeline.permissions.run && (
                <RunPipelineDialog pipeline={pipeline}>
                  {(onClick) => (
                    <Button
                      leadingIcon={<PlayIcon className="w-4" />}
                      onClick={onClick}
                    >
                      {t("Run")}
                    </Button>
                  )}
                </RunPipelineDialog>
              )}
              {pipeline.permissions.delete && (
                <Button
                  onClick={() => setDeletePipelineDialogOpen(true)}
                  className="bg-red-700 hover:bg-red-700 focus:ring-red-500"
                  leadingIcon={<TrashIcon className="w-4" />}
                >
                  {t("Delete")}
                </Button>
              )}
            </div>
          </div>
        </WorkspaceLayout.Header>

        <WorkspaceLayout.PageContent className="space-y-6">
          <DataCard item={pipeline} className="divide-y-2 divide-gray-100">
            <DataCard.FormSection
              title={t("Information")}
              onSave={pipeline.permissions.update ? onSavePipeline : undefined}
              collapsible={false}
            >
              <TextProperty
                id="name"
                accessor={"name"}
                label={t("Name")}
                visible={(value, isEditing) => isEditing}
              />
              <TextProperty
                id="code"
                accessor={"code"}
                label={t("Code")}
                help={t(
                  "This is the code used to identify this pipeline using the cli.",
                )}
                readonly
              />
              <RenderProperty id="type" label={t("Type")} accessor="type">
                {(property) => (
                  <Badge className="bg-gray-50">
                    {formatPipelineType(property.displayValue)}
                  </Badge>
                )}
              </RenderProperty>
              <TextProperty
                id="description"
                accessor={"description"}
                label={t("Description")}
                defaultValue="-"
                visible={(value, isEditing) => isEditing || value}
                hideLabel
                markdown
              />
              {pipeline.type === PipelineType.Notebook && (
                <>
                  <RenderProperty
                    id="notebookPath"
                    accessor={"notebookPath"}
                    label={t("Notebook path")}
                    readonly
                  >
                    {(property) => (
                      <div className="flex items-center gap-1.5 text-xs">
                        <Clipboard value={property.displayValue}>
                          <Link
                            customStyle="hover:opacity-80"
                            href={`/workspaces/${encodeURIComponent(
                              workspace.slug,
                            )}/files/${property.displayValue.split("/").slice(0, -1).join("/")}`}
                          >
                            <code>{property.displayValue}</code>
                          </Link>
                        </Clipboard>
                      </div>
                    )}
                  </RenderProperty>
                </>
              )}
            </DataCard.FormSection>
            {pipeline.type === PipelineType.ZipFile && (
              <DataCard.Section
                collapsible={false}
                title={() => (
                  <div className="flex flex-1 gap-2 items-center">
                    <h4 className="font-medium">{t("Version")}</h4>
                    <div className="flex-1"></div>
                    <Link
                      className="text-sm"
                      href={{
                        pathname:
                          "/workspaces/[workspaceSlug]/pipelines/[pipelineCode]/versions",
                        query: {
                          workspaceSlug: workspace.slug,
                          pipelineCode: pipeline.code,
                        },
                      }}
                    >
                      {t("View all versions")}
                    </Link>
                  </div>
                )}
              >
                {pipeline.currentVersion ? (
                  <>
                    <DescriptionList>
                      <DescriptionList.Item label={t("Name")}>
                        {pipeline.currentVersion.name}
                      </DescriptionList.Item>
                      {pipeline.currentVersion.description && (
                        <DescriptionList.Item
                          label={t("Description")}
                          fullWidth
                        >
                          {pipeline.currentVersion.description}
                        </DescriptionList.Item>
                      )}
                      {pipeline.currentVersion.externalLink && (
                        <DescriptionList.Item label={t("External link")}>
                          <Link
                            href={pipeline.currentVersion.externalLink}
                            target={"_blank"}
                          >
                            {pipeline.currentVersion.externalLink}
                          </Link>
                        </DescriptionList.Item>
                      )}
                      <DescriptionList.Item label={t("Created at")}>
                        <Time datetime={pipeline.currentVersion.createdAt} />
                      </DescriptionList.Item>
                      <DescriptionList.Item label={t("Created by")}>
                        {pipeline.currentVersion.user?.displayName ?? "-"}
                      </DescriptionList.Item>
                    </DescriptionList>
                  </>
                ) : (
                  <span className="italic text-sm text-gray-500">
                    {t("This pipeline has no versions yet")}
                  </span>
                )}
              </DataCard.Section>
            )}
            <DataCard.FormSection
              title={t("Scheduling")}
              onSave={
                pipeline.permissions.update && pipeline.permissions.schedule
                  ? onSaveScheduling
                  : undefined
              }
              collapsible={false}
            >
              {pipeline.permissions.schedule ? (
                <>
                  <SwitchProperty
                    id="enableScheduling"
                    label={t("Enabled")}
                    accessor={(item) => Boolean(item.schedule)}
                  />
                  <CronProperty
                    id="schedule"
                    accessor="schedule"
                    label={t("Schedule")}
                    help={t(
                      "The schedule value should follow the CRON syntax.",
                    )}
                    placeholder="0 15 * * *"
                    visible={(_, __, values) =>
                      Boolean(values.enableScheduling || pipeline.schedule)
                    }
                    required={(_, __, values) =>
                      Boolean(values.enableScheduling)
                    }
                  />
                  <WorkspaceMemberProperty
                    id="recipients"
                    label={t("Notification Recipients")}
                    accessor={(pipeline) => pipeline.recipients}
                    slug={workspace.slug}
                    multiple
                    defaultValue="-"
                    visible={(_, __, values) =>
                      Boolean(values.enableScheduling || pipeline.schedule)
                    }
                  />
                </>
              ) : (
                <p className="text-sm font-medium italic text-gray-500">
                  {t(
                    "Pipeline with parameters can be scheduled only if all parameters are optional or have default values.",
                  )}
                </p>
              )}
            </DataCard.FormSection>
            {isWebhookFeatureEnabled ? (
              <DataCard.FormSection
                title={t("Webhook")}
                onSave={onSaveWebhook}
                collapsible={false}
              >
                <div className="text-gray-700">
                  <p className="text-sm">
                    {t(
                      "You can use a webhook to trigger this pipeline from an external system using a POST request.",
                    )}
                  </p>
                  <div className="mt-2 flex  items-center text-sm">
                    <ExclamationCircleIcon className="inline-block w-6 h-6 text-yellow-500 mr-1.5" />
                    {t(
                      "Webhooks are experimental and don't require any form of authentication for now: anyone with the URL will be able to trigger this pipeline",
                    )}
                  </div>
                </div>
                <SwitchProperty
                  id="webhookEnabled"
                  label={t("Enabled")}
                  accessor={"webhookEnabled"}
                />
                <RenderProperty
                  visible={(_, isEdited) =>
                    !isEdited && Boolean(pipeline.webhookUrl)
                  }
                  readonly
                  id="webhookUrl"
                  label={t("URL")}
                  accessor="webhookUrl"
                >
                  {(property) => (
                    <div className="flex gap-1.5">
                      <Clipboard value={property.displayValue}>
                        {property.displayValue}
                      </Clipboard>
                    </div>
                  )}
                </RenderProperty>
              </DataCard.FormSection>
            ) : null}
          </DataCard>

          <div>
            <Title level={4} className="font-medium">
              {t("Runs")}
            </Title>
            <Block>
              <DataGrid
                defaultPageSize={perPage}
                data={pipeline.runs.items}
                totalItems={pipeline.runs.totalItems}
                fixedLayout={false}
                fetchData={({ page, pageSize }) => {
                  router.push({
                    pathname: router.pathname,
                    query: {
                      ...router.query,
                      page,
                      perPage: pageSize,
                    },
                  });
                }}
              >
                <BaseColumn id="name" label={t("Executed on")}>
                  {(item) => (
                    <Link
                      customStyle="text-gray-700 font-medium"
                      href={{
                        pathname:
                          "/workspaces/[workspaceSlug]/pipelines/[pipelineCode]/runs/[runId]",
                        query: {
                          pipelineCode: pipeline.code,
                          workspaceSlug: workspace.slug,
                          runId: item.id,
                        },
                      }}
                    >
                      <Time datetime={item.executionDate} />
                    </Link>
                  )}
                </BaseColumn>
                <BaseColumn<PipelineRunTrigger>
                  label={t("Trigger")}
                  accessor="triggerMode"
                >
                  {(value) => (
                    <span>
                      {value === PipelineRunTrigger.Scheduled && t("Scheduled")}
                      {value === PipelineRunTrigger.Manual && t("Manual")}
                      {value === PipelineRunTrigger.Webhook && t("Webhook")}
                    </span>
                  )}
                </BaseColumn>
                <BaseColumn label={t("Status")} id="status">
                  {(item) => <PipelineRunStatusBadge run={item} />}
                </BaseColumn>
                <TextColumn accessor="version.number" label={t("Version")} />
                <BaseColumn label={t("Duration")} accessor="duration">
                  {(value) => (
                    <span suppressHydrationWarning>
                      {value ? formatDuration(value) : "-"}
                    </span>
                  )}
                </BaseColumn>
                <UserColumn label={t("User")} accessor="user" />
                <ChevronLinkColumn
                  accessor="id"
                  url={(value: any) => ({
                    pathname:
                      "/workspaces/[workspaceSlug]/pipelines/[pipelineCode]/runs/[runId]",
                    query: {
                      workspaceSlug: workspace.slug,
                      pipelineCode: pipeline.code,
                      runId: value,
                    },
                  })}
                />
              </DataGrid>
            </Block>
          </div>
        </WorkspaceLayout.PageContent>
      </WorkspaceLayout>
      <DeletePipelineDialog
        open={isDeletePipelineDialogOpen}
        onClose={() => setDeletePipelineDialogOpen(false)}
        pipeline={pipeline}
        workspace={workspace}
      />
    </Page>
  );
};

WorkspacePipelinePage.getLayout = (page) => page;

export const getServerSideProps = createGetServerSideProps({
  requireAuth: true,
  async getServerSideProps(ctx, client) {
    await WorkspaceLayout.prefetch(ctx, client);
    const page = parseInt(ctx.query.page as string, 10) || 1;
    const perPage = parseInt(ctx.query.perPage as string, 10) || 5;
    const { data } = await client.query<
      WorkspacePipelinePageQuery,
      WorkspacePipelinePageQueryVariables
    >({
      query: WorkspacePipelinePageDocument,
      variables: {
        workspaceSlug: ctx.params!.workspaceSlug as string,
        pipelineCode: ctx.params!.pipelineCode as string,
        page,
        perPage,
      },
    });

    if (!data.workspace || !data.pipeline) {
      return { notFound: true };
    }
    return {
      props: {
        workspaceSlug: ctx.params!.workspaceSlug,
        pipelineCode: ctx.params!.pipelineCode,
        page,
        perPage,
      },
    };
  },
});

export default WorkspacePipelinePage;
